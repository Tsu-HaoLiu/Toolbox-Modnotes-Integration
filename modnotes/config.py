import os
import re
import configparser

"""Save, retrive and delete praw.ini data"""

praw_file = "praw.ini"
ini_keys = ["client_id", "client_secret", "username", "password", "subreddit"]
config = configparser.ConfigParser(interpolation=None)


def save_praw(ci, cs, u, p, s):
    """Saved login information in a standard praw.ini file"""
    config_var = {
            "client_id": ci,
            "client_secret": cs,
            "username":u,
            "password":p,
            "subreddit": s,
            "user_agent":f"/u/{u} Toolbox to Modnotes for r/{s}"
        }
    
    # Check if praw.ini already exists and 
    # if true replace old value with new values
    if os.path.exists(praw_file):
        config.read(praw_file)
        config_parser_dict = {x:config.get('DEFAULT', x) for x in ini_keys}
        if config_var == config_parser_dict:
            return

    # Add new data to ini file
    config['DEFAULT'] = config_var
    config.write(open(praw_file, 'w'))
    return


def retrive_ini():
    """Retrives and gathers necessary info from ini and returns a list"""
    if os.path.exists(praw_file):
        details = []
        config.read(praw_file)
        
        for x in ini_keys:
            try:
                data = config.get('DEFAULT', x)
            except configparser.NoOptionError:
                pass # ignore missing items as this will only go to UI 
            
            # If password has colon (:) followed and ending by 6 number digits 
            # remove 2fa code. Accounts with 2fa submit passwords like "password:123456"
            if re.search('\:\d{6}$', data) and x == "password":
                data = data.split(":")[0]
            details.append(data)
        return details
    return None


def burn_everything():
    """Delete praw.ini"""
    if not os.path.exists(praw_file):
        return "File not found"    
    os.remove(praw_file)
    