import os.path

class ConnectorFile:
    
    def __init__(self, file_name, file_type):
        self.file_name = file_name
        self.file_type = file_type

    def extension(self):
        ext = os.path.splitext(self.file_name)[-1]
        #Remove the leading period.
        return ext if not ext else ext[1:]
    
