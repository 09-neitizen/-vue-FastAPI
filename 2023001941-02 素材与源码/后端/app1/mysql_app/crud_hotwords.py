from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from mysql_app import models


def create_search_hotword(session: Session, search_hotword: models.SearchHotwords):
    """
    创建搜索关键词记录
    """
    # 将搜索热词记录插入到 MySQL 数据库中
    try:
        session.add(search_hotword)
        session.flush()
        hotword_id = search_hotword.id
        session.commit()
        session.close()
        return hotword_id
    except Exception as e:
        session.rollback()
        # 如果插入记录时发生唯一性冲突，则忽略该记录
        return None



