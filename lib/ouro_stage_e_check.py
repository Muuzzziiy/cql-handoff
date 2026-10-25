"""Independent CPU verification of the public contrasts."""
from .independent import ROOT,crossed
OUT=ROOT/'experiments/2026-10-12-ouro-stage-e-swap'
def main():
    crossed(OUT)
if __name__=='__main__':
    main()
