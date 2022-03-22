import os
import io
import eel
import traceback
import logging
import ModnotesConverter as mc


eel.init(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'webpage'))


class ForwardToFunctionStream(io.TextIOBase):
    def __init__(self, output_function=print):
        self.output_function = output_function

    def write(self, string):
        self.output_function(string)
        return len(string)


def uiconsole(text):
    eel.printjs(text)
    

def logger_console():
    """init logger to display on ui"""
    module_logger = logging.getLogger('modnotes')
    module_logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(ForwardToFunctionStream(uiconsole))
    handler.setFormatter(logging.Formatter('%(message)s'))
    handler.setLevel(logging.DEBUG)
    module_logger.addHandler(handler)
    module_logger.info("Welcome! Fill out your info above and click the \"login\" button to get started!")


def error_catcher(func):
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            uiconsole(str(e)) # Throw error to console
    return wrap


@error_catcher
def processnotes():
    """Function to process notes and convert them to modnotes"""
    for x, _ in enumerate(mc.process_notes(mc.conv.combinednotes(), mc.bDecode.conv_blob())):
        eel.eelActionedNotes(x) # Update ui note counter
        eel.eelCoinsLeft(mc.ratelimit()) # Update ratelimit coins
    uiconsole("Finished converting notes!")


@error_catcher
def setupConvertion(form_details):
    # Authenticate PRAW
    mc.OAuth(form_details)
    
    # Validate subreddit
    mc.safe_checks(form_details[4])  
    
    # Retrive usernote from wiki
    usernotes = mc.get_usernotes_wiki()
    
    # Decode blob
    cleaned_notes = mc.bDecode.blob_to_string(usernotes["blob"])
    
    # Save decoded notes
    mc.conv.add(usernotes, cleaned_notes)
    return True
    

@eel.expose
def downloadCSV():
    mc.conv.csv_format()
    
    
@eel.expose
def downloadJSON():
    mc.conv.json_format()
    
    
@eel.expose
def startNotes():
    processnotes()


@eel.expose
def browser__init():
    """Retrive login from .ini"""
    return mc.retrive_ini()


@eel.expose
def authentication(details):
    if setupConvertion(details):
        
        # Total note counter to ui
        eel.eelTotalNotes(mc.bDecode.note_length())
        
        # Ratelimit coins remaining to ui
        eel.eelCoinsLeft(mc.ratelimit())
        
        # Successful auth update ui buttons
        eel.eelupdateBtn()
        
        # Notify user on next steps
        uiconsole("Click the \"convert\" button to start converting your toolbox notes to modnotes!")
    

def main():
    logger_console()
    try:
        #Start the application and pass all initial params below
        eel.start("index.html", size=(600, 850))
    except Exception:
        #Handle errors and the potential hanging python.exe process
        print(traceback.format_exc())


if __name__ == '__main__':
    main()
