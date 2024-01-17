from fastapi import APIRouter, Body, Depends

from dependencies import get_session
from mysql_app.crud_comment import *

router = APIRouter(
    prefix="/comment",
    tags=["评论模块"]
)


@router.get('/get_comment_id/{id}',summary="根据id获取评论")
async def get_comment_id(id: int, session=Depends(get_session)):
    comment = get_comment_by_id(session, id)
    return comment


@router.post('/create_new_comment',summary="创建新的评论")
async def create_new_comment(comment: schemas.create_comment = Body(...), session=Depends(get_session)):
    status = create_comment(comment=comment, session=session)
    return status
