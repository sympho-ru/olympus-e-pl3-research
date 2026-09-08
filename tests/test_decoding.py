from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from epl3_research import decoding
from epl3_research.decoding import Instruction, parse_disassembly, require_verified, verify_instructions
from epl3_research.evidence import load_instruction_rows
from epl3_research.source import verify_source


def row(source, offset, length, text, address=None):
    return (offset + 0x1000 if address is None else address, text, 0, offset, length,
            source.slice_sha256(0, offset, length))


@pytest.fixture
def decoder(monkeypatch, synthetic_source):
    class FakeDecoder:
        version = 'fixture'
        tool_sha256 = 'fixture'
        def __init__(self, source, executable=None):
            self.source = source
        def window(self, block, offset, address, length):
            # A six-byte instruction at 8, plus a separately decodable interior
            # alternate at 12. Starts on other bytes are one-byte instructions.
            result = []
            end = offset + length
            cursor = offset
            while cursor < end:
                width = 6 if cursor == 8 else 1
                if cursor + width > end:
                    break
                result.append(Instruction(address + cursor - offset,
                    self.source.blocks[block][cursor:cursor + width],
                    'mov d0,a0' if cursor == 8 else 'nop'))
                cursor += width
            return result
    monkeypatch.setattr(decoding, 'Decoder', FakeDecoder)


def test_wrapped_output_is_one_complete_instruction():
    output = '1000:\taa bb cc dd \tcall\t0x1020,[],0\n1004:\tee ff 11\n1007:\t22\tnop\n'
    items = parse_disassembly(output)
    assert len(items) == 2
    assert len(items[0].data) == 7
    assert items[1].address == 0x1007


def test_orphan_continuation_is_rejected():
    with pytest.raises(ValueError, match='orphan'):
        parse_disassembly('1004:\taa bb\n')


def test_truncated_lookahead_is_not_a_record():
    assert len(parse_disassembly('1000:\t01\tnop\n1001:\tAddress 0x1001 is out of bounds.\n')) == 1


def test_lookahead_exposes_truncated_row(decoder, synthetic_source):
    old = row(synthetic_source, 8, 4, 'mov d0,a0')
    report = verify_instructions(synthetic_source, (old,))
    assert report['results'][0]['reasons'] == ['length_mismatch']
    assert report['results'][0]['observed_length'] == 6
    with pytest.raises(ValueError, match='decode verification failed'):
        require_verified(report)


def test_fragment_beyond_stale_endpoint_is_found(decoder, synthetic_source):
    stale = row(synthetic_source, 8, 4, 'mov d0,a0')
    interior = row(synthetic_source, 12, 1, 'nop')
    report = verify_instructions(synthetic_source, (interior,), (stale,))
    assert len(report['overlaps']) == 1
    assert any(r['role'] == 'overlapping_canonical' and r['status'] == 'fail' for r in report['results'])


def test_valid_alternate_requires_exact_adjudication(decoder, synthetic_source, tmp_path):
    full = row(synthetic_source, 8, 6, 'mov d0,a0')
    alternate = row(synthetic_source, 12, 1, 'nop')
    report = verify_instructions(synthetic_source, (alternate,), (full,))
    assert all(r['status'] == 'pass' for r in report['results'])
    assert report['boundary_status'] == 'decode_only_start_anchors_not_proven'
    with pytest.raises(ValueError, match='explicit adjudication'):
        require_verified(report)
    path = tmp_path / 'review.json'
    entry = {'rows': report['overlaps'][0]['rows'], 'reason': 'Retain alternate hypothesis; no path claim.'}
    path.write_text(json.dumps({'overlaps': [entry]}))
    require_verified(report, path)
    with pytest.raises(ValueError, match='stale'):
        require_verified(verify_instructions(synthetic_source, (full,)), path)


def test_changed_length_cannot_be_waived(decoder, synthetic_source, tmp_path):
    old = row(synthetic_source, 8, 4, 'mov d0,a0')
    full = row(synthetic_source, 8, 6, 'mov d0,a0')
    report = verify_instructions(synthetic_source, (full,), (old,))
    path = tmp_path / 'review.json'
    path.write_text(json.dumps({'overlaps': [dict(rows=report['overlaps'][0]['rows'], reason='waive')]}))
    with pytest.raises(ValueError, match='decode verification failed'):
        require_verified(report, path)


def test_zero_byte_decode_is_not_suppressed():
    assert parse_disassembly('1000:\t00\tclr\td0\n')[0].data == bytes(1)


def test_digest_and_text_are_both_checked(decoder, synthetic_source):
    bad = (*row(synthetic_source, 8, 6, 'wrong')[:5], '0' * 64)
    result = verify_instructions(synthetic_source, (bad,))['results'][0]
    assert result['reasons'] == ['source_digest_mismatch', 'text_mismatch']


