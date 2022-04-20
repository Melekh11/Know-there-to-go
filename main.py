# import requests
from flask import render_template, Flask, request, redirect
import datetime
from data import db_session
from PIL import Image

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)


def main():
    db_session.global_init("db/blogs.db")
    app.run()



@app.route("/", methods=['GET', 'POST'])
def header():
    all = {}
    all["title_place"] = "Парк Горького"
    all["text"] = "Парк, подходящий как и для неспешных прогулой возле Москвы реки, так и для активного отдыха: в парке есть качели, даже верёвочный городок. В солгечные дни здесь солнечно а в пасмурные естьь гру укрыться от дождя. Всем советую"

    all["photo"] = "/static/img/photo_park.jpg"
    all["address"] = "Москва, ул. Глваная"
    all["budget"] = "0 - 5000(₽)"
    all["picture"] = "photo_park.jpg"
    all["turnout"] = "желательно c компанией"
    all["distance"] = 1600

    return render_template("main_page.html", **all)


@app.route("/choose_place")
def choose_place():
    return "yep"


@app.route("/sing_up", methods=['GET', 'POST'])
def sing_up():
    if request.method == "GET":
        return render_template("sing_up.html")
    if request.method == "POST":
        easy_passwords = ["qwerty", "123456", "1234567890", "password", "012345", "Password", "QWERTY"]
        if request.form["Password"] != request.form["PasswordAgain"]:
            return render_template("sing_up.html", message="Пароли не совпадают")
        elif len(request.form["Password"]) < 6:
            return render_template("sing_up.html", message="Слишком короткий пароль")
        elif request.form["Password"] in easy_passwords:
            return render_template("sing_up.html", message="Слишком простой пароль")
        elif len(request.form["name"]) == 0:
            return render_template("sing_up.html", message="Имя не должоно быть пустым")

        name = request.form['name']
        password = request.form['name']
        email = request.form["email"]
        print(name, email, password)
        return redirect("/")


@app.route("/log_in", methods=['GET', 'POST'])
def log_in():
    if request.method == "GET":
        return render_template("log_in.html")
    if request.method == "POST":

        # TODO: сравнение введённых с БД

        return render_template("log_in.html", message="неправльный пароль")

@app.route("/settings_user", methods=['GET', 'POST'])
def settings():
    # при финальном соединении оформлю нормально
    name = "Матвей"
    all = {}
    all["name"] = "Матвей"
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
    all["tags"] = ["тег1", "тег2", "тег3", "тег4"]
    if request.method == "GET":
        return render_template("add_place.html", **all)


if __name__ == "__main__":
    main()
