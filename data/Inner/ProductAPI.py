from operator import or_

from data import db_session
from data.Inner.OrderAPI import get_order_by_product
from data.Inner.main_file import raise_error, check_admin
from data.category import Category
from data.product import Product
from sqlalchemy import func, and_


def find_by_id(id, session):
    product = session.query(Product).get(id)
    if not product:
        return raise_error(f"Товар не найден", session)
    return product, session


def get_product_by_id(product_id):
    session = db_session.create_session()
    product, session = find_by_id(product_id, session)
    if type(product) is dict:
        return product
    data = product.to_dict(only=("name", "link", "max_discount", "bad_count", "bad_price", "good_count", 'good_price',
                                 "in_stoke", "image", "id", "description", "specifications"))
    session.close()
    return data


def get_product_by_category_id(category_id):
    session = db_session.create_session()
    products = session.query(Product).filter(Product.category_id == category_id).all()
    data = [item.to_dict(only=("name", "link", "max_discount", "bad_count", "bad_price", "good_count", 'good_price',
                               "in_stoke", "image", "id", "description", "specifications")) for item in products]
    session.close()
    return data


def get_all_products(indexes):
    session = db_session.create_session()
    res = []
    for ind in indexes:
        prod = session.query(Product).get(ind)
        if prod:
            res.append(prod.to_dict(only=("name", "link", "max_discount", "bad_count", "bad_price", "good_count",
                                          'good_price', "in_stoke", "image", "id", "description", "specifications")))
    session.close()
    return res

def get_list_products(max_id=None, min_id=None):
    session = db_session.create_session()
    if max_id is None:
        max_id = 999999999999
    if min_id is None:
        min_id = 0
    products = session.query(Product).filter(and_(Product.id <= max_id, Product.id >= min_id)).all()
    data = [item.to_dict(only=("name", "link", "max_discount", "bad_count", "bad_price", "good_count", 'good_price',
                               "in_stoke", "image", "id", "description", "specifications")) for item in products]
    session.close()
    return data


def search_product_by_text(text):
    text = text[:min(len(text), 10)]
    session = db_session.create_session()
    products = []
    for el in [item.to_dict(only=("name", "link", "max_discount", "bad_count", "bad_price", "good_count", 'good_price', "in_stoke", "image", "id", "description", "specifications")) for item in session.query(Product).all()]:
        products.append([0, el])

    for elem in products:
        name = elem[1]["name"].lower()
        for word in text:
            if word in name:
                elem[0] += 1

    products.sort(key=lambda x: -x[0])
    # products = products[:min(len(products), 50)]
    products = list(filter(lambda x: x[0] > 0, products))
    session.close()
    return [prod[1] for prod in products]


def get_more_cheap_products(count):
    session = db_session.create_session()
    prods = session.query(Product).all()
    prods.sort(key=lambda x: -x.max_discount)
    prods = [item.to_dict(only=("name", "link", "max_discount", "bad_count", "bad_price", "good_count", 'good_price',
                                "in_stoke", "image", "id", "description", "specifications")) for item in prods]
    session.close()
    return prods[:min(len(prods), count)]


def get_list_products_by_discount(disc):
    session = db_session.create_session()
    products = session.query(Product).filter(Product.max_discount >= disc).all()
    data = [item.to_dict(only=("name", "link", "max_discount", "bad_count", "bad_price", "good_count", 'good_price',
                               "in_stoke", "image", "id", "description", "specifications")) for item in products]
    session.close()
    # print(len(data))
    return data


def put_product(admin_email, product_id, args):
    admin, session = check_admin(admin_email)
    if type(admin) is dict:
        return admin
    product, session = find_by_id(product_id, session)
    if type(product) is dict:
        return product
    count = 0
    product_dict = product.to_dict(only=("name", "link", "max_discount", "bad_count", "bad_price", "good_count",
                                         'good_price', "in_stoke", "image", "description", "specifications"))
    keys = list(filter(lambda key: args[key] is not None and key in product_dict and args[key] != product_dict[key], list(args.keys())))
    for key in keys:
        count += 1
        if key == 'name':
            product.name = args["name"]
        if key == 'link':
            product.link = args["link"]
        if key == 'max_discount':
            product.max_discount = args["max_discount"]
        if key == 'bad_count':
            product.bad_count = args["bad_count"]
        if key == 'bad_price':
            product.bad_price = args["bad_price"]
        if key == 'good_count':
            product.good_count = args["good_count"]
        if key == 'good_price':
            product.good_price = args["good_price"]
        if key == 'in_stoke':
            product.in_stoke = args["in_stoke"]
        if key == 'image':
            product.image = args["image"]
        if key == 'description':
            product.description = args["description"]
        if key == 'specifications':
            product.specifications = args["specifications"]
    if count == 0:
        return raise_error("Пустой запрос", session)[0]
    session.commit()
    name = product.name
    session.close()
    return {"success": f"Товар {name} успешно изменён"}


def delete_product(admin_email, admin_password, product_id):
    admin, session = check_admin(admin_email)
    if not admin.check_password(admin_password):
        return raise_error("Неправильный пароль")[0]
    product, session = find_by_id(product_id, session)
    if type(product) is dict:
        return product
    session.delete(product)
    session.commit()
    session.close()
    return {'success': f'Товар со всеми заявками успешно удалён'}


def create_product(admin_email, args):
    admin, session = check_admin(admin_email)
    if type(admin) is dict:
        return admin
    if not all(args[key] is not None for key in ["name", "link", "max_discount", "bad_count", "bad_price", "good_count",
                                                 'good_price', "in_stoke", "image", "category_id", "description", "specifications"]):
        return raise_error('Пропущены некоторые аргументы, необходимые для создания товара', session)[0]
    category = session.query(Category).filter(Category.id == args["category_id"]).first()
    if not category:
        return raise_error("Не найдена категория с таким id", session)[0]
    new_product = Product()
    new_product.name = args["name"]
    new_product.link = args["link"]
    new_product.max_discount = args["max_discount"]
    new_product.bad_count = args["bad_count"]
    new_product.bad_price = args["bad_price"]
    new_product.good_count = args["good_count"]
    new_product.good_price = args["good_price"]
    new_product.in_stoke = args["in_stoke"]
    new_product.image = args["image"]
    new_product.description = args["description"]
    new_product.specifications = args["specifications"]
    category.add(new_product)
    session.merge(category)
    session.commit()
    product_id = new_product.id
    session.close()
    return {'success': f'Товар {args["name"]} создан', 'id': int(product_id)}
