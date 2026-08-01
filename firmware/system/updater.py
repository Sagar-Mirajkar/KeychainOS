"""Transactional KeychainOS selective OTA updater."""
import gc
import json
import os
import time
try:
    import uhashlib as hashlib
except ImportError:
    import hashlib
try:
    import ubinascii as binascii
except ImportError:
    import binascii

UPDATE_URL = "https://raw.githubusercontent.com/Sagar-Mirajkar/KeychainOS/refs/heads/main/ota/update_manifest.json"
CHUNK = 1024


def exists(path):
    try: os.stat(path); return True
    except OSError: return False


def mkdirs(path):
    current = ""
    for part in path.split("/"):
        if part:
            current += "/" + part
            if not exists(current): os.mkdir(current)


def parent(path):
    position = path.rfind("/")
    return path[:position] if position > 0 else "/"


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        while True:
            block = stream.read(CHUNK)
            if not block: break
            digest.update(block)
    return binascii.hexlify(digest.digest()).decode()


def requests_module():
    try:
        import requests
        return requests
    except ImportError:
        import urequests
        return urequests


def get_bytes(url):
    response = requests_module().get(url)
    try:
        status = getattr(response, "status_code", getattr(response, "status", 200))
        if status != 200: raise RuntimeError("HTTP %s" % status)
        if hasattr(response, "content"): return response.content
        if hasattr(response, "raw"):
            parts=[]
            while True:
                block=response.raw.read(CHUNK)
                if not block: break
                parts.append(block)
            return b"".join(parts)
        return response.text.encode()
    finally:
        response.close()


def download(url, destination):
    response = requests_module().get(url)
    try:
        status = getattr(response, "status_code", getattr(response, "status", 200))
        if status != 200: raise RuntimeError("HTTP %s" % status)
        with open(destination, "wb") as output:
            if hasattr(response, "raw"):
                while True:
                    block=response.raw.read(CHUNK)
                    if not block: break
                    output.write(block)
            elif hasattr(response, "content"):
                output.write(response.content)
            else:
                output.write(response.text.encode())
    finally:
        response.close()


def update(progress=None):
    """Download only changed files, verify all, commit, and return count."""
    manifest = json.loads(get_bytes(UPDATE_URL).decode())
    files = manifest.get("files", [])
    pending=[]
    for index,item in enumerate(files):
        path=item["path"]; expected=item["sha256"]
        if exists(path) and sha256(path)==expected:
            if progress: progress(index+1,len(files),path,"current")
            continue
        mkdirs(parent(path)); temp=path+".new"
        if progress: progress(index+1,len(files),path,"download")
        download(item["url"],temp)
        if sha256(temp)!=expected:
            try: os.remove(temp)
            except OSError: pass
            raise ValueError("SHA mismatch: "+path)
        if path.endswith(".py"):
            with open(temp) as stream: compile(stream.read(),path,"exec")
        pending.append((path,temp)); gc.collect()

    backups=[]
    try:
        for path,temp in pending:
            backup=path+".bak"
            if exists(backup): os.remove(backup)
            if exists(path): os.rename(path,backup); backups.append((path,backup))
            os.rename(temp,path)
        for path,backup in backups:
            if exists(backup): os.remove(backup)
    except Exception:
        for path,backup in reversed(backups):
            try: os.remove(path)
            except OSError: pass
            if exists(backup): os.rename(backup,path)
        raise
    return len(pending)
