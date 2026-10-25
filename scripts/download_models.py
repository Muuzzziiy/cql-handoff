"""Download only the requested pinned preprint checkpoints."""
import argparse
from pathlib import Path

MODELS={
 'Ouro-1.4B':('ByteDance/Ouro-1.4B','574fa66cb8bf5abdc979642d01cf2b79b16bfab1'),
 'Ouro-2.6B':('ByteDance/Ouro-2.6B','1ed04250da1a9936042725d302e81c8fa2ab5abd'),
 'Qwen3-1.7B-Base':('Qwen/Qwen3-1.7B-Base','ea980cb0a6c2ae4b936e82123acc929f1cec04c1'),
 'layerskip-llama3-8B':('facebook/layerskip-llama3-8B','3b9e03eaf3cc90812a7bd2b69106b626d63bac1f'),
}
ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('models',nargs='*',help='Folder names from: '+', '.join(MODELS))
    args=parser.parse_args()
    unknown=set(args.models)-MODELS.keys()
    if unknown: parser.error('unknown models: '+', '.join(sorted(unknown)))
    from huggingface_hub import snapshot_download
    for name in args.models or MODELS:
        repo,revision=MODELS[name]
        print('Downloading',name,revision,flush=True)
        snapshot_download(repo,revision=revision,local_dir=ROOT/'models'/name)

if __name__=='__main__': main()
