import requests
from flask import Flask
from flask import redirect, make_response, request, session, render_template, jsonify, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data import db_session, news_api

# дб
from data.users import User
from data.places import Places
from data.place_tag import PlaceTag
from data.tags import Tags

# формы
from forms.user import RegisterForm, LoginForm
from forms.places import PlaceForm, SearchForm

import requests
import math
import os
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class
import datetime


app = Flask(__name__)

# вспомогательные штуки для сохранения картинок
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = 'static/img/'

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, UPLOAD_FOLDER)

login_manager = LoginManager()
login_manager.init_app(app)

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)

# функции для геокодера


def get_coordinates(city_name):
    try:
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            'geocode': city_name,
            'format': 'json'
        }
        response = requests.get(url, params)
        json = response.json()
        coordinates_str = json['response']['GeoObjectCollection'][
            'featureMember'][0]['GeoObject']['Point']['pos']
        long, lat = map(float, coordinates_str.split())
        return long, lat
    except Exception as e:
        return None


def get_distance(p1, p2):
    radius = 6373.0

    lon1 = math.radians(p1[0])
    lat1 = math.radians(p1[1])
    lon2 = math.radians(p2[0])
    lat2 = math.radians(p2[1])

    d_lon = lon2 - lon1
    d_lat = lat2 - lat1

    a = math.sin(d_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(d_lon / 2) ** 2
    c = 2 * math.atan2(a ** 0.5, (1 - a) ** 0.5)

    distance = radius * c
    return round(distance)


def main():
    db_session.global_init("db/blogs.db")
    # app.register_blueprint(news_api.blueprint)
    app.run()


@app.route("/")
def index():
    db_sess = db_session.create_session()
    # places = Places()
    # places.title = "ВДНХ"
    # places.address = "Проспект мира, 119"
    # places.description = "Выставка достижений"
    # places.user_id = 1
    # db_sess.add(places)
    # db_sess.commit()

    # if current_user.is_authenticated:
    places = db_sess.query(Places).filter(Places.title != '')
    return render_template("index.html", places=places)


# регистрация
@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        # сохранение картинки
        filename = None
        if form.photo.data:
            filename = photos.save(form.photo.data)
            file_url = photos.url(filename)

        user = User(
            name=form.name.data,
            email=form.email.data,
            photo=filename
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


# логин
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


# добавление места
@app.route('/postplace', methods=['GET', 'POST'])
@login_required
def postplace():
    form = PlaceForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        # проверка, правильный ли адрес через геокодер
        if not get_coordinates(form.address.data):
            return render_template('post.html', title='Добавление места',
                                   form=form,
                                   message="Такого адреса не существует")

        filename = None
        if form.photo.data:
            filename = photos.save(form.photo.data)
            file_url = photos.url(filename)

        place = Places(
            title=form.title.data,
            address=form.address.data,
            description=form.description.data,
            cost=form.cost.data,
            user_id=current_user.id,
            photo=filename

        )
        db_sess.add(place)
        db_sess.commit()

        # теги по умолчанию (посидеть одному, итд)
        DEFAULT_TAGS = [
            (form.alone.data, 1), (form.together.data, 2), (form.outside.data, 3),
            (form.eat.data, 4),
            (form.move.data, 5), (form.work.data, 6), (form.hide.data, 7), (form.exciting.data, 8)
        ]
        valid_tags = list(filter(lambda x: x[0], DEFAULT_TAGS))
        for i in valid_tags:
            place_tag = PlaceTag(
                tag_id=i[1],
                place_id=place.id
            )
            db_sess.add(place_tag)
            db_sess.commit()

        # доп. тег (проверка, существует ли он, если нет, добалвение его)
        if form.tag.data:
            if not db_sess.query(Tags).filter(Tags.title.like(form.tag.data)).first():
                tag = Tags(
                    title=form.tag.data
                )
                db_sess.add(tag)
                db_sess.commit()
                place_tag = PlaceTag(
                    tag_id=tag.id,
                    place_id=place.id
                )
                db_sess.add(place_tag)
                db_sess.commit()
            else:
                tag = db_sess.query(Tags).filter(Tags.title.like(form.tag.data)).first()
                place_tag = PlaceTag(
                    tag_id=tag.id,
                    place_id=place.id
                )
                db_sess.add(place_tag)
                db_sess.commit()
        return redirect('/')
    return render_template('post.html', title='Добавление места', form=form)


# поиск места
@app.route('/searchplace', methods=['GET', 'POST'])
def searchplace():
    form = SearchForm()
    if form.validate_on_submit():
        if not get_coordinates(form.address.data) and form.address.data:
            return render_template('search.html', title='Поиск места',
                                   form=form,
                                   message="Такого адреса не существует")
        DEFAULT_TAGS = [
            (form.alone.data, 1), (form.together.data, 2), (form.outside.data, 3),
            (form.eat.data, 4),
            (form.move.data, 5), (form.work.data, 6), (form.hide.data, 7), (form.exciting.data, 8)]

        # передаем всю инфу с этой формы на страницу с результатами поиска

        db_sess = db_session.create_session()
        valid_tags = list(filter(lambda x: x[0], DEFAULT_TAGS))

        # теги
        tags = list(i[1] for i in valid_tags)
        if form.tag.data:
            if db_sess.query(Tags).filter(Tags.title.like(form.tag.data)).first():
                tag = db_sess.query(Tags).filter(Tags.title.like(form.tag.data)).first()
                tags.append(tag.id)

        # адрес и цена
        address = form.address.data
        cost = form.cost.data


        return redirect(url_for('searchresults', tags=tags, address=address, cost=cost))
    return render_template('search.html', title='Поиск места', form=form)


# результаты поиска
@app.route('/searchresults', methods=['GET', 'POST'])
def searchresults():
    # получаем инфу
    address = request.args.get('address', '')
    tags = [int(i) for i in request.args.getlist('tags')]
    cost = request.args.get('cost', 0)

    db_sess = db_session.create_session()

    # фильтруем результаты ПО ТЕГАМ и ЦЕНЕ
    posts = db_sess.query(Places).filter(Places.cost >= cost, PlaceTag.place_id == Places.id)
    filtered_by_tags = []
    for i in posts:
        a = [i.tag_id for i in db_sess.query(PlaceTag).filter(PlaceTag.place_id == i.id)]
        if set(tags).issubset(a):
            filtered_by_tags.append(i)

    # и сортируем по АДРЕСУ
    sorted_all = filtered_by_tags
    if address:
        sorted_by_address = sorted(filtered_by_tags,
                                   key=lambda x: get_distance(get_coordinates(address),
                                                              get_coordinates(x.address)))
        sorted_all = sorted_by_address
        print(get_coordinates(address))
        for i in sorted_all:
            print(i.title)
            print(get_distance(get_coordinates(address), get_coordinates(i.address)))
    return render_template('results.html', title='Результаты поиска', posts=sorted_all)


# профиль пользователя
@login_required
@app.route('/user_profile')
def user_profile():
    db_sess = db_session.create_session()
    posts = db_sess.query(Places).filter(Places.user_id == current_user.id).all()
    photo = ''
    if current_user.photo:
        photo = UPLOAD_FOLDER + current_user.photo
    params = {
        'name': current_user.name,
        'photo': photo,
        'posts': posts,
        'created_date': current_user.created_date
    }
    return render_template("profile.html", **params)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    main()
