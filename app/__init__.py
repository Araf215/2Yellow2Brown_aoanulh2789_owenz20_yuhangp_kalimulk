# Aoanul Hoque (PM), Kalimul Kaif, Owen Zeng, Yuhang Pan
# 2Y2B TierList Creator by 2Yellow2Brown
# SoftDev
# P02: Makers Makin' It, Act I
# Jan 2026

from flask import Flask, render_template, request, session, redirect, url_for

from data import check_acc, check_password, insert_acc, get_recent_tierlists

app = Flask(__name__)
app.secret_key = "secret"

@app.route("/", methods=['GET', 'POST'])
def index():
    if 'username' in session:
        return redirect(url_for("home"))

    return redirect(url_for("login"))

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip().lower()
        password = request.form.get('password').strip()

        # reload page if no username or password was entered
        if not username or not password:
            return render_template("register.html", error="No username or password inputted")

        acc = check_acc(username)
        if acc:
            return render_template("register.html", error="Username already exists")
        
        insert_acc(username, password)

        session['username'] = username
        return redirect(url_for("home"))
    return render_template("register.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # store username and password as a variable
        username = request.form.get('username').strip().lower()
        password = request.form.get('password').strip()

        # render login page if username or password box is empty
        if not username or not password:
            return render_template('login.html', error="No username or password inputted")

        #search user table for password from a certain username
        account = check_password(username)

        #if there is no account then reload page
        if account is None:
            return render_template("login.html", error="Username or password is incorrect")

        # check if password is correct, if not then reload page
        if account[0] != password:
            return render_template("login.html", error="Username or password is incorrect")

        # if password is correct redirect home
        session["username"] = username
        return redirect(url_for("home"))

    return render_template('login.html')

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    tierlists = get_recent_tierlists()
    return render_template('dashboard.html',
                           tierlists = tierlists)

@app.route("/profile", methods=['GET', 'POST'])
def profile():
    return render_template('profile.html')

@app.route("/view", methods=['GET', 'POST'])
def view():
    return render_template('view.html')

@app.route("/editor", methods=['GET', 'POST'])
def editor():
    return render_template('editor.html')

@app.route("/error", methods=['GET', 'POST'])
def error():
    return render_template('error.html')