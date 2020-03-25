from typing import Union

from tdvt.config_gen.datasource_list import LinuxRegistry, MacRegistry, WindowsRegistry


OSSpecificRegistry = Union[LinuxRegistry, MacRegistry, WindowsRegistry]
