import os
# 如果需要装依赖就取消注释下一行
# os.system("pip install -U pip fastapi mongoengine python-multipart uvicorn pymongo[srv]")

from fastapi import *

from fastapi.responses import *

# from pydantic import BaseModel

from mongoengine import *

你的连接串 = 'mongodb+srv://<用户名>:<密码>@<集群名>.mongodb.net/irori_oss?retryWrites=true&w=majority'

口令 = ''

端口: int = 22000 # 改成需要的端口

你的ip = "localhost"

外部url = f"http://{你的ip}:{端口}/"

connect(host=你的连接串)

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
    
    
    fs.content.put(f.file)
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
        return Response(fs.content.read())

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=端口
    )
