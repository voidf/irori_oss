import os
# 如果需要装依赖就取消注释下一行
# os.system("pip install -U pip fastapi mongoengine python-multipart uvicorn pymongo[srv] motor[srv]")
# tier2 asyncio upload
from fastapi import *

from fastapi.responses import *

import motor

from mongoengine import *
from mongoengine import connect
from mongoengine.document import Document
from mongoengine.fields import *

你的连接串 = 'mongodb+srv://<用户名>:<密码>@<集群名>.mongodb.net/irori_oss?retryWrites=true&w=majority'

数据库名称 = 'irori_oss'

口令 = ''

端口: int = 22000 # 改成需要的端口

你的ip = "localhost"

外部url = f"http://{你的ip}:{端口}/"

connect(host=你的连接串)

# -----------------------------
from mongoengine.fields import FileField
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from io import BytesIO
client = motor.motor_asyncio.AsyncIOMotorClient(你的连接串)
db = client[数据库名称]

class GridFSError(Exception):
    pass
async def afsput(self: FileField, source):
    """mongoengine的FileField对象异步放入
    - `source`: The source stream of the content to be uploaded. Must be
    a file-like object that implements :meth:`read` or a string."""
    if self.grid_id:
        raise GridFSError(
            "This document already has a file. Either delete "
            "it or call replace to overwrite it"
        )
    afs = AsyncIOMotorGridFSBucket(db, self.collection_name)
    fname = repr(self.instance) + '.' + self.key
    self.grid_id = await afs.upload_from_stream(fname, source)
    self._mark_as_changed()

async def afsread(self: FileField) -> bytes:
    """mongoengine的FileField对象异步读出为bytes"""
    if self.grid_id is None:
        return None
    afs = AsyncIOMotorGridFSBucket(db, self.collection_name)
    b = BytesIO()
    await afs.download_to_stream(self.grid_id, b)
    b.seek(0)
    return b.read()

async def afsdelete(self: FileField):
    """mongoengine的FileField对象异步删除"""
    afs = AsyncIOMotorGridFSBucket(db, self.collection_name)
    await afs.delete(self.grid_id)
    self.grid_id = None
    self.gridout = None
    self._mark_as_changed()

# -----------------------------------

app = FastAPI()

class FileStorage(Document):
    # fname = StringField()
    content = FileField()

class Test(Document):
    sth = StringField()


@app.post('/upload')
async def upload_(authkey: str='', f: UploadFile = File(...)):
    if authkey != 口令:
        return HTTPException(401)
    fs = FileStorage()
    print(f.filename)
    print(f.content_type)
    
    await afsput(fs.content, f.file)
    # fs.content.put(f.file)
    fs.save()
    return {'url': 外部url + 'download/' + str(fs.pk)}

import json
@app.post('/uploadsth')
async def upload_sth(string: str):
    t = Test(sth = string).save()
    return json.loads(t.to_json())

    # bs = FileStorage(content=f.file.read())

@app.get('/download/{fspk}')
async def download_(fspk: str):
    fs = FileStorage.objects(pk=fspk).first()
    if not fs:
        return HTTPException(404)
    else:
        return Response(await afsread(fs.content))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=端口
    )
