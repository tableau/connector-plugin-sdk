# A class containing properties pertaining to the entire connector
class ConnectorProperties:
    def __init__(self):
        self.uses_tcd = False
        self.connection_fields = []
        self.vendor_defined_fields = []
        self.backwards_compatibility_mode = False
        self.is_jdbc = False
        self.connection_metadata_database = True
