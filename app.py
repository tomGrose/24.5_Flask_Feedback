
from flask import Flask, request, render_template,  redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = "turtlezrock"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['DEBUG'] = True

toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


@app.route('/')
def index_page():
    """Renders index page"""
    return redirect("/register")

### View functions for logging in, registering, and logging out
@app.route('/register', methods=["GET", "POST"])
def register_user():
    """Show user registration form, handle registration form submission to register user"""

    if "username" in session:
        user = session["username"]
        return redirect(f"/users/{user}")

    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username, pwd, email, first_name, last_name)

        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken.  Please pick another')
            return render_template('register.html', form=form)

        session['username'] = user.username
    
        return redirect(f"/users/{user.username}")

    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login_user():
    """Show user login form and handle login form submission"""

    if "username" in session:
        user = session["username"]
        return redirect(f"/users/{user}")

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        pwd = form.password.data
    
        user = User.authenticate(username, pwd)

        if user:
            session['username'] = username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ["Invalid name or password"]

    return render_template("login.html", form=form)


@app.route("/logout", methods=["POST"])
def logout_user():
    """ Log a user out by clearing username out of the session, redirect to login page"""

    session.pop("username")

    return redirect("/login")


### View functions pertaining to the user
@app.route("/users/<username>")
def show_user_page(username):
    """ Show a user their profile page with all the feedback they have written"""

    
    if "username" not in session:
        flash ("Please Login!")
        return redirect("/login")
    
    user = User.query.get(session["username"])
    
    if session['username'] != username:
        flash ("You don't have permission to do that!")
        return redirect(f"/users/{session['username']}")

    if user.is_admin:
        all_feedback = db.session.query(Feedback).join(User).all()
    else:
        all_feedback = None
    feedback = db.session.query(Feedback).join(User).filter_by(username=user.username).all()

    return render_template("user_page.html", user=user, feedback=feedback, all_feedback=all_feedback)


@app.route("/users/<username>/delete", methods=["POST"])
def delete_user(username):
    """ Validate a user is logged in and it is the right user. Delete their account. 
    Delete the user will delete their feedback """

    
    if "username" not in session:
        flash ("Please Login!")
        return redirect("/login")
    
    user = User.query.get(session["username"])
    
    if session['username'] != username:
        flash ("You don't have permission to do that!")
        return redirect(f"/users/{session['username']}")
    
    db.session.delete(user)
    db.session.commit()
    session.pop("username")
    return redirect("/register")
    

### View functions for handling a users feedback
@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def show_feedback_form(username):
    """ Show a user the feedback form and handle the form submit. 
    Validate if user is logged in and it is the correct user """

     
    if 'username' not in session:
        flash ("You must be logged in to do that!")
        return redirect("/login")

    post_user = User.query.get_or_404(username)
    user = User.query.get(session["username"])

    if user.is_admin == False:
        if session["username"] != user.username:
            flash ("You don't have permission to do that!")
            return redirect(f"/users/{session['username']}")

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
    
        feedback = Feedback(title=title, content=content, username=username)

        db.session.add(feedback)
        db.session.commit()

        return redirect(f"/users/{session['username']}")

    return render_template("add_form.html", user=user, form=form)


@app.route("/feedback/<int:f_id>/update", methods=["GET", "POST"])
def update_feedback_form(f_id):
    """ Show a user the update feedback form and handle the form submit. 
    Validate if user is logged in and it is the correct user """
    
    if 'username' not in session:
        flash ("You must be logged in to do that!")
        return redirect("/login")

    feedback = Feedback.query.get_or_404(f_id)
    user = User.query.get(session["username"])

    if user.is_admin == False:
        if session["username"] != user.username:
            flash ("You don't have permission to do that!")
            return redirect(f"/users/{session['username']}")
    

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.add(feedback)
        db.session.commit()

        return redirect(f"/users/{user.username}")

    return render_template("edit_form.html", form=form)
    

@app.route("/feedback/<int:f_id>/delete", methods=["POST"])
def delete_feedback(f_id):
    """ Delete a users feedback """

    if 'username' not in session:
        flash ("You must be logged in to do that!")
        return redirect("/login")

    feedback = Feedback.query.get_or_404(f_id)
    user = User.query.get(session["username"])

    if user.is_admin == False:
        if session["username"] != user.username:
            flash ("You don't have permission to do that!")
            return redirect(f"/users/{session['username']}")
    
    db.session.delete(feedback)
    db.session.commit()
    flash("Post deleted")
    return redirect(f"/users/{session['username']}")






#### server error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404