
create table users
(username varchar, user_Id varchar primary key, points integer, ts timestamp without time zone default (now() at time zone 'utc'), team varchar);

create table items
(id serial primary key, name varchar);

create table inventory (id serial primary key, user_id varchar references users(user_id) , item_id integer references items(id),  ts timestamp without time zone default (now() at time zone 'utc’));

insert into items (name) values ('Bamboo');
insert into items (name) values ('Bonsai');
insert into items (name) values ('Sakura');
insert into items (name) values ('Shiso');
insert into items (name) values ('Wasabi');
insert into items (name) values ('Yuzu');
insert into items (name) values ('Pyrite');
insert into items (name) values ('Pearl');
insert into items (name) values ('Amethyst');
insert into items (name) values ('Calcite');
insert into items (name) values ('Jade');
insert into items (name) values ('Clear Quartz');
insert into items (name) values ('First Quarter');
insert into items (name) values ('Full Moon');
insert into items (name) values ('Lunar Eclipse');
insert into items (name) values ('New Moon');
insert into items (name) values ('Super Full Moon');
insert into items (name) values ('Third Quarter');
insert into items (name) values ('Total Eclipse');
insert into items (name) values ('Waning Crescent');
insert into items (name) values ('Waning Gibbous');
insert into items (name) values ('Waxing Crescent');
insert into items (name) values ('Waxing Gibbous');