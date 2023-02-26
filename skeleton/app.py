######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login

#for image uploading
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Z@c!sstupid123'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Users")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/register", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
		#adding additional inputs in registeration 
		first_name=request.form.get('fname')
		last_name=request.form.get('lname')
		birthday = request.form.get('DOB')
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	#Adding test of birthdate 
	testDOB = isDOBvalid(birthday)
	if test:
		print(cursor.execute("INSERT INTO Users (email, password) VALUES ('{0}', '{1}')".format(email, password)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=first_name, message='Account Created!')
	else:
		print("couldn't find all valid tokens")
		return flask.redirect(flask.url_for('register'))

import datetime
def isDOBvalid(birthday):
	date_format = '%m-%d-%y'
	try: 
		dateObject = datetime.datetime.strptime(birthday, date_format)
		return True
	except ValueError:
		return False

#NEW FUNCTION ADDED
def getAllPhotos():
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures")
	return cursor.fetchall()

def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE return a list of tuples, [(imgdata, pid, caption), ...]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code



@app.route('/profile')
@flask_login.login_required
def protected():
	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile")

#Adding connections to each link 
@app.route('/add_friend')
@flask_login.login_required #means that login must be provided to enter page
def friend_rec():
	return render_template('add_friend.html', name=flask_login.current_user.id, message="Here are your friend recommendations")

@app.route('/allalbums')
def all_albums():
	return render_template('allalbums.html', message="Here are all the albums")

@app.route('/allphotos')
def all_photos():
	return render_template('allphotos.html', message = "Here are all the photos", photos=getAllPhotos(), base64=base64)
	#need to add option to add a tag -- this should be in upload photo
	#need to add option to comment
	#need to add option to like photo

@app.route('/userphotos')
@flask_login.login_required
def user_photos():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('userphotos.html', name =flask_login.current_user.id, message="Here are your photos", photos=getUsersPhotos(), base64=base64)
	#need to add option to delete or modify photos here 
	#option to select photos to add to album or create new album 

@app.route('/create_album', methods=['GET', 'POST'])
@flask_login.login_required
def create_album():
	if request.method == 'POST':
		aname = request.form.get('album_name') #need to figure out how to get this
		uid = uid = getUserIdFromEmail(flask_login.current_user.id)
		mycursor = conn.cursor()
		sql = "INSERT INTO Album (album_name, user_id) VALUES (%s, %s )", (aname, uid)
		mycursor.execute(sql)
		conn.commit()
		return render_template('create_album.html', name = flask_login.current_user.id, message="You can create an album here!")
	#should be able to choose photos from user photos
	#also need to add album to database
	else:
		return render_template('create_album.html') 


@app.route('/delete_photo')
@flask_login.login_required
def delete_photo():
	#NEED TO FINISH IN FUNCTIONALITY SQL
	#Remove photo from specific user database 
	photo_id = "" #need to figure out what current photo id is, maybe use something like this @app.route('/<int:post_id>')
	mycursor = conn.cursor()
	sql = "DELETE FROM Pictures where picture_id = %s", photo_id
	mycursor.execute(sql)
	conn.commit()
	return 
	

@app.route('/add_tag', methods = ['GET', 'POST'])
@flask_login.login_required
def add_tag():
	if request.method == 'POST':
		tag_w = request.form.get('add_tag')
		mycursor = conn.cursor()
		sql = "INSERT INTO Tag (tag_word) VALUES (%s)", (tag_w)
		mycursor.execute(sql)
		conn.commit()
		return render_template()#not sure which template should be rendered
	return
	#Add a tag attribute associated with every photo and add periodically

@app.route('/Like')
def like():
	return 
	#NEED TO finish FUNCTIONALITY  in SQL
	#Add a like attribute associated with every photo and increase periodically

@app.route("/add_comment", methods = ['GET', 'POST'])
def add_comment():
	
	comment = request.form.get('add_comment')
	if request.method == 'POST':
		comment_text = request.form.get('add_comment')
		uid = getUserIdFromEmail(flask_login.current_user.id)
		photo_id = "" #need to figure this out
		mycursor = conn.cursor()
		sql = "INSERT INTO Comments (comment_text, user_id, photo_id) VALUES (%s, %s, %s)", (comment_text, uid, photo_id)
		mycursor.execute(sql)
		conn.commit()
	return #not sure what to return here
	#NEED TO FILL IN FUNCTIONALITY SQL 




#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		photo_data =imgfile.read()
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Pictures (imgdata, user_id, caption) VALUES (%s, %s, %s )''', (photo_data, uid, caption))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid), base64=base64)
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html')
#end photo uploading code


#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welecome to Photoshare')


if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
