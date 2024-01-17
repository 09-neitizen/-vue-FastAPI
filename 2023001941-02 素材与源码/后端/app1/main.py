import os
import sys

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi_jwt_auth.exceptions import AuthJWTException
from starlette.staticfiles import StaticFiles

from internal import admin
from mysql_app.database import Base, engine
from redis_app.redis_pool import redis_pool
from routers.Articles import router as article_router
from routers.Email_code import router as email_router
from routers.FileLoad import router as file_router
from routers.Search import router as search_router
from routers.Users import router as user_router
from routers.Chat import router as chat_router
from routers.Comment import router as comment_router

sys.path.append(os.path.join(os.path.dirname(__file__)))  # 防止相对路径导入出错
Base.metadata.create_all(bind=engine)  # 数据库初始化，如果没有库或者表，会自动创建
app = FastAPI()


# 生产中 authjwt 的异常处理程序
# 您可以使用 orjson 响应调整性能
@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


# 配置允许域名列表、允许方法、请求头、cookie等
app.add_middleware(
    CORSMiddleware,
    # 允许跨域的源列表，例如 ["http://www.example.org"] 等等，["*"] 表示允许任何源
    allow_origins=["*"],
    # 跨域请求是否支持 cookie，默认是 False，如果为 True，allow_origins 必须为具体的源，不可以是 ["*"]
    allow_credentials=False,
    # 允许跨域请求的 HTTP 方法列表，默认是 ["GET"]
    allow_methods=["*"],
    # 允许跨域请求的 HTTP 请求头列表，默认是 []，可以使用 ["*"] 表示允许所有的请求头
    # 当然 Accept、Accept-Language、Content-Language 以及 Content-Type 总之被允许的
    allow_headers=["*"],
    # 可以被浏览器访问的响应头, 默认是 []，一般很少指定
    # expose_headers=["*"]
    # 设定浏览器缓存 CORS 响应的最长时间，单位是秒。默认为 600，一般也很少指定
    # max_age=1000
)


@app.get("/")
def home():
    return {"你好": "欢迎来到学生助助平台的后端"}


app.mount("/src", StaticFiles(directory="src"), name="src")

# # 处于调试阶段的时候才显示该接口
# if settings.debug:
#     app.include_router(debug_router)

app.include_router(user_router)
app.include_router(email_router)
app.include_router(file_router)
app.include_router(article_router)
app.include_router(search_router)
app.include_router(chat_router)
app.include_router(comment_router)

app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"]
)

if __name__ == '__main__':
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=False)
    redis_pool.disconnect()
