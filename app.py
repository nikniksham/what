from flask import Flask, render_template
from flask_login import LoginManager
from flask import Flask, render_template, redirect, request
from data import db_session
from data.category import Category
from data.person import Person
from data.Inner.ProductAPI import get_list_products, get_product_by_category_id
import app_logic

app = Flask(__name__)

db_session.global_init("db/opt4you.sqlite")
login_manager = LoginManager()
login_manager.init_app(app)

category_map = {}
need_load = True


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
        else:
            category_map[category.pra_father]["children"][category.name] = {
                "goods": [get_product_by_category_id(category.id)]}
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
def hello_world():  # put app's code here
    return get_render_template('main.html', title='Главная')


@app.route('/catalog')
def catalog():  # put app's code here
    return get_render_template('catalog.html', title='Каталог', products=get_list_products(50, 5))


@app.route('/order')
def order():
    return get_render_template('place_an_order.html', title="Оформление заказа")


@app.route('/product/<string:name>')
def product(name):
    return get_render_template('product.html', title="Страница товара", name="some thing")


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
