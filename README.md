<h1 align="center">Toolbox to Modnotes Integration</h1>

<p align="center">Convert Toolbox's Usernotes to Reddit's Modnotes. Recent announcement of <a href="https://www.reddit.com/r/modnews/comments/t8vafc/announcing_mod_notes/">Modnotes.</a></p>

<p align="center">
  <img src="https://img.shields.io/github/v/release/Tsu-HaoLiu/Toolbox-Modnotes-Integration" />
  <img src="https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue" />
  <img src="https://img.shields.io/badge/platform-windows-lightgrey" />

</p>

## Screenshots


<p align="center">
  <img src="https://user-images.githubusercontent.com/96331813/160275505-ed23fe3a-bc39-479f-b73c-1bccbbd48ab0.png" width="250" />
  <img src="https://user-images.githubusercontent.com/96331813/160275589-febc18c1-13f3-4653-b837-ccd6b58eec20.png" width="250" /> 
  <img src="https://user-images.githubusercontent.com/96331813/160275510-1778ac4c-8044-4d25-a18a-80f7243aa4ed.png" width="250" height="360"/>
</p>

<p align="center">
<img src="https://user-images.githubusercontent.com/96331813/160275513-151548a3-9243-4c5a-9dff-08fe33d74e9a.png" width="500" /> 
</p>

## Features

- Simple UI
- Quick Login
- Easy CSV & JSON export
- Remember me (praw.ini)
- Live console
- Ratelimit tracker
- Notes tracker
- Error logging (Local)


## Getting Started

_Note: To have the interface displayed in the images, you will need chrome. If chrome is not installed the default browser will be used._

### Installation

You can install Modnotes using one of the following methods:
1. To clone a project, use the command: `git clone https://github.com/Tsu-HaoLiu/Toolbox-Modnotes-Integration.git`
2. Download the .exe from [GitHub Releases](https://github.com/Tsu-HaoLiu/Toolbox-Modnotes-Integration/releases/tag/v2022.0.12) and install it.


#### [PRAW Authenticating via OAuth](https://praw.readthedocs.io/en/stable/getting_started/authentication.html) - [praw.ini](https://praw.readthedocs.io/en/stable/getting_started/configuration/prawini.html#praw-ini)
```
[DEFAULT]
client_id=SI8pN3DSbt0zor
client_secret=xaxkj7HNh8kwg8e5t4m6KvSrbTI
username=fakebot3
password=hunter2
subreddit=birdswitharms
user_agent=/u/USERNAME Toolbox to Modnotes for r/SUBREDDIT
```


## CLI Usage
```python
$ python3 modnotes.py --help
usage: modnotes.py [-h] [-ci CLIENT_ID] [-cs CLIENT_SECRET] [-u USERNAME]
                   [-p PASSWORD] -s SUBREDDIT [-fa FA] [-save SAVE_INFO]
```

| Argument                                                     | Type                | Description                                                                                                                |
| ------------------------------------------------------------ | ------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| -ci, --client_id                    | optional | Your client_id is found in your /prefs/app page.                                               |
| -cs, --client_secret             | optional            | Your client_secret is found in your /prefs/app page.                                  |
| -u, --username             | optional            | The Reddit username of the mod account in which you would like to convert toolbox notes to modnotes.|
| -p, --password | optional            | Provide a configuration file (json) to pre-fill the UI. These can be generated in the settings tab.                        |
| -s, --subreddit              | required            | The subreddit you want to convert toolbox notes to modnotes.                      |
| -fa  | optional            | If your account has 2fa enabled you will have to enter the 2FA code. |
| -save, --save_info  | optional            | If you would like to save your info to a praw.ini file. (Default: False) |

