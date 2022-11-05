# Reddit To Ebook
This script allows you to generate an ebook from the top posts of a subreddit.

## Credentials
The script requires reddit application credentials: `CLIENT_ID`, `CLIENT_SECRET` and `USER_AGENT` in `credentials.py`.

Id and secret can be generated from https://www.reddit.com/prefs/apps creating a new script app.

User agent should be: `<platform>:<app ID>:<version string> (by /u/<reddit username>)` as specified in reddit doc.

## Usage
- Clone this repository and install requirements specified in `requirements.txt`
- Create `credentials.py` with your reddit credentials
- Change the user options in `redditToEbook.py`
- Run `python redditToEbook.py`
- Enjoy reddit on your ebook reader!

## User options
Ebook `identifier` is used to name the epub file and also to identify the ebook in the database. Use the same identifier when creating multiple versions from the same subreddit, otherwise posts could be duplicated.

## Manually add links to ebook
If you want to manually add some posts in the ebook you can add the id/url of the post in `links_to_add.txt`.

The posts in this file will be processed before the top ones and added at the start of the ebook.