def test_missing_tool_fails_closed(synthetic_source):
    with pytest.raises(ValueError, match='missing'):
        verify_instructions(synthetic_source, (row(synthetic_source, 8, 1, 'nop'),), executable='no-such-mn103-tool')


@pytest.mark.skipif(not os.environ.get('OLYMPUS_IMAGE') or not os.environ.get('MN103_OBJDUMP'),
                    reason='real-source regression requires local official image and MN103 objdump')
def test_real_repaired_incidents():
    source = verify_source(Path(os.environ['OLYMPUS_IMAGE']))
    directory = Path(__file__).parent / 'fixtures' / 'decode-regressions'
    old = load_instruction_rows(directory / 'old.jsonl', source.registry, source)
    fixed = load_instruction_rows(directory / 'fixed.jsonl', source.registry, source)
    bad = verify_instructions(source, old)
    intersecting = {r for pair in bad['overlaps'] for r in pair['rows']}
    assert all(item['status'] == 'fail' or item['row_id'] in intersecting for item in bad['results'])
    with pytest.raises(ValueError):
        require_verified(bad)
    good = verify_instructions(source, fixed)
    assert all(item['status'] == 'pass' for item in good['results'])


def test_acceptance_checks_before_mutating_files(decoder, synthetic_source, tmp_path):
    from epl3_research.contributions import accept_contribution
    from epl3_research.evidence import instruction_object, write_jsonl
    from epl3_research.source import sha256_bytes
    evidence = tmp_path / 'evidence'
    evidence.mkdir()
    write_jsonl(evidence / 'ranges.jsonl', [dict(block=0, offset=0, length=1,
        sha256=synthetic_source.slice_sha256(0, 0, 1))])
    write_jsonl(evidence / 'instructions.jsonl', [instruction_object(row(synthetic_source, 0, 1, 'nop'))])
    incoming = tmp_path / 'incoming'
    incoming.mkdir()
    candidate = incoming / 'temporary'
    write_jsonl(candidate, [instruction_object(row(synthetic_source, 8, 4, 'mov d0,a0'))])
    target = incoming / ('instructions-' + sha256_bytes(candidate.read_bytes()) + '.jsonl')
    candidate.rename(target)
    before = (evidence / 'instructions.jsonl').read_bytes()
    with pytest.raises(ValueError, match='decode verification failed'):
        accept_contribution(tmp_path, synthetic_source, [target])
    assert target.is_file()
    assert (evidence / 'instructions.jsonl').read_bytes() == before
    target.unlink()
    write_jsonl(candidate, [instruction_object(row(synthetic_source, 8, 6, 'mov d0,a0'))])
    target = incoming / ('instructions-' + sha256_bytes(candidate.read_bytes()) + '.jsonl')
    candidate.rename(target)
    assert accept_contribution(tmp_path, synthetic_source, [target]).new_instructions == 1
    assert not target.exists()


def test_block_end_cannot_supply_a_complete_instruction(decoder, synthetic_source, monkeypatch):
    monkeypatch.setattr(decoding.Decoder, 'window', lambda *a: [])
    report = verify_instructions(synthetic_source, (row(synthetic_source, len(synthetic_source.blocks[0])-1, 1, 'mov d0,a0'),))
    assert report['results'][0]['reasons'] == ['not_an_instruction']


def test_check_contribution_enforces_decoder(decoder, synthetic_source, tmp_path):
    from epl3_research.contributions import check_contribution
    from epl3_research.evidence import instruction_object
    from test_contributions import init_repository, write_incoming, git
    base = init_repository(tmp_path, synthetic_source)
    write_incoming(tmp_path, 'instructions', [instruction_object(row(synthetic_source, 8, 4, 'mov d0,a0'))])
    git(tmp_path, 'add', 'incoming')
    git(tmp_path, 'commit', '-q', '-m', 'bad width')
    with pytest.raises(ValueError, match='decode verification failed'):
        check_contribution(tmp_path, base, synthetic_source)


def test_decoder_rejects_wrong_bytes(synthetic_source):
    instance = decoding.Decoder.__new__(decoding.Decoder)
    instance.source = synthetic_source
    instance._run = lambda *a: '1000:\t00\tnop\n'
    with pytest.raises(ValueError, match='source bytes'):
        instance.window(0, 0, 0x1000, 1)


def test_decoder_rejects_wrong_tool_version(synthetic_source, monkeypatch):
    monkeypatch.setattr(decoding.shutil, 'which', lambda p: 'fixture')
    monkeypatch.setattr(decoding.Decoder, '_run', lambda *a: 'GNU objdump (GNU Binutils) 2.44\n')
    with pytest.raises(ValueError, match='2.45'):
        decoding.Decoder(synthetic_source)
