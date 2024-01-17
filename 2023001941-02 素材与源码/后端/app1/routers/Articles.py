from typing import List

from fastapi import APIRouter, Body, Depends, Form
from sqlalchemy.exc import SQLAlchemyError

from dependencies import get_session, auth_depend
from mysql_app.crud_article import *
from mysql_app.crud_category import *
from mysql_app.crud_tags import *

router = APIRouter(
    prefix="/article",
    tags=["帖子模块"]
)


@router.post("/create_article", summary="创建帖子")
async def create_article(form_data: schemas.Create_Article = Body(..., description="用户提交的帖子表"),
                         tags: List[str] = Body(...), me: schemas.User = Depends(auth_depend),
                         session=Depends(get_session)):
    """
    创建一个新的文章
    """
    form_data.user_id = me.id
    try:
        new_article_id = create_new_article(session, form_data)
        tags_id = []
        for tag in tags:
            if tag not in get_all_tags_desc(session):
                new_tag_id = create_new_tag(session, tag)
                tags_id.append(new_tag_id)
            else:
                tags_id.append(get_tag_id_by_tag_name(session, tag))
        print(tags_id)
        for tag_id in tags_id:
            create_tags_relatioalship(session, new_article_id, tag_id)
        return new_article_id
    except SQLAlchemyError as e:
        print(e)
        return {"error": "帖子发表失败"}, 500


# 作者修改文章
@router.post("/update_article", summary="修改帖子")
async def update_article(
        form_data: schemas.Update_Article = Body(...),
        me: schemas.User = Depends(auth_depend),
        session=Depends(get_session)):
    """
    修改一个新的文章
    """
    form_data.user_id = me.id
    try:
        update_article_by_article_id(session, form_data)
        return {"msg": "修改成功"}
    except SQLAlchemyError as e:
        print(e)
        return {"error": "帖子修改失败"}, 500


@router.get("/get_article/{article_id}", summary="获取指定的帖子")
async def get_article(article_id: int, session=Depends(get_session)):
    """
    获取指定的文章
    """
    try:
        article = get_article_by_article_id(session, article_id)
        increase_article_views(session, article_id)
        return article
    except SQLAlchemyError as e:
        print(e)
        return {"error": "获取文章失败"}, 500


@router.post("/create_category", summary="创建分类")
async def create_category(category_name: str = Form(..., description="用户提供的分类"), session=Depends(get_session)):
    """
    创建一个新的分类
    """
    try:
        new_category_id = create_new_category(session, category_name)
        return new_category_id
    except SQLAlchemyError as e:
        print(e)
        return {"error": "分类创建失败"}, 500


@router.get("/get_categories", summary="获取所有分类")
async def get_categories(session=Depends(get_session)):
    """
    获取所有分类
    """
    try:
        categories = get_all_categorys(session)

        return categories
    except SQLAlchemyError as e:
        print(e)
        return {"error": "获取分类失败"}, 500


@router.get("/get_tags", summary="获取所有标签")
async def get_tags(session=Depends(get_session)):
    """
    获取所有标签
    """
    try:
        tags = []
        for tag in get_all_tags_desc(session):
            tag_data = {
                "value": tag
            }
            tags.append(tag_data)
        return tags
    except SQLAlchemyError as e:
        print(e)
        return {"error": "获取标签失败"}, 500


@router.post("/create_tag", summary="创建标签")
async def create_tag(tag_name: str = Form(..., description="用户提供的标签"), session=Depends(get_session)):
    """
    创建一个新的标签
    """
    try:
        new_tag_id = create_new_tag(session, tag_name)
        return new_tag_id
    except SQLAlchemyError as e:
        print(e)
        return {"error": "标签创建失败"}, 500


@router.post("/search_tag", summary="搜索标签")
async def search_tag(search_word: str = Form(...), session=Depends(get_session)):
    try:
        tags = search_tag_by_name(session, search_word)
        return tags
    except SQLAlchemyError as e:
        print(e)
        return {"error": "找不到匹配的标签"}, 500


@router.post("/get_lastest_article", summary="获取最新文章")
async def get_lastest_article(page: int = Form(default=1), session=Depends(get_session)):
    """
    获取最新文章
    """
    try:
        lastest_articles = get_aticles_by_create_time_desc(session, page_index=page, page_size=6)
        return lastest_articles
    except SQLAlchemyError as e:
        print(e)
        return {"error": "获取最新文章失败"}, 500


@router.get("/week_hot_articles", summary="获取本周热门文章")
async def get_week_hot_article(session=Depends(get_session)):
    """
    获取本周热门文章
    """
    article_data = []
    try:
        week_hot_articles = get_week_hot_articles(session)
        for article in week_hot_articles:
            title = article["title"]
            views = article["views"]
            article_id = article["id"]
            article_type = article["article_type"]
            data = {
                "title": title,
                "article_id": article_id,
                "views": views,
                "article_type": article_type
            }
            article_data.append(data)
        return article_data
    except SQLAlchemyError as e:
        print(e)
        return {"error": "获取本周热门文章失败"}, 500


@router.post("/get_hotest_article", summary="获取最热文章")
async def get_hot_article(page: int = Form(default=1), session=Depends(get_session)):
    """
    获取最热文章
    """
    article_data = []
    try:
        hot_articles = get_aticles_by_views_desc(session, page_index=page, page_size=6)
        # for article in hot_articles:
        #     title = article["title"]
        #     views = article["views"]
        #     article_id = article["id"]
        #     data = {
        #         "title": title,
        #         "article_id": article_id,
        #         "views": views
        #     }
        #     article_data.append(data)
        return hot_articles
    except SQLAlchemyError as e:
        print(e)
        return {"error": "获取最热文章失败"}, 500


