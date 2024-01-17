from fastapi import APIRouter, File, UploadFile, Depends
import uuid
from dependencies import auth_depend, get_session
from mysql_app.crud_user import change_avatar, get_avatar
from mysql_app.schemas import User

router = APIRouter(
    prefix="/file",
    tags=["文件模块"]
)
"""
UploadFile 的属性如下：
    filename：上传文件的文件名
        例如， myimage.jpg；
    content_type：内容类型（MIME 类型 / 媒体类型）字符串（str）
        例如，image/jpeg；
    file： SpooledTemporaryFile（ file-like 对象）。
        其实就是 Python文件，可直接传递给其他预期 file-like 对象的函数或支持库。
        
UploadFile 支持以下 async 方法，（使用内部 SpooledTemporaryFile）可调用相应的文件方法。
    write(data)：把 data （str 或 bytes）写入文件；
    read(size)：按指定数量的字节或字符（size (int)）读取文件内容；
    seek(offset)：移动至文件 offset （int）字节处的位置；
    close()：关闭文件。
"""


@router.post("/upload/avatar", summary="上传头像")
async def avatar_upload(image: UploadFile = File(..., description="上传的图片"), me: User = Depends(auth_depend),
                        session=Depends(get_session)):
    username = me.username
    image_id = str(uuid.uuid1())
    file_path = ".\\src\\" + image_id + "." + image.content_type.split("/")[1]
    file_name = image_id + "." + image.content_type.split("/")[1]
    with open(file_path, 'wb') as f:
        for i in iter(lambda: image.file.read(1024 * 1024 * 10), b''):
            f.write(i)
    f.close()
    change_avatar(session, username, file_name)
    return {"file_name": image.filename}


@router.get("/get/avatar", summary="获取头像")
async def avatar_get(me: User = Depends(auth_depend), session=Depends(get_session)):
    username = me.username
    file_name = get_avatar(session, username)
    file_url = "http://" + "10.131.10.156:8000/src/" + file_name
    return file_url


@router.post("/upload/article_img", summary="上传图片")
async def avatar_upload(image: UploadFile = File(..., description="上传的图片"), me: User = Depends(auth_depend),
                        session=Depends(get_session)):
    image_id = str(uuid.uuid1())
    file_path = ".\\src\\article_img\\" + image_id + "." + image.content_type.split("/")[1]
    file_name = image_id + "." + image.content_type.split("/")[1]
    with open(file_path, 'wb') as f:
        for i in iter(lambda: image.file.read(1024 * 1024 * 10), b''):
            f.write(i)
    f.close()
    return {"file_name": file_name}
