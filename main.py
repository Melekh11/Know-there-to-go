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


if __name__ == "__main__":
    main()