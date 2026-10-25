"""Verify and unpack the released records without following archive links."""
from pathlib import Path,PurePosixPath
import hashlib
import json
import tarfile

ROOT=Path(__file__).resolve().parents[1]

def main():
    manifest=json.loads((ROOT/'data/records_manifest.json').read_text(encoding='utf-8'))
    seen=set()
    with tarfile.open(ROOT/'data/experiment_records.tar.xz','r:xz') as archive:
        for member in archive:
            rel=PurePosixPath(member.name)
            assert member.isfile() and member.name in manifest['files'],member.name
            assert not rel.is_absolute() and '..' not in rel.parts and ':' not in member.name,member.name
            assert rel.parts[0]=='experiments' or rel.parts[:2]==('data','runtime'),member.name
            target=ROOT.joinpath(*rel.parts)
            assert target.resolve().is_relative_to(ROOT.resolve()),member.name
            data=archive.extractfile(member).read()
            expected=manifest['files'][member.name]
            assert len(data)==expected['bytes'] and hashlib.sha256(data).hexdigest()==expected['sha256'],member.name
            target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data); seen.add(member.name)
    assert seen==set(manifest['files'])
    print('Verified and extracted',len(seen),'record files')

if __name__=='__main__': main()
