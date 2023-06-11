import sqlite3

con = sqlite3.connect('database.db', check_same_thread=False)

con.execute("CREATE TABLE users(id BIGINT, username TEXT, status TEXT, PRIMARY KEY(id))")