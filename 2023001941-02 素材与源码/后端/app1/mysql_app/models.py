# 用于存放数据库模型 数据库模型表
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    String,
    VARCHAR,
    Boolean,
    ForeignKey
)
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship

from mysql_app.database import Base


class BaseMixin:
    """model的基类,所有model都必须继承"""
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    updated_at = Column(DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now(),
                        index=True)
    deleted_at = Column(DateTime)  # 可以为空, 如果非空, 则为软删


# __tablename__ 代表表名
# Column : 代表数据表中的一列，内部定义了数据类型
# primary_key：主键
'''
Column常用参数
    default：默认值。
    nullable：是否为空。
    primary_key：是否是为主键。
    unique：是否唯一。
    autoincrement：是否自增长。
    onupdate：更新的时间执行的函数。
    name：该属性在数据库中的字段映射。
'''


class Category(Base):
    __tablename__ = "Category"
    category_id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment="分类id")
    category_name = Column(String(10), unique=True, comment="分类名字")


# class Data(Base):
#     __tablename__ = "Data"
#     data_id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment="数据id")
#     likes = Column(Integer, default=0, comment="点赞量")
#     views = Column(Integer, default=0, comment="浏览量")
#     comments = Column(Integer, default=0, comment="评论数")

class User(Base, BaseMixin):
    __tablename__ = "User"
    username = Column(String(20), unique=True, comment="用户名")
    password = Column(String(300), comment="密码，通过hash进行编码过")
    gender = Column(Integer, default=0, comment="性别")
    # gender为0时为未知 为1时为男性 为2时为女性 为3时为保密 为4时为其他
    email = Column(VARCHAR(length=36), unique=True, comment="邮箱")
    description = Column(VARCHAR(length=200), default="你还没有任何个人简介，快来添加属于你自己的个性介绍吧！！", comment="个人简介")
    avatar = Column(String(300), default="default_avatar.jpg", comment="头像地址")
    student_ID_Certification = Column(String(10), default="", comment="学号认证")
    is_active = Column(Boolean, default=True, comment="是否处于使用")
    article = relationship("Article", back_populates="user")


class Article(Base, BaseMixin):
    __tablename__ = "Article"
    category_id = Column(Integer, ForeignKey(Category.category_id), comment="分类Id")
    article_type = Column(Integer, comment="文章类型")
    # article_type为0时为普通文章
    # article_type为1时为交易文章
    # article_type为2时为树洞文章
    transaction_url = Column(String(200), nullable=True, comment="交易URL")
    User_id = Column(Integer, ForeignKey(User.id), comment="文章创建者")
    title = Column(VARCHAR(length=200), comment="标题")
    description = Column(VARCHAR(length=200), comment="描述")
    content = Column(LONGTEXT, comment="帖子内容,内为为富文本内容")
    # 价格
    price = Column(Integer, default=0, comment="价格")
    # trade_type 1为出售，2为求购
    trade_type = Column(Integer, default=0, comment="交易类型")
    # trade_stutas为0时为未失效，1为已失效
    trade_stutas = Column(Integer, default=0, comment="交易状态")
    # data_id = Column(Integer, ForeignKey(Data.data_id), comment="点赞量,浏览量,评论数")
    likes = Column(Integer, default=0, comment="点赞量")
    views = Column(Integer, default=0, comment="浏览量")
    comments = Column(Integer, default=0, comment="评论数")
    Article_status = Column(Integer, comment="帖子转态,0草稿，1发布")
    user = relationship("User", back_populates="article")


class Tags(Base):
    __tablename__ = "Tags"
    tag_id = Column(Integer, primary_key=True, autoincrement=True, index=True, comment="标签id")
    tag_name = Column(String(10), unique=True, comment="标签名字")
    count_used = Column(Integer, default=0, comment="标签被使用的次数")


class TagRelationship(Base, BaseMixin):
    __tablename__ = "Tag_Relationship"
    article_id = Column(Integer, ForeignKey(Article.id), comment="帖子id")
    tag_id = Column(Integer, ForeignKey(Tags.tag_id), comment="tag_id")


# 评论表
class CommentInfo(Base, BaseMixin):
    __tablename__ = "Comments_info"
    article_id = Column(Integer, ForeignKey(Article.id), comment="帖子id")
    from_uid = Column(Integer, ForeignKey(User.id), comment="评论者id")
    from_user = relationship("User", foreign_keys=[from_uid], backref="comments")
    content = Column(LONGTEXT, comment="内容")
    reply_id = Column(Integer, comment="回复id（评论id2）")
    likes = Column(Integer, default=0, comment="点赞量")


'''
我们设计的评论表是一张递归表
上图的第三条评论的replyid为0，可以将它分为第一层的数据；
第二条评论是针对第三条评论的回复，故评论三是评论二的上级，那么评论二可以分为第二层数据；
以此类推，第一条评论可以分为第三层的数据……因此，我们可以先将第一层的数据查出来，追加到评论列表中，之后再根据它的主键ID去查询它下一层的评论数据。
不停的遍历它的下一层，直到下一层没有数据为止
'''


# class CommentReply(Base, BaseMixin):
#     __tablename__ = "Comments_Reply"
#     comment_id = Column(Integer, ForeignKey(CommentInfo.id), comment="帖子id")
#     reply_id = Column(Integer, ForeignKey(User.id), comment="回复目标id")
#     # 如果reply_type是comment的话，那么reply_id＝comment_id
#     # 如果reply_type是reply的话，这表示这条回复的父回复
#     reply_type = Column(Integer, comment="回复的类型")
#     # 回复可以是针对评论的回复(comment)  0表示
#     # 也可以是针对回复的回复(reply)     1表示
#     from_uid = Column(Integer, ForeignKey(User.id), comment="回复用户id")
#     to_uid = Column(Integer, ForeignKey(User.id), comment="目标用户id")
#     content = Column(LONGTEXT, comment="内容")
#     likes = Column(Integer, default=0, comment="点赞量")

class Collection(Base, BaseMixin):
    __tablename__ = "Collection"
    user_id = Column(Integer, ForeignKey(User.id), comment="用户id")
    article_id = Column(Integer, ForeignKey(Article.id), comment="文章id")


# 文章点赞关系表
class ArticleLike(Base):
    __tablename__ = "article_like"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    article_id = Column(Integer, ForeignKey(Article.id), comment="文章id")
    user_id = Column(Integer, ForeignKey(User.id), comment="用户id")


class SearchHotwords(Base):
    __tablename__ = "search_hotwords"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    date = Column(DateTime, nullable=False)
    hotword = Column(String(255), nullable=False, unique=True, comment="热词")
    score = Column(Integer, nullable=False, comment="次数")
    rank = Column(Integer, nullable=False, comment="排序")


# 公告表
class Announcement(Base, BaseMixin):
    __tablename__ = "announcement"
    title = Column(String(255), nullable=False, comment="标题")
    content = Column(LONGTEXT, nullable=False, comment="内容")
    is_active = Column(Boolean, default=True, comment="是否处于使用")


# 聊天记录表
class ChatMsg(Base):
    __tablename__ = "ChatMsg"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    date = Column(DateTime, nullable=False, default=datetime.now())
    from_name = Column(String(20), unique=False, comment="发信人用户名")
    to_name = Column(String(20), unique=False, comment="收信人用户名")
    from_user_avatar = Column(String(300), comment="发信人的头像")
    content = Column(LONGTEXT, nullable=False, comment="内容")
    is_read = Column(Boolean, default=False, comment="是否已读")
