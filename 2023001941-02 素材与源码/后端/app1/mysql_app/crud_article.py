import datetime

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session, joinedload

from . import schemas, models
from .crud_category import get_category_id_by_name
from .crud_tags import update_tag_count_used, get_tags_id_by_search


def get_article_by_article_id(session: Session, article_id: int):
    article = session.query(models.Article, models.User.username, models.User.avatar) \
        .join(models.User) \
        .filter(models.Article.id == article_id) \
        .options(joinedload(models.Article.user)) \
        .first()

    article_data = article[0].__dict__
    article_data["user"] = {
        "username": article[1],
        "avator": article[2]
    }
    return article_data


def get_articles_by_user_id(session: Session, user_id: int):
    articles = session.query(models.Article).filter(models.Article.User_id == user_id).all()
    return articles


def create_new_article(session: Session, article_schema: schemas.Article):
    category_id = get_category_id_by_name(session, article_schema.category_name)
    # article_type为0时为普通文章
    # article_type为1时为交易文章
    # article_type为2时为树洞文章
    new_article = models.Article(
        category_id=category_id,
        article_type=article_schema.article_type,
        transaction_url=article_schema.transaction_url,
        description=article_schema.description,
        User_id=article_schema.user_id,
        title=article_schema.title,
        content=article_schema.content,
        Article_status=article_schema.Article_status,
        trade_type=article_schema.trade_type,
        trade_stutas=article_schema.trade_status,
        price=article_schema.price,
    )
    session.add(new_article)
    session.flush()
    article_id = new_article.id
    session.commit()
    session.refresh(new_article)
    return article_id


def update_article_by_article_id(session: Session, article_schema: schemas.Update_Article):
    """
    更新文章
    """
    article = get_article_by_article_id(session, article_schema.article_id)
    if not article:
        return False
    article.title = article_schema.title
    article.content = article_schema.content
    article.Article_status = article_schema.Article_status
    article.category_id = get_category_id_by_name(session, article_schema.category_name)
    article.updated_at = datetime.datetime.now()
    session.commit()
    return True


def create_tags_relatioalship(session: Session, article_id: int, tag_id: int):
    """
    创建标签关联
    """
    if not article_id or not tag_id:
        return False
    new_tag_rel = models.TagRelationship(article_id=article_id, tag_id=tag_id)
    session.add(new_tag_rel)
    session.flush()
    session.commit()
    update_tag_count_used(session, tag_id)
    return True


def get_article_ids_by_search(session: Session, search_text: str):
    """
    根据文章名称或文章标签寻找文章ID
    """
    if not search_text:
        return []
    search_text = search_text.strip().lower()
    search_text_list = search_text.split()
    search_text_list_len = len(search_text_list)
    if search_text_list_len == 0:
        return []


def get_articles_id_by_tagrelationship(session: Session, tag_id: int):
    """
    寻找标签下的所有文章ID
    """
    if not tag_id:
        return []
    articles_id = []
    for article_id in session.query(models.TagRelationship.article_id).filter(
            models.TagRelationship.tag_id == tag_id).all():
        articles_id.append(article_id[0])
    return articles_id


def get_articles_id_by_tags_id(session: Session, tags_id: list):
    """
    根据标签ID列表寻找文章ID列表
    """
    if not tags_id:
        return []
    if len(tags_id) == 0:
        return []
    articles_id = []
    for tag_id in tags_id:
        ids = get_articles_id_by_tagrelationship(session, tag_id)
        if len(ids) == 0:
            continue
        articles_id.extend(ids)
    articles_id = list(set(articles_id))
    return articles_id


def get_articles_id_by_search(session: Session, search_text: str):
    """
    模糊查询标题和文章内容中符合搜索词的文章 寻找文章ID列表
    """
    if not search_text:
        return []
    ids = []
    article_ids1 = session.query(models.Article.id).filter(models.Article.title.like("%" + search_text + "%")).all()
    if len(article_ids1) != 0:
        for article_id in article_ids1:
            ids.append(article_id[0])
    article_ids2 = session.query(models.Article.id).filter(
        models.Article.content.like("%" + search_text + "%")).all()
    if len(article_ids2) != 0:
        for article_id in article_ids2:
            ids.append(article_id[0])
    ids = list(set(ids))
    return ids


