
/*this script is used for create a new database*/

drop database if exists testdb;

create database testdb;

use testdb;

grant select, insert,update,delete on testdb.* to 'wei'@'localhost' identified by 'mysql';

create table users (
	`id` varchar(50) not null,
	`email` varchar(50) not null,
	`name` varchar(50),
	`nickname` varchar(50),
	`sex` bool not null,
	`passwd` varchar(50) not null,
  `admin` bool not null,
  `image` varchar(500) not null,
  `created_at` real not null,
  unique key `idx_email` (`email`),
  key `idx_created_at` (`created_at`),
  primary key (`id`)
)engine=innodb default charset=utf8;

create table blogs (
	`id` varchar(50) not null,
  `user_id` varchar(50) not null,
  `title` varchar(50) not null,
  `summary` varchar(200) not null,
  `content` mediumtext not null,
  `created_at` real not null,
  key `idx_created_at` (`created_at`),
  primary key (`id`)
)engine=innodb default charset=utf8;

create table comments (
  `id` varchar(50) not null,
  `blog_id` varchar(50) not null,
  `user_id` varchar(50) not null,
  `content` mediumtext not null,
  `created_at` real not null,
  key `idx_created_at` (`created_at`),
  primary key (`id`)
) engine=innodb default charset=utf8;

create table collect (
  `id` varchar(50) not null,
  `col_title` varchar(50) not null,
  `user_id` varchar(50) not null,
  `link`  varchar(2048) not null,
  `content` mediumtext not null,
  `created_at` real not null,
  key `idx_created_at` (`created_at`),
  primary key (`id`)
) engine=innodb default charset=utf8;
