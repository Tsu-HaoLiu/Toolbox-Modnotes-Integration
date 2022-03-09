import praw
import base64
import zlib
import json

praw_config = {
    'user_agent': '/u/USERNAME Toolbox to Modnotes'
}

r = praw.Reddit('indexbot', **praw_config)  # praw auth w/ praw.ini

subreddit = ''  # subreddit name here without r/
note_api = "/api/mod/notes"


def get_blob_wiki(notes: str) -> str:
    return json.loads(notes)["blob"]


def js_byte_to_string(data: bytes) -> str:
    return data.decode("utf-8")


def b64d(data: str) -> bytes:
    return base64.b64decode(data)


def pInflate(data) -> bytes:
    decompress = zlib.decompressobj(15)
    decompressed_data = decompress.decompress(data)
    decompressed_data += decompress.flush()
    return decompressed_data
  
  
def get_usernotes_wiki(subreddit):
    wiki = r.subreddit(subreddit).wiki["usernotes"]
    return wiki.content_md


def delete_notes(subreddit, user, note_id):
    """Function to delete notes from a user
    :param subreddit: a fullname of a subreddit (should have a t5_ prefix)
    :param user: a fullname of an account (should have a t2_ prefix)
    :param note_id: a unique ID for the note to be deleted (should have a ModNote_ prefix)
    :return: Unknown
    """
    data = {"subreddit_id": subreddit, "user_id": user, "note_id": note_id}
    return r.request("DELETE", note_api, data)


def get_notes(subreddit, user, limit: int = 25, label: str = None, before: str = None) -> dict:
    """ Function to retrieve specific user notes from a given subreddit

    :param subreddit: a fullname of a subreddit (should have a t5_ prefix)
    :param user: a fullname of an account (should have a t2_ prefix)
    :param limit: (optional) the number of mod notes to return in the response payload (default: 25, max: 100)
    :param label: (optional) NOTE, APPROVAL, REMOVAL, BAN, MUTE, INVITE, SPAM, CONTENT_CHANGE, MOD_ACTION, ALL,
     to be used for querying specific types of mod notes (default: all)
    :param before: (optional) an encoded string used for pagination with mod notes
    :return: Function will return a dict with all mod notes info regarding specific user
    """
    data = {"subreddit_id": subreddit, "user_id": user, "limit": limit, "label": label, "before": before}
    return r.request("GET", note_api, data)


def create_notes(subreddit, user, note, action_item: str = None, label: str = None):
    """Create a mod note for a particular user

    :param subreddit: a fullname of a subreddit (should have a t5_ prefix)
    :param user: a fullname of an account (should have a t2_ prefix)
    :param note: Content of the note, should be a string with a maximum character limit of 250
    :param action_item: (optional) a fullname of a comment or post (should have either a t1 or t3 prefix)
    :param label: (optional) BOT_BAN, PERMA_BAN, BAN, ABUSE_WARNING, SPAM_WARNING, SPAM_WATCH, SOLID_CONTRIBUTOR, HELPFUL_USER
    :return: Unknown
    """
    data = {"subreddit_id": subreddit, "user_id": user, "note": note, "reddit_id": action_item, "label": label}
    return r.request("POST", note_api, data)


def blob_to_string(blob: str) -> dict:
    """
    Decode toolbox's base64encode + zlib compression 
    Base64 -> zlib-compressed -> string -> dict
    """
    # base64 decode blob
    zcomp = b64d(blob)
    
    # zlib-uncompress to byte
    uncomp_bytes = pInflate(zcomp)
    
    # byte to string
    cstring = js_byte_to_string(uncomp_bytes)
    
    # Return dict
    return json.loads(cstring)


def note_name_generator(notes):
    for key, value in notes.items():
        yield key, value
        
        
def process_notes(notes):
    sub_id = r.subreddit(subreddit).id

    for note_info in note_name_generator(notes):
        note_gather = note_info[1]['ns'][0]

        user_id = r.redditor(note_info[0]).id  # api call
        note = note_gather['n']
        action_item = note_gather['l']
        create_notes(sub_id, user_id, note, action_item)

        
def main(subreddit):
    usernotes = get_usernotes_wiki(subreddit)
    cleaned_notes = blob_to_string(get_blob_wiki(usernotes))
    process_notes(cleaned_notes)
    # todo since Reddit is funky, add try except for safety

  
if __name__ == '__main__':
    main(subreddit)
