

from flask import Flask, render_template, request, session, redirect, url_for, jsonify

from data import check_acc, check_password, insert_acc, search_tierlist, get_best_tierlists, get_tierlist, get_user_info, get_user_tierlists, upvote_tierlist

app = Flask(__name__)
app.secret_key = "secret"

@app.route("/", methods=['GET', 'POST'])
def index():
    if 'username' in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for("login"))

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip().lower()
        password = request.form.get('password').strip()


        if not username or not password:
            return render_template("register.html", error="No username or password inputted")

        acc = check_acc(username)
        if acc:
            return render_template("register.html", error="Username already exists")

        insert_acc(username, password)

        session['username'] = username
        return redirect(url_for("dashboard"))
    return render_template("register.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # store username and password as a variable
        username = request.form.get('username').strip().lower()
        password = request.form.get('password').strip()


        if not username or not password:
            return render_template('login.html', error="No username or password inputted")


        account = check_password(username)


        if account is None:
            return render_template("login.html", error="Username or password is incorrect")


        if account[0] != password:
            return render_template("login.html", error="Username or password is incorrect")


        session["username"] = username
        return redirect(url_for("dashboard"))

    return render_template('login.html')

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if request.is_json:
        data = request.get_json()
        upvotes = upvote_tierlist(session['username'], data['tierlist_id'], data['value'])
        return jsonify({"upvotes": upvotes})

    search = request.args.get("searchbar")
    if search:
        search = search.strip().lower()
        tierlists = search_tierlist(search)
    else:
        tierlists = get_best_tierlists()
    return render_template('dashboard.html',
                           tierlists = tierlists)

@app.route("/profile", methods=['GET', 'POST'])
def profile():
    username = request.args.get('username') or session.get('username')
    if not username:
        return redirect(url_for('login'))
    
    user_info = get_user_info(username)
    if not user_info:
        return render_template('error.html', message="User not found")
        
    user_tierlists = get_user_tierlists(username)
    
    return render_template('profile.html', 
                         user=user_info, 
                         tierlists=user_tierlists,
                         is_own_profile=(username == session.get('username')))

@app.route("/view", methods=['GET', 'POST'])
def view():
    tierlist_id = request.args.get('id')
    if not tierlist_id:
        return redirect(url_for('dashboard'))

    tierlist = get_tierlist(tierlist_id)
    if not tierlist:
        return render_template('error.html', message="Tier List not found")

    return render_template('view.html', tierlist=tierlist)

@app.route("/editor", methods=['GET', 'POST'])
def editor():
    return render_template('editor.html')

@app.route("/error", methods=['GET', 'POST'])
def error():
    return render_template('error.html')
if __name__ == "__main__":
    app.debug = True
    app.run()
