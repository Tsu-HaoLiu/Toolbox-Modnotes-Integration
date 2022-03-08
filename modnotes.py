from urllib.parse import quote, unquote
import praw
import base64
import zlib
import json


praw_config = {
    'user_agent': '/u/USERNAME Toolbox to Modnotes'
}

r = praw.Reddit('indexbot', **praw_config)  # praw auth w/ praw.ini

subreddit = ''  # subreddit name here without r/


def get_blob_wiki(notes):
    return json.loads(notes)["blob"]


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
  
  
def main(subreddit):
    usernotes = get_usernotes_wiki(subreddit)
    print(blob_to_string(get_blob_wiki(usernotes)))

  
if __name__ == '__main__':
    main(subreddit)
