#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Created Date: Wednesday March 23 9:35:00 UTC 2022
"""modnotes.py: Easily convert Toolbox's usernotes to Reddit's modnotes"""
#----------------------------------------------------------------------------

__author__ = "Tsu-Hao Liu"

import sys
import re
import prawcore
import logging
from auth import *
from convert import *
from decode import *


subreddit = '' 
note_api = "/api/mod/notes"
logger = logging.getLogger('modnotes')


conv = Converter()
bDecode = Blob_decoder()


def OAuth(auth_details: list):
    global r
    r = auth(auth_details)
    return r
    
    
def ratelimit():
    return r.auth.limits['remaining']
    
    
def delete_notes(user, note_id):
    """Function to delete notes from a user
    
    :param subreddit: a fullname of a subreddit (should have a t5_ prefix)
    :param user: a fullname of an account (should have a t2_ prefix)
    :param note_id: a unique ID for the note to be deleted (should have a ModNote_ prefix)
    :return: dict
    """
    data = {"subreddit": subreddit, "user": user, "note_id": note_id}
    return r.request("DELETE", note_api, data)


def get_notes(user, limit: int = 25, label: str = None, before: str = None) -> dict:
    """ Function to retrieve specific user notes from a given subreddit

    :param subreddit: a fullname of a subreddit (should have a t5_ prefix)
    :param user: a fullname of an account (should have a t2_ prefix)
    :param limit: (optional) the number of mod notes to return in the response payload (default: 25, max: 100)
    :param label: (optional) NOTE, APPROVAL, REMOVAL, BAN, MUTE, INVITE, SPAM, CONTENT_CHANGE, MOD_ACTION, ALL,
    to be used for querying specific types of mod notes (default: all)
    :param before: (optional) an encoded string used for pagination with mod notes
    :return: Function will return a dict with all mod notes info regarding specific user
    """
    data = {"subreddit": subreddit, "user": user, "limit": limit, "label": label, "before": before}
    return r.request("GET", note_api, data)


def create_notes(user, note, action_item: str = None, label: str = None):
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
    data = {"subreddit": subreddit, "user": user, "note": note}
    try:
        result = r.request("POST", note_api, data)
        logger.info(f"Created note for u/{result['created']['user']} - {result['created']['id']} ")
    except Exception as e:
        logger.info(f"NoteCreationFailed: Note was not created for {user} - {e} skipping...")
        return 


def get_usernotes_wiki(sub) -> dict:
    """Retrive usernotes from subreddit wiki and checks the version compatibility"""
    try:
        wiki = subreddit.wiki["usernotes"].content_md
        wiki = json.loads(wiki)
    except prawcore.exceptions.NotFound:
        raise Exception(f"NameError: r/{subreddit.display_name} is missing the `usernotes` wiki page!")
    except prawcore.exceptions.Forbidden:
        raise Exception(f"Unauthorized: You don't have `wiki` access on r/{subreddit.display_name}!")
    except Exception as e:
        raise Exception("Did not reach Reddit https://redditstatus.com/")
    else:
        if wiki['ver'] != 6:
            raise Exception(f"VersionError: TB usernotes v{wiki['var']} is not supported. Supported v6") 
        return wiki
    
    
def note_name_generator(notes):
    for key, value in notes.items():
        yield key, value


def process_notes(sub_id: str, full_notes: dict, notes: dict):
    """Convert Toolbox's usernotes to Reddit's modnotes"""
    mods = full_notes['constants']['users']
    
    for note_info in note_name_generator(notes):
        for note_gather in note_info[1]['ns']:
            logger.info(f"Adding note for: {note_info[0]}")
            try:
                r.redditor(note_info[0]).id  # api call
                user_id = r.redditor(note_info[0]).name
            except Exception:
                logger.info(f"u/{note_info[0]} is banned/deleted skipping")
                continue
            note = note_gather['n']  # note
            mod = mods[note_gather['m']]  # mod
            
            if len(note)+len(mod)+3 <= 250:
                note = f"{note} - {mod}"
            
            create_notes(user_id, note)
            yield True


def subreddit_validation(user_input):
    """Checks if the subreddit entered is valid and that you moderate it"""
    if not re.match('^[\/:A-Za-z0-9_]+$', user_input):
        raise Exception(f"NameError: [{user_input}] does not look like a valid subreddit")
        
    try:
        global subreddit
        subreddit = re.sub("/?r/", "", user_input)
        subreddit = r.subreddit(subreddit)
        mod_list = subreddit.moderator()
    except prawcore.exceptions.Redirect:
        raise Exception(f"NameError: r/{subreddit} doesn't exist")
    except Exception as e:
        if not any(keyword in str(e) for keyword in ["500 HTTP", "502 HTTP", "503 HTTP", "504 HTTP", "RequestException"]):
            raise Exception(f"NameError: r/{subreddit} is banned/private or doesn't exist")
        raise Exception("ConnectionError: Having trouble connecting to Reddit. Try again later.")
    else:
        current_user = r.user.me().name.lower()
        if current_user not in mod_list:
            raise Exception(f"ImposterError: You are not a mod of r/{subreddit}")
        logger.info(f"Checking out r/{subreddit}...")
        return subreddit
    
    
def main(form_details):
    
    # Authenticate PRAW
    OAuth(form_details)
    
    # Validate subreddit
    subreddit_validation(form_details[4])  
    
    # Retrive usernote from wiki
    usernotes = get_usernotes_wiki()
    
    # Decode blob
    cleaned_notes = bDecode.blob_to_string(usernotes["blob"])
    
    # Save decoded notes
    conv.add(usernotes, cleaned_notes)
    
    process_notes(conv.combinednotes(), bDecode.conv_blob())
    
    
def arg_parser():
    """Parse commands from CLI """
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
    


if __name__ == '__main__':
    arg_parser()
