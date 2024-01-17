from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, load_only
from sqlalchemy import func, and_, or_
from . import schemas, models


def create_new_msg(session: Session, msg: schemas.New_msg):
    session_msg = models.ChatMsg(from_name=msg.from_name, to_name=msg.to_name, content=msg.content,
                                 from_user_avatar=msg.from_user_avatar)
    session.add(session_msg)
    session.commit()
    session.flush()
    session.close()
    return session_msg


def get_history_msg(session: Session, username: str, to_name: str):
    msg1 = session.query(models.ChatMsg). \
        filter(models.ChatMsg.to_name == to_name). \
        filter(models.ChatMsg.from_name == username).all()
    msg2 = session.query(models.ChatMsg). \
        filter(models.ChatMsg.to_name == username). \
        filter(models.ChatMsg.from_name == to_name).all()
    msg = msg1 + msg2

    new_msg = sorted(msg, key=lambda x: x.date, reverse=True)
    return msg


def get_chatlist(session: Session, username: str):
    recives = session.query(models.ChatMsg). \
        filter(models.ChatMsg.to_name == username). \
        order_by(models.ChatMsg.date.desc()).all()
    sends = session.query(models.ChatMsg). \
        filter(models.ChatMsg.from_name == username). \
        order_by(models.ChatMsg.date.desc()).all()
    chatlist = []
    chatlist2 = []
    for data in recives:
        if data.from_name not in chatlist:
            chatlist.append(data.from_name)
            chatlist2.append({"from_name": data.from_name, "is_read": data.is_read, "avatar": data.from_user_avatar})
    for data in sends:
        if data.to_name not in chatlist:
            chatlist.append(data.to_name)
            chatlist2.append({"from_name": data.to_name, "is_read": "null", "avatar": data.from_user_avatar})

    return chatlist2


def set_is_read(session: Session, username: str, to_name: str):
    session.query(models.ChatMsg). \
        filter(and_(models.ChatMsg.from_name == username,
                    models.ChatMsg.to_name == to_name,
                    models.ChatMsg.is_read == False)). \
        update({'is_read': True})
    session.commit()
