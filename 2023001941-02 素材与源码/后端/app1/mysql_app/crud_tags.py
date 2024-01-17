from sqlalchemy.orm import Session

from mysql_app import models


def create_new_tag(session: Session, tag: str):
    """
    创建标签
    """
    if not tag:
        return None
    if tag in get_all_tags_desc(session):
        return None
    new_tag = models.Tags(tag_name=tag)
    session.add(new_tag)
    session.flush()
    id = new_tag.tag_id
    session.commit()
    return id


def get_tag_id_by_tag_name(session: Session, tag_name: str):
    """
    根据标签名称获取标签id
    """
    if not tag_name:
        return None
    return session.query(models.Tags.tag_id).filter(models.Tags.tag_name == tag_name).first()[0]


def get_tag_by_id(session: Session, tag_id: int):
    """
    根据标签编号获取标签名称
    """
    if not tag_id:
        return None
    tag = session.query(models.Tags.tag_name).filter(
        models.Tags.tag_id == tag_id).first()
    return tag[0]


def search_tag_by_name(session: Session, tag_name: str):
    """
    按标签名称搜索标签列表
    """
    if not tag_name:
        return None
    tags = []
    tags_name = session.query(models.Tags.tag_name).filter(
        models.Tags.tag_name.like("%" + tag_name + "%")).order_by(models.Tags.count_used.desc()).all()
    for tag_name in tags_name:
        tags.append(tag_name[0])
    return tags


def get_all_tags_desc(session: Session):
    """
    列出所有标签, 按数量升序排列
    """
    tags = []
    for tag_name in session.query(models.Tags.tag_name).order_by(models.Tags.count_used.desc()).all():
        tags.append(tag_name[0])
    return tags


def get_article_tags_by_article_id(session: Session, article_id: int):
    """
    获取文章的标签关联数量
    """
    tags = []
    tags_id = (session.query(models.TagRelationship.tag_id).filter(
        models.TagRelationship.article_id == article_id).all())
    for tag_id in tags_id:
        tag = get_tag_by_id(session, tag_id[0])
        tags.append(tag)
    return tags


def update_tag_count_used(session: Session, tag_id: int):
    """
    更新标签使用次数
    """
    session.query(models.Tags).filter(
        models.Tags.tag_id == tag_id).update({models.Tags.count_used: models.Tags.count_used + 1})
    session.commit()


def get_tags_id_by_search(session: Session, search_string: str):
    """
    根据搜索字符串搜索标签列表
    """
    tags_id = []
    tag_ids = (session.query(
        models.Tags.tag_id).filter(models.Tags.tag_name.like("%" + search_string + "%")).all())
    if len(tag_ids) != 0:
        for tag_id in tag_ids:
            tags_id.append(tag_id[0])
    return tags_id