def search_get_articles(session: Session, search_word: str):
    # 搜索文章
    article_ids = []
    ids1 = get_articles_id_by_search(session, search_word)
    tag_ids = get_tags_id_by_search(session, search_word)
    ids2 = get_articles_id_by_tags_id(session, tag_ids)
    if len(ids1) == 0 and len(ids2) == 0:
        return []
    if len(ids1) != 0:
        article_ids.extend(ids1)
    if len(ids2) != 0:
        article_ids.extend(ids2)
    article_ids = list(set(article_ids))
    if len(article_ids) == 0:
        return []
    articles = []
    for article_id in article_ids:
        article = get_article_by_article_id(session, article_id)
        if article["Article_status"] == 1:
            articles.append(article)
    return articles


def get_count_collecion_by_userid(session: Session, user_id: int):
    """
    查询用户的收藏数量
    """
    collections = session.query(models.Collection.article_id).filter(
        models.Collection.user_id == user_id).count()
    return collections


def get_count_article_by_userid(session: Session, user_id: int):
    """
    查询用户的文章数量
    """
    count = session.query(models.Article.id).filter(
        and_(models.Article.User_id == user_id, or_(models.Article.article_type == 0, models.Article.article_type == 2))
    ).count()
    return count


def get_count_transaction_by_userid(session: Session, user_id: int):
    """
    查询用户的交易数量
    """
    count = session.query(models.Article.id).filter(
        models.Article.User_id == user_id, models.Article.article_type == 1).count()
    return count


def get_count_views_by_userid(session: Session, user_id: int):
    """
    查询用户找到的所有数据的Views总和
    """
    views = 0
    views_list = session.query(models.Article.views).filter(models.Article.User_id == user_id).all()
    if len(views_list) == 0:
        return views
    for view in views_list:
        views += view[0]
    return views


# 检测用户是否已经点赞了该文章，如果数据库检索到了数据则为点赞返回id，否则返回None
def check_user_like_article(session: Session, user_id: int, article_id: int):
    """
    检测用户是否已经点赞了该文章
    """
    if not user_id or not article_id:
        return False
    like = session.query(models.ArticleLike).filter(
        and_(
            models.ArticleLike.article_id == article_id,
            models.ArticleLike.user_id == user_id)).first()
    if not like:
        return False
    else:
        return True


# 用户点赞文章
def user_like_article(session: Session, user_id: int, article_id: int):
    """
    用户点赞文章
    """
    if not user_id or not article_id:
        return False
    like = models.ArticleLike(article_id=article_id, user_id=user_id)
    session.add(like)
    session.commit()
    return True


# 用户取消点赞文章
def user_unlike_article(session: Session, user_id: int, article_id: int):
    """
    用户取消点赞文章
    """
    if not user_id or not article_id:
        return False
    like = session.query(models.ArticleLike).filter(
        and_(
            models.ArticleLike.article_id == article_id,
            models.ArticleLike.user_id == user_id)).first()
    if not like:
        return False
    session.delete(like)
    session.commit()
    return True


# 检测用户是否已经收藏了该文章，如果数据库检索到了数据则为收藏返回id，否则返回None
def check_user_collection_article(session: Session, user_id: int, article_id: int):
    """
    检测用户是否已经收藏了该文章
    """
    if not user_id or not article_id:
        return False
    collection = session.query(models.Collection).filter(
        and_(
            models.Collection.article_id == article_id,
            models.Collection.user_id == user_id)).first()
    if not collection:
        return False
    else:
        return True


# 用户收藏文章
def user_collection_article(session: Session, user_id: int, article_id: int):
    """
    用户收藏文章
    """
    if not user_id or not article_id:
        return False
    collection = models.Collection(article_id=article_id, user_id=user_id)
    session.add(collection)
    session.commit()
    return True


# 用户取消收藏文章
def user_uncollection_article(session: Session, user_id: int, article_id: int):
    """
    用户取消收藏文章
    """
    if not user_id or not article_id:
        return False
    collection = session.query(models.Collection).filter(
        and_(
            models.Collection.article_id == article_id,
            models.Collection.user_id == user_id)).first()
    if not collection:
        return False
    session.delete(collection)
    session.commit()
    return True


