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

import re
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
	#email = flask.request.form['email']
	email = request.form.get('email')
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
		#adding contribution score
		contribution_score = 0
		print(cursor.execute("INSERT INTO Users (email, password, first_name, last_name, birthdate, contribution_score) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}')".format(email, password, first_name, last_name, birthday, contribution_score)))
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

def getUserNameFromId(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT first_name  FROM Users WHERE user_id = '{0}'".format(user_id))
    return cursor.fetchone()[0]

#NEW FUNCTION ADDED
def getAllPhotos():
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures")
	return cursor.fetchall()
    
def getAllPIDS():
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id FROM Pictures")
	I = cursor.fetchall()
	ids = [int(item[0]) for item in I]
	return ids


def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE return a list of tuples, [(imgdata, pid, caption), ...]

#Adding too function to increment contribution score of specific user 
#WORK ON 

def get_caption(picture_id):
	cursor = conn.cursor()
	cursor.execute("SELECT caption from Pictures WHERE picture_id = '{0}'".format(picture_id))
	return cursor.fetchall()

def get_contribution_score(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT contribution_score from Users WHERE user_id = '{0}'".format(uid))
	return cursor.fetchone()[0]

def increment_score(uid):
	cursor = conn.cursor()
	contribution_score = get_contribution_score(uid)
	cursor.execute("UPDATE Users SET contribution_score = '{0}' WHERE user_id = '{1}'".format(int(contribution_score) + 1, uid))  
	return 

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



@app.route('/allalbums')
def all_albums():
	return render_template('allalbums.html', message="Here are all the albums")


#all comments and number of likes along with name of user listed here 
@app.route('/allphotos')
def all_photos():
	email = flask_login.current_user.id
	return render_template('allphotos.html',
							#comments=get_all_comments(getAllPIDS()), 
							#usersLiked=getLikesUsers(getAllPIDS()),
							name = email,
							photos = getAllPictureIds(),
							message = "Here are all the photos", base64=base64)
							
	#need to see all tags
@app.route('/<picture_id>')
def viewlikecomment(picture_id):
	#picture_id = request.form.get("picture_id")
	picture_id = int(picture_id)
	return render_template('like-comment.html',
							#Add a option to add photo and then a function to get photo from picture_id
							caption = get_caption(picture_id),
							comments=get_photo_comments(picture_id), 
							usersLiked=getLikesUsers(picture_id),
							likes = getNoLikes(picture_id),
							message = "Here are all the comments and likes", 
							base64 = base64)












	

@app.route('/userphotos')
@flask_login.login_required
def user_photos():
	uid = getUserIdFromEmail(flask_login.current_user.id)
	return render_template('userphotos.html', 
							name =flask_login.current_user.id, 
							message="Here are your photos", 
							photos=getUserPictureIds(uid), 
							base64=base64)



	#need to add option to delete or modify photos here 
	#option to select photos to add to album or create new album 

#Added new top 10 contributers function 

def top_10_users():
	Users =[]
	cursor = conn.cursor()
	cursor.execute("SELECT first_name, last_name, contribution_score FROM Users order by contribution_score ASC LIMIT 3") 
	U = cursor.fetchall()
	Users.append(U)
	return Users
	 
	 

@app.route('/top_10_users')
@flask_login.login_required
def projecting_users():
	return render_template('top_10_users.html', name = flask_login.current_user.id, message = "Here are the top 10 users", content = top_10_users(), base64=base64)
	




#------------FRIEND MANAGEMENT-----------
#SOMETHING IS WRONG WITH LOADING THIS BUT IM NOT SURE WHAT


""" 
@app.route('/add_friend')
@flask_login.login_required #means that login must be provided to enter page
def friend_rec():
	return render_template('add_friend.html', name=flask_login.current_user.id, message="Here are your friend recommendations")
"""

#what to show on the add friend page right away

@app.route('/add_friend')#, methods = ['GET'])

@flask_login.login_required

def add_friend_page():
	email = flask_login.current_user.id
	uid = getUserIdFromEmail(email)
	return render_template('add_friend.html', name=flask_login.current_user.id, friends=showFriends(uid))

#showing a list of all of a user's friends

def showFriends(uid):
	mycursor = conn.cursor()
	sql = "SELECT friend_id FROM friends_with WHERE user_id = '%s'"
	mycursor.execute(sql, uid)
	Res = mycursor.fetchall()
	friendIds = [x[0] for x in Res]
	Friends = []
	for index in friendIds:
		sql2 = "SELECT first_name, last_name FROM Users WHERE user_id = '%s'"
		mycursor.execute(sql2, index)
		F = (cursor.fetchone())
		if(F!=None):
			F = (str(F[0]), str(F[1]))
		Friends.append(F)
	return Friends

	





#get someone's name from their email
def getUserNameFromEmail(email):
	mycursor = conn.cursor()
	sql = "SELECT first_name, last_name FROM Users WHERE email = '%s'"
	mycursor.execute(sql, email)
	U = cursor.fetchone()
	U = [str(item) for item in U]
	return U

""" 

 #get the user name from email function:

def getUserNameFromEmail(email):

	mycursor = conn.cursor()

	sql = "SELECT first_name, last_name  FROM Users WHERE email = '{0}'".format(email)

	mycursor.execute(sql)

	N = cursor.fetchone()

	#N = [str(x) for x in N]

	return N 

	"""



#getting results of searched friends
@app.route('/results', methods = ['POST', 'GET'])
@flask_login.login_required #means that login must be provided to enter page
def results():
	if request.method == 'POST':
		friendEmail = request.form.get('friendEmail')
		#user_creds = getUserNameFromEmail(friendEmail) 
		friend_id = getUserIdFromEmail(friendEmail)
		user_id = getUserIdFromEmail(flask_login.current_user.id)
		mycursor = conn.cursor()
		sql = "INSERT IGNORE INTO friends_with (user_id, friend_id) VALUES ('{0}', '{1}')".format(user_id, friend_id)
		mycursor.execute("INSERT IGNORE INTO friends_with (user_id, friend_id) VALUES ('{0}', '{1}')".format(user_id, friend_id))
		conn.commit()
		return render_template('add_friend.html')#, user_creds = user_creds, friend_id=friend_id)
	else:
		return render_template() #need to figure out what to redirect to

#adding friends function	
@app.route('/add_friends', methods = ['POST', 'GET'])
@flask_login.login_required
def add_friend():
	friend_id = getUserIdFromEmail(request.form.get('friend_id'))
	user_id = getUserIdFromEmail(flask_login.current_user.id)
	mycursor = conn.cursor()
	sql = "INSERT IGNORE INTO friends_with (user_id, friend_id) VALUES ('{0}', '{1}')".format(user_id, friend_id)
	mycursor.execute(sql)
	conn.commit()
	return flask.redirect(flask.url_for('add_friend_page')) 

	

#-------END OF FRIEND MANAGEMENT--------

	
#--------------TAG MANAGEMENT----------
@app.route('/add_tag', methods = ['GET', 'POST'])
@flask_login.login_required
def add_tag():
	if request.method == 'POST':
		tag_w = request.form.get('add_tag')
		p = request.values.get('picture_id')
		picture_id = int(p) 
		mycursor = conn.cursor()
		sql = "INSERT IGNORE INTO Tag (tag_word) VALUES (%s)"
		mycursor.execute(sql, tag_w)
		conn.commit()
		mycursor.execute("SELECT tag_id FROM Tag")
		tid = mycursor.fetchone()[0]
		sql2 = "INSERT INTO assigned_tag (picture_id, tag_id) VALUE (%s, %s)"
		mycursor.execute(sql2, (picture_id, tid))
		conn.commit()
		return render_template('userphotos.html')#not sure which template should be rendered
	return render_template('userphotos.html')
	#Add a tag attribute associated with every photo and add periodically

#create intersection function
def searchByTagPicture(tags):
	tags = re.split("\s|,|:|\.|!|\?|@|#|$|%|\(|\)|-|_|\+|=|{|}|\[|\]|\"", tags)
	picture_ids = []
	mycursor = conn.cursor()
	for t in tags:
		mycursor.execute("SELECT picture_id FROM Tag T, assigned_tag A WHERE tag_word = '{0}'".format(t))
		output = cursor.fetchall()
		output = [item[0] for item in output]
		picture_ids.append(output) 
	intersection = []
	if len(picture_ids) > 1:
		intersection = list(set(picture_ids[0]) & set(picture_ids[1]))
	else:
		intersection = picture_ids[0]
	for index in range (len(picture_ids)-2):
		intersection = list(set(intersection)) & set(picture_ids[index])
	return intersection

#search by tags function:
#this will be in the all photos area
#need to include routing
@app.route('/search_tag', methods = ['GET', 'POST'])
def search_tag_page():
	if(request.method == 'POST'):
		tag_word=request.form.get('searchTag')
		tag_word = str(tag_word)
		mycursor = conn.cursor()
		intersectList = searchByTagPicture(tag_word)
		photos = []
		for pid in intersectList:
			mycursor.execute("SELECT imgdata, caption FROM Pictures WHERE picture_id = '{0}'".format(pid))
			output = cursor.fetchall()
			output = [item[0] for item in output]
			photos.append(output)
		return render_template('allphotos.html', search_tags = photos)
	return render_template('allphotos.html')

#view all tags

#------LIKE MANAGEMENT---------
@app.route('/add_like', methods = ['GET', 'POST'])
def like():
	pid = request.form.get('picture_id')
	photo_id = int(pid)
	if request.method == 'POST':
		user_id = getUserIdFromEmail(flask_login.current_user.id)
		mycursor = conn.cursor()
		sql = "INSERT INTO Likes (user_id, picture_id) VALUES (%s, %s)"
		mycursor.execute(sql, (user_id, photo_id))
		conn.commit()
		return render_template('allphotos.html') 
	else:
		return render_template('allphotos.html')
	 
	
#function directly called when rendering all_photos page
#SOMETHING WRONG WITH FUNCTION 
def getLikesUsers(pid):
	cursor = conn.cursor()
	Likes = [] 
	cursor.execute("SELECT picture_id, user_id FROM Likes where picture_id = '{0}'".format(pid))
	T = cursor.fetchall()
	C = [(str(item[0]), str(getUserNameFromId(int(item[1])))) for item in T]
	Likes.append(C)
	return Likes
	
def getNoLikes(pid):
	cursor = conn.cursor()
	No_likes = []
	cursor.execute("SELECT COUNT(*) FROM Likes where picture_id = '{0}'".format(pid))
	L = cursor.fetchone()
	L = int(L[0])
	No_likes.append(L)
	return No_likes


#-----COMMENT MANAGEMENT------

#new functions to add 
def getAllPictureIds():
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id FROM Pictures")
	R = cursor.fetchall()
	row= [int(item[0]) for item in R]
	return row


def getUserPictureIds(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id FROM Pictures WHERE user_id = '{0}'".format(uid))
	R = cursor.fetchall()
	row = [int(item[0]) for item in R]
	return row


@app.route("/add_comment", methods = ['GET', 'POST'])
@flask_login.login_required
def add_comment():
	pid = request.form.get('picture_id')
	photo_id = int(pid)
	#print(photo_id)
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		comment_text = request.form.get('comment')
		increment_score(uid)
		mycursor = conn.cursor()
		sql = "INSERT INTO Comments (comment_text, user_id, picture_id) VALUE (%s, %s, %s)"
		mycursor.execute(sql, (comment_text, uid, photo_id))
		conn.commit()
		return render_template('allphotos.html')
	else:
		return render_template('allphotos.html')
	

#function directly called when rendering all_photos page 
def get_all_comments(pids):
	cursor = conn.cursor()
	Comments = []
	for id in pids:
		cursor.execute("SELECT comment_text, user_id FROM Comments where picture_id = '{0}'".format(id))
		T = cursor.fetchall()
		C = [(str(item[0]), str(getUserNameFromId(int(item[1])))) for item in T]
		Comments.append(C)
	return Comments

def get_photo_comments(pid):
	cursor = conn.cursor()
	Comments = []
	cursor.execute("SELECT comment_text, user_id FROM Comments where picture_id = '{0}'".format(pid))
	T = cursor.fetchall()
	C = [(str(item[0]), str(getUserNameFromId(int(item[1])))) for item in T]
	Comments.append(C)
	return Comments


		
		

#------PHOTO MANAGEMENT ------

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
		#Adding line to call function to increment contribution score
		increment_score(uid)
		cursor = conn.cursor()
		cursor.execute('''INSERT INTO Pictures (imgdata, user_id, caption) VALUES (%s, %s, %s )''', (photo_data, uid, caption))
		conn.commit()
		return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!')
	#The method is GET so we return a  HTML form to upload the a photo.
	else:
		return render_template('upload.html')
#end photo uploading code

#DELETE PHOTOS
@app.route('/delete_photo', methods = ['POST'])
@flask_login.login_required
def delete_photo(): 
	if request.method == "POST":
		picture_id = request.form.get('picture_id')
		photo_id = int(picture_id)
		uid = getUserIdFromEmail(flask_login.current_user.id)
		mycursor = conn.cursor()
		mycursor.execute("DELETE FROM Pictures where picture_id = '{0}'".format(photo_id))
		conn.commit()
		return render_template('userphotos.html', photos = getUsersPhotos(uid))
	else:
		return render_template('userphotos.html', photos = getUsersPhotos(uid))
		

#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', message='Welecome to Photoshare')


#------------ALBUM MANAGEMENT-----------

@app.route('/photos', methods=['GET'])
@flask_login.login_required
def photos():
    email = flask_login.current_user.id
    uid = getUserIdFromEmail(email)
    print(flask_login.current_user.id)
    return render_template('photos.html',
                           name=email,
                           albums=getUsersAlbums(uid))
                           #friends=getFriendsList(uid),
                           #recommendedPhotos=picturesRecommendation(),
                           #activeUsers=userActivity())



@app.route('/create_album', methods = ['POST'])
@flask_login.login_required
def create_album():
	if request.method == 'POST':
		aname = request.form.get('albumName') 
		uid = getUserIdFromEmail(flask_login.current_user.id)
		mycursor = conn.cursor()
		sql = "INSERT INTO Album (album_name, user_id) VALUES ('{0}', '{1}')".format(aname, uid)
		mycursor.execute(sql)
		conn.commit()
		return flask.redirect(flask.url_for('photos'))
	#should be able to choose photos from user photos
	#also need to add album to database
	else:
		return flask.redirect(flask.url_for('photos')) 


def getUsersAlbums(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT album_name FROM Album where user_id = '{0}'".format(uid))
	R = cursor.fetchall()
	row = [item[0] for item in R]
	return row

def getAlbumIdFromName(albumName, uid):
	cursor = conn.cursor()
	cursor.execute("SELECT album_id FROM Album WHERE album_name = '{0}'AND user_id = '{1}'".format(albumName, uid))
	return cursor.fetchone()[0]

#new functions to add 
def getAllPictureIds():
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id FROM Pictures")
	R = cursor.fetchall()
	row= [int(item[0]) for item in R]
	return row


def getUserPictureIds(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT picture_id FROM Pictures WHERE user_id = '{0}'".format(uid))
	R = cursor.fetchall()
	row = [int(item[0]) for item in R]
	return row




def getAlbumsPhotos(album_id):
	cursor = conn.cursor()
	cursor.execute("SELECT imgdata,caption FROM Pictures WHERE album_id = '{0}'".format(album_id))
	Photos = cursor.fetchall()
	P = cursor.execute("SELECT picture_id FROM Pictures WHERE album_id = '{0}'".format(album_id))
	p = cursor.fetchall()
	pids = [item[0] for item in p]
	return Photos, pids

'''
@app.route('/photos/upload/<albumName>/', methods = ['GET', 'POST'])
@flask_login.login_required
def upload_files(albumName):
	if request.method == "POST":
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo'] #unsure of where the photo files is being requested in HTML
		album_id = getAlbumIdFromName(albumName, uid)
		caption = request.form.get('caption')
		photo_data = base64.standard_b64encode(imgfile.read())
		cursor = conn.cursor()
		cursor.execute("INSERT INTO Pictures (imgdata, user_id, caption, album_id) VALUES ('{0}', '{1}', '{2}', '{3}')".format(photo_data, uid, caption, album_id))
		conn.commit()
		return render_template('photos.html', name=flask_login.current_user.id, message='Photo uploaded!',
                               photos=getAlbumsPhotos(album_id)[0], album=albumName)
	else:
		return render_template('upload.html', album = albumName)

'''	

@app.route('/remove_album', methods = ['GET', 'POST'])
@flask_login.login_required
def remove_album():
	if request.method == 'POST':
		albumName = request.form.get('albumName')
		user_id = getUserIdFromEmail(flask_login.current_user.id)
		album_id = getAlbumIdFromName(albumName, user_id)
		album_id = int(album_id)
		cursor = conn.cursor()
		cursor.execute("DELETE FROM Album WHERE album_id= '{0}'".format(album_id))
		conn.commit()
		return render_template('photos.html', name=flask_login.current_user.id)
	else:
		return render_template('hello.html', name=flask_login.current_user.id)
		

@app.route('/upload_album_photos', methods = ['GET', 'POST'])
@flask_login.login_required
def show_photos():
	user_id = getUserIdFromEmail(flask_login.current_user.id)
	#tags = getTags(getAlbumsPhotos(album_id)[1])
	if request.method == "POST":
		uid = user_id
		albumName = request.form.get('albumName')
		album_id = getAlbumIdFromName(albumName, user_id)
		imgfile = request.files['photo'] 
		caption = request.form.get('caption')
		photo_data =base64.standard_b64encode(imgfile.read())
		cursor = conn.cursor()
		#Something wrong with syntax of this line 
		sql = "INSERT INTO Pictures (imgdata, user_id, album_id, caption) VALUE (%s, %s, %s, %s)"
		cursor.execute(sql ,(photo_data, user_id ,album_id, caption))
		
		conn.commit()
		return render_template('photos.html', name=flask_login.current_user.id, message='Photo uploaded!',
                               photos=getAlbumsPhotos(album_id)[0])
	
	else:
		return render_template('photos.html', 
								albums=albumName,
								message = 'Here are your albums and photos', 
								photos=getAlbumsPhotos(album_id)[0],
                            	pids=getAlbumsPhotos(album_id)[1])






if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
