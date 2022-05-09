import requests
from flask import Flask
from flask import redirect, make_response, request, render_template, jsonify, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

# дб
from data import db_session
from data.users import User
from data.places import Places
from data.place_tag import PlaceTag
from data.tags import Tags

# формы
from forms.user import RegisterForm, LoginForm, ChangeProfileForm
from forms.places import PlaceForm, SearchForm

import requests
import math
import os
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class


app = Flask(__name__)

# вспомогательные штуки для сохранения картинок
basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = 'static/img/uploads/'

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, UPLOAD_FOLDER)

login_manager = LoginManager()
login_manager.init_app(app)

photos = UploadSet('photos', IMAGES)
configure_uploads(app, photos)
patch_request_class(app)


# константы для тегов
DEFAULT_TAGS_NAMES = [
            ('alone', 'посидеть одному'), ('together', 'посидеть с друзьями'),
            ('outside', 'побыть на свежем воздухе'), ('eat', 'поесть'), ('move', 'подвигаться'),
            ('work', 'поработать/поучиться'), ('hide', 'спрятаться от дождя/жары'),
            ('exciting', 'получить новые впечатления')]


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


# проверить аватарку юзера:
def user_photo(user):
    if user.is_authenticated:
        if user.photo:
            return f'url({UPLOAD_FOLDER + user.photo})'
        else:
            return f'url(static/img/default_user_logo.png)'


def main():
    db_session.global_init("db/blogs.db")
    app.run()


@app.route("/")
def index():
    db_sess = db_session.create_session()
    places = db_sess.query(Places).filter(Places.title != '')
    place_tags = db_sess.query(PlaceTag).filter()
    tags = db_sess.query(Tags).filter()

    url_im = user_photo(current_user)

    return render_template("main_page.html", places=places, tags=tags, place_tags=place_tags, url_im=url_im)


