"""Move files and apps to recoverable Trash."""
import time
from system import file_operations as ops
def trash_path(source,kind='files'):
 name=source.rstrip('/').rsplit('/',1)[-1]
 return '/trash/%s/%d_%s'%(kind,time.ticks_ms(),name)
def put(source,kind='files'):
 destination=trash_path(source,kind); ops.move(source,destination); return destination
def restore(source,destination): ops.move(source,destination); return destination
def empty(kind='files'):
 folder='/trash/'+kind
 for name in list(__import__('os').listdir(folder)): ops.remove(folder+'/'+name)
