"""Convert toolbox notes to csv or json and download as a file"""

import pandas as pd
import logging

logger = logging.getLogger('modnotes')


class Converter:
    def __init__(self) -> None:
        self.wiki_notes = dict()
        self.cleaned_usernotes = dict()
        self.combined_notes = dict()
        self.df = pd.DataFrame()

    def add(self, wiki, notes):
        self.wiki_notes = wiki
        self.cleaned_usernotes = notes
        self.wiki_notes = self.combine_json()
        self.df = pd.DataFrame.from_dict(self.cleaned_usernotes)

    def empty_notes(func):
        def f(self):
            if not self.wiki_notes: 
                raise Exception(f"Not authenticated or no information provided.")
            format_name = func(self)
            logger.info(f"{format_name} file created in current directory")
        return f

    def combine_json(self):
        self.wiki_notes['blob'] = self.cleaned_usernotes
        return self.wiki_notes.copy()

    def combinednotes(self):
        return self.wiki_notes
    
    @empty_notes
    def json_format(self):
        self.df.to_json('modnotes/usernotes_json.json')
        return "JSON"
    
    @empty_notes
    def csv_format(self):
        self.df.to_csv('modnotes/usernotes_csv.csv', encoding='utf-8', index=False)
        return "CSV"
    
    
