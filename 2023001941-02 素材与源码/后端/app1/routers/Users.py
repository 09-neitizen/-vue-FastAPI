import math
from datetime import timedelta

import redis
from fastapi import APIRouter, Body, Depends, Form, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status

from auth import create_access_token, Auth_tool
from config import settings
from dependencies import get_session, auth_depend
from mysql_app.crud_article import *
from mysql_app.crud_user import *
from mysql_app.schemas import TokenModel, User
from redis_app.redis_pool import redis_pool
from routers.Articles import get_articles_by_userid

router = APIRouter(
    prefix="/user",
    tags=["用户模块"]
)

r = redis.Redis(connection_pool=redis_pool)


# 生产中 authjwt 的异常处理程序
# 您可以使用 orjson 响应调整性能
# @app.exception_handler(AuthJWTException)
# def authjwt_exception_handler(request: Request, exc: AuthJWTException):
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"detail": exc.message}
#     )


@router.post("/signup", summary="注册接口")
async def signup(
        form_data: schemas.UserCreate = Body(..., description="用户注册提交的表单数据"),
        session=Depends(get_session)
):
    # 拿到前端传过来的数据
    username = form_data.username
    password = form_data.password
    email = form_data.email
    verify_code = form_data.validcode

    # 根据用户名去数据库望面查对应的 User
    user = get_user_by_username(session, username)
    # 如果已经有了，就返回错误信息
    if user is not None:
        return {"msg": "当前用户名被占用"}
    else:
        user = get_user_by_email(session, email)
        if user is not None:
            return {"msg": "当前邮箱已经注册"}
    # 校验数据
    # 判断验证码是否过期
    print(r.ttl(email))
    if r.ttl(email) < 0:
        r.delete(email)
        return {"msg": "验证码已经过期"}
    elif r.get(email).decode('utf-8') == verify_code:
        r.delete(email)
        print("{}的验证码校验成功".format(email))
    else:
        return {"msg": '验证码输入错误'}
    # 保存到数据库
    encode_password = Auth_tool.encode_password(password)
    form_data.password = encode_password
    user = create_user(session=session, user=form_data)
    # 给前端响应信息
    return {"msg": "用户注册成功"}


@router.post("/login", summary="登录接口", response_model=TokenModel)
# def login(form_data: UserLogin = Body(..., description="表单传入的登录信息")):
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session=Depends(get_session)):
    # 第一步拿到用户名和密码，校验
    email = form_data.username
    password = form_data.password
    # 第二步通过用户名去数据库中查找到对应的 User
    user = get_user_by_email(session, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录失败，用户名与密码不匹配",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 第三步检查密码
    if not Auth_tool.verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录失败，用户名与密码不匹配",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 第四步生成 token
    # Authorization:bearer header.payload.sign
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        data={
            "username": user.username,
            "user_id": user.id
        },
        expires_delta=access_token_expires
    )
    # 给前端响应信息
    return {"access_token": token, "token_type": "bearer"}


@router.post("/password/change", summary="修改密码")
async def password_change(email: str = Form(...), password: str = Form(...), validcode: str = Form(...),
                          me: User = Depends(auth_depend),
                          session=Depends(get_session)):
    # 根据邮箱去数据库望面查对应的 User
    user = get_user_by_email(session, email)
    # 如果已经有了，就返回错误信息
    if user is not None:
        print(r.ttl(email))
        if r.ttl(email) < 0:
            r.delete(email)
            return {"msg": "验证码已经过期"}
        elif r.get(email).decode('utf-8') == validcode:
            r.delete(email)
            print("{}的验证码校验成功".format(email))
        else:
            return {"msg": '验证码输入错误'}
        encode_password = Auth_tool.encode_password(password)
        if change_password(session, email, encode_password):
            return {"msg": "密码修改成功"}
        else:
            return {"msg": "密码修改失败"}
    else:
        return {"msg": "该用户不存在"}


@router.get("/me", summary="查看个人信息")
async def get_my_info(me: User = Depends(auth_depend), session=Depends(get_session)):
    user_id = me.id
    user = get_user_by_id(session, user_id)
    article_count = get_count_article_by_userid(session, user_id)
    collection_count = get_count_collecion_by_userid(session, user_id)
    transaction_count = get_count_transaction_by_userid(session, user_id)
    views_count = get_count_views_by_userid(session, user_id)
    # gender为0时为未知 为1时为男性 为2时为女性 为3时为保密 为4时为其他
    gender = ["未知", "男性", "女性", "保密", "其他"]
    user_data = {
        "username": user.username,
        "user_id": user_id,
        "gender": gender[user.gender],
        "description": user.description,
        "avatar": user.avatar,
        "article_count": article_count,
        "collection_count": collection_count,
        "transaction_count": transaction_count,
        "views_count": views_count
    }
    return user_data


