from datetime import datetime

from fastapi import HTTPException, Depends
from jose import JWTError, jwt
from jwt.exceptions import InvalidKeyError,ExpiredSignatureError
from starlette import status

from auth import oauth2_scheme
from config import settings
from mysql_app import crud_user
from mysql_app.database import SessionLocal
from mysql_app.schemas import User


async def get_query_token(x_token: str):
    if x_token != "secret-token":
        raise HTTPException(status_code=400, detail="no secret-token...")


# Dependency
async def get_session():
    """
    每一个请求处理完毕后会关闭当前连接
    不同的请求使用不同的连接
    :return:
    """
    session = SessionLocal()
    try:
        yield session
        # session.commit()  # 通过commit()可以提交所有剩余的更改到数据库。
    except Exception as e:
        session.rollback()  # 回滚
        raise e
    finally:
        session.close()  # 关闭session


async def auth_depend(token: str = Depends(oauth2_scheme), session=Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效token / token已过期",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # 1. 解析 token 中的 payload 信息
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        # payload中获取的过期时间戳exp字段的值
        exp = payload.get('exp')
        if exp is not None and datetime.utcnow() > datetime.fromtimestamp(exp):
            # Token 已过期，执行相应的处理逻辑
            print("token解码失败")
            raise credentials_exception
        # Token 未过期，继续处理请求
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
    except ExpiredSignatureError as e:
        print("token 过期了,{}".format(str(e)))
        raise credentials_exception
    except JWTError as e:
        print("token解码失败,{}".format(str(e)))
        raise credentials_exception
    # 2. 根据 payload 中的信息去数据库中找到对应的用户
    user = crud_user.get_user_by_username(session, username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证不通过")
    return user


async def get_current_active_user(current_user: User = Depends(auth_depend)):
    if current_user.is_active is not True:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="封号用户")
    return current_user
