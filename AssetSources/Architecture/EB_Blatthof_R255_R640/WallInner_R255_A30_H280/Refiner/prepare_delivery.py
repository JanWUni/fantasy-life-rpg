"""Read the designated Git revision; write only to this Refiner directory."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[4]
COMMIT = 'e66d5beed7bb85313501659d646f25778515134b'
PREFIX = 'AssetSources/Architecture/EB_Blatthof_R255_R640/WallInner_R255_A30_H280/Creator/'

def git(*args):
    return subprocess.check_output(['git', '--no-optional-locks', *args], cwd=REPO)

def digest(data):
    return hashlib.sha256(data).hexdigest()

def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')

def blob(name):
    data = git('show', COMMIT + ':' + PREFIX + name)
    if data.startswith(b'version https://git-lfs.github.com/spec/v1\n'):
        fields = dict(line.split(' ', 1) for line in data.decode().splitlines()[1:])
        oid = fields['oid'].split(':')[1]
        common = Path(git('rev-parse', '--path-format=absolute', '--git-common-dir').decode().strip())
        data = (common / 'lfs' / 'objects' / oid[:2] / oid[2:4] / oid).read_bytes()
        assert digest(data) == oid and len(data) == int(fields['size'])
    return data

def main():
    assert Path(git('rev-parse', '--show-toplevel').decode().strip()).resolve() == REPO
    assert git('branch', '--show-current').decode().strip() == 'assets/refiner'
    assert git('rev-parse', COMMIT).decode().strip() == COMMIT
    evidence = ROOT / 'Evidence'
    evidence.mkdir(exist_ok=True)
    assert not (evidence / 'input_verification.json').exists(), 'Do not overwrite a prior intake.'
    baseline = {p: digest((REPO / p).read_bytes()) for p in git('ls-files', '-z').decode().split('\0') if p and (REPO / p).is_file()}
    write_json(evidence / 'preservation_before.json', {'head': git('rev-parse', 'HEAD').decode().strip(), 'files': baseline})
    sums = blob('SHA256SUMS')
    expected = dict((line.split('  ', 1)[1], line.split('  ', 1)[0]) for line in sums.decode().splitlines() if line)
    payloads = {name: blob(name) for name in expected}
    assert all(digest(data) == expected[name] for name, data in payloads.items())
    payloads['SHA256SUMS'] = sums
    manifest = json.loads(payloads['manifest.json'])
    verification = json.loads(payloads['verification.json'])
    assert manifest['asset_name'] == 'SM_EB_WallInner_R255_A30_H280'
    assert manifest['interface_version'] == 1 and manifest['status'] == 'creator_ready'
    for name, value in manifest['sha256'].items():
        assert digest(payloads[name]) == value == verification['hashes_verified'][name]
    assert digest(payloads['verification.json']) == manifest['verification']['sha256']
    for name, data in payloads.items():
        target = (evidence / 'Input' / name).resolve()
        assert target.is_relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        assert not target.exists()
        target.write_bytes(data)
    own_source = ROOT / manifest['sources']['blend']
    assert not own_source.exists()
    own_source.write_bytes(payloads[manifest['sources']['blend']])
    write_json(evidence / 'input_verification.json', {
        'commit': COMMIT, 'creator_path': PREFIX, 'creator_base_commit': manifest['base_commit'],
        'creator_revision': manifest['revision'], 'all_sha256sums_passed': True,
        'manifest_and_verification_hashes_passed': True,
        'files': {name: digest(data) for name, data in payloads.items()},
        'copy_sha256': digest(own_source.read_bytes()),
        'method': 'git show exact commit; LFS payload resolved read-only from local object store; no checkout/cherry-pick',
        'refiner_head': git('rev-parse', 'HEAD').decode().strip()})
    print('INTAKE_OK', COMMIT, len(expected), 'verified files; independent source copied')

if __name__ == '__main__':
    main()
