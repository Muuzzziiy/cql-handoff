"""Preserve shipped results before replaying a round's frozen inputs."""
import argparse
import datetime
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
KEEP={'INPUTS.json','CONFIG.json','FRESH_INPUTS.json','REFERENCE_ROWS.jsonl','DESIGN.md','RESULTS.md'}

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('round'); args=parser.parse_args()
    manifest=json.loads((ROOT/'PUBLIC_SCOPE.json').read_text(encoding='utf-8'))
    if args.round not in manifest['rounds']: parser.error('choose a round listed in PUBLIC_SCOPE.json')
    directory=ROOT/'experiments'/args.round
    assert directory.resolve().parent==(ROOT/'experiments').resolve()
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    destination=directory/'shipped_results'/stamp; destination.mkdir(parents=True)
    count=0
    for path in directory.iterdir():
        if path.is_file() and path.name not in KEEP:
            path.rename(destination/path.name); count+=1
    print('Preserved',count,'files in',destination)

if __name__=='__main__': main()
