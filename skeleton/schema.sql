CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;

DROP TABLE IF EXISTS assigned_tag CASCADE;
DROP TABLE IF EXISTS Tag CASCADE;
DROP TABLE IF EXISTS friends_with CASCADE;
DROP TABLE IF EXISTS Comments CASCADE;
DROP TABLE IF EXISTS Likes CASCADE;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Album CASCADE;
DROP TABLE IF EXISTS Users CASCADE;



CREATE TABLE Users (
    user_id int4  AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    password varchar(255),
    first_name varchar(225),
    last_name varchar(225),
    birthdate varchar(225),
    hometown varchar(225),
  CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Album (
	album_id int4 AUTO_INCREMENT,
    album_name VARCHAR(225),
    created_date DATE NOT NULL,
    user_id int4,
    CONSTRAINT album_pk PRIMARY KEY (album_id),
    CONSTRAINT user_fk FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Pictures
(
  picture_id int4  AUTO_INCREMENT,
  user_id int4,
  imgdata longblob ,
  caption VARCHAR(255),
  INDEX upid_idx (user_id),
  album_id int4,
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id),
  CONSTRAINT user_fk1 FOREIGN KEY (user_id) REFERENCES Users(user_id),
  CONSTRAINT album_fk FOREIGN KEY (album_id) REFERENCES Album(album_id)
);


CREATE TABLE Comments (
	comment_id int4 AUTO_INCREMENT,
    comment_text VARCHAR(225),
    comment_date DATE,
    user_id int4,
    photo_id int4,
    CONSTRAINT comment_pk PRIMARY KEY (comment_id),
    CONSTRAINT user_fk2 FOREIGN KEY (user_id) REFERENCES Users(user_id),
    CONSTRAINT photo_fk1 FOREIGN KEY (photo_id) REFERENCES Pictures(picture_id)
);

CREATE TABLE Likes (
	like_id int4 AUTO_INCREMENT,
    user_id int4,
    photo_id int4,
    CONSTRAINT like_pk PRIMARY KEY (like_id),
    CONSTRAINT user_fk3 FOREIGN KEY (user_id) REFERENCES Users(user_id),
    CONSTRAINT photo_fk2 FOREIGN KEY (photo_id) REFERENCES Pictures(picture_id) 
);

CREATE TABLE Tag(
	tag_word VARCHAR(225),
    CONSTRAINT word_pk PRIMARY KEY (tag_word)
);

CREATE TABLE assigned_tag(
	photo_id int4,
    tag_word VARCHAR(225),
    CONSTRAINT photo_tag_pk PRIMARY KEY (photo_id, tag_word),
    CONSTRAINT photo_fk3 FOREIGN KEY (photo_id) REFERENCES Pictures(picture_id),
	CONSTRAINT tag_fk FOREIGN KEY (tag_word) REFERENCES Tag(tag_word)

);

CREATE TABLE friends_with(
	user_id int4,
    friend_id int4,
    CONSTRAINT friends_pk PRIMARY KEY (user_id, friend_id),
    CONSTRAINT user_fk4 FOREIGN KEY (user_id) REFERENCES Users(user_id),
    CONSTRAINT friend_fk FOREIGN KEY (friend_id) REFERENCES Users(user_id)
); #getting error with this table: duplicate foreign key constraint


INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
