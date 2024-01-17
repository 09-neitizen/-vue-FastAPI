# CRUD来源于：Çreate，Read，Update，delete
# 数据库操作相关
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from . import schemas, models


def get_username(session: Session, user_id: int):
    """
    通过 id 查询
    :param session: 连接数据库的会话
    :param user_id: 用户的id
    :return: user :返回user模型
    """
    user = session.query(models.User).filter(models.User.id == user_id).first()
    return user.username


def get_user_by_email(session: Session, email: str):
    """
    通过 email 查询
    :param session: 连接数据库的会话
    :param email: 用户的email
    :return: 返回user模型
    """
    user = session.query(models.User).filter(models.User.email == email).first()
    return user


def get_user_by_username(session: Session, username: str):
    """
    通过 username 查询
    :param session: 连接数据库的会话
    :param username: 用户的username
    :return: 返回user模型
    """
    user = session.query(models.User).filter(models.User.username == username).first()
    return user


def get_users(session: Session):
    """
    查询所有用户
    :param session: 连接数据库的会话
    :return: 返回user模型列表
    """
    return session.query(models.User).all()


def get_user_by_id(session: Session, user_id: int):
    """
    通过 id 查询
    :param session: 连接数据库的会话
    :param user_id: 用户的id
    :return: user :返回user模型
    """
    user = session.query(models.User).filter(models.User.id == user_id).first()
    return user


def create_user(session: Session, user: schemas.UserCreate):
    """
    添加用户
    :param session: 连接数据库的会话
    :param user: 带数据的user模型
    :return: 返回user模型
    """
    session_user = models.User(username=user.username, email=user.email, password=user.password)
    session.add(session_user)
    # flush 预提交，等于提交到数据库内存，还未写入数据库文件
    session.flush()
    # commit 就是把内存里面的东西直接写入，可以提供查询了；
    session.commit()
    session.refresh(session_user)
    return session_user


def get_avatar(session: Session, username: str):
    """
    通过username获取头像地址
    :param session: 连接数据库的会话
    :param username: 用户的username
    :return:
    """
    user = session.query(models.User).filter(models.User.username == username).first()
    return user.avatar


def get_avatar_id(session: Session, user_id: int):
    """
    通过username获取头像地址
    :param session: 连接数据库的会话
    :param user_id: 用户的username
    :return:
    """
    user = session.query(models.User).filter(models.User.id == user_id).first()
    return user.avatar


def change_avatar(session: Session, username: str, file_path: str):
    """
    改变avatar的值
    :param session: 连接数据库的会话
    :param username: 用户的username
    :param file_path: avatar的值
    :return: True/False
    """
    try:
        user = session.query(models.User).filter(models.User.username == username).update(
            {models.User.avatar: file_path})
        session.flush()
        session.commit()
    except SQLAlchemyError:
        return False
    return True


def change_password(session: Session, email: str, password: str):
    """
    修改用户密码
    :param session: 连接数据库的会话
    :param email: 用户的email
    :param password: 修改后的password值
    :return: True/False
    """
    try:
        user = session.query(models.User).filter(models.User.email == email).update(
            {models.User.password: password})
        session.flush()
        session.commit()
    except SQLAlchemyError:
        print("修改失败")
        return False
    return True


# 更新用户学号认证信息
def update_student_id_certification(session: Session, user_id: int, Student_ID: str):
    if not Student_ID:
        return False
    session.query(models.User).filter(models.User.id == user_id).update(
        {models.User.student_ID_Certification: Student_ID})
    return True


def update_user_info(session: Session, user_id: int, user: schemas.Update_User_Info):
    """
    更新用户信息
    :param session: 连接数据库的会话
    :param user_id: 用户的id
    :param user: 带数据的user模型
    :return: True/False
    """
    try:
        session.query(models.User) \
            .filter(models.User.id == user_id).update(
            {
                models.User.gender: user.gender,
                models.User.description: user.description
            }
        )
        session.flush()
        session.commit()
    except SQLAlchemyError:
        return False
    return True



