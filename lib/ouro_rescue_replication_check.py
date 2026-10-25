"""Independent CPU verification of the public contrasts."""
from .independent import ROOT,replication
OUT=ROOT/'experiments/2026-10-15-ouro14-rescue-replication'
def main():
    replication(OUT)
if __name__=='__main__':
    main()
