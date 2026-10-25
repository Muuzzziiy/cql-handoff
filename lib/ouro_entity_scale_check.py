"""Independent CPU verification of the public contrasts."""
from .independent import ROOT,scope
OUT=ROOT/'experiments/2026-10-15-ouro-entity-scale'
def main():
    scope(OUT, 20261015302)
if __name__=='__main__':
    main()
