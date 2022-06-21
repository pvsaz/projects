import re
from flask import Flask, render_template, request, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import LoginManager, login_user, UserMixin, current_user, login_required, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(app)

class BlogPost(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(100), nullable=False)
	content = db.Column(db.Text,nullable=False)
	#author = db.Column(db.String(20),nullable=False, default='N/A')
	date_posted = db.Column(db.DateTime,nullable=False,default=datetime.utcnow)
	email = db.Column(db.String(100), unique=False)
	
class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(100), unique=True)
	password = db.Column(db.String(100))
	#name = db.Column(db.String(1000))
	
	def __repr__(self):
		return 'Blog post ' + str(self.id)

@app.route('/')
def index():
	return render_template('index.html')

# new additions below 6/2022

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

@app.route('/signup', methods=['POST'])
def signup_post():
	email = request.form.get('email')
	#name = request.form.get('name')
	password = request.form.get('password')
	user = User.query.filter_by(email=email).first()
	if user: # if a user is found, we want to redirect back to signup page so user can try again
		flash('Email address already exists, please login under Your Account.')
		return redirect(url_for('signup'))
	if email == "" or password == "":
		flash('Please enter both an email address and a password.')
		return redirect(url_for('signup'))
	new_user = User(email=email, password=generate_password_hash(password, method='sha256'))
	
	db.session.add(new_user)
	db.session.commit()
	
    # code to validate and add user to database goes here
	flash('Account successfully made!')
	return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
	return render_template('profile.html', email=current_user.email)
	
@app.route('/login', methods=['POST'])
def login_post():
	email = request.form.get('email')
	password = request.form.get('password')
	remember = True if request.form.get('remember') else False
	user = User.query.filter_by(email=email).first()
	
	if not user or not check_password_hash(user.password, password):
		flash('Please check your login details and try again.')
		return redirect(url_for('login'))
	login_user(user, remember=remember)
	return redirect(url_for('profile'))

@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/signup')
def signup():
	return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))


# new additions above 6/2022

@app.route('/home/<string:name>')
def hello(name):
	return "Hello, " + name
	
@app.route('/posts', methods = ['GET', 'POST'])
def posts():

	if request.method == 'POST':
		post_title = request.form['title']
		post_content = request.form['content']
		#post_author = request.form['author']
		post_username = current_user.email
		new_post = BlogPost(title=post_title,content=post_content,email=post_username)
		db.session.add(new_post)
		db.session.commit()
		return redirect('/posts')
	else:
		all_posts = BlogPost.query.order_by(BlogPost.date_posted).all()
		return render_template('posts.html', posts=all_posts)


@app.route('/onlyget', methods=['POST'])
def get_req():
	return 'You can only get this webpage.'

@app.route('/posts/delete/<int:id>')
def delete(id):
		post = BlogPost.query.get_or_404(id)
		db.session.delete(post)
		db.session.commit()
		return redirect('/posts')

@app.route('/posts/edit/<int:id>',methods=['GET','POST'])
def edit(id):
	post = BlogPost.query.get_or_404(id)
	if request.method == 'POST':
		
		post.title = request.form['title']
		#post.author = request.form['author']
		post.content = request.form['content']
		db.session.commit()
		return redirect('/posts')
	else:
		return render_template('edit.html',post=post)

if __name__ == "__main__":
	app.run(debug=True)
