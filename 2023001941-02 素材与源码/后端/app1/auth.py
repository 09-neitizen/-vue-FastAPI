from datetime import datetime, timedelta
from logging import getLogger
from passlib.context import CryptContext  # 用于哈希密码
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt

from config import settings

# from loguru import logger
logger = getLogger(__name__)
# 获取token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login")


class Auth():
    # hasher= CryptContext() 哈希使用的加密算法是Bcrypt
    hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def encode_password(self, password):
        return self.hasher.hash(password)

    def verify_password(self, password, encoded_password):
        return self.hasher.verify(password, encoded_password)


def create_access_token(
        data: dict,
        expires_delta: timedelta) -> str:
    to_encode = data.copy()
    # 检测token的有效时间是否为空，如果为空，则默认设置有效时间为60分钟
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_exp_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


Auth_tool = Auth()
