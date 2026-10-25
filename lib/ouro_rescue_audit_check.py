"""Independent CPU verification of the public contrasts."""
from .independent import ROOT,audit
OUT=ROOT/'experiments/2026-10-12-ouro-rescue-audit'
def main():
    audit(OUT)
if __name__=='__main__':
    main()
