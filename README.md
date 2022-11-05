# Reddit To Ebook
This script allows you to generate an ebook from the top posts of a subreddit.

Change the user options in `main.py` before starting.

Ebook `identifier` is used to name the epub file and also to identify the ebook in the database. Use the same identifier when creating multiple versions from the same subreddit, otherwise posts could be duplicated.

## Credentials
The script requires `CLIENT_ID`, `CLIENT_SECRET` and `USER_AGENT`. Id and secret can be generated from https://www.reddit.com/prefs/apps. User agent should be: `<platform>:<app ID>:<version string> (by /u/<reddit username>)` as specified in reddit doc.

## TODOs
- Add `identifier` field in Ebooks table to allow keeping track of more than one subreddit ebook
  - Check each function in `db_helper.py` if requires also the `identifier` parameter
  - Add `identifier` also to ReadPosts as foreign key. (Modify also ebook_version to be a foreign key)
