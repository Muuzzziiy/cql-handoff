"""Fetch and verify the official natural QA files used by the preprint."""
from pathlib import Path
import hashlib
import shutil
import tempfile
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[1]
DST=ROOT/'data/sources'

def sha256(path):
    h=hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda:source.read(8*1024*1024),b''): h.update(block)
    return h.hexdigest()

def main():
    import gdown
    DST.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='preprint-qa-') as directory:
        temporary=Path(directory)
        for name,url,expected,member,output in (
            ('2wiki.zip','https://www.dropbox.com/s/ms2m13252h6xubs/data_ids_april7.zip?dl=1',
             '95df2bf56fdabe034e27aebc580e02264232203cf52552f9efe8a919e5529eef','dev.json','2wiki_dev.json'),
            ('musique.zip','1tGdADlNjWFaHLeZZGShh2IRcpO6Lv24h',
             '98f839bf2fd5319f5c688aed77901a6d5c30b3b9f9f691ab9a8ecafb045ee0cd','data/musique_ans_v1.0_train.jsonl','musique_ans_v1.0_train.jsonl')):
            archive=temporary/name
            print('Downloading',name,flush=True)
            if name=='2wiki.zip': urllib.request.urlretrieve(url,archive)
            else: gdown.download(id=url,output=str(archive),quiet=False)
            assert sha256(archive)==expected,('archive checksum mismatch',name)
            target=temporary/output
            with zipfile.ZipFile(archive) as z, z.open(member) as source, target.open('wb') as destination:
                shutil.copyfileobj(source,destination)
            if name=='musique.zip': assert sha256(target)=='83a75b1e11e4e9bb8f8308e72ac40ca617ae4431b3a0d955b61cab259248490a'
            target.replace(DST/output)
    print('Natural QA files verified in',DST)

if __name__=='__main__': main()
