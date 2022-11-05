import sqlite3


def get_connection():
    _con = sqlite3.connect("../db.sqlite3")
    _cur = _con.cursor()
    _cur.execute("""
        CREATE TABLE IF NOT EXISTS Ebooks (
            identifier varchar(10),
            version INTEGER,
            last_fullname varchar(10),
            posts_loaded integer,
            posts_added integer,
            PRIMARY KEY(identifier, version))
    """)
    _cur.execute("""
        CREATE TABLE IF NOT EXISTS ReadPosts (
            fullname varchar(10) PRIMARY KEY,
            title varchar(30),
            flair varchar(15),
            ebook_identifier VARCHAR(10),
            ebook_version INTEGER)
    """)
    _cur.close()
    return _con


def get_last_fullname(db_cursor: sqlite3.Cursor, identifier):
    res = db_cursor.execute("""
        SELECT last_fullname 
        FROM Ebooks 
        WHERE identifier = ? AND version = (SELECT MAX(version) FROM Ebooks WHERE identifier = ?)
    """, [identifier, identifier]).fetchone()
    if res:
        return res[0]
    else:
        return None


def get_last_version(db_cursor: sqlite3.Cursor, identifier):
    res = db_cursor.execute("SELECT MAX(version) FROM Ebooks WHERE identifier = ?", [identifier]).fetchone()
    if res:
        return res[0]
    else:
        return None


# Remember to commit after calling this function
def insert_ebook(db_cursor: sqlite3.Cursor, identifier, version, last_fullname, posts_loaded, posts_added):
    db_cursor.execute("""
        INSERT INTO Ebooks(identifier, version, last_fullname, posts_loaded, posts_added) VALUES (?, ?, ?, ?, ?)""",
                      [identifier, version, last_fullname, posts_loaded, posts_added])


# Remember to commit after calling this function
def insert_read_post(db_cursor: sqlite3.Cursor, fullname, title, flair, ebook_identifier, ebook_version):
    db_cursor.execute("""
        INSERT INTO ReadPosts(fullname, title, flair, ebook_identifier, ebook_version) VALUES (?, ?, ?, ?, ?)""",
                      [fullname, title, flair, ebook_identifier, ebook_version])


def post_in_read_posts(db_cursor: sqlite3.Cursor, ebook_identifier, fullname):
    res = db_cursor.execute("SELECT fullname FROM ReadPosts WHERE fullname = ? AND ebook_identifier = ?", [fullname, ebook_identifier]).fetchone()
    if res:
        return True
    else:
        return False


def post_loaded_cumulative(db_cursor: sqlite3.Cursor, identifier):
    res = db_cursor.execute("SELECT SUM(posts_loaded) FROM Ebooks WHERE identifier = ?", [identifier]).fetchone()
    if res:
        return res[0]
    else:
        return 0
