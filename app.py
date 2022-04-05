from config import secret_key, key1, key2

from flask import Flask, render_template, request, redirect
from flask_login import LoginManager, logout_user, current_user, login_user
from forms import LoginForm, \
    RegisterForm, Add_Commentform, Edit_form
from data import db_session
from data.ratings import Rating
from data.studies import Studie
from data.comments import Comment
from data.images import Image
from data.users import User
import datetime

app = Flask(__name__)

app.config['SECRET_KEY'] = secret_key
app.config['RECAPTCHA_PUBLIC_KEY'] = key1
app.config['RECAPTCHA_PRIVATE_KEY'] = key2

db_session.global_init("db/data.db")

login_manager = LoginManager()
login_manager.init_app(app)


# _________Вспомогательные функции_______________
def search_follow(A, key):
    left = -1
    right = len(A)
    while right > left + 1:
        middle = (left + right) // 2
        if A[middle] >= key:
            right = middle
        else:
            left = middle
    return right


def f_insert(list, n):
    index = len(list)
    for i in range(len(list)):
        if list[i] > n:
            index = i
            break
        if list[i] == n:
            index = -1
            break
    return index


# ___________________________________________________

# _________функции инициализации пользователя_______________
@app.route('/logout')
def logout():
    if not current_user.is_authenticated:
        return redirect("/login")
    logout_user()
    return redirect("/")


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.Password.data != form.Password_again.data:
            return render_template('register.html',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.Email.data).first():
            return render_template('register.html',
                                   form=form,
                                   message="Такой пользователь уже есть(Почта)")
        if session.query(User).filter(User.login == form.Login.data).first():
            return render_template('register.html',
                                   form=form,
                                   message="Такой пользователь уже есть(Логин)")
        if form.photo.data:
            image = Image(
                image=form.photo.data.read()
            )
        else:
            image = Image(
                image=open("static/images/img1.png", "rb").read()
            )
        session.add(image)
        session.commit()
        user = User(
            email=form.Email.data,
            login=form.Login.data,
            surname=form.Surname.data,
            name=form.Name.data,
            id_foto=image.id,
            data_reg=datetime.datetime.now(),
            type_of_user="basic",
            follow=''
        )
        user.set_password(form.Password.data)
        session.add(user)
        session.commit()
        return redirect("/login")
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', form=form)


@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    if not current_user.is_authenticated:
        return redirect("/login")
    if current_user.id != id:
        return "ОШИБКА ДОСТУПА"
    session = db_session.create_session()
    user = session.query(User).filter(User.id == id).first()
    form = Edit_form()
    if request.method == 'POST':
        if form.Login.data:
            user.login = form.Login.data
        if form.Surname.data:
            user.surname = form.Surname.data
        if form.Name.data:
            user.name = form.Name.data
        if form.photo.data:
            image = Image(
                image=form.photo.data.read()
            )
            session.add(image)
            session.commit()
            session.delete(user.image)
            session.commit()
            user.id_foto = image.id
        session.add(user)
        session.commit()
        return redirect("/myprofile")
    return render_template("edit_user.html", form=form)


# ___________________________________________________

# _________Создания и отображение курса_______________
@app.route('/make_new_studies', methods=['GET', 'POST'])
def make_new_studies():
    if not current_user.is_authenticated:
        return redirect("/login")
    if current_user.type_of_user == "basic":
        return "Отказано в доступе"
    if request.method == 'POST':
        if len(request.form) == 1:
            num = request.form.get("n")
            if not num.isdigit():
                num = 1
            num = min(max(1, int(num)), 20)
            return render_template('make_new_studies.html', n=int(num))
        else:
            data = []
            main_text = request.form.get('main_text')
            main_photo = request.files.get('main_photo').read()
            description = request.form.get("description")
            data.append((main_text, main_photo))
            for i in range(len(request.form) - 2):
                data.append([request.form.get(f'text{i}'), request.files.get(f'photo{i}').read()])
            session = db_session.create_session()
            images_id = ""
            texts = ""
            for i in range(1, len(request.form) - 1):
                image = Image(
                    image=data[i][1]
                )
                session.add(image)
                session.commit()
                images_id += str(image.id) + '|'
                texts += data[i][0] + '—'
            image = Image(
                image=data[0][1]
            )
            session.add(image)
            session.commit()
            studie = Studie(
                user_id=current_user.id,
                main_images=image.id,
                main_name=data[0][0],
                images=images_id,
                texts=texts,
                made_data=datetime.datetime.now(),
                description=description
            )
            session.add(studie)
            session.commit()
            return redirect("/")
    return render_template('make_new_studies.html', n=1)


