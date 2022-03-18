import sys
import praw, prawcore
import base64
import zlib
import json
import re


subreddit = ''  # subreddit name here without r/
note_api = "/api/mod/notes"


def auth(auth_details: list = None):
    """Reddit authentication with global r variable"""
    global r
     
    try:
        r = praw.Reddit('indexbot')  # praw auth w/ praw.ini
        print(f"Successfully logged in as u/{r.user.me().name}")
    except Exception:
        if auth_details: 
            remember = auth_details.pop(-1)
            fa = auth_details.pop(-1)
            client_id, client_secret, username, password, subreddit = auth_details
            if fa is not None:
                password = f"{password}:{fa}"
            try:
                r = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    username=username,
                    password=password,
                    user_agent=f"/u/{username} Toolbox to Modnotes for r/{subreddit}"
                )
                print(f"Successfully logged in as u/{r.user.me().name}")
                if remember:
                    save_praw(client_id, client_secret, username, password, subreddit)
                else:
                    burn_everything()
                return
            except Exception:
                raise SystemExit(f"Reddit sign-in failed. Please fix info and try again!")
        raise SystemExit(f"Reddit sign-in failed. Correct OAuth info. Is Reddit down?")


def js_byte_to_string(data: bytes) -> str:
    return data.decode("utf-8")


def b64d(data: str) -> bytes:
    return base64.b64decode(data)


def pInflate(data) -> bytes:
    decompress = zlib.decompressobj(15)
    decompressed_data = decompress.decompress(data)
    decompressed_data += decompress.flush()
    return decompressed_data


def note_name_generator(notes):
    for key, value in notes.items():
        yield key, value

    
def delete_notes(sub_id, user, note_id):
    """Function to delete notes from a user
    
    :param subreddit: a fullname of a subreddit (should have a t5_ prefix)
    :param user: a fullname of an account (should have a t2_ prefix)
    :param note_id: a unique ID for the note to be deleted (should have a ModNote_ prefix)
    :return: dict
    """
    data = {"subreddit_id": sub_id, "user_id": user, "note_id": note_id}
    return r.request("DELETE", note_api, data)


def get_notes(sub_id, user, limit: int = 25, label: str = None, before: str = None) -> dict:
    """ Function to retrieve specific user notes from a given subreddit

    :param subreddit: a fullname of a subreddit (should have a t5_ prefix)
    :param user: a fullname of an account (should have a t2_ prefix)
    :param limit: (optional) the number of mod notes to return in the response payload (default: 25, max: 100)
    :param label: (optional) NOTE, APPROVAL, REMOVAL, BAN, MUTE, INVITE, SPAM, CONTENT_CHANGE, MOD_ACTION, ALL,
    to be used for querying specific types of mod notes (default: all)
    :param before: (optional) an encoded string used for pagination with mod notes
    :return: Function will return a dict with all mod notes info regarding specific user
    """
    data = {"subreddit_id": sub_id, "user_id": user, "limit": limit, "label": label, "before": before}
    return r.request("GET", note_api, data)


def create_notes(sub_id, user, note, action_item: str = None, label: str = None):
    """Create a mod note for a particular user

    :param subreddit: a fullname of a subreddit (should have a t5_ prefix)
    :param user: a fullname of an account (should have a t2_ prefix)
    :param note: Content of the note, should be a string with a maximum character limit of 250
    :param action_item: (optional) a fullname of a comment or post (should have either a t1 or t3 prefix)
    :param label: (optional) BOT_BAN, PERMA_BAN, BAN, ABUSE_WARNING, SPAM_WARNING, SPAM_WATCH, SOLID_CONTRIBUTOR, HELPFUL_USER
    :return: None
    # NOTE `reddit_id` and `label` are not valid parameters for /api/mod/notes
    # "reddit_id": action_item, "label": label
    """
    data = {"subreddit_id": sub_id, "user_id": user, "note": note}
    try:
        result = r.request("POST", note_api, data)
        print(f"Created note for u/{result['created']['user']} - {result['created']['id']} ")
    except Exception as e:
        print(f"NoteCreationFailed: Note was not created for {user} - {e} skipping...")
        return 


def decode_blob(blob: str) -> dict:
    """Decode toolbox's base64encode + zlib compression"""
    # base64 decode blob
    decode_notes = b64d(blob)
    
    # zlib-uncompress to byte
    inflated_bytes = pInflate(decode_notes)
    
    # byte to string
    cstring = js_byte_to_string(inflated_bytes)
    
    # Return dict
    return json.loads(cstring)


