from fastapi import APIRouter

router = APIRouter(
    prefix="/manage"
)


@router.get("/menus")
async def get_menus():
    return [{"title": "用户管理"}]
