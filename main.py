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
    place_tags = db_sess.query(PlaceTag).filter()
    tags = db_sess.query(Tags).filter()

    return render_template("main_page.html", places=places, tags=tags, place_tags=place_tags)


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
            file_url = photos.url(filename)

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
    all = {}
    all["tags"] = ["посидеть одному", "посидеть с друзьями", "побыть на свежем воздухе", "поесть",
                   "подвигаться",
                   "поработать", "спрятаться от дождя / жары", "получить новые впечателния"]
    if request.method == "GET":
        return render_template("add_place.html", **all)
    if request.method == "POST":
        try:
            int(request.form["Min_Cost"])
        except ValueError:
            all["message"] = "Цена долдна быть целым положтельным числом"
            return render_template("add_place.html", **all)

        db_sess = db_session.create_session()

        # проверка, правильный ли адрес через геокодер
        if not get_coordinates(request.form['Address']):
          all["message"] = "такого места не сущесвует в яндекс картах;("
          return render_template("add_place.html", **all)

        result_tags = request.form.getlist("tags")
        print(result_tags)
        arr = []
        for i in range(len(all["tags"])):
            if all["tags"][i] in result_tags:
                arr.append((True, i + 1))
            else:
                arr.append((False, i + 1))
        print(arr)  # бедный список со значениями тегов
        print(request.form["Title"])  # тайтл
        print(request.form["Address"])  # адрес
        print(request.form["TextArea"])  # описание
        file = request.files['PicPlace']  # картинка
        print(file.filename)
        if file:
            photos.save(file)
        print(int(request.form["Min_Cost"]))  # минимальная цена
        tags_self = request.form["TagsArea"].split("\n")
        for i in range(len(tags_self)):
            print(tags_self[i][-2:-1])
            if tags_self[i][-1] == "\r":
                tags_self[i] = tags_self[i][:-1]
        print(tags_self, "!!!")
        print([(i, tags_self[i][1:]) for i in range(len(tags_self))])  # самодельные теги

        place = Places(
                    title=request.form["Title"],
                    address=request.form["Address"],
                    description=request.form["TextArea"],
                    cost=int(request.form["Min_Cost"]),
                    user_id=current_user.id,
                    photo=file.filename
                             )

        db_sess.add(place)
        db_sess.commit()

        valid_tags = list(filter(lambda x: x[0], arr))
        for i in valid_tags:
            place_tag = PlaceTag(
                        tag_id=i[1],
                        place_id=place.id
                    )
            db_sess.add(place_tag)
            db_sess.commit()


        new_tags = [i[1:] for i in tags_self]
        # доп. теги (проверка, существует ли он, если нет, добалвение его)
        if new_tags:
            for i in new_tags:
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


        return redirect("/")
    return render_template('add_place.html', title='Добавление места')
#     form = PlaceForm()
#     if form.validate_on_submit():
#         db_sess = db_session.create_session()
#
#         # проверка, правильный ли адрес через геокодер
#         if not get_coordinates(form.address.data):
#             return render_template('post.html', title='Добавление места',
#                                    form=form,
#                                    message="Такого адреса не существует")
#
#         filename = None
#         if form.photo.data:
#             filename = photos.save(form.photo.data)
#             file_url = photos.url(filename)
#
#         place = Places(
#             title=form.title.data,
#             address=form.address.data,
#             description=form.description.data,
#             cost=form.cost.data,
#             user_id=current_user.id,
#             photo=filename
#
#         )
#         db_sess.add(place)
#         db_sess.commit()
#
#         # теги по умолчанию (посидеть одному, итд)
#         DEFAULT_TAGS = [
#             (form.alone.data, 1), (form.together.data, 2), (form.outside.data, 3),
#             (form.eat.data, 4),
#             (form.move.data, 5), (form.work.data, 6), (form.hide.data, 7), (form.exciting.data, 8)
#         ]
#         valid_tags = list(filter(lambda x: x[0], DEFAULT_TAGS))
#         for i in valid_tags:
#             place_tag = PlaceTag(
#                 tag_id=i[1],
#                 place_id=place.id
#             )
#             db_sess.add(place_tag)
#             db_sess.commit()
#
#         # доп. тег (проверка, существует ли он, если нет, добалвение его)
#         if form.tag.data:
#             if not db_sess.query(Tags).filter(Tags.title.like(form.tag.data)).first():
#                 tag = Tags(
#                     title=form.tag.data
#                 )
#                 db_sess.add(tag)
#                 db_sess.commit()
#                 place_tag = PlaceTag(
#                     tag_id=tag.id,
#                     place_id=place.id
#                 )
#                 db_sess.add(place_tag)
#                 db_sess.commit()
#             else:
#                 tag = db_sess.query(Tags).filter(Tags.title.like(form.tag.data)).first()
#                 place_tag = PlaceTag(
#                     tag_id=tag.id,
#                     place_id=place.id
#                 )
#                 db_sess.add(place_tag)
#                 db_sess.commit()
#         return redirect('/')
#     return render_template('add_place.html', title='Добавление места', form=form)







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

        # теги

        valid_tags = list(filter(lambda x: x[0], DEFAULT_TAGS))
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
    form = ChangeProfileForm()
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.id == current_user.id,
                                          User.name == current_user.name
                                          ).first()

        if form.name.data:
            user.name = form.name.data
        else:
            user.name = current_user.name
        if form.email.data:
            user.email = form.email.data
        else:
            user.email = current_user.email
        if form.photo.data:
            user.photo = form.name.data
        else:
            user.name = current_user.name
        if form.photo.data:
            filename = photos.save(form.photo.data)
            file_url = photos.url(filename)

        # news.is_private = form.is_private.data
        # db_sess.commit()
        # db_sess.commit()

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