def get_usernotes_wiki(sub) -> dict:
    """Retrive usernotes from subreddit wiki and checks the version compatibility"""
    try:
        wiki = sub.wiki["usernotes"].content_md
        wiki = json.loads(wiki)
    except prawcore.exceptions.NotFound:
        raise SystemExit(f"NameError: r/{sub.display_name} is missing the `usernotes` wiki page!")
    except json.decoder.JSONDecodeError:
        raise SystemExit(f"CorruptWiki: Looks like your usernotes is corrupted, please make an issue on Github")
    
    if wiki['ver'] != 6:
        raise SystemExit(f"VersionError: TB usernotes v{wiki['var']} is not supported. Supported v6") 
    
    return wiki
    
    
def process_notes(sub_id: str, full_notes: dict, notes: dict):
    """Convert Toolbox's usernotes to Reddit's modnotes"""
    mods = full_notes['constants']['users']
    
    # todo add a way to mitigate reddit outages
    for user, note_info in note_name_generator(notes):
        for note_gather in note_info['ns']:
            
            try:
                user_id = r.redditor(user).fullname
            except Exception:
                print(f"u/{user} is banned/deleted skipping...")
                continue
            
            note = note_gather['n']
            mod = mods[note_gather['m']]
            # reddit_id not working
            # labels not working, future use
            
            if len(note)+len(mod)+2 <= 250:
                note = f"{note} -{mod}"
            
            create_notes(sub_id, user_id, note)

            
def safe_checks(user_input):
    """Checks if the subreddit entered is valid and that you moderate it"""
    if not re.match('^[\/:A-Za-z0-9_]+$', user_input):
        raise SystemExit(f"NameError: [{user_input}] does not look like a valid subreddit")
    subreddit = re.sub("/?r/", "", user_input)
    
    try:
        sub = r.subreddit(subreddit)
        mod_list = sub.moderator()
    except Exception as e:
        if not any(keyword in str(e) for keyword in ["500 HTTP", "502 HTTP", "503 HTTP", "504 HTTP", "RequestException"]):
            raise SystemExit(f"NameError: r/{subreddit} is banned/private or doesn't exist")
        raise SystemExit(f"ConnectionError: Having trouble connecting to Reddit. Try again later.")
    
    if r.user.me().name not in mod_list:
        raise SystemExit(f"PermissionError: You are not a mod of r/{sub.display_name}")


def main(OAuth_data):
    ci, cs, u, p, s, fa, save = OAuth_data

    auth(OAuth_data)
    sub = safe_checks(s)
    
    usernotes = get_usernotes_wiki(sub)
    cleaned_notes = decode_blob(usernotes["blob"])
    process_notes(sub.fullname, usernotes, cleaned_notes)
    

def arg_parser():
    import argparse # only needed if called from CLI
    app_dev = "\nPlease check out the README.md for more info"

    parse = argparse.ArgumentParser()
    parse.add_argument(
        '-ci',
        '--client_id',
        type=str,
        help=f'Your client_id is found in your /prefs/app page.{app_dev}'
    )
    parse.add_argument(
        '-cs',
        '--client_secret',
        type=str,
        help=f'Your client_secret is found in your /prefs/app page.{app_dev}'
    )
    parse.add_argument(
        '-u',
        '--username',
        type=str,
        help='The Reddit username of the mod account in which you would like to convert toolbox notes to modnotes.'
    )
    parse.add_argument(
        '-p',
        '--password',
        type=str,
        help='The password of your Reddit account.'
    )
    parse.add_argument(
        '-s',
        '--subreddit',
        type=str,
        required=True,
        help='The subreddit you want to convert toolbox notes to modnotes.'
    )
    parse.add_argument(
        '-fa',
        type=int,
        default=None,
        help='If your account has 2fa enabled you will have to enter the 2FA code.'
    )
    parse.add_argument(
        '-save',
        '--save_info',
        type=bool,
        default=False,
        help='If you would like to save your info to a praw.ini file. (Default: %(default)s)'
    )

    args = parse.parse_args()
    OAuth_details = [*vars(args).values()]
    
    filled_info = [l for x, l in enumerate(OAuth_details) if x < 5]
    filled_info = all(x is not None for x in filled_info)

    prawfile_detected = os.path.exists(praw_file)
    if args.subreddit and prawfile_detected:
        """use praw.ini and use sub provided"""
        main(OAuth_details)

    if not prawfile_detected and not filled_info:
        """No praw and no info entered pass help info"""
        print(f'Missing arguments, exiting.')
        parse.print_help()
        sys.exit(1)

    if filled_info:
        # checks ci,cs,u,p,s
        main(OAuth_details)
        
        

if __name__ == '__main__':
    arg_parser()
