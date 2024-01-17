import redis
from redis_app.redis_pool import redis_pool
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Form

from dependencies import get_session, auth_depend
# from mysql_app.crud_chat import get_history_msg, get_chatlist, create_new_msg
from mysql_app.crud_chat import *
from mysql_app.schemas import New_msg

# 连接 Redis 数据库
pool = redis_pool
redis_conn = redis.Redis(connection_pool=pool)
max_length = 2000

router = APIRouter(
    prefix="/chat",
    tags=["聊天模块"]
)


# public

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/to/public")
async def chat_public(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            redis_conn.ltrim('chat_history', 0, max_length - 1)
            redis_conn.rpush('public', data)
            await manager.broadcast(f"{data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.get("/clearhistory/pulic", summary="清楚聊天大厅历史")
async def clear_history(me: schemas.User = Depends(auth_depend)):
    redis_conn.delete('public')
    return {"msg": "清除成功"}


@router.get("/online", summary="在线人数")
async def get_online():
    return len(manager.active_connections)


@router.get("/history/pulic", summary="聊天大厅历史")
async def get_history(me: schemas.User = Depends(auth_depend)):
    chat_history = redis_conn.lrange('public', -200, -1)
    return chat_history


# personal
to_users = {}


@router.websocket("/to/{from_name}")
async def websocket_endpoint(websocket: WebSocket, from_name, session=Depends(get_session)):
    await websocket.accept()
    to_users[from_name] = websocket
    msg = None
    try:
        while True:
            # 接收来自客户端的消息
            message = await websocket.receive_text()

            msg = New_msg.parse_raw(message)

            # 将消息发送到目标用户
            await websocket.send_text(message)
            if msg.to_name in to_users.keys():
                await to_users[msg.to_name].send_text(message)

            # 将消息储存
            create_new_msg(session, msg)
            print(msg)
    finally:
        if msg is not None:
            if msg.from_name in to_users:
                del to_users[msg.from_name]


@router.post("/history/person", summary="获取私聊记录")
async def get_history(username: str = Form(...), to_name: str = Form(...), session=Depends(get_session),
                      me: schemas.User = Depends(auth_depend)):
    try:
        history_msg = get_history_msg(session, username, to_name)
        # set_is_read(session, username, to_name)
        return history_msg
    except SQLAlchemyError as e:
        print(e)
        return {"error": "获取chatlist失败"}, 500


@router.get("/chatlist/{to_name}", summary="获取聊天列表")
async def get_chat_list(to_name: str, session=Depends(get_session), me: schemas.User = Depends(auth_depend)):
    try:
        chatlist = get_chatlist(session, to_name)
        return chatlist
    except SQLAlchemyError as e:
        print(e)
        return {"error": "获取chatlist失败"}, 500


@router.post("/create_msg", summary="测试接口，创建消息")
async def get_chat_list(msg: schemas.New_msg, session=Depends(get_session), me: schemas.User = Depends(auth_depend)):
    try:
        msg = create_new_msg(session, msg)
        return msg
    except SQLAlchemyError as e:
        print(e)
        return {"error": "获取chatlist失败"}, 500
