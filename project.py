from flask import Flask, url_for, request, render_template, make_response, redirect
from data import db_session
from data.users import User
from data.users import Data_rezult
from data.user_sessions import UserSession
import pymorphy2

db_session.global_init("db/development.db")
db_sess = db_session.create_session()

app = Flask(__name__)

user_id = 0
user_num_analiz = 0

morph = pymorphy2.MorphAnalyzer()


def analiz_texta(text):
    text_norm = []
    for i in text.split():
        p = morph.parse(i)[0]
        text_norm.append(p.normal_form)
    non_rep_words = set(text_norm)
    pop_num = 0
    pop_word = ''
    for i in non_rep_words:
        k = text_norm.count(i)
        if k > pop_num:
            pop_num = k
            pop_word = i

    num_simb = len(text)
    num_space = text.count(' ')
    num_simb_without_space = num_simb - num_space
    text = text.replace(".", ' ')
    text = text.replace("!", ' ')
    text = text.replace("-", ' ')
    text = text.replace("?", ' ')
    text = text.replace(":", ' ')
    text = text.replace('"', ' ')
    text = text.replace(":", ' ')
    text = text.replace("(", ' ')
    text = text.replace(")", ' ')
    text = text.split()
    num_words = len(text)
    num_noun = 0
    num_verb = 0
    num_adjf = 0
    num_numr = 0
    for i in text:
        p = morph.parse(i)[0]
        if 'NOUN' in p.tag:
            num_noun += 1
        elif "VERB" in p.tag:
            num_verb += 1
        elif "ADJF" in p.tag:
            num_adjf += 1
        elif "NUMR" in p.tag:
            num_numr += 1
    param = {
        "num_simbol": num_simb,
        "num_simb_without_space": num_simb_without_space,
        "num_words": num_words,
        "num_noun": num_noun,
        'num_verb': num_verb,
        "num_adjf": num_adjf,
        "num_numr": num_numr,
        "pop_word": pop_word,
        "pop_num": pop_num
    }
    return param


def check_if_user_signed_in(cookies, db_sess):
    return User.check_cookies(cookies, db_sess)


@app.route("/sign_in_user", methods=['POST'])
def sign_in_user():
    global user_num_analiz, user_id
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    if current_user:
        return redirect("/analiz")
    else:
        res = User.authenticate_user(request.form["login"], request.form["password"], db_sess)
        user = res[0]

        if None == user:
            return redirect("/sign_in/не найдено")
        else:
            user_id = user.id
            user_num_analiz = user.num_analizs
            user_session = res[1]
            res = make_response(redirect("/"))
            res.set_cookie("user_secret", str(user_session.value),
                           max_age=60 * 60 * 24 * 365 * 2)
            return res


@app.route('/')
def landing():
    return redirect("/sign_in/Введите пароль")


@app.route("/sign_in/<status>")
def sign_in(status):
    param = {
        "status": status
    }
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    if current_user:
        return redirect("/analiz")
    return render_template('index.html', **param)


@app.route('/sign_up')
def sign_up():
    param = {}
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    if current_user:
        return redirect("/users/analiz")
    return render_template('sign_up.html', **param)


@app.route("/sign_up_user", methods=["post"])
def sign_up_user():
    global user_num_analiz, user_id
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    if current_user:
        print('k')
        return redirect("/analiz")
    res = User.create(request.form["login"], request.form["password"], db_sess)
    user = res[0]
    user_id = user.id
    user_num_analiz = user.num_analizs
    user_session = res[1]
    http_res = make_response(redirect("/"))
    http_res.set_cookie("user_secret", str(user_session.value),
                        max_age=60 * 60 * 24 * 365 * 2)
    return http_res

@app.route("/rez_analiz/<text_id>", methods=['POST', 'GET'])
def analiz_output(text_id):
    global user_id
    data = db_sess.query(Data_rezult).filter(Data_rezult.id == text_id).first()
    params = {
        "num_simbol": data.num_simbol,
        "num_simb_without_space": data.num_simb_without_space,
        "num_words": data.num_words,
        "num_noun": data.num_noun,
        'num_verb': data.num_verb,
        "num_adjf": data.num_adjf,
        "num_numr": data.num_numr,
        "pop_word": data.pop_word,
        "pop_num": data.pop_num,
        "text": data.text,
        "name_text": data.name_text
    }
    print(params)
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    if not current_user:
        return redirect("/")

    data = list(db_sess.query(Data_rezult).filter(Data_rezult.user_id == user_id))
    data = sorted(data, key=lambda x: x.order)
    data.reverse()
    return render_template("rez.html", data=data, **params)


@app.route("/analiz", methods=['POST', 'GET'])
def analiz():
    global user_id
    current_user = check_if_user_signed_in(request.cookies, db_sess)
    if not current_user:
        return redirect("/")
    params = {
        "current_user": current_user
    }
    data = list(db_sess.query(Data_rezult).filter(Data_rezult.user_id == user_id))
    data = sorted(data, key=lambda x: x.order)
    return render_template("w.html", data=data, params=params)


@app.route("/text_analiz", methods=['POST', "GET"])
def rez_analiz_output():
    global user_num_analiz, user_id
    params = analiz_texta(request.form["text"])
    params["name_text"] = request.form["name"]
    print(params["name_text"])
    params["text"] = request.form["text"]

    text_id = Data_rezult.update_history_analiz(params, user_num_analiz, user_id,  db_sess)
    return redirect(f"/rez_analiz/{int(text_id)}")


@app.route("/sign_out")
def sign_out():
    current_user = UserSession.sign_out(request.cookies, db_sess)
    return redirect("/")


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
