from typing import Union

from tdvt.config_gen.datasource_list import LinuxRegistry, MacRegistry, WindowsRegistry


OsSpecificTestRegistry = Union[LinuxRegistry, MacRegistry, WindowsRegistry]
