import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class UserSession(SqlAlchemyBase):
    __tablename__ = 'user_sessions'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    value = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    @classmethod
    def sign_out(cls, cookies, db_sess):
        found_sessions = db_sess.query(UserSession).filter((UserSession.value == cookies.get("user_secret")))
        for session in list(found_sessions):
            db_sess.delete(session)
        db_sess.commit()
