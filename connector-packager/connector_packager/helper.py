import os
import logging

from pathlib import Path


PATH_ENVIRON = "PATH"
logger = logging.getLogger('packager_logger')


def check_jdk_environ_variable(exe_name: str) -> bool:
    """
    Check if executable needed in jdk is available
    """
    path_list = os.environ[PATH_ENVIRON].split(os.pathsep)
    for path in path_list:
        if os.path.isfile(Path(path) / exe_name):
            return True

    logger.error("Java Error: jdk_create_jar: no jdk set up in PATH environment variable, "
                 "please download JAVA JDK and add it to PATH")
    return False
