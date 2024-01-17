from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload
from . import schemas, models


def get_comment_by_id(session: Session, id: int):
    comment = session.query(models.CommentInfo).options(joinedload(models.CommentInfo.from_user)).filter(
        models.CommentInfo.article_id == id).all()
    comments = []
    for a in comment:
        comments.append({
            "content": a.content,
            "reply_id": a.reply_id,
            "likes": a.likes,
            "id": a.id,
            "created_at": a.created_at,
            "username": a.from_user.username,
            "avatar": a.from_user.avatar
        })
    return comments


def create_comment(comment: schemas.create_comment, session: Session):
    new_comment = models.CommentInfo(article_id=comment.article_id,
                                     from_uid=comment.user_id,
                                     content=comment.content,
                                     reply_id=comment.reply_id)
    session.add(new_comment)
    session.commit()
    session.flush()
    return {"status": 'ok'}
