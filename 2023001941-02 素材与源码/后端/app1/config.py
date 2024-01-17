from pydantic import BaseSettings


# 文档：https://pydantic-docs.helpmanual.io/usage/settings/
# 配置项放到setting中管理
class Settings(BaseSettings):
    # debug模式
    debug: bool = True

    # jwt加密的 key
    jwt_secret_key: str = "299f95c7e51e4bec3ae34edaa7e528440ab6bc40e57c934c872dd1817287444d"
    # jwt加密算法
    jwt_algorithm: str = 'HS256'
    # token过期时间，单位：秒
    jwt_exp_minutes: int = 60
    # token过期时间
    ACCESS_TOKEN_EXPIRE_MINUTES = 60


settings = Settings()
