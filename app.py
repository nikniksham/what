import json
import os
from flask import Flask, render_template
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask import Flask, render_template, redirect, request
from flask_restful import abort
from data import db_session
from data.Inner.CategoryAPI import get_list_categorys, get_category_by_name
from data.Inner.OrderAPI import get_order_by_product, create_order, put_order, change_info
from data.Inner.PersonAPI import create_person, person_order_change
from data.category import Category
from data.forms import LoginForm, RegisterForm
from data.person import Person
from data.Inner.ProductAPI import get_list_products, get_product_by_category_id, get_product_by_id, \
    get_list_products_by_discount, get_more_cheap_products
from data.product import Product

application = Flask(__name__)
application.config['SECRET_KEY'] = "test_key"  # os.urandom(64)

db_session.global_init("db/opt4you.sqlite")
login_manager = LoginManager()
login_manager.init_app(application)

category_map = {}
for_udobstvo = {}
need_load = False


def load_category_map():
    session = db_session.create_session()
    # prods = session.query(Product).all()
    # for prod in prods:
    #     session.delete(prod)
    # session.commit()
    for category in session.query(Category).all():
        if category.pra_father not in category_map:
            category_map[category.pra_father] = {"children": {}}
        if category.father:
            if category.father not in category_map[category.pra_father]["children"]:
                category_map[category.pra_father]["children"][category.father] = {"kids": {}}
            category_map[category.pra_father]["children"][category.father]["kids"][category.name] = {
                "goods": [get_product_by_category_id(category.id)]}
            for_udobstvo[category.name] = f"{category.pra_father}||{category.father}"
        else:
            category_map[category.pra_father]["children"][category.name] = {
                "goods": [get_product_by_category_id(category.id)]}
            for_udobstvo[category.name] = f"{category.pra_father}"
    session.close()


def get_render_template(template_name, title, **kwargs):
    return render_template(template_name, title=title, category_map=get_list_categorys(), user_is_auth=not current_user.is_anonymous, **kwargs)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    user = session.query(Person).get(user_id)
    session.close()
    return user


@application.route('/')
def hello_world():
    return redirect("/catalog")
    # return get_render_template('main.html', title='Главная')


@application.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if not current_user.is_anonymous:
        return redirect("/")
    if request.method == 'POST':
        res = "Пароли не совпадают"
        if form.password.data == form.password_again.data:
            res = create_person(args={"fullname": form.fullname.data, "email": form.email.data, "new_password":
                form.password.data})
            if "success" in res:
                return redirect("/login")
            res = res["error"]
        return get_render_template('register.html', title='Регистрация', message=res, form=form)
    return get_render_template('register.html', title='Регистрация', form=form)


@application.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if not current_user.is_anonymous:
        return redirect("/")
    if request.method == 'POST':
        session = db_session.create_session()
        user = session.query(Person).filter(Person.email == form.email.data).first()
        session.close()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return get_render_template('login.html', title='Авторизация', message="Неправильный логин или пароль",form=form)
    return get_render_template('login.html', title='Авторизация', form=form)


@application.route('/logout')
@login_required
def logout_page():
    logout_user()
    return redirect("/")


@application.route('/catalog')
def catalog():
    return get_render_template('catalog.html', title='Каталог', products=get_more_cheap_products(50))


@login_required
@application.route('/profile')
def profile():
    return get_render_template('profile.html', title='Профиль')


@application.route('/catalog/<string:cat>')
def catalog_category(cat):
    cat = get_category_by_name(cat)
    if "error" in cat:
        return redirect("/")
    return get_render_template('catalog.html', title='Каталог', products=get_product_by_category_id(cat["id"]))


@application.route('/order')
def order():
    return get_render_template('place_an_order.html', title="Оформление заказа")


@application.route('/product/<int:id>')
def product(id):
    product = get_product_by_id(id)
    if "error" in product:
        abort(404)
    return get_render_template('product.html', title="Страница товара", product=product)


@application.route('/tmp')
def tmp():
    return get_render_template('tmp.html', title="Оформление заказа")


# @application.route('/place_an_order', methods=['POST', 'GET'])
# def place_an_order():
#     if request.method == 'POST':
#         name = request.form.get('name')
#         email = request.form.get('email')
#         tel = request.form.get('tel')
#         address = request.form.get('address')
#         index = request.form.get('index')
#         payment_method = request.form.get('payment_method')
#         comment = request.form.get('comment')
#         app_logic.make_an_order(name, email, tel, address, index, payment_method, comment)
#     return redirect('/')

@application.route("/change-count-in-basket", methods=["POST"])
def change_count_in_basket():
    req = json.loads(request.form['canvas_data'])
    product = get_product_by_id(req["prod_id"])

    if product is dict:
        print("Самый умный?", product)

    order = get_order_by_product(req["prod_id"], product["good_count"])

    res = change_info(order["id"], current_user.id, req['count'])

    if res["id"] in [1, 2, 3]:
        person_order_change(current_user.email, order["id"], True)
    elif res["id"] == 0:
        person_order_change(current_user.email, order["id"], False)
    print(res)

    order = get_order_by_product(req["prod_id"], product["good_count"])

    # sid = str(res['item'])
    # if 'message' not in product:
    #     if not session.get('cart'):
    #         session['cart'] = {'total_cost': 0, 'total_count': 0, 'total_saving': 0}
    #     if sid not in session['cart']:
    #         session['cart'][sid] = {"count": 0, "cost": 0, "saving": 0, 'image': ""}
    #     session['cart'][sid]['count'] += 1
    #     session['cart'][sid]['image'] = product['image'].split("//")[0]
    #     session['cart'][sid]['name'] = product['name']
    #     session['cart'][sid]['price'] = product['price']
    #     session['cart'][sid]['old_price'] = product['old_price']
    #     session['cart'][sid]['cost'] = session['cart'][sid]['count'] * int(product['price'])
    #     session['cart'][sid]['saving'] = session['cart'][sid]['count'] * (int(product['old_price']) - int(product['price']))
    #     session.modified = True
    # eval_cart()
    # # print(session['cart'])
    # # print("INCREMENT")
    # return json.dumps(session['cart'])
    for key in order.keys():
        product[key] = order[key]
    return json.dumps(product)


@application.route("/load-order", methods=["POST"])
def load_order():
    req = json.loads(request.form['canvas_data'])
    return json.dumps(get_order_by_product(req["prod_id"], req["good_count"]))


if __name__ == '__main__':
    application.run()
