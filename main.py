from flask import render_template, Flask
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


@app.route("/")
def header():
    all = {}
    all["title"] = "Парк Горького"
    all["text"] = "Парк, подходящий как и для неспешных прогулой возле Москвы реки, так и для активного отдыха: в парке есть качели, даже верёвочный городок. В солгечные дни здесь солнечно а в пасмурные естьь гру укрыться от дождя. Всем советую"
    all["photo"] = "/static/img/photo_park.jpg"
    all["value"] = "0 - 5000(₽)"
    all["turnout"] = "неограниченно, желательно компанией"
    return render_template("main_page.html")


@app.route("/choose_place")
def choose_place():
    return "yep"


if __name__ == "__main__":
    main()