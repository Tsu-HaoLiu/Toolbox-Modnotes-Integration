import base64
import zlib
import json


"""Decode toolbox Base64 & zlib-compression"""


def pInflate(data) -> bytes:
    decompress = zlib.decompressobj(15)
    decompressed_data = decompress.decompress(data)
    decompressed_data += decompress.flush()
    return decompressed_data


def b64d(data: str) -> bytes:
    return base64.b64decode(data)


def js_byte_to_string(data: bytes) -> str:
    return data.decode("utf-8")
    

class BlobDecoder:
    def __init__(self):
        self.cleaned_notes = dict()
        self.notelength = int
    
    def blob_to_string(self, blob: str) -> dict:
        """Base64 -> zlib-compressed -> string -> dict"""
        # base64 decode blob
        zlib_bytes = b64d(blob)
        
        # zlib-uncompress to byte
        decompressed_bytes = pInflate(zlib_bytes)
        
        # byte to string
        clean_string = js_byte_to_string(decompressed_bytes)
        
        # Return dict
        self.cleaned_notes = json.loads(clean_string)
        
        # sum of values to get total
        note_count = [len(x['ns']) for x in self.cleaned_notes.values()]
        self.notelength = sum(note_count) - 1
        
        return self.cleaned_notes
    
    def conv_blob(self) -> dict:
        return self.cleaned_notes
    
    def note_length(self) -> int:
        return self.notelength