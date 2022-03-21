import os
import configparser


praw_file = "praw.ini"
config = configparser.ConfigParser()

def save_praw(ci, cs, u, p, s):
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

    config['indexbot'] = config_var
    config.write(open(praw_file, 'w'))
    
    return


def retrive_ini():
    if os.path.exists(praw_file):
        config.read(praw_file)
        ini_dict = {s:dict(config.items(s)) for s in config.sections()}
        if ":" in ini_dict.get('password', ""):
            ini_dict['password'] = ini_dict['password'].split(":")[0]
        ini_dict.pop('user_agent', None)
        ini_list = [*ini_dict.values()]
        return ini_list
    return [""] * 5


def burn_everything():
    if not os.path.exists(praw_file):
        return "File not found"    
    os.remove(praw_file)
    
