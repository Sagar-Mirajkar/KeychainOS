"""Transaction-aware recursive file operations."""
import os
def exists(p):
 try: os.stat(p); return True
 except OSError: return False
def isdir(p):
 try: return bool(os.stat(p)[0]&0x4000)
 except OSError: return False
def mkdirs(path):
 cur=''
 for part in path.split('/'):
  if part:
   cur+='/'+part
   if not exists(cur): os.mkdir(cur)
def copy(src,dst):
 if isdir(src):
  mkdirs(dst)
  for name in os.listdir(src): copy(src.rstrip('/')+'/'+name,dst.rstrip('/')+'/'+name)
 else:
  mkdirs(dst.rsplit('/',1)[0] or '/')
  with open(src,'rb') as a, open(dst+'.new','wb') as b:
   while True:
    block=a.read(4096)
    if not block: break
    b.write(block)
  try: os.remove(dst)
  except OSError: pass
  os.rename(dst+'.new',dst)
def remove(path):
 if isdir(path):
  for name in os.listdir(path): remove(path.rstrip('/')+'/'+name)
  os.rmdir(path)
 else: os.remove(path)
def move(src,dst): copy(src,dst); remove(src)