@app.route('/view_of_studies/<int:id>', methods=['GET', 'POST'])
def view_of_studies(id):
    session = db_session.create_session()
    form = Add_Commentform()
    if form.validate_on_submit():
        comment = Comment(
            user_id=current_user.id,
            studie_id=id,
            made_data=datetime.datetime.now(),
            text=form.text.data,
            check_this=False
        )
        session.add(comment)
        session.commit()
    studie = session.query(Studie).filter(Studie.id == id).first()
    ratings = session.query(Rating).filter(Rating.id_studie == id).all()
    check = False
    if current_user.is_authenticated:
        follow_list = current_user.follow.split('|')
        if follow_list[0] == '':
            del follow_list[0]
        follow_list = list(map(int, follow_list))
        check = studie.id in follow_list
    if len(ratings) > 0:
        score = round(sum(i.score for i in ratings) / len(ratings), 1)
    else:
        score = 0
    check_edit = False
    if current_user.is_authenticated:
        check_edit = studie.id in list(
            map(lambda x: x.id, current_user.studies)) or current_user.type_of_user == "SAdmin"
    images = studie.images.split('|')[:-1]
    k = 0
    if current_user.is_authenticated:
        images.append(current_user.image.id)
        k = 1
    texts = studie.texts.split('—')[:-1]
    comments = session.query(Comment).filter(Comment.studie_id == id).all()
    images.extend([i.user.id_foto for i in comments])
    len_img = 0
    for i in images:
        img = session.query(Image).filter(Image.id == int(i)).first()
        out = open(f"static/img/tmp/{i}.jpg", "wb")
        out.write(img.image)
        len_img += 1
        out.close()
    images = images[:len(images) - k]
    len_img -= k
    person_score = 0
    if current_user.is_authenticated:
        person_rat = session.query(Rating).filter(Rating.id_studie == id, Rating.id_user == current_user.id).first()
        if person_rat:
            person_score = person_rat.score
    print(person_score)
    return render_template('view_of_studies.html',
                           n=len_img - len(comments), imgs=images, texts=texts,
                           comments=comments, form=form, id=id, score=score, check=check, check_edit=check_edit,
                           person_score=person_score)


# @app.route('/edit_studie/<int:id>', methods=['GET', 'POST'])
# def edit_studie(id):
#    if not current_user.is_authenticated:
#        return redirect("/login")
#    session = db_session.create_session()
#    studie = session.query(Studie).filter(Studie.id == id).first()
#    if current_user.id != studie.user_id:
#        return "Отказано в доступе"
#    if request.method == 'POST':
#        pass
#
#    images = studie.images.split('|')[:-1]
#    texts = studie.texts.split('—')[:-1]
#    srcs = []
#    out = open(f"static/img/tmp/{studie.image.id}.jpg", "wb")
#    out.write(studie.image.image)
#    out.close()
#    srcs.append((f"/static/img/tmp/{studie.image.id}.jpg", studie.description))
#    ind = 0
#    for i in images:
#        img = session.query(Image).filter(Image.id == int(i)).first()
#        out = open(f"static/img/tmp/{str(img.id)}.jpg", "wb")
#        out.write(img.image)
#        out.close()
#        srcs.append((f"/static/img/tmp/{str(img.id)}.jpg", texts[ind]))
#        ind += 1
#    l = len(srcs)
#    return render_template("edit_studie.html", title="anime", srcs=srcs, l=l, n=l - 1)


