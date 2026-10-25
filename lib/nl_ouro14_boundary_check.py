"""Independent CPU verification of the public contrasts."""
from .independent import ROOT,nl_boundary
OUT=ROOT/'experiments/2026-10-17-nl-ouro14-boundary'
def main():
    nl_boundary(OUT)
if __name__=='__main__':
    main()
