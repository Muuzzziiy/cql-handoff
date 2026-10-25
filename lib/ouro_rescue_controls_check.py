"""Independent CPU verification of the public contrasts."""
from .independent import ROOT,controls
OUT=ROOT/'experiments/2026-10-12-ouro-rescue-controls'
def main():
    controls(OUT)
if __name__=='__main__':
    main()
