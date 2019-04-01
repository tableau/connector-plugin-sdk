
class ConnectorFile:
    
    def __init__(self, file_name, file_type):
        self.file_name = file_name
        self.file_type = file_type

    def extension(self):
        return self.file_name.split(".")[-1]
    