# ___________________________________________

# Отображение профиля, админ панель, главный экран
@app.route('/profile/<int:id>', methods=['GET', 'POST'])
def myprofile(id):
    if not current_user.is_authenticated:
        return redirect("/login")
    session = db_session.create_session()
    user = session.query(User).filter(User.id == id).first()
    checks = []
    follow_list = user.follow.split('|')
    if follow_list[0] == '':
        del follow_list[0]
    follow_list = list(map(int, follow_list))
    studies = session.query(Studie).filter(Studie.id.in_(follow_list)).all()
    for i in studies:
        checks.append(i.id in follow_list)
    my_studies = user.studies
    out = open(f"static/img/tmp/{user.image.id}.jpg", "wb")
    out.write(user.image.image)
    out.close()
    return render_template("myprofile.html", data=user, studies=studies, my_studies=my_studies,
                           checks=checks)


@app.route('/adminpanel', methods=['GET', 'POST'])
def adminpanel():
    session = db_session.create_session()
    user = session.query(User).filter(User.id == current_user.id).first()
    if user.type_of_user == 'admin' or user.type_of_user == 'SAdmin':
        data = session.query(User).all()
        comments = session.query(Comment).filter(Comment.check_this).all()
        return render_template("admin_panel.html", data=data, current_user=current_user,
                               comments=comments)
    else:
        return "Отказано в доступе"


@app.route('/', methods=['GET', 'POST'])
def index():
    session = db_session.create_session()
    if current_user.is_authenticated:
        out = open(f"static/img/tmp/{current_user.image.id}.jpg", "wb")
        out.write(current_user.image.image)
        out.close()
    studies = session.query(Studie).all()
    scores = session.query(Rating).all()
    score = {}
    for i in scores:
        if i.id_studie not in score:
            score[i.id_studie] = [0, 0]
        score[i.id_studie][0] += i.score
        score[i.id_studie][1] += 1
    for i in score.keys():
        score[i] = round(score[i][0] / score[i][1], 1)
    for i in [i.image for i in studies]:
        out = open(f"static/img/tmp/{i.id}.jpg", "wb")
        out.write(i.image)
        out.close()
    checks = []
    if current_user.is_authenticated:
        li = current_user.follow.split('|')
        if li[0] == '':
            del li[0]

        li = list(map(int, li))
        for i in studies:
            checks.append(i.id in li)
    return render_template("index.html", title="anime", data=studies, current_user=current_user, score=score,
                           checks=checks)


# ___________________________________________
# Функции для изменения свойств пользоватлей
@app.route('/newtype', methods=['GET', 'POST'])
def change_type():
    if not current_user.is_authenticated:
        return redirect("/login")
    session = db_session.create_session()
    user = session.query(User).filter(User.id == current_user.id).first()
    if user.type_of_user == 'admin' or user.type_of_user == 'SAdmin':
        user_id = request.args.get('user_id')
        new_type = request.args.get('type')
        user = session.query(User).filter(User.id == user_id).first()
        user.type_of_user = new_type
        session.commit()
        return redirect("/adminpanel")
    else:
        return "Отказано в доступе"


@app.route('/follow/', methods=['GET', 'POST'])
def follow():
    if not current_user.is_authenticated:
        return redirect("/login")
    session = db_session.create_session()
    num = int(request.args.get('studie_id'))
    n = int(request.args.get('main_menu'))
    li = current_user.follow.split('|')
    if li[0] == '':
        del li[0]
    li = list(map(int, li))
    ind = f_insert(li, num)
    if ind == -1:
        if n == 1:
            return redirect(f"/")
        elif n == 2:
            return redirect(f"/profile/{current_user.id}")
        else:
            return redirect(f"/view_of_studies/{num}")
    li.insert(ind, num)
    user = session.query(User).filter(User.id == current_user.id).first()
    user.follow = "|".join(list(map(str, li)))
    session.commit()
    if n == 1:
        return redirect(f"/")
    elif n == 2:
        return redirect(f"/profile/{current_user.id}")
    else:
        return redirect(f"/view_of_studies/{num}")


