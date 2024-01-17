# 用于存放pydantic模型 模型验证
from typing import Optional, Union
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


# 登录成功返回token模型
class TokenModel(BaseModel):
    access_token: str
    token_type: str


# 在生产中，您可以使用 pydantic 中的设置管理从 .env 获取密钥
class Settings(BaseModel):
    authjwt_secret_key: str = "secret"


# 注册账号模型
class UserCreate(UserBase):
    """
        请求模型验证：
        email:
        username:
        password:
        validcode:
    """
    password: str = Field(..., example="123")
    validcode: str = Field(...)


class User(UserBase):
    """
        响应模型：
        id:
        email:
        is_active
        并且设置orm_mode与之兼容
    """
    id: int
    student_ID_Certification: str = Field(default=None)
    is_active: bool = Field(default=True, description="是否处于启用")

    class Config:
        orm_mode = True


# 用户登录模型
class LoginModel(BaseModel):
    username: str = None
    password: str = None


# Pydanticorm_mode会告诉 Pydantic模型读取数据，
# 即使它不是dict，而是 ORM 模型。

class UserInfo(BaseModel):
    username: str
    email: str
    is_active: bool = True


class Article(BaseModel):
    user_id: int = Field(...)
    title: str = Field(...)
    article_type: int = Field(...)
    category_name: str = Field(...)
    content: str = Field(...)
    # zhanghe
    price: int = Field(...)
    trade_type: int = Field(...)
    trade_status: int = Field(...)
    transaction_url: Optional[str] = Field()

    class Config:
        orm_mode = True


class Create_Article(BaseModel):
    user_id: int = Field(..., example=1)
    title: str = Field(..., example="学习打篮球")
    description: str = Field(..., example="学习打篮球")
    article_type: int = Field(..., example=0)
    category_name: str = Field(..., example="运动")
    content: str = Field(..., example="<p>要想学会打篮球，还得向我哥哥学习</p><p>成为爱坤，是你学会篮球的第一步</p>")
    Article_status: int = Field(..., example=1, description="0:草稿 1:发布")
    price: int = Field(..., example=0)
    trade_type: int = Field(..., example=1)
    trade_status: int = Field(..., example=0)
    transaction_url: Optional[str]


class Update_Article(BaseModel):
    article_id: int = Field(..., example=1)
    user_id: int = Field(..., example=1)
    title: str = Field(..., example="学习打篮球")
    article_type: int = Field(..., example=0)
    category_name: str = Field(..., example="运动")
    content: str = Field(..., example="<p>要想学会打篮球，还得向我哥哥学习</p><p>成为爱坤，是你学会篮球的第一步</p>")
    Article_status: int = Field(..., example=1, description="0:草稿 1:发布")
    transaction_url: Optional[str] = ""


class create_comment(BaseModel):
    user_id: int = Field(..., example=1)
    article_id: int = Field(..., example=1)
    content: str = Field(..., example="这是一条评论")
    reply_id: int = Field(..., example=0)


# 创建消息模型
class New_msg(BaseModel):
    from_name: str = Field(...)
    to_name: str = Field(...)
    content: str = Field(...)
    from_user_avatar: str = Field(...)


# 修改个人信息模型
class Update_User_Info(BaseModel):
    gender: int = Field(..., example="3")
    description: str = Field(..., example="这是一条个性签名")
