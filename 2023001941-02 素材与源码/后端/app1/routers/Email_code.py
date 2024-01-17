from fastapi import APIRouter, Form
from redis_app.redis_pool import redis_pool
import redis
from email_Captcha.email_send import send_code_email

router = APIRouter(
    prefix="/email",
    tags=["邮箱模块"]
)

# 连接 Redis 数据库
pool = redis_pool
r = redis.Redis(connection_pool=pool)


@router.post("/sendcode/register", summary="注册账号    ：发送邮箱验证码")
async def send_code(email: str = Form(..., description="用户邮箱")):
    code = send_code_email(email, "register")
    if code != None:
        r.setex(email, 120, code)
        return {"msg": "success"}
    else:
        return {"msg": "fail"}


@router.post("/sendcode/retrieve", summary="找回密码：发送邮箱验证码")
async def send_code(email: str = Form(..., description="用户邮箱")):
    print(email)
    code = send_code_email(email, "retrieve")
    if code != None:
        r.setex(email, 120, code)
        return {"msg": "success"}
    else:
        return {"msg": "fail"}
