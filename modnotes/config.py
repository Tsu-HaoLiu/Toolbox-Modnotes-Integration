import os
import configparser


praw_file = "praw.ini"

def save_praw(ci, cs, u, p, s):
    config = configparser.ConfigParser()
    config_var = {
            "client_id": ci,
            "client_secret": cs,
            "password":p,
            "username":u,
            "subreddit": s,
            "user_agent":f"/u/{u} Toolbox to Modnotes for r/{s}"
        }
    
    if os.path.exists(praw_file):
        config.read(praw_file)
        config_parser_dict = {s:dict(config.items(s)) for s in config.sections()}
        if config_var == config_parser_dict:
            return

    config['DEFAULT'] = config_var
    config.write(open(praw_file, 'w'))
    
    return


def burn_everything():
    if not os.path.exists(praw_file):
        return "File not found"    
    os.remove(praw_file)
    
