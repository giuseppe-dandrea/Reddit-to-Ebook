import sqlite3


def get_connection():
    _con = sqlite3.connect("db.sqlite3")
    _cur = _con.cursor()
    _cur.execute("""
        CREATE TABLE IF NOT EXISTS ReadPosts (
            fullname varchar(10) PRIMARY KEY,
            title varchar(30),
            flair varchar(15),
            ebook_version INTEGER)
    """)
    _cur.execute("""
        CREATE TABLE IF NOT EXISTS Ebooks (
            version INTEGER PRIMARY KEY,
            last_fullname varchar(10),
            posts_loaded integer,
            posts_added integer)
    """)
    _cur.close()
    return _con


def get_last_fullname(db_cursor: sqlite3.Cursor):
    res = db_cursor.execute("""
        SELECT last_fullname 
        FROM Ebooks 
        WHERE version = (SELECT MAX(version) FROM Ebooks)
    """).fetchone()
    if res:
        return res[0]
    else:
        return None


def get_last_version(db_cursor: sqlite3.Cursor):
    res = db_cursor.execute("SELECT MAX(version) FROM Ebooks").fetchone()
    if res:
        return res[0]
    else:
        return None


# Remember to commit after calling this function
def insert_ebook(db_cursor: sqlite3.Cursor, version, last_fullname, posts_loaded, posts_added):
    db_cursor.execute("""
        INSERT INTO Ebooks(version, last_fullname, posts_loaded, posts_added) VALUES (?, ?, ?, ?)""",
                      [version, last_fullname, posts_loaded, posts_added])


# Remember to commit after calling this function
def insert_read_post(db_cursor: sqlite3.Cursor, fullname, title, flair, ebook_version):
    db_cursor.execute("""
        INSERT INTO ReadPosts(fullname, title, flair, ebook_version) VALUES (?, ?, ?, ?)""",
                      [fullname, title, flair, ebook_version])


def post_in_read_posts(db_cursor: sqlite3.Cursor, fullname):
    res = db_cursor.execute("SELECT fullname FROM ReadPosts WHERE fullname = ?", [fullname]).fetchone()
    if res:
        return True
    else:
        return False


def post_loaded_cumulative(db_cursor: sqlite3.Cursor):
    res = db_cursor.execute("SELECT SUM(posts_loaded) FROM Ebooks").fetchone()
    if res:
        return res[0]
    else:
        return 0
