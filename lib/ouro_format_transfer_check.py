"""Independent CPU verification of the public contrasts."""
from .independent import ROOT,scope
OUT=ROOT/'experiments/2026-10-15-ouro-format-transfer'
def main():
    scope(OUT, 20261015702)
if __name__=='__main__':
    main()