@app.route('/delfollow/', methods=['GET', 'POST'])
def delfollow():
    if not current_user.is_authenticated:
        return redirect("/login")
    session = db_session.create_session()
    n = int(request.args.get('main_menu'))
    num = int(request.args.get('studie_id'))
    li = current_user.follow.split('|')
    if li[0] == '':
        del li[0]
    li = list(map(int, li))
    ind = search_follow(li, num)
    if len(li) <= ind:
        if n == 1:
            return redirect(f"/")
        elif n == 2:
            return redirect(f"/profile/{current_user.id}")
        else:
            return redirect(f"/view_of_studies/{num}")
    if num != li[ind]:
        if n == 1:
            return redirect(f"/")
        elif n == 2:
            return redirect(f"/profile/{current_user.id}")
        else:
            return redirect(f"/view_of_studies/{num}")
    del li[ind]
    user = session.query(User).filter(User.id == current_user.id).first()
    user.follow = "|".join(list(map(str, li)))
    session.commit()
    if n == 1:
        return redirect(f"/")
    elif n == 2:
        return redirect(f"/profile/{current_user.id}")
    else:
        return redirect(f"/view_of_studies/{num}")


@app.route('/ratings/', methods=['GET', 'POST'])
def ratings():
    if not current_user.is_authenticated:
        return redirect("/login")
    session = db_session.create_session()
    studie_id = request.args.get('studie_id')
    val = request.args.get('val')
    if session.query(Rating).filter(Rating.id_user == current_user.id, Rating.id_studie == studie_id).first():
        r = session.query(Rating).filter(Rating.id_user == current_user.id, Rating.id_studie == studie_id).first()
        r.score = val
        session.commit()
        return redirect(f"/view_of_studies/{studie_id}")
    rating = Rating(
        id_studie=studie_id,
        id_user=current_user.id,
        score=val
    )
    session.add(rating)
    session.commit()
    return redirect(f"/view_of_studies/{studie_id}")


@app.route('/delcomment', methods=['GET', 'POST'])
def delcomment():
    if not current_user.is_authenticated:
        return redirect("/login")
    session = db_session.create_session()
    studie_id = request.args.get('studie_id')
    comment_id = request.args.get('val')

    comment = session.query(Comment).filter(Comment.id == comment_id).first()
    if current_user.id != comment.user_id and comment_id.type_of_user in ['creative', 'basic']:
        return "Отказано в доступе"
    session.delete(comment)
    session.commit()
    return redirect(f"/view_of_studies/{studie_id}")


@app.route('/addcheck/', methods=['GET', 'POST'])
def addcheck():
    session = db_session.create_session()
    studie_id = request.args.get('studie_id')
    comment_id = request.args.get('val')

    comment = session.query(Comment).filter(Comment.id == comment_id).first()
    comment.check_this = True
    session.commit()
    return redirect(f"/view_of_studies/{studie_id}")


@app.route('/delstudie/<int:id>', methods=["GET", "POST"])
def delstudie(id):
    if not current_user.is_authenticated:
        return redirect("/login")
    session = db_session.create_session()
    studie = session.query(Studie).filter(Studie.id == id).first()

    if current_user.id != studie.user_id:
        return "Отказано в доступе"
    users = session.query(User).all()
    for i in users:
        li = i.follow.split('|')
        if li[0] == '':
            del li[0]
        li = list(map(int, li))
        ind = search_follow(li, id)
        if len(li) <= ind:
            continue
        if id != li[ind]:
            continue
        del li[ind]
        i.follow = "|".join(list(map(str, li)))
        session.commit()
    for i in studie.commemts:
        session.delete(i)
    for j in studie.images.split("|")[:-1]:
        img = session.query(Image).filter(Image.id == j).first()
        session.delete(img)
    session.delete(studie)
    session.commit()
    return redirect("/")


# ___________________________________________

if __name__ == '__main__':
    app.run()
