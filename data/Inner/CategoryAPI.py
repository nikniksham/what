from data import db_session
from data.category import Category
from data.Inner.main_file import raise_error, check_admin
from data.product import Product
from data.ticket import Ticket


def find_by_id(id, session):
    category = session.query(Category).get(id)
    if not category:
        return raise_error(f"Категория не найдена", session)[0]
    return category, session


def get_category_by_id(category_id):
    session = db_session.create_session()
    category, session = find_by_id(category_id, session)
    if type(category) is dict:
        return category
    data = category.to_dict()
    session.close()
    return data


def get_list_categorys():
    session = db_session.create_session()
    categorys = session.query(Category).all()
    data = [item.to_dict(only=("name", "father", "pra_father", "link")) for item in categorys]
    session.close()
    return data


def put_category(admin_email, category_id, args):
    admin, session = check_admin(admin_email)
    if type(admin) is dict:
        return admin
    category, session = find_by_id(category_id, session)
    if type(category) is dict:
        return category
    count = 0
    category_dict = category.to_dict(only=("name", "father", "pra_father", "link"))
    keys = list(filter(lambda key: args[key] is not None and key in category_dict and args[key] != category_dict[key], list(args.keys())))
    for key in keys:
        count += 1
        if key == 'name':
            category.name = args["name"]
        if key == 'father':
            category.father = args["father"]
        if key == 'pra_father':
            category.pra_father = args["pra_father"]
        if key == 'link':
            category.link = args["link"]
    if count == 0:
        return raise_error("Пустой запрос", session)[0]
    session.commit()
    name = category.name
    session.close()
    return {"success": f"Категория {name} успешно изменена"}


def delete_category(admin_email, admin_password, category_id):
    admin, session = check_admin(admin_email)
    if not admin.check_password(admin_password):
        return raise_error("Неправильный пароль")[0]
    category, session = find_by_id(category_id, session)
    if type(category) is dict:
        return category
    products = session.query(Product).filter(Product.category_id == category.id).all()
    if products:
        for product in products:
            tickets = session.query(Ticket).filter(Ticket.product_id == product.id).all()
            if tickets:
                for ticket in tickets:
                    session.delete(ticket)
            session.delete(product)
    session.delete(category)
    session.commit()
    session.close()
    return {'success': f'Категория со всеми товарами успешно удалена'}


def create_category(admin_email, args):
    admin, session = check_admin(admin_email)
    if type(admin) is dict:
        return admin
    if not all(args[key] is not None for key in ['name', 'father', 'pra_father', 'link']):
        return raise_error('Пропущены некоторые аргументы, необходимые для создания темы', session)[0]
    new_category = Category()
    new_category.name = args["name"]
    new_category.father = args["father"]
    new_category.pra_father = args["pra_father"]
    new_category.link = args["link"]
    session.add(new_category)
    session.commit()
    category_id = new_category.id
    session.close()
    return {'success': f'Категория товаров {args["name"]} создана', 'id': int(category_id)}