# # 用户评论文章，评论表中的reply_id为0
# def get_comment_list(session: Session, article_id: int, page_index: 1, page_size: 10):
#     comment_list = session.query(models.CommentInfo).filter(
#         and_(models.CommentInfo.article_id == article_id, models.CommentInfo.reply_id == 0)).order_by(
#         models.CommentInfo.created_at.desc()).offset((page_index - 1) * page_size).limit(page_size).all()
#     return comment_list
#
#
# # 用户回复评论，评论表中的reply_id为评论id
# def get_comment_reply_list(session: Session, article_id: int, reply_id: int):
#     comment_list = session.query(models.CommentInfo).filter(
#         and_(models.CommentInfo.article_id == article_id, models.CommentInfo.reply_id == reply_id)).order_by(
#         models.CommentInfo.created_at.desc()).all()
#     return comment_list
#
#
# # 用户评论文章，评论表中的reply_id为0
# def user_comment_article(session: Session, comment: schemas.create_comment):
#     """
#     用户评论文章
#     """
#     if not comment:
#         return None
#     comment = models.CommentInfo(article_id=comment.article_id, from_uid=comment.user_id, content=comment.content,
#                                  replay_id=comment.replay_id)
#     session.add(comment)
#     session.flush()
#     comment_id = comment.id
#     session.commit()
#     return comment_id
#
#
# def increase_article_comments(session: Session, article_id: int):
#     """
#     增加文章评论数
#     """
#     if not article_id:
#         return False
#     article = session.query(models.Article).filter(models.Article.id == article_id).first()
#     if not article:
#         return False
#     article.comments += 1
#     session.commit()
#     return True


def increase_article_views(session: Session, article_id: int):
    """
    增加文章浏览数
    """
    if not article_id:
        return False
    article = session.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        return False
    article.views += 1
    session.commit()
    return True


def increase_article_likes(session: Session, article_id: int):
    """
    增加文章点赞数
    """
    if not article_id:
        return False
    article = session.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        return False
    article.likes += 1
    session.commit()
    return True


def decrease_article_likes(session: Session, article_id: int):
    """
    减少文章点赞数
    """
    if not article_id:
        return False
    article = session.query(models.Article).filter(models.Article.id == article_id).first()
    if not article:
        return False
    article.likes -= 1
    session.commit()
    return True


def get_aticles_by_views_desc(session: Session, page_index: int = 1, page_size: int = 10):
    """
    根据Views从大到小查询并返回多个查询结果的函数
    """
    article_list = session.query(
        models.Article,
        models.User.username,
        models.User.avatar
    ).join(models.User) \
        .order_by(models.Article.views.desc()) \
        .options(joinedload(models.Article.user)) \
        .offset((page_index - 1) * page_size) \
        .limit(page_size).all()

    # 将查询结果转换为字典
    data = []
    for row in article_list:
        article = row[0].__dict__
        article["user"] = {
            "username": row[1],
            "avatar": row[2]
        }
        data.append(article)
    return data


def get_aticles_by_create_time_desc(session: Session, page_index: int, page_size: int):
    """
    获取文章列表，按照创建时间倒序
    """
    article_list = session.query(
        models.Article,
        models.User.username,
        models.User.avatar
    ).join(models.User) \
        .filter(models.Article.Article_status == 1) \
        .order_by(models.Article.created_at.desc()) \
        .options(joinedload(models.Article.user)) \
        .offset((page_index - 1) * page_size) \
        .limit(page_size).all()
    # 将查询结果转换为字典
    data = []
    for row in article_list:
        article = row[0].__dict__
        article["user"] = {
            "username": row[1],
            "avatar": row[2]
        }
        data.append(article)
    return data


def get_week_hot_articles(session: Session):
    """
    获取本周热议文章
    """
    week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    article_list = session.query(
        models.Article,
        models.User.username,
        models.User.avatar
    ).join(models.User) \
        .filter(models.Article.created_at >= week_ago) \
        .order_by(models.Article.views.desc()) \
        .options(joinedload(models.Article.user)) \
        .limit(6).all()
    # 将查询结果转换为字典
    data = []
    for row in article_list:
        article = row[0].__dict__
        article["user"] = {
            "username": row[1],
            "avatar": row[2]
        }
        data.append(article)
    return data


def get_announcement_by_id(session: Session, notice_id: int):
    """
    获取公告详情
    """
    notice = session.query(models.Announcement).filter(models.Announcement.id == notice_id).first()
    return notice


def get_announcement_list_by_create_time_desc(session: Session, page_index: int, page_size: int):
    """
    获取公告列表，按照创建时间倒序
    """
    notice_list = session.query(models.Announcement).order_by(models.Announcement.created_at.desc()).offset(
        (page_index - 1) * page_size).limit(page_size).all()
    return notice_list


# 获取交易帖
def get_transaction(session: Session, page_index: int, page_size: int, trade_type: int):
    article_list = session.query(
        models.Article,
        models.User.username,
        models.User.avatar
    ).join(models.User) \
        .order_by(models.Article.created_at.desc()) \
        .options(joinedload(models.Article.user)) \
        .filter(and_(models.Article.Article_status == 1, models.Article.article_type == 1,
                     models.Article.trade_type == trade_type)) \
        .offset((page_index - 1) * page_size) \
        .limit(page_size).all()
    # 将查询结果转换为字典
    data = []
    for row in article_list:
        article = row[0].__dict__
        article["user"] = {
            "username": row[1],
            "avatar": row[2]
        }
        data.append(article)
    return data


