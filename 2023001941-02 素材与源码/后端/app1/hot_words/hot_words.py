from datetime import datetime

import redis

from mysql_app.crud_hotwords import create_search_hotword
from mysql_app.database import SessionLocal
from mysql_app.models import SearchHotwords
from redis_app.redis_pool import redis_pool

# 统计当日搜索热词 top10 的 Sorted Set 名称
sorted_set_today = 'search_hotwords_today'

# 统计当周搜索热词 top10 的 Sorted Set 名称
sorted_set_this_week = 'search_hotwords_this_week'

redis_conn = redis.Redis(connection_pool=redis_pool, charset="utf-8", decode_responses=True)

Se = SessionLocal()


def record_top10_to_mysql(sorted_set_name, date_format, session=Se):
    """
    将指定 Sorted Set 中的 top10 记录插入到 MySQL 数据库中，并清空 Sorted Set。
    """
    # 获取当前日期和时间
    current_time = datetime.now()
    current_date = current_time.strftime(date_format)

    # 获取 Sorted Set 中前 10 个搜索热词和它们的分数
    hotwords_with_scores = redis_conn.zrevrangebyscore(sorted_set_name, '+inf', '-inf', start=0, num=10,
                                                       withscores=True)
    for i, (hotword, score) in enumerate(hotwords_with_scores):
        hotword = hotword.decode('utf-8')
        search_hotword = SearchHotwords(
            date=current_date,
            hotword=hotword,
            score=int(score),
            rank=i + 1
        )
        # 将搜索热词记录插入到 MySQL 数据库中
        create_search_hotword(session, search_hotword)
    # 清空 Sorted Set
    redis_conn.delete(sorted_set_name)


# 每次搜索时，将搜索热词添加到 Sorted Set 中并增加分数
def record_search_hotword(hotword):
    """
    将搜索热词添加到当日和当周的 Sorted Set 中，并增加分数
    """
    # 当日 Sorted Set 名称
    sorted_set_name_today = sorted_set_today + ':' + datetime.now().strftime('%Y-%m-%d')

    # 当周 Sorted Set 名称
    sorted_set_name_this_week = sorted_set_this_week + ':' + datetime.now().strftime('%Y-W%U')

    # 将搜索热词添加到 Sorted Set 中并增加分数
    redis_conn.zincrby(sorted_set_name_today, 1, hotword)
    redis_conn.zincrby(sorted_set_name_this_week, 1, hotword)

    # 每天 0 点，将当日 Sorted Set 中的前 10 个搜索热词记录到 MySQL 中，并清空 Sorted Set
    print(datetime.now().hour, datetime.now().weekday())
    IsTime = datetime.now().hour == 0 and datetime.now().minute == 0 and datetime.now().second == 0
    if IsTime:
        record_top10_to_mysql(sorted_set_name_today, '%Y-%m-%d')

    # 每周日，将当周 Sorted Set 中的前 10 个搜索热词记录到 MySQL 中，并清空 Sorted Set
    if datetime.now().weekday() == 6 and IsTime:
        record_top10_to_mysql(sorted_set_name_this_week, '%Y-W%U')
