import sys
import platform


class TabQueryPath(object):
    def __init__(self, linux_path, mac_path, mac_arm_path, windows_path):
        self.linux_path = linux_path
        self.mac_path = mac_path
        self.mac_arm_path = mac_arm_path
        self.windows_path = windows_path

    @staticmethod
    def from_array(paths):
        if len(paths) != 4:
            raise IndexError
        t = TabQueryPath(paths[0], paths[1], paths[2], paths[3])
        return t

    def to_array(self):
        return [self.linux_path, self.mac_path, self.mac_arm_path, self.windows_path]

    def get_path(self, operating_system):
        if operating_system.startswith("darwin") and platform.machine() == 'arm64':
            return self.mac_arm_path
        elif operating_system.startswith("darwin"):
            return self.mac_path
        elif operating_system.startswith("linux"):
            return self.linux_path
        else:
            return self.windows_path