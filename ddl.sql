use wcscdb_db;
-- drop table if exists professional;
-- drop table if exists item;
drop table if exists post;
drop table if exists `profile`;
drop table if exists user;

CREATE TABLE user (
	userID varchar(30) not null,
	hashed varchar(60) not null,
	`name` varchar(30) not null,
	classYear year not null,
	email varchar(50),
	PRIMARY KEY (userID)
)
ENGINE = InnoDB;

-- default value for visibility is automatically set to 'N'
CREATE TABLE `profile` (
	userID varchar(30) not null,
	visibility enum('N','Y') not null,
	interests varchar(100),
	introduction varchar(200),
	career varchar(300),
	PRIMARY KEY (userID),
	FOREIGN KEY (userID) REFERENCES user(userID)
		on update restrict
		on delete restrict
)
ENGINE = InnoDB;

CREATE TABLE post (
	postID int(12) zerofill auto_increment not null,
	authorID varchar(30) not null,
	`datetime` datetime not null,
	title varchar(30) not null,
	content varchar(1000) not null,
	primary key (postID),
	foreign key (authorID) references user(userID)
		on update restrict
		on delete restrict
)
ENGINE = InnoDB;

-- CREATE TABLE item (
-- 	itemID char(12) not null,
-- 	authorID varchar(30) not null,
-- 	`datetime` datetime not null,
--     primary key (itemID),
--     foreign key (itemID) references user(userID)
--         on update restrict
--         on delete restrict	
-- )
-- ENGINE = InnoDB;

-- CREATE TABLE professional (
-- 	itemID char(12) not null,
-- 	`name` varchar(30) not null,
-- 	company varchar(30) not null,
-- 	`type` enum('Referrer','Recruiter') not null,
-- 	email varchar(50) not null,
-- 	notes varchar(100),
-- 	primary key (itemID),
-- 	foreign key (itemID) references item(itemID)
-- 		on update restrict
-- 		on delete restrict
-- )
-- ENGINE = InnoDB;