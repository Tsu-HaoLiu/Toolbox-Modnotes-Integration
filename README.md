# Toolbox-Modnotes-Integration
Convert Toolbox Usernotes to Modnotes. Recent announcement of [Modnotes](https://www.reddit.com/r/modnews/comments/t8vafc/announcing_mod_notes/).

## [PRAW Authenticating via OAuth](https://praw.readthedocs.io/en/stable/getting_started/authentication.html)
  
**Password Flow** is the simplest type of authentication flow to work with because no
callback process is involved in obtaining an ``access_token``.

While **password flow** applications do not involve a redirect URI, Reddit still
requires that you provide one when registering your script application --
``http://localhost:8080`` is a simple one to use.

In order to use a **password flow** application with PRAW you need four pieces of
information:
||Description|    
| ------------- | ------------- |
| client_id  | The client ID is the 14-character string listed just under “personal use script” for the desired [developed application](https://www.reddit.com/prefs/apps/)  |
| client_secret  | The client secret is at least a 27-character string listed adjacent to `secret` for the application.  |
| password  | The password for the Reddit account used to register the application.  |
| username  | The username of the Reddit account used to register the application.  |

```
reddit = praw.Reddit(
    client_id="SI8pN3DSbt0zor",
    client_secret="xaxkj7HNh8kwg8e5t4m6KvSrbTI",
    password="hunter2",
    user_agent="u/USERNAME toolbox to modnotes",
    username="fakebot3",
)
```
### praw.ini alternative 
```
[indexbot]
client_id=SI8pN3DSbt0zor
client_secret=xaxkj7HNh8kwg8e5t4m6KvSrbTI
password=hunter2
username=fakebot3
```
```
praw_config = {
    'user_agent': '/u/USERNAME Toolbox to Modnotes for r/SUBREDDIT'
}
r = praw.Reddit('indexbot', **praw_config)

```

## Usage

```
pip3 install -r requirements.txt
python3 modnotes.py "SUBREDDITNAME"
```