# 获取用户点赞转态
@router.post("/like_statue", summary="获取用户点赞文章的转态")
def get_like_statue(article_id: int = Form(...), session=Depends(get_session), me: schemas.User = Depends(auth_depend)):
    try:
        statue = check_user_like_article(session, me.id, article_id)
        if statue:
            return {"statue": True}
        else:
            return {"statue": False}
    except SQLAlchemyError as e:
        print(e)
        return {"error": "获取点赞状态失败"}, 500


# 点赞或者取消点赞文章
@router.post("/like_article", summary="用户点赞文章")
def like_article(article_id: int = Form(...), session=Depends(get_session), me: schemas.User = Depends(auth_depend)):
    try:
        statue = check_user_like_article(session, me.id, article_id)
        if statue:
            user_unlike_article(session, me.id, article_id)
            decrease_article_likes(session, article_id)
            return {"statue": "取消点赞"}
        else:
            user_like_article(session, me.id, article_id)
            increase_article_likes(session, article_id)
            return {"statue": "成功点赞"}
    except SQLAlchemyError as e:
        print(e)
        return {"error": "操作失败"}, 500


# 获取用户收藏状态
@router.post("/collect_statue", summary="获取用户收藏文章状态")
def get_collect_statue(article_id: int = Form(...), session=Depends(get_session),
                       me: schemas.User = Depends(auth_depend)):
    try:
        statue = check_user_collection_article(session, me.id, article_id)
        if statue:
            return {"statue": True}
        else:
            return {"statue": False}
    except SQLAlchemyError as e:
        print(e)
        return {"error": "获取收藏状态失败"}, 500


# 收藏或者取消收藏文章
@router.post("/collect_article", summary="用户收藏文章")
def collect_article(article_id: int = Form(...), session=Depends(get_session), me: schemas.User = Depends(auth_depend)):
    try:
        statue = check_user_collection_article(session, me.id, article_id)
        if statue:
            user_uncollection_article(session, me.id, article_id)
            return {"statue": "取消收藏"}
        else:
            user_collection_article(session, me.id, article_id)
            return {"statue": "成功收藏"}
    except SQLAlchemyError as e:
        print(e)
        return {"error": "操作失败"}, 500


#
# # 用户评论文章
# @router.post("/comment_article", summary="用户评论文章")
# def comment_article(form_data: schemas.create_comment = Body(...), me: schemas.User = Depends(auth_depend),
#                     session=Depends(get_session)):
#     try:
#         comment_id = user_comment_article(session, form_data)
#         increase_article_comments(session, form_data.article_id)
#         return {
#             "statue": "评论成功",
#             "comment_id": comment_id
#         }
#     except SQLAlchemyError as e:
#         print(e)
#         return {"error": "评论失败"}, 500
#
#
# # 获取文章评论
# @router.post("/get_article_comment", summary="获取文章评论")
# def get_article_comment(article_id: int = Form(...), session=Depends(get_session)):
#     try:
#         comments = get_comment_list(session, article_id)
#         return comments
#     except SQLAlchemyError as e:
#         print(e)
#         return {"error": "获取评论失败"}, 500
#
#
# # 获取文章评论的回复
# @router.post("/get_comment_reply", summary="获取文章评论的回复")
# def get_comment_reply(article_id: int = Form(...), comment_id: int = Form(...), session=Depends(get_session)):
#     try:
#         replies = get_comment_reply_list(session, article_id, comment_id)
#         return replies
#     except SQLAlchemyError as e:
#         print(e)
#         return {"error": "获取回复失败"}, 500


# 获取公告
@router.post("/get_announcement", summary="获取指定公告详情")
def get_notice(announcement_id: int = Form(...), session=Depends(get_session)):
    try:
        notice = get_announcement_by_id(session, announcement_id)
        return notice
    except SQLAlchemyError as e:
        print(e)
        return {"error": "获取公告失败"}, 500


# 获取公告列表
@router.post("/get_announcement_list", summary="获取公告列表")
def get_announcement_list(page: int = Form(...), session=Depends(get_session)):
    try:
        announcements = get_announcement_list_by_create_time_desc(session, page_index=page, page_size=8)
        return announcements
    except SQLAlchemyError as e:
        print(e)
        return {"error": "获取公告列表失败"}, 500


# 获取交易帖
@router.post("/get_trade_article", summary="获取交易帖")
async def get_trade_article(trade_type: int = Form(default=0), page: int = Form(default=1),
                            session=Depends(get_session)):
    try:
        article = get_transaction(session, page_index=page, page_size=6, trade_type=trade_type)
        return article
    except SQLAlchemyError as e:
        print(e)
        return {"error": "获取文章失败"}, 500


# 获取失物招领
@router.post("/get_lost_article", summary="获取失物招领")
async def get_trade_article(page: int = Form(default=1), session=Depends(get_session)):
    try:
        article = get_lost(session, page_index=page, page_size=6)
        return article
    except SQLAlchemyError as e:
        print(e)
        return {"error": "获取文章失败"}, 500


# 获取树洞帖
@router.post("/get_article_tree_hole", summary="获取树洞帖")
async def get_article(page: int = Form(default=1), session=Depends(get_session)):
    try:
        article = get_article_list(session, page_index=page, page_size=6)
        return article
    except SQLAlchemyError as e:
        print(e)
        return {"error": "获取文章失败"}, 500
