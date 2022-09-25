import openpyxl
from data import db_session
from data.category import Category
from data.product import Product
from data.Inner.ProductAPI import put_product

db_session.global_init("db/opt4you.sqlite")

session = db_session.create_session()

wb = openpyxl.load_workbook(filename='opt.xlsx')


def create_category(args):
    session = db_session.create_session()
    cat = session.query(Category).filter(Category.name == args["name"]).first()
    if not cat:
        cat = Category()
        cat.name = args["name"]
        cat.id = int(args["id"])
        session.add(cat)
        session.commit()
    cat_id = cat.id
    session.close()
    return {'success': f'Категория {args["name"]} создана', 'id': cat_id}


def create_product(args):
    session = db_session.create_session()
    cat = session.query(Category).filter(Category.id == args["cat_id"]).first()
    prod_id = None
    if cat:
        old = session.query(Product).filter(Product.name == args["name"]).first()
        if not old:
            prod = Product()
            # if args["cur_id"]:
            #     prod.id = args["cur_id"]
            prod.name = args["name"]
            prod.link = args["link"]
            prod.max_discount = args["max_discount"]
            prod.in_stoke = args["in_stoke"] == '=TRUE()'
            prod.bad_count = args["bad_count"]
            prod.bad_price = args["bad_price"]
            prod.good_count = args["good_count"]
            prod.good_price = args["good_price"]
            prod.image = args["image"]
            cat.product.append(prod)
            session.merge(cat)
            # session.add(prod)
            session.commit()
            prod_id = prod.id
    session.close()
    return {'success': f'Товар {args["name"]} создан', 'id': prod_id}


# sheet = wb["категории"]
# ind = 2
# while True:
#     if not sheet[f'A{ind}'].value:
#         break
#     print(create_category({"name": sheet[f'B{ind}'].value, "id": sheet[f"A{ind}"].value}))
#     ind += 1
#
# sheet = wb["товары"]
# ind = 2
# while True:
#     if not sheet[f'A{ind}'].value:
#         break
#     print(create_product(
#         {"cat_id": sheet[f'B{ind}'].value, "name": sheet[f'C{ind}'].value, "max_discount": sheet[f'D{ind}'].value,
#          "in_stoke": sheet[f'E{ind}'].value, "link": sheet[f'F{ind}'].value, "bad_price": sheet[f'G{ind}'].value,
#          "bad_count": sheet[f'H{ind}'].value, "good_price": sheet[f'I{ind}'].value,
#          "good_count": sheet[f'J{ind}'].value, "id": sheet[f"A{ind}"].value,
#          "image": sheet[f'K{ind}'].value}))
#     ind += 1
#
# sheet = wb["товары"]
# ind = 2
# while True:
#     if not sheet[f'A{ind}'].value:
#         break
#     print(int(sheet[f'A{ind}'].value), sheet[f"L{ind}"].value, sheet[f'M{ind}'].value)
#     print(put_product("admin@admin.com", ind - 1, {"description": sheet[f"L{ind}"].value, "specifications": sheet[f'M{ind}'].value}))
#     ind += 1
# session.commit()
# session.close()
