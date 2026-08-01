"""Extract a KeychainOS ZIP into a local Git clone and push it."""
import os, subprocess, sys, zipfile
from pathlib import Path

def run(command, cwd):
    print("$", " ".join(command)); subprocess.run(command,cwd=cwd,check=True)

def main():
    if len(sys.argv)<3:
        print("Usage: python publish_keychainos.py ZIP_PATH REPO_PATH [message]"); return 2
    archive=Path(sys.argv[1]).expanduser().resolve(); repo=Path(sys.argv[2]).expanduser().resolve()
    message=sys.argv[3] if len(sys.argv)>3 else "Publish KeychainOS update"
    if not (repo/'.git').exists(): raise RuntimeError("REPO_PATH is not a Git clone")
    with zipfile.ZipFile(archive) as z: z.extractall(repo)
    run(['git','add','.'],repo); run(['git','commit','-m',message],repo); run(['git','push'],repo)
    print("Published. On the ESP open Settings > Update.")
if __name__=='__main__': main()
