import re
import praw
import os.path
from ebooklib import epub

import print_progress_bar
import db_helper as db
from credentials import CLIENT_ID, CLIENT_SECRET, USER_AGENT

# ----------------------------------- USER OPTIONS -----------------------------------#

# Reddit options
SUBREDDIT_NAME = "talesfromtechsupport"
N_POSTS = 50
TIME_FILTER = "all"
FLAIR_FILTERS = ["Long", "Epic"]
N_TOP_LEVEL_COMMENTS = 3
DEPTH_COMMENTS = 5

# Ebook options
IDENTIFIER = "tfts"
TITLE = "Tales From Tech Support Vol. "
AUTHOR = "Reddit Community"
LANGUAGE = "en"

OUTPUT_FOLDER = "out"

# ------------------------------------------------------------------------------------#


# Use script credentials from https://www.reddit.com/prefs/apps
#
# user_agent should be: <platform>:<app ID>:<version string> (by /u/<reddit username>)
#     example: User-Agent: android:com.example.myredditapp:v1.2.3 (by /u/kemitche)
def get_reddit_instance():
    instance = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )
    return instance


def get_top_posts(subreddit: praw.reddit.Subreddit, n_posts, book, db_cursor, version, time_filter="all",
                  flair_filters=None, css=None, top_comments=3):
    # flair filters must be a list
    if flair_filters and not isinstance(flair_filters, list):
        raise TypeError("flair_filters must be None or a list of strings")

    _chapters = []
    _toc = []
    posts_loaded = 0
    posts_loaded_cumulative = db.post_loaded_cumulative(db_cursor) or 0
    posts_added_to_ebook = 0
    last_fullname = None
    after = db.get_last_fullname(db_cursor)

    reddit_link_pattern = re.compile("https://www.reddit")
    if not after:
        submissions_listing = subreddit.top(limit=None, time_filter=time_filter)
    else:
        submissions_listing = subreddit.top(limit=None, time_filter=time_filter,
                                            params={"after": after, "count": posts_loaded_cumulative})

    for i, submission in enumerate(submissions_listing):
        last_fullname = submission.fullname
        posts_loaded += 1
        if not flair_filters or submission.link_flair_text and any(substr in submission.link_flair_text for substr in flair_filters):
            if not db.post_in_read_posts(db_cursor, submission.fullname):
                chapter = epub.EpubHtml(title=submission.title, file_name=f"{submission.fullname}.xhtml", lang="hr")
                if css:
                    chapter.add_item(css)
                html_title = f"<h1>{submission.title}</h1>"
                html_author = f"<h3>{submission.author}</h3>"
                html_flair = f"<h3 style=\"font-style: italic;\">{submission.link_flair_text}</h3>"
                html_url = f"<a href=\"{submission.url}\">Link to post</a><br>"
                html_old_url = f"<a href=\"{reddit_link_pattern.sub('https://old.reddit', submission.url)}\">Link to post (old.reddit)</a>"
                chapter.content = html_author + html_title + html_flair + submission.selftext_html + html_url + html_old_url
                comments_tree = get_comments_tree(submission.comments, top=top_comments)
                add_comments_to_chapter(chapter, comments_tree)
                book.add_item(chapter)
                _chapters.append(chapter)
                _toc.append(epub.Link(f"{submission.fullname}.xhtml",
                                      f"{submission.title} - {submission.author} - {submission.link_flair_text}",
                                      submission.title))
                posts_added_to_ebook += 1
                print_progress_bar.printProgressBar(posts_added_to_ebook, N_POSTS)
                db.insert_read_post(db_cursor, submission.fullname, submission.title, submission.link_flair_text,
                                    version)
                if n_posts and posts_added_to_ebook >= n_posts:
                    db.insert_ebook(db_cursor, version, last_fullname, posts_loaded, posts_added_to_ebook)
                    print(
                        f"STATS: posts_loaded={posts_loaded} posts_loaded_cumulative={posts_loaded_cumulative + posts_loaded} last_fullname={last_fullname} posts_added_to_ebook={posts_added_to_ebook}")
                    return _chapters, _toc

    db.insert_ebook(db_cursor, version, last_fullname, posts_loaded, posts_added_to_ebook)
    print(
        f"STATS: posts_loaded={posts_loaded} posts_loaded_cumulative={posts_loaded_cumulative + posts_loaded} last_fullname={last_fullname} posts_added_to_ebook={posts_added_to_ebook}")
    return _chapters, _toc


def get_comments_tree(comments, top=1, depth=5, html_comments=None, state=0):
    if not html_comments:
        html_comments = []
        for i in range(top):
            html_comments.append([])
    if depth == 0 or top == 0:
        return html_comments
    for i, top_level_comment in enumerate(comments):
        if i >= top:
            break
        try:
            comment = {
                "html": top_level_comment.body_html,
                "author": top_level_comment.author.name,
                "upvotes": top_level_comment.ups
            }
            html_comments[state].append(comment)
        # print(top_level_comment.body_html)
        except AttributeError:
            continue
        html_comments = get_comments_tree(top_level_comment.replies, top=1, depth=depth - 1,
                                          html_comments=html_comments, state=state)
        state = i + 1
    return html_comments


def add_comments_to_chapter(chapter, comments):
    for el in comments:
        # print(el)
        chapter.content += "<ul class=\"commentTree\">"
        for i, comm in enumerate(el):
            chapter.content += f"<ul class=\"commentNode\">"
            chapter.content += f"<p class=\"author\">{comm['upvotes']}⇧ - u/{comm['author']}</p>"
            chapter.content += comm["html"]
        chapter.content += "</ul>" * len(el)


if __name__ == '__main__':
    print("Connecting to reddit...")
    reddit = get_reddit_instance()
    print("Connection complete...\nGetting posts and creating epub...")
    subreddit = reddit.subreddit(SUBREDDIT_NAME)

    db_connection = db.get_connection()
    db_cursor = db_connection.cursor()
    last_version = db.get_last_version(db_cursor)
    version = (last_version or 0) + 1

    book = epub.EpubBook()
    book.set_identifier(f"{IDENTIFIER}{version}")
    book.set_title(f"{TITLE}{version}")
    book.set_language(LANGUAGE)

    book.add_author(AUTHOR)

    with open("style.css") as f:
        css = f.read()
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=css)
    book.add_item(nav_css)

    print_progress_bar.printProgressBar(0, N_POSTS)

    chapters, toc = get_top_posts(subreddit, book=book, css=nav_css, flair_filters=FLAIR_FILTERS, n_posts=N_POSTS,
                                  db_cursor=db_cursor, version=version)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    book.toc = toc
    book.spine = ['nav', *chapters]

    filename = f"{IDENTIFIER}{version}.epub"
    if OUTPUT_FOLDER:
        if not os.path.exists(OUTPUT_FOLDER):
            os.makedirs(OUTPUT_FOLDER)
        epub.write_epub(f"{OUTPUT_FOLDER}/{filename}", book)
    else:
        epub.write_epub(filename, book)

    print(f"Done.\nFilename: {filename}")
    db_connection.commit()
    db_connection.close()