# регистрация
@app.route('/sign_up', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        print(form.send_emails.data)
        easy_passwords = ["qwerty", "123456", "1234567890", "password", "012345", "Password", "QWERTY"]

        if form.password.data != form.password_again.data:
            return render_template('sign_up.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        elif len(form.password.data) < 6:
            return render_template('sign_up.html', title='Регистрация',
                                   form=form,
                                   message="Слишком короткий пароль")
        elif form.password.data in easy_passwords:
            return render_template('sign_up.html', title='Регистрация',
                                   form=form,
                                   message="Слишком простой пароль")
        elif len(form.name.data) == 0:
            return render_template('sign_up.html', title='Регистрация',
                                   form=form,
                                   message="Имя не должно быть пустым")

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('sign_up.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        # сохранение картинки
        filename = None
        if form.photo.data:
            filename = photos.save(form.photo.data)

        user = User(
            name=form.name.data,
            email=form.email.data,
            photo=filename,
            send_emails=form.send_emails.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/log_in')
    return render_template('sign_up.html', title='Регистрация', form=form)


# логин
@app.route('/log_in', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user:
            if user.check_password(form.password.data):
                login_user(user)
                return redirect("/")
        return render_template('log_in.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('log_in.html', title='Авторизация', form=form)


# добавление места
@app.route('/post_place', methods=['GET', 'POST'])
@login_required
def postplace():
    url_im = user_photo(current_user)
    form = PlaceForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()

        # проверка, правильный ли адрес через геокодер
        if not get_coordinates(form.address.data):
            return render_template('add_place.html', title='Добавление места',
                                   form=form,
                                   message="Такого адреса не существует", tags=DEFAULT_TAGS_NAMES, url_im=url_im)
        try:
            a = int(form.cost.data)
        except ValueError:
            return render_template('add_place.html', title='Добавление места',
                                   form=form,
                                   message="Цена должна быть положительным целым числом", tags=DEFAULT_TAGS_NAMES, url_im=url_im)

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

        # доп. теги (проверка, существует ли они, если нет, добалвение их)
        added_tags = (''.join((form.tag.data).split('\n'))).split('\r')
        for i in added_tags:
            if i:
                if not db_sess.query(Tags).filter(Tags.title.like(i)).first():
                    tag = Tags(
                        title=i
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
                    tag = db_sess.query(Tags).filter(Tags.title.like(i)).first()
                    place_tag = PlaceTag(
                        tag_id=tag.id,
                        place_id=place.id
                    )
                    db_sess.add(place_tag)
                    db_sess.commit()
        return redirect('/')
    return render_template('add_place.html', title='Добавление места', form=form, tags=DEFAULT_TAGS_NAMES, url_im=url_im)


# поиск места
@app.route('/searchplace', methods=['GET', 'POST'])
def searchplace():
    url_im = user_photo(current_user)
    form = SearchForm()

    if form.validate_on_submit():
        if not get_coordinates(form.address.data) and form.address.data:
            return render_template('search_place.html', title='Поиск места',
                                   form=form,
                                   message="Такого адреса не существует", url_im=url_im)
        try:
            a = int(form.cost.data)
        except ValueError:
            return render_template('add_place.html', title='Поиск места',
                                   form=form,
                                   message="Цена должна быть положительным целым числом", url_im=url_im)
        DEFAULT_TAGS = [
            (form.alone.data, 1), (form.together.data, 2), (form.outside.data, 3),
            (form.eat.data, 4),
            (form.move.data, 5), (form.work.data, 6), (form.hide.data, 7), (form.exciting.data, 8)]

        # передаем всю инфу с этой формы на страницу с результатами поиска

        db_sess = db_session.create_session()

        # теги
        valid_tags = list(filter(lambda x: x[0], DEFAULT_TAGS))
        tags = list(i[1] for i in valid_tags)

        added_tags = (''.join((form.tag.data).split('\n'))).split('\r')
        for i in added_tags:
            if i:
                if db_sess.query(Tags).filter(Tags.title.like(i)).first():
                    tag = db_sess.query(Tags).filter(Tags.title.like(i)).first()
                    tags.append(tag.id)

        # адрес и цена
        address = form.address.data
        cost = form.cost.data

        return redirect(url_for('searchresults', tags=tags, address=address, cost=cost))
    return render_template('search_place.html', title='Поиск места', form=form, tags=DEFAULT_TAGS_NAMES, url_im=url_im)


# результаты поиска
@app.route('/searchresults', methods=['GET', 'POST'])
def searchresults():
    url_im = user_photo(current_user)

    # получаем инфу
    address = request.args.get('address', '')
    tags = [int(i) for i in request.args.getlist('tags')]
    cost = request.args.get('cost', 0)

    db_sess = db_session.create_session()

    # фильтруем результаты ПО ТЕГАМ и ЦЕНЕ
    posts = db_sess.query(Places).filter(Places.cost <= cost, PlaceTag.place_id == Places.id)
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

    places = db_sess.query(Places).filter(Places.title != '')
    place_tags = db_sess.query(PlaceTag).filter()
    tags = db_sess.query(Tags).filter()
    return render_template('results.html', title='Результаты поиска', places=sorted_all, tags=tags, place_tags=place_tags, url_im=url_im)


# профиль пользователя
@login_required
@app.route('/user_profile', methods=['GET', 'POST'])
def user_profile():
    form = ChangeProfileForm()
    db_sess = db_session.create_session()

    posts = db_sess.query(Places).filter(Places.user_id == current_user.id).all()
    url_im = user_photo(current_user)

    all = {
        'name': current_user.name,
        'url_im': url_im,
        'image_way': url_im[4:-1],
        'email': current_user.email,
        'arr_title': [i.title for i in posts],
        'images_way': [f'{UPLOAD_FOLDER + str(i.photo)}' for i in posts],
        'arr_text': [i.description for i in posts],
        'count_posts': len([i.id for i in posts]),
        'place_id': [i.id for i in posts]

    }
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.id == current_user.id,
                                          User.name == current_user.name
                                          ).first()

        print(current_user, 123, user)

        user.name = form.name.data
        print(form.name.data, user.name)

        if not (form.email.data == current_user.email) and db_sess.query(User).filter(User.email == form.email.data).all():
            return render_template("settings.html", **all, form=form)
        else:
            user.email = form.email.data
        if form.photo.data:
            photos.save(form.photo.data)
            user.photo = form.photo.data.filename

        print(user.name, user.email, user.photo)
        db_sess.commit()

        return redirect("/")

    return render_template("settings.html", **all, form=form)


@app.route("/place/<int:id>", methods=["POST", "GET"])
def place(id):
    url_im = user_photo(current_user)

    db_sess = db_session.create_session()
    place = db_sess.query(Places).filter(Places.id == id).first()

    place_tags = db_sess.query(PlaceTag).filter(PlaceTag.place_id == place.id)
    tags = []
    for i in place_tags:
        tags.append((db_sess.query(Tags).filter(i.tag_id == Tags.id).first().title))

    all = {
            "title": place.title,
            "address": place.address,
            "text": place.description,
            "scr": f'/{UPLOAD_FOLDER + str(place.photo)}',
            "tags": tags,
            "cost": place.cost,
            "url_im": 'url(/' + url_im[4:-1] + ')'
        }
    if request.method == "GET":
        return render_template("place.html", **all)


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
    return 'Ой! Что-то пошло не так. Скорее всего, такой страницы не существует :(', 404


@app.errorhandler(401)
def unauthorized(e):
    return 'Зарегистрируйтесь, чтобы просмотреть эту страницу ;)', 401


if __name__ == '__main__':
    main()
