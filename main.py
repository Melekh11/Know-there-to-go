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



@app.route("/", methods=['GET', 'POST'])
def header():
    all = {}
    all["title_place"] = "Парк Горького"
    all["text"] = "Парк, подходящий как и для неспешных прогулой возле Москвы реки, так и для активного отдыха: в парке есть качели, даже верёвочный городок. В солгечные дни здесь солнечно а в пасмурные естьь гру укрыться от дождя. Всем советую" \
                  "fcghvjbkjkjhugyfc ugfyguhijouyt ytfguhijokp drtfyguhi rdtfyguhijo 5dr6ftyguhi jtrdfyguhi tyuh 6fr5t7gyhu tdryguh tcdrvgb rxcty trcdygu tyu tdr tfy try tfyg tcrfyvug tyfug ftygu yftgu ytfguhi ytfguhi  tfygu yft iytvguih ytguhi ytug " \
                  " yftguih tyfguhi utgyih ouygiho igyuihoi guyih oguyih uygih vytfuh "
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

@app.route("/settings_user/<int:user_id>", methods=['GET', 'POST'])
def settings(user_id):
    if request.method == "GET":
        all = {}
        all["name"] = "Матвей"
        all["email"] = "cktkutxd@gmail.com"
        all["image_way"] = "/static/img/icon_user.png"
        return render_template("settings.html", **all)

if __name__ == "__main__":
    main()