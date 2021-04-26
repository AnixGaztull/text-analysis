import datetime
import sqlalchemy
import random
from .db_session import SqlAlchemyBase
import hashlib
from data.user_sessions import UserSession


def calc_hash(password):
    return hashlib.md5(password.encode()).hexdigest()


class Data_rezult(SqlAlchemyBase):
    __tablename__ = 'data_rezults'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    order = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    num_simbol = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    num_simb_without_space = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    num_words = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    num_noun = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    num_verb = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    num_adjf = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    num_numr = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    pop_num = sqlalchemy.Column(sqlalchemy.String, primary_key=True)

    pop_word = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name_text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=True)


    @classmethod
    def update_history_analiz(cls, params, order_num, user_id, db_sess):
        new_data = Data_rezult()
        new_data.user_id = user_id
        new_data.order = order_num + 1

        new_data.num_numr = params["num_numr"]
        new_data.num_adjf = params["num_adjf"]
        new_data.num_verb = params["num_verb"]
        new_data.num_noun = params["num_noun"]
        new_data.num_words = params["num_words"]
        new_data.num_simb_without_space = params["num_simb_without_space"]
        new_data.num_simbol = params["num_simbol"]
        new_data.pop_num = params["pop_num"]
        new_data.pop_word = params["pop_word"]
        new_data.name_text = params["name_text"]
        new_data.text = params["text"]

        db_sess.add(new_data)
        db_sess.commit()
        return new_data.id


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    cell = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True,
                             default="fewfeewf", nullable=True)
    num_analizs = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    def __str__(self):
        return f"{self.cell} - {self.id}"

    @classmethod
    def authenticate_user(cls, _user_login, _user_pass_hash, db_sess):
        print("Searching for user")
        found_users = db_sess.query(User).filter((User.cell == _user_login),
                                                 (User.password == calc_hash(_user_pass_hash)))
        found = []
        for i in found_users:
            found.append(i)
            print(i)

        if len(found) == 0:
            return [None, None]
        else:
            new_user_session = UserSession()
            new_user_session.user_id = found[0].id
            new_user_session.value = f"{random.random()}{random.random()}"
            db_sess.add(new_user_session)
            db_sess.commit()
            return [found[0], new_user_session]

    @classmethod
    def create(cls, _cell, _password, db_sess):
        new_user = User()
        new_user.cell = _cell
        new_user.password = calc_hash(_password)
        new_user.num_analizs = 0
        db_sess.add(new_user)
        db_sess.commit()

        new_user_session = UserSession()
        new_user_session.user_id = new_user.id
        new_user_session.value = f"{random.random()}{random.random()}"
        db_sess.add(new_user_session)
        db_sess.commit()
        return [new_user, new_user_session]

    @classmethod
    def check_session(cls, _secret):
        for user in User.users:
            for session_secret in user.session_secrets:
                if _secret == session_secret:
                    return user
        return None

    @classmethod
    def check_cookies(cls, cookies, db_sess):
        found_sessions = list(db_sess.query(UserSession).filter((UserSession.value == cookies.get("user_secret"))))
        if len(found_sessions) > 0:
            found_session = list(found_sessions)[0]
            if len(list(db_sess.query(User).filter((User.id == found_session.user_id)))) > 0:
                user = list(db_sess.query(User).filter((User.id == found_session.user_id)))[0]
                return user
        return None

    @classmethod
    def all(cls, db_sess):
        all_users = db_sess.query(User).filter(User.id > 0)
        found = []
        for i in all_users:
            found.append(i)
        return found
