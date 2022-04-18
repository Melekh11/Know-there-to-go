from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField
from wtforms import SelectMultipleField, IntegerField, FileField
from wtforms.validators import DataRequired


class PlaceForm(FlaskForm):
    title = StringField("Название места", validators=[DataRequired()])
    address = StringField("Адрес места", validators=[DataRequired()])
    description = TextAreaField("Расскажите о месте")
    photo = FileField("Выберите фото")
    # SelectMultipleField("Выберите тег(и)", choices=[
    #     ("посидеть одному", "посидеть одному"),
    #     ("посидеть c друзьями", "посидеть c друзьями"),
    #     ("побыть на свежем воздухе", "побыть на свежем воздухе"),
    #     ("поесть", "поесть"),
    # ], option_widget=None)
    alone = BooleanField("посидеть одному")
    together = BooleanField("посидеть с друзьями")
    outside = BooleanField("побыть на свежем воздухе")
    eat = BooleanField("поесть")
    move = BooleanField("подвигаться")
    work = BooleanField("поработать/поучиться")
    hide = BooleanField("спрятаться от дождя/жары")
    exciting = BooleanField("получить новые впечатления")

    tag = StringField("Другой тег")

    cost = IntegerField("Минимальная цена для места", default=0)


    # email = EmailField('Почта', validators=[DataRequired()])

    # password = PasswordField('Пароль', validators=[DataRequired()])
    # password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    # name = StringField('Имя пользователя', validators=[DataRequired()])
    # about = TextAreaField("Немного о себе")
    submit = SubmitField('Опубликовать')


class SearchForm(FlaskForm):
    address = StringField("Сортировать от самого близкого к адресу:")
    # SelectMultipleField("Выберите тег(и)", choices=[
    #     ("посидеть одному", "посидеть одному"),
    #     ("посидеть c друзьями", "посидеть c друзьями"),
    #     ("побыть на свежем воздухе", "побыть на свежем воздухе"),
    #     ("поесть", "поесть"),
    # ], option_widget=None)
    alone = BooleanField("посидеть одному")
    together = BooleanField("посидеть с друзьями")
    outside = BooleanField("побыть на свежем воздухе")
    eat = BooleanField("поесть")
    move = BooleanField("подвигаться")
    work = BooleanField("поработать/поучиться")
    hide = BooleanField("спрятаться от дождя/жары")
    exciting = BooleanField("получить новые впечатления")

    tag = StringField("Другой тег")

    cost = IntegerField("Минимальная цена для места", default=0)

    search = SubmitField('Искать')
