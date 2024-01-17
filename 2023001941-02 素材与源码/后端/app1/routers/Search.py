from datetime import datetime

import redis
from fastapi import APIRouter, Form, Depends, Body

from dependencies import get_session
from hot_words.hot_words import record_search_hotword
from mysql_app.crud_article import search_get_articles
from redis_app.redis_pool import redis_pool

router = APIRouter(
    prefix="/search",
    tags=["搜索模块"]
)

r = redis.Redis(connection_pool=redis_pool, charset="utf-8", decode_responses=True)
# 统计当日搜索热词 top10 的 Sorted Set 名称
sorted_set_today = 'search_hotwords_today'

# 统计当周搜索热词 top10 的 Sorted Set 名称
sorted_set_this_week = 'search_hotwords_this_week'


@router.get("/todat_hotwords", summary="获取10个热门搜索词")
async def get_search_hotwords():
    """
    获取10个热门搜索词
    """
    # 当日 Sorted Set 名称
    sorted_set_name_today = sorted_set_today + ':' + datetime.now().strftime('%Y-%m-%d')
    # 获取当前热搜前十的记录
    hotwords = r.zrevrange(sorted_set_name_today, 0, 6, withscores=True)
    words = []
    for hotword in list(hotwords):
        words.append(dict(word=hotword[0].decode('utf-8')))
    return words


@router.get("/thisweek_hotwords", summary="获取本周的10个热门搜索词")
async def get_search_hotwords():
    """
    获取本周的10个热门搜索词
    """
    # 当周 Sorted Set 名称
    sorted_set_name_this_week = sorted_set_this_week + ':' + datetime.now().strftime('%Y-W%U')
    # 获取当前热搜前十的记录
    hotwords = r.zrevrange(sorted_set_name_this_week, 0, 6, withscores=True)
    words = []
    for hotword in list(hotwords):
        words.append(dict(word=hotword[0].decode('utf-8')))
    return words


@router.post("/tips", summary="搜索提示词")
async def search_tips(search_word: str = Form(...)):
    """
    搜索目标
    """
    # 当周 Sorted Set 名称
    sorted_set_name_this_week = sorted_set_this_week + ':' + datetime.now().strftime('%Y-W%U')
    # 模糊匹配本周搜索词并按照 score 从大到小返回匹配的搜索词
    matched_hotwords = r.zrevrangebyscore(sorted_set_name_this_week, '+inf', '-inf', start=0, num=6, withscores=True)

    matched_hotwords = [hotword for hotword in matched_hotwords if search_word in hotword[0].decode('utf-8')]

    hotwords = []
    if len(matched_hotwords) == 0:
        return [{"value": "没有匹配的搜索词"}]
    # 输出匹配的搜索词
    for i, (hotword, score) in enumerate(matched_hotwords):
        hotword_data = {
            "value": hotword
        }
        hotwords.append(hotword_data)
    return hotwords


@router.post("/searchword", summary="搜索与关键词匹配的文章")
async def search_word(search_word: str = Form(...), session=Depends(get_session)):
    """
    搜索目标
    """
    record_search_hotword(search_word)
    articles = search_get_articles(session, search_word)
    if len(articles) == 0:
        return {"msg": "没有匹配的文章"}
    return articles


# @router.post("/searchwords", summary="搜索与关键词匹配的文章")
# async def search_by_keyword(search_word: str = Body(...), page: int = Body(default=1)):
#     record_search_hotword(search_word)
#     articles = get_aticles_by_search(search_word, page)
#     return articles


@router.post("/clear_redis", summary="清除Redis中的所有数据")
async def clear_redis():
    # 当周 Sorted Set 名称
    sorted_set_name_this_week = sorted_set_this_week + ':' + datetime.now().strftime('%Y-W%U')
    r.delete(sorted_set_name_this_week)
    return {"msg": "清除成功"}
