"""Run every shipped CPU checker and fail if any checker fails."""
from pathlib import Path
import json
import os
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]

def main():
    failed=[]
    environment=dict(os.environ,PYTHONUTF8='1',PYTHONDONTWRITEBYTECODE='1')
    modules=sorted((ROOT/'lib').glob('*_check.py'))
    for path in modules:
        module='lib.'+path.stem
        run=subprocess.run([sys.executable,'-m',module],cwd=ROOT,env=environment,capture_output=True,text=True,encoding='utf-8')
        if run.returncode or 'FAIL' in run.stdout:
            failed.append(module); print(run.stdout,run.stderr)
        print(module,'FAIL' if module in failed else 'PASS',flush=True)
    print(f'{len(modules)-len(failed)}/{len(modules)} checkers passed')
    if failed: raise SystemExit(1)

if __name__=='__main__': main()
