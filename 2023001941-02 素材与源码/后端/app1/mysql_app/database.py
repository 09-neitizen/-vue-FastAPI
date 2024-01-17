# 数据库配置相关
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 创建引擎
# echo参数为True时，会显示每条执行的SQL语句
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:523615@localhost:3306/fastapp1?charset=utf8mb4"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # echo=True,
    # poolclass=NullPool
    pool_size=10,  # 连接池大小
    pool_recycle=3600,  # 超时时间，单位 ms
    pool_pre_ping=True,  # 预检测池中连接是否有效，并替换无效连接
    pool_use_lifo=True,  # 使用后进先出的方式获取连接，允许多余连接保持空闲
    echo_pool=True,  # 会打印输出连接池的异常信息，帮助排查问题
    max_overflow=7,  # 最大允许溢出连接池大小的连接数量
    # echo=True # 会打印输出连接池的异常信息，帮助排查问题
)
# 连接
conn = engine.connect()
# 构建session对象
# SQLAlchemy中，CRUD是通过会话进行管理的，所以需要先创建会话，
# 每一个SessionLocal实例就是一个数据库session
# flush指发送到数据库语句到数据库，但数据库不一定执行写入磁盘
# commit是指提交事务，将变更保存到数据库文件中
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# SQLORM基类 创建ORM模型并映射到数据建库中
Base = declarative_base()


def get_session():
    """
    获取一个session对象
    """
    # 创建session对象
    session = SessionLocal()
    try:
        yield session
        # 提交事务
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        # 释放资源
        session.close()
