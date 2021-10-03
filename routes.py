from flask import redirect, render_template, request, session
from app import app
import users
import courses
import questions

@app.route("/")
def index():
    course_list = courses.get_active_courses()
    return render_template("index.html", courses=course_list)

@app.route("/courses/<int:course_id>")
def course_pages(course_id):
    user_id = session["user_id"]
    course = courses.get_course(course_id)
    user_in_course = courses.check_if_user_in_course(user_id, course_id)
    textmaterial = courses.get_latest_textmaterial(course_id)
    textquestions = questions.get_active_textquestions(course_id)
    course_stats = questions.get_statistics_for_one_course(user_id, course_id)
    if course:
        return render_template("course.html", course=course, textmaterial=textmaterial,
                                textquestions=textquestions, course_stats=course_stats,
                                user_in_course=user_in_course)
    return render_template("error.html", message="Kurssia ei löydy")

@app.route("/join_course")
def join_course():
    user_id = session["user_id"]
    course_id =session["course_id"]
    if courses.add_user_to_course(user_id, course_id):
        return redirect(f"/courses/{course_id}")
    return render_template("error.html", message="Kurssille liittyminen ei onnistunut")

@app.route("/remove_from_course")
def remove_from_course():
    user_id = session["user_id"]
    course_id =session["course_id"]
    if courses.remove_user_from_course(user_id, course_id):
        return redirect(f"/courses/{course_id}")
    return render_template("error.html", message="Kurssilta poistuminen ei onnistunut")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if not users.valid_input(username) or not users.valid_input(password):
            return render_template("login.html", message="Käyttäjätunnus tai salasana ei kelpaa") 
        if users.login(username, password):
            return redirect("/")
        return render_template("login.html", message="Väärä tunnus tai salasana")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        teacher = request.form.getlist("teacher")
        if (not users.valid_input(username) or not users.valid_input(password1)
            or not users.valid_input(password2)):
            return render_template("register.html", message="Käyttäjätunnus tai salasana ei kelpaa") 
        if users.check(username):
            return render_template("register.html", message="Käyttäjätunnus on jo olemassa")
        if password1 != password2:
            return render_template("register.html", message="Salasanat eroavat")
        if users.register(username, password1, teacher):
            return redirect("/")
        return render_template("register.html", message="Rekisteröinti ei onnistunut")

@app.route("/add_course", methods=["POST"])
def add_course():
    course_name = request.form["course_name"]
    if courses.add_course(course_name):
        return redirect("/")
    return render_template("error.html", message="Kurssin lisääminen ei onnistu")

@app.route("/delete_course")
def delete_course():
    if courses.delete_course(session["course_id"]):
        return redirect("/")
    return render_template("error.html", message="Kurssin lisääminen ei onnistu")

@app.route("/add_textmaterial", methods=["POST"])
def add_textmaterial():
    textmaterial = request.form["textmaterial"]
    course_id = session["course_id"]
    if courses.add_textmaterial(course_id, textmaterial):
        return redirect(f"/courses/{course_id}")
    return render_template("error.html", message="Materiaalin lisääminen ei onnistu")

@app.route("/add_textquestion", methods=["POST"])
def add_textquestion():
    textquestion = request.form["textquestion"]
    textanswer = request.form["textanswer"]
    course_id = session["course_id"]
    if questions.add_textquestion(course_id, textquestion, textanswer):
        return redirect(f"/courses/{course_id}")
    return render_template("error.html", message="Kysymyksen lisääminen ei onnistu")

@app.route("/delete_textquestion", methods=["POST"])
def delete_textquestion():
    course_id = session["course_id"]
    question_id = request.form["question_id"]
    if questions.delete_textquestion(question_id):
        return redirect(f"/courses/{course_id}")
    return render_template("error.html", message="Kysymyksen poistaminen ei onnistu")

@app.route("/answer_textquestion", methods=["POST"])
def answer_textquestion():
    course_id = session["course_id"]
    user_id = session["user_id"]
    question_id = request.form["question_id"]
    answer = request.form["textanswer"]
    if questions.add_textanswer(user_id, question_id, answer):
        return redirect(f"/courses/{course_id}")
    return render_template("error.html", message="Vastaaminen ei onnistu")

@app.route("/statistics")
def statistics():
    user_id = session["user_id"]
    courses_stats = questions.get_statistics_for_all_courses(user_id)
    return render_template("statistics.html", courses = courses_stats)

@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")
