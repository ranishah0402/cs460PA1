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
    user_id int4  NOT NULL AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    password varchar(255) NOT NULL DEFAULT '',
    first_name varchar(225) NOT NULL DEFAULT '',
    last_name varchar(225) NOT NULL DEFAULT '',
    birthdate DATE,
    hometown varchar(225),
    gender varchar(6),
  CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Album (
	album_id int4 AUTO_INCREMENT,
    album_name VARCHAR(225) NOT NULL DEFAULT '',
    created_date DATETIME DEFAULT current_timestamp,
    user_id int4 NOT NULL,
    CONSTRAINT album_pk PRIMARY KEY (album_id),
    CONSTRAINT user_fk FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

CREATE TABLE Pictures
(
  picture_id int4  AUTO_INCREMENT,
  user_id int4,
  imgdata longblob ,
  caption VARCHAR(255),
  INDEX upid_idx (user_id),
  album_id int4 NOT NULL,
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id),
  CONSTRAINT user_fk1 FOREIGN KEY (user_id) REFERENCES Users(user_id),
  CONSTRAINT album_fk FOREIGN KEY (album_id) REFERENCES Album(album_id) ON DELETE CASCADE
);


CREATE TABLE Comments (
	comment_id int4 NOT NULL AUTO_INCREMENT,
    comment_text VARCHAR(225) NOT NULL,
    comment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id int4 NOT NULL,
    photo_id int4 NOT NULL,
    CONSTRAINT comment_pk PRIMARY KEY (comment_id),
    CONSTRAINT user_fk2 FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    CONSTRAINT photo_fk1 FOREIGN KEY (photo_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE
);

CREATE TABLE Likes (
    user_id int4,
    photo_id int4,
    CONSTRAINT like_pk PRIMARY KEY (photo_id, user_id),
    CONSTRAINT user_fk3 FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    CONSTRAINT photo_fk2 FOREIGN KEY (photo_id) REFERENCES Pictures(picture_id) ON DELETE CASCADE
);

CREATE TABLE Tag(
	tag_id int4 auto_increment,
	tag_word VARCHAR(225),
    CONSTRAINT tag_pk PRIMARY KEY (tag_id)
);

CREATE TABLE assigned_tag(
	photo_id int4,
    tag_id int4,
    CONSTRAINT photo_tag_pk PRIMARY KEY (photo_id, tag_id),
    CONSTRAINT photo_fk3 FOREIGN KEY (photo_id) REFERENCES Pictures(picture_id),
	CONSTRAINT tag_fk FOREIGN KEY (tag_id) REFERENCES Tag(tag_id)

);

CREATE TABLE friends_with(
	user_id int4,
    friend_id int4,
    CHECK (user_id <> friend_id),
    CONSTRAINT friends_pk PRIMARY KEY (user_id, friend_id),
    CONSTRAINT user_fk4 FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    CONSTRAINT friend_fk FOREIGN KEY (friend_id) REFERENCES Users(user_id) ON DELETE CASCADE
); #getting error with this table: duplicate foreign key constraint

/*CREATE ASSERTION Comment-Constraint CHECK(
	NOT EXISTS ( SELECT * FROM Comments C, Pictures P
		WHERE C.photo_id = P.photo_id AND P.user_id = C.user_id));*/

INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
