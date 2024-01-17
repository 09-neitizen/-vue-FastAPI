class Config:
    """配置信息"""
    SECRET_KEY = "FDHUFHSIFHSOIAFJSIOAJDShuhdh242424"
    # 数据库　　
    # dialect + driver  ://  username :password@host   :port/database
    # 数据库 + 数据库驱动 ：// 数据库用户名:密码 @ 部署ip地址：端口/数据库库名
    SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:523615@localhost:3306/fastapp1?charset=utf8mb4"
    # SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    # redis　　
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    # 对cookie中的session_id进行隐藏处理　　
    PERMANENT_SESSION_LIFETIME = 86400  # session数据的过期时间　　　　


class DevelopmentConfig(Config):
    # 开发环境
    DEBUG = True


class TestingConfig(Config):
    # 测试环境
    TESTING = True


config = Config()
