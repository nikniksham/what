from flask import Flask, render_template
from flask_login import LoginManager
from flask import Flask, render_template, redirect, request
from data import db_session
from data.person import Person
import app_logic

app = Flask(__name__)

db_session.global_init("db/opt4you.sqlite")
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    user = session.query(Person).get(user_id)
    session.close()
    return user


@app.route('/')
def hello_world():  # put app's code here
    return render_template('main.html', title='Главная')


@app.route('/catalog')
def catalog():  # put app's code here
    return render_template('catalog.html', title='Каталог')


@app.route('/order')
def order():
    return render_template('place_an_order.html')


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
