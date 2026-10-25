"""Independent CPU verification of the public contrasts."""
from .independent import ROOT,converse
OUT=ROOT/'experiments/2026-10-12-ouro-converse-kv'
def main():
    converse(OUT)
if __name__=='__main__':
    main()
