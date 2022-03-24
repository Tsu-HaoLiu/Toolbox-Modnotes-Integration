import praw
import logging
from config import *

"""Authenticate user with PRAW"""

logger = logging.getLogger('modnotes')


def auth_manual(auth_details: list):
    """Manual login if praw.ini file not available"""
    remember = auth_details.pop(-1)
    fa = auth_details.pop(-1)
    client_id, client_secret, username, password, subreddit = auth_details
    
    # Merge password and 2fa together
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
        logger.info(f"Successfully logged in as u/{r.user.me().name}")

        # Save login details to praw.ini if remember checked
        if remember:
            save_praw(client_id, client_secret, username, password, subreddit)

    except Exception:
        raise Exception(f"Reddit sign-in failed. Please fix info and try again!")

    return r


def auth(auth_details: list = None):
    """Reddit authentication with praw.ini or alternative"""

    if os.path.exists(praw_file):
        try:
            r = praw.Reddit('DEFAULT')
            logger.info(f"[praw.ini] Successfully logged in as u/{r.user.me().name}")
            
            """If `remember me` is false delete ini file"""
            if not auth_details[-1]:
                burn_everything()
            
            return r
        except Exception: # if praw.ini doesn't exist
            if not auth_details: 
                raise Exception(f"Reddit sign-in failed. Correct info then try again!")
                
    if auth_details:
        return auth_manual(auth_details)
    
    raise Exception(f"ValueError: Missing praw.ini and no sign-in details entered.")
    
