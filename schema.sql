drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  ts_date text not null,
  weight integer not null
  );
