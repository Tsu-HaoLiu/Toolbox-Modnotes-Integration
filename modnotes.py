import sys
import praw, prawcore
import base64
import zlib
import json
import re

praw_config = {
    'user_agent': '/u/USERNAME Toolbox to Modnotes for r/SUBREDDIT'
}

try:
    r = praw.Reddit('indexbot', **praw_config)  # praw auth w/ praw.ini
    print(f"Successfully logged in as u/{r.user.me().name}")
except Exception:
    raise SystemExit(f"Reddit signin failed. Correct OAuth info. Is Reddit down?")

subreddit = ''  # subreddit name here without r/
note_api = "/api/mod/notes"


def js_byte_to_string(data: bytes) -> str:
    return data.decode("utf-8")


def b64d(data: str) -> bytes:
    return base64.b64decode(data)


def pInflate(data) -> bytes:
    decompress = zlib.decompressobj(15)
    decompressed_data = decompress.decompress(data)
    decompressed_data += decompress.flush()
    return decompressed_data

    
def delete_notes(sub_id, user, note_id):
    """Function to delete notes from a user
    
    :param subreddit: a fullname of a subreddit (should have a t5_ prefix)
    :param user: a fullname of an account (should have a t2_ prefix)
    :param note_id: a unique ID for the note to be deleted (should have a ModNote_ prefix)
    :return: Unknown
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
    :return: Unknown
    # NOTE `reddit_id` and `label` are not valid parameters for /api/mod/notes
    # "reddit_id": action_item, "label": label
    """
    data = {"subreddit_id": sub_id, "user_id": user, "note": note}
    return r.request("POST", note_api, data)


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


def note_name_generator(notes):
    for key, value in notes.items():
        yield key, value
    
    
def process_notes(sub_id, full_notes, notes):
    mods = full_notes['constants']['users']
    
    for note_info in note_name_generator(notes):
        for note_gather in note_info[1]['ns']:
            
            try:
                user_id = r.redditor(note_info[0]).fullname
            except Exception:
                print(f"u/{note_info[0]} is banned/deleted")
                continue
            
            note = note_gather['n']
            mod = mods[note_gather['m']]
            # reddit_id not working
            # labels not working, future use
            
            if len(note)+len(mod)+2 <= 250:
                note = f"{note} -{mod}"
            
            create_notes(sub_id, user_id, note)


def main(sub):
    usernotes = get_usernotes_wiki(sub)
    cleaned_notes = decode_blob(usernotes["blob"])
    process_notes(sub.fullname, usernotes, cleaned_notes)
    

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

    main(sub)
    

if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit(f"TypeError: {sys.argv[0]} takes one argument ({len(sys.argv)-1} given)")

    safe_checks(sys.argv[1].strip())
