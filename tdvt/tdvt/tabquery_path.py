class TabQueryPath(object):
    def __init__(self, linux_path, mac_path, windows_path):
        self.linux_path = linux_path
        self.mac_path = mac_path
        self.windows_path = windows_path

    @staticmethod
    def from_array(paths):
        if len(paths) != 3:
            raise IndexError
        t = TabQueryPath(paths[0], paths[1], paths[2])
        return t

    def to_array(self):
        return [self.linux_path, self.mac_path, self.windows_path]

    def get_path(self, os):
        if os.startswith("darwin"):
            return self.mac_path
        elif os.startswith("linux"):
            return self.linux_path
        else:
            return self.windows_path