"""Independent CPU verification of the public contrasts."""
from .independent import ROOT,scope
OUT=ROOT/'experiments/2026-10-16-format-scale'
def main():
    scope(OUT, 20261017302)
if __name__=='__main__':
    main()
