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
    return render_template("base.html")


if __name__ == "__main__":
    main()