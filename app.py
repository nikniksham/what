import os

from flask import Flask, render_template
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask import Flask, render_template, redirect, request
from data import db_session
from data.Inner.PersonAPI import create_person
from data.category import Category
from data.forms import LoginForm, RegisterForm
from data.person import Person
from data.Inner.ProductAPI import get_list_products, get_product_by_category_id
import app_logic

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

db_session.global_init("db/opt4you.sqlite")
login_manager = LoginManager()
login_manager.init_app(app)

category_map = {}
for_udobstvo = {}
need_load = False


def load_category_map():
    session = db_session.create_session()
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
    if not category_map and need_load:
        load_category_map()
    return render_template(template_name, title=title, category_map=category_map, **kwargs)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    user = session.query(Person).get(user_id)
    session.close()
    return user


@app.route('/')
def hello_world():
    return get_render_template('main.html', title='Главная')


@app.route("/register", methods=['GET', 'POST'])
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


@app.route('/login', methods=['GET', 'POST'])
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


@app.route('/logout')
@login_required
def logout_page():
    logout_user()
    return redirect("/")


@app.route('/catalog')
def catalog():
    return get_render_template('catalog.html', title='Каталог', products=get_list_products(50))


@app.route('/catalog/<string:cat>')
def catalog_category(cat):
    if not category_map and need_load:
        load_category_map()
    products = []
    if cat in for_udobstvo:
        res = for_udobstvo[cat]
        if "||" in res:
            res = res.split("||")
            products = category_map[res[0]]["children"][res[1]]["kids"][cat]["goods"][0]
        else:
            products = category_map[res]["children"][cat]["goods"][0]
    return get_render_template('catalog.html', title='Каталог', products=products)


@app.route('/order')
def order():
    return get_render_template('place_an_order.html', title="Оформление заказа")


@app.route('/tmp')
def tmp():
    return get_render_template('tmp.html', title="Оформление заказа")


# @app.route('/place_an_order', methods=['POST', 'GET'])
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


if __name__ == '__main__':
    app.run()