# 获取失物招领
def get_lost(session: Session, page_index: int, page_size: int):
    article_list = session.query(
        models.Article,
        models.User.username,
        models.User.avatar
    ).join(models.User) \
        .order_by(models.Article.created_at.desc()) \
        .options(joinedload(models.Article.user)) \
        .filter(and_(models.Article.Article_status == 1, models.Article.category_id == 14)) \
        .offset((page_index - 1) * page_size) \
        .limit(page_size).all()
    # 将查询结果转换为字典
    data = []
    for row in article_list:
        article = row[0].__dict__
        article["user"] = {
            "username": row[1],
            "avatar": row[2]
        }
        data.append(article)
    return data


def get_articles_by_userid(session: Session, user_id: int, page_index: int, page_size: int):
    """
    根据用户id查询用户文章
    :param session:
    :param user_id:
    :param page_index:
    :param page_size:
    :return:
    """
    articles = session.query(models.Article).filter(models.Article.User_id == user_id).order_by(
        models.Article.created_at.desc()).offset(
        (page_index - 1) * page_size).limit(page_size).all()
    return articles


def get_collections_by_userid(session: Session, user_id: int, page_index: int, page_size: int):
    """
    根据用户id查询用户收藏
    :param session:
    :param user_id:
    :param page_index:
    :param page_size:
    :return:
    """
    collections = session.query(models.Collection) \
        .join(models.Article) \
        .filter(models.Collection.user_id == user_id) \
        .order_by(models.Collection.created_at.desc()) \
        .offset((page_index - 1) * page_size) \
        .limit(page_size) \
        .all()
    article_collections = []
    for collection in collections:
        article_query = session.query(models.Article, models.User) \
            .join(models.User) \
            .filter(models.Article.id == collection.article_id) \
            .options(joinedload(models.Article.user)) \
            .first()
        article = article_query[0].__dict__
        article["user"] = {
            "username": article_query[1].username,
            "avatar": article_query[1].avatar
        }
        article_collections.append(article)
    return article_collections


def get_transactions_by_userid(session: Session, user_id: int, page_index: int, page_size: int):
    """
    根据用户id查询用户交易
    :param session:
    :param user_id:
    :param page_index:
    :param page_size:
    :return:
    """
    transactions = session.query(models.Article, models.User) \
        .join(models.User) \
        .filter(models.Article.article_type == 1) \
        .filter(models.Article.User_id == user_id) \
        .options(joinedload(models.Article.user)) \
        .order_by(models.Article.created_at.desc()) \
        .offset((page_index - 1) * page_size) \
        .limit(page_size).all()
    article_transactions = []
    for transaction in transactions:
        article = transaction[0].__dict__
        article["user"] = {
            "username": transaction[1].username,
            "avatar": transaction[1].avatar
        }
        article_transactions.append(article)
    return article_transactions


def get_pages_articles_by_userid(session: Session, user_id: int):
    """
    根据用户id查询用户文章总数
    :param session:
    :param user_id:
    :return:
    """
    articles = session.query(models.Article).filter(models.Article.User_id == user_id).all()
    return len(articles)


def get_pages_collections_by_userid(session: Session, user_id: int):
    """
    根据用户id查询用户收藏总数
    :param session:
    :param user_id:
    :return:
    """
    collections = session.query(models.Collection) \
        .filter(models.Collection.user_id == user_id) \
        .all()
    return len(collections)


def get_pages_transactions_by_userid(session: Session, user_id: int):
    """
    根据用户id查询用户交易总数
    :param session:
    :param user_id:
    :return:
    """
    transactions = session.query(models.Article) \
        .filter(models.Article.article_type == 1) \
        .filter(models.Article.User_id == user_id) \
        .all()
    return len(transactions)


def get_article_list(session: Session, page_index: int, page_size: int):
    """
    获取用户文章列表
    :param session: 连接数据库的会话
    :param user_id: 用户的id
    :return: 返回文章列表
    """
    article_list = session.query(models.Article, models.User) \
        .join(models.User) \
        .filter(models.Article.article_type == 2) \
        .order_by(models.Article.created_at.desc()) \
        .options(joinedload(models.Article.user)) \
        .offset((page_index - 1) * page_size) \
        .limit(page_size) \
        .all()
    article_tree = []
    for tree in article_list:
        article = tree[0].__dict__
        article["user"] = {
            "username": tree[1].username,
            "avatar": tree[1].avatar
        }
        article_tree.append(article)
    return article_tree