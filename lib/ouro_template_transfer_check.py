"""Independent CPU verification of the public contrasts."""
from .independent import ROOT,scope
OUT=ROOT/'experiments/2026-10-12-ouro-template-transfer'
def main():
    scope(OUT, 20261013602)
if __name__=='__main__':
    main()
