# Reddit To Ebook
This script allows you to generate an ebook from the top posts of a subreddit.

## Usage
Change the user options in `redditToEbook.py`.

Ebook `identifier` is used to name the epub file and also to identify the ebook in the database. Use the same identifier when creating multiple versions from the same subreddit, otherwise posts could be duplicated.

## Credentials
The script requires `CLIENT_ID`, `CLIENT_SECRET` and `USER_AGENT` in `credentials.py`. Id and secret can be generated from https://www.reddit.com/prefs/apps. User agent should be: `<platform>:<app ID>:<version string> (by /u/<reddit username>)` as specified in reddit doc.
