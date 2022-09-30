import json
import os
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask import Flask, render_template, redirect, request, session
from flask_restful import abort
from data import db_session
from data.Inner.CategoryAPI import get_list_categorys, get_category_by_name
from data.Inner.OrderAPI import get_order_by_product, get_orders_by_product_indexes, create_orders_by_info, \
    get_list_orders_by_indexes
from data.Inner.PersonAPI import create_person, person_order_change
from data.category import Category
from data.forms import LoginForm, RegisterForm
from data.person import Person
from data.Inner.ProductAPI import get_product_by_category_id, get_product_by_id, get_more_cheap_products, \
    search_product_by_text, get_all_products

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
    if "products" in kwargs:
        kwargs["pages"] = []
        for i in range(1, len(kwargs["products"]) // 20 + (0 if (len(kwargs["products"]) % 20 == 0) else 1) + 1):
            kwargs["pages"].append([(i - 1) * 20, min([i * 20, len(kwargs['products'])])])
        kwargs["cur_page"] = 0
    return render_template(template_name, title=title, category_map=get_list_categorys(), user_is_auth=not current_user.is_anonymous,
                           cart=(session['cart'] if session.get('cart') else None), **kwargs)


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
    if current_user.is_anonymous:
        return redirect("/login")
    logout_user()
    return redirect("/")


@application.route('/cart')
def cart():
    return get_render_template('cart.html', title='Каталог', products=get_more_cheap_products(50))


@application.route('/catalog')
def catalog():
    return get_render_template('catalog.html', title='Каталог', products=get_more_cheap_products(50))


@application.route('/profile')
def profile():
    if current_user.is_anonymous:
        return redirect("/login")
    return get_render_template('profile.html', title='Профиль')


@application.route('/catalog/<string:cat>')
def catalog_category(cat):
    cat = get_category_by_name(cat)
    if "error" in cat:
        return redirect("/")
    if cat["id"] == 0:
        return redirect("/catalog")
    return get_render_template('catalog.html', title='Каталог', products=get_product_by_category_id(cat["id"]))


@application.route("/catalog/request/<string:text>")
def catalog_search(text):
    res = search_product_by_text(text.lower().split("||"))
    return get_render_template("catalog.html", title="Каталог", products=res)


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


@application.route("/place-an-order")
def place_an_order():
    if current_user.is_anonymous:
        return redirect("/login")

    res = make_order()

    return redirect("/profile")


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
    # print(req)

    if "error" in product:
        return redirect("/")
    #
    if not session.get('cart'):
        session['cart'] = {'orders': {}, 'total_count': 0, 'total_cost': 0}

    req["prod_id"] = str(req["prod_id"])

    if req["prod_id"] not in session['cart']['orders'] and req["count"] > 0:
        # print(req["prod_id"], session['cart']['orders'])
        session['cart']['orders'][req["prod_id"]] = [min(999, req["count"]), product['good_price']]
    elif req["count"] > 0:
        # print(req["count"], session['cart']['orders'][req["prod_id"]][0])
        session['cart']['orders'][req["prod_id"]][0] = min(999, req["count"] + session['cart']['orders'][req["prod_id"]][0])
    elif req["prod_id"] in session['cart']['orders'] and req["count"] < 0:
        if session['cart']['orders'][req["prod_id"]][0] + req["count"] > 0:
            session['cart']['orders'][req["prod_id"]][0] += req["count"]
        else:
            del session['cart']['orders'][req["prod_id"]]

    session.modified = True

    keys = list(session['cart']['orders'].keys())
    session['cart']['total_count'] = sum([session['cart']['orders'][key][0] for key in keys])
    session['cart']['total_cost'] = sum([session['cart']['orders'][key][0] * session['cart']['orders'][key][1] for key in keys])
    # print(session['cart'])
    return json.dumps(session['cart'])


@application.route("/load-order", methods=["POST"])
def load_order():
    req = json.loads(request.form['canvas_data'])
    return json.dumps(get_order_by_product(req["prod_id"]))


@application.route("/load-all-orders", methods=["POST"])
def load_all_orders():
    res = get_orders_by_product_indexes(json.loads(request.form['canvas_data'])["indexes"])
    return json.dumps(res)


@application.route("/load-all-products", methods=["POST"])
def load_all_products():
    res = get_all_products(json.loads(request.form['canvas_data'])["indexes"])
    return json.dumps(res)


@application.route("/load-all-orders-by-indexes", methods=["POST"])
def load_all_orders_by_indexes():
    res = get_list_orders_by_indexes([int(key.split(":")[0]) for key in json.loads(request.form['canvas_data'])["indexes"].split("|")])
    return json.dumps(res)


def make_order():
    if current_user.is_anonymous:
        return redirect("/")

    if not session.get('cart'):
        res = {"error": "cart is empty"}
    else:
        res = create_orders_by_info(session["cart"]["orders"], current_user.id)

    session['cart'] = {'orders': {}, 'total_count': 0, 'total_cost': 0}

    session.modified = True

    return res


if __name__ == '__main__':
    application.run()