@router.post("/get_other_person_detail", summary="获取其他人信息")
async def get_other_person_detail(user_id: int = Form(...), session=Depends(get_session)):
    user = get_user_by_id(session, user_id)
    if user is None:
        return {"msg": "该用户不存在"}
    else:
        username = user.username
        article_count = get_count_article_by_userid(session, user_id)
        collection_count = get_count_collecion_by_userid(session, user_id)
        transaction_count = get_count_transaction_by_userid(session, user_id)
        views_count = get_count_views_by_userid(session, user_id)
        gender = ["未知", "男性", "女性", "保密", "其他"]
        user_data = {
            "username": username,
            "user_id": user_id,
            "gender": gender[user.gender],
            "description": user.description,
            "avatar": user.avatar,
            "article_count": article_count,
            "collection_count": collection_count,
            "transaction_count": transaction_count,
            "views_count": views_count
        }
        return user_data


@router.get("/Certification", summary="查看是否认证学号")
async def get_certification_info(me: User = Depends(auth_depend)):
    student_id = str(me.student_ID_Certification)
    if len(student_id) == 10:
        return {"msg": "学号已认证"}
    else:
        return {"msg": "学号未认证"}


@router.post("/update/Certification", summary="认证学号")
async def update_certification_info(
        student_id: str = Form(..., min_length=10, max_length=10),
        me: User = Depends(auth_depend),
        session=Depends(get_session)
):
    if len(student_id) == 10:
        if update_student_id_certification(session, me.id, student_id):
            return {"msg": "学号认证成功"}
        else:
            return {"msg": "学号认证失败"}
    else:
        return {"msg": "学号格式不正确"}


@router.post("/update/information", summary="修改个人信息")
async def update_information(Formdata: schemas.Update_User_Info = Body(...),
                             me: User = Depends(auth_depend),
                             session=Depends(get_session)):
    if update_user_info(session, me.id, Formdata):
        return {"msg": "修改成功"}
    else:
        return {"msg": "修改失败"}


@router.post("/get_user_articles", summary="获取用户发布的全部文章，按照时间排序")
async def get_user_articles(page: int = Form(default=1), user_id=Form(...), session=Depends(get_session)):
    user_id = user_id
    articles = get_articles_by_userid(session=session, user_id=user_id, page_index=page, page_size=6)
    if len(articles) == 0:
        return {"msg": "您还没有发布过任何文章"}
    return articles


@router.post("/get_user_collections", summary="获取用户收藏的全部文章，按照时间排序")
async def get_user_collections(page: int = Form(default=1), user_id=Form(...),
                               session=Depends(get_session)):
    user_id = user_id
    articles = get_collections_by_userid(session=session, user_id=user_id, page_index=page, page_size=6)
    if len(articles) == 0:
        return {"msg": "您还没有收藏任何文章"}
    return articles


@router.post("/get_user_transactions", summary="获取用户交易的全部文章，按照时间排序")
async def get_user_transactions(page: int = Form(default=1), user_id=Form(...),
                                session=Depends(get_session)):
    user_id = user_id
    articles = get_transactions_by_userid(session=session, user_id=user_id, page_index=page, page_size=6)
    if len(articles) == 0:
        return {"msg": "您还没有交易过任何文章"}
    return articles


# 返回给前端的用户发布的全部文章页数的api
@router.post("/get_user_articles_page", summary="获取用户发布的全部文章页数")
async def get_user_articles_page(user_id=Form(...), session=Depends(get_session)):
    pages = get_pages_articles_by_userid(session=session, user_id=user_id)
    if pages == 0:
        return {"msg": "这里空空如也！"}
    else:
        page_count = math.ceil(pages / 6)
        return {"pages": page_count}


@router.post("/get_user_collections_page", summary="获取用户收藏的全部文章页数")
async def get_user_collections_page(user_id=Form(...), session=Depends(get_session)):
    pages = get_pages_collections_by_userid(session=session, user_id=user_id)
    if pages == 0:
        return {"msg": "这里空空如也！"}
    else:
        page_count = math.ceil(pages / 6)
        return {"pages": page_count}


@router.post("/get_user_transactions_page", summary="获取用户交易的全部文章页数")
async def get_user_transactions_page(user_id=Form(...), session=Depends(get_session)):
    pages = get_pages_transactions_by_userid(session=session, user_id=user_id)
    if pages == 0:
        return {"msg": "这里空空如也！"}
    else:
        page_count = math.ceil(pages / 6)
        return {"pages": page_count}
