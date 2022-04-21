# import requests
from flask import render_template, Flask, request, redirect
import datetime
from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)


def main():
    db_session.global_init("db/blogs.db")
    app.run()



# для отображения лого во все all - ы нужно добавить all["url_im"] = "url(путь к аватарке)"

@app.route("/", methods=['GET', 'POST'])
def header():
    all = {}

    all["title_place"] = "Парк Горького"
    all["text"] = "Парк, подходящий как и для неспешных прогулой возле Москвы реки, так и для активного отдыха: в парке есть качели, даже верёвочный городок. В солгечные дни здесь солнечно а в пасмурные естьь гру укрыться от дождя. Всем советую"
    all["url_im"] = "url(/static/img/default_user_logo.png)"
    all["photo"] = "/static/img/photo_park.jpg"
    all["address"] = "Москва, ул. Глваная"
    all["budget"] = "0 - 5000(₽)"
    all["picture"] = "photo_park.jpg"
    all["turnout"] = "желательно c компанией"
    all["distance"] = 1600

    return render_template("main_page.html", **all)


@app.route("/choose_place", methods=["POST", "GET"])
def choose_place():
    all = {}
    all["tags"] = ["посидеть одному", "посидеть с друзьями", "побыть на свежем воздухе", "поесть", "подвигаться",
                   "поработать", "спрятаться от дождя / жары", "получить новые впечателния"]
    if request.method == "GET":
        return render_template("search_place.html", **all)
    if request.method == "POST":

        print("!!!!!")

        try:
            int(request.form["MinCost"])
        except ValueError:
            all["message"] = "Цена должна быть целым положительным числом"
            return render_template("search_place.html", **all)

        print(request.form.getlist("tags"))
        arr = []
        result_tags = request.form.getlist("tags")
        for i in range(len(all["tags"])):
            if all["tags"][i] in result_tags:
                arr.append((True, i))
            else:
                arr.append((False, i))
        print(arr)  # бедный список со значениями тегов

        tags_self = request.form["TagsArea"].split("\n")
        for i in range(len(tags_self)):
            print(tags_self[i][-2:-1])
            if tags_self[i][-1] == "\r":
                tags_self[i] = tags_self[i][:-1]
        print(tags_self, "!!!")
        print([(i, tags_self[i][1:]) for i in range(len(tags_self))])  # самодельные теги

        print(request.form["Address"])  # адрес
        print(request.form["MinCost"])
        return redirect("/")


@app.route("/sing_up", methods=['GET', 'POST'])
def sing_up():
    all = {}
    all["url_im"] = "/static/img/icon_user.png"
    if request.method == "GET":
        return render_template("sing_up.html", **all)
    if request.method == "POST":
        easy_passwords = ["qwerty", "123456", "1234567890", "password", "012345", "Password", "QWERTY"]
        if request.form["Password"] != request.form["PasswordAgain"]:
            return render_template("sing_up.html", message="Пароли не совпадают", **all)
        elif len(request.form["Password"]) < 6:
            return render_template("sing_up.html", message="Слишком короткий пароль", **all)
        elif request.form["Password"] in easy_passwords:
            return render_template("sing_up.html", message="Слишком простой пароль", **all)
        elif len(request.form["name"]) == 0:
            return render_template("sing_up.html", message="Имя не должоно быть пустым", **all)

        name = request.form['name']
        password = request.form['name']
        email = request.form["email"]
        print(name, email, password)
        return redirect("/")


@app.route("/log_in", methods=['GET', 'POST'])
def log_in():
    all = {}
    all["url_im"] = "/static/img/icon_user.png"
    if request.method == "GET":
        return render_template("log_in.html", **all)
    if request.method == "POST":
        all["message"] = "неправльный пароль"
        # TODO: сравнение введённых с БД
        return render_template("log_in.html")

@app.route("/settings_user", methods=['GET', 'POST'])
def settings():
    # при финальном соединении оформлю нормально
    name = "Матвей"
    all = {}
    all["name"] = "Матвей"
    all["url_im"] = "/static/img/icon_user.png"
    all["image_way"] = "/static/img/icon_user.png"
    all["email"] = "cktkutxd@gmail.com"
    all["arr_title"] = ["Парк Горького" for i in range(6)]
    all["images_way"] = ["/static/img/photo_park.jpg" for i in range(6)]
    all["arr_text"] = [
        "Парк, подходящий как и для неспешных прогулой возле Москвы реки, так и для активного отдыха: в парке есть качели, даже верёвочный городок. В солгечные дни здесь солнечно а в пасмурные естьь гру укрыться от дождя. Всем советую"
        for i in range(6)]
    all["count_posts"] = 6
    if request.method == "GET":
        return render_template("settings.html", **all)

    if request.method == "POST":

        # данные нового имени, новой почты, путь к картинке указывай сама!

        print(request.form["ChangeName"])
        print(request.form["ChangeEmail"])
        file = request.files['ProfPic']
        if file:
            file.save("!way_here!")
        return redirect("/")



@app.route("/add_place", methods=["POST", "GET"])
def add_place():
    all = {}
    all["tags"] = ["посидеть одному", "посидеть с друзьями", "побыть на свежем воздухе", "поесть", "подвигаться",
                   "поработать", "спрятаться от дождя / жары", "получить новые впечателния"]
    if request.method == "GET":
        return render_template("add_place.html", **all)
    if request.method == "POST":
        try:
            int(request.form["Min_Cost"])
        except ValueError:
            all["message"] = "Цена долдна быть целым положтельным числом"
            return render_template("add_place.html", **all)

        # условие на существование места
        #   all["message"] = "такого места не сущесвует в яндекс картах;("
        #   return render_template("add_place.html", **all)

        result_tags = request.form.getlist("tags")
        print(result_tags)
        arr = []
        for i in range(len(all["tags"])):
            if all["tags"][i] in result_tags:
                arr.append((True, i))
            else:
                arr.append((False, i))
        print(arr)  # бедный список со значениями тегов
        print(request.form["Title"])  # тайтл
        print(request.form["Address"])  # адрес
        print(request.form["TextArea"])  # описание
        file = request.files['PicPlace']  # картинка
        if file:
            file.save("!way_here!")
        print(int(request.form["Min_Cost"]))  # минимальная цена
        tags_self = request.form["TagsArea"].split("\n")
        for i in range(len(tags_self)):
            print(tags_self[i][-2:-1])
            if tags_self[i][-1] == "\r":
                tags_self[i] = tags_self[i][:-1]
        print(tags_self, "!!!")
        print([(i, tags_self[i][1:]) for i in range(len(tags_self))])  # самодельные теги
        return redirect("/")


@app.route("/place/<int:id>", methods=["POST", "GET"])
def place(id):
    all = {
            "title": "Заголовок",
            "address": "Москва, ул. Солянка 14",
            "text": "Парк, подходящий как и для неспешных прогулой возле Москвы реки, так и для активного отдыха: в парке есть качели, даже верёвочный городок. В солгечные дни здесь солнечно а в пасмурные естьь гру укрыться от дождя. Всем советую",
            "scr": "/static/img/photo_park.jpg",
            "tags": ["еда", "вода", "зелля", "огонь", "ветер", "вода"],
            "cost": 5000,
            "url_im": "urm(/static/img/icon_user.png)"
        }
    if request.method == "GET":
        return render_template("place.html", **all)






if __name__ == "__main__":
    main()
