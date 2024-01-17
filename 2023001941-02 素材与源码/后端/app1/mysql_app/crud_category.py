from sqlalchemy.orm import Session

from mysql_app import models


def create_new_category(session: Session, category_name: str):
    if not category_name:
        return None
    if category_name in get_all_categorys(session):
        return None
    new_category = models.Category(category_name=category_name)
    session.add(new_category)
    session.flush()
    session.commit()
    session.refresh(new_category)
    return new_category.category_id


def get_all_categorys(session: Session):
    categorys = session.query(models.Category).all()
    return categorys


def get_category_id_by_name(session: Session, category_name: str):
    category_id = session.query(models.Category.category_id).filter(
        models.Category.category_name == category_name).first()
    if not category_id:
        category_id = create_new_category(session, category_name)
    return category_id[0]
