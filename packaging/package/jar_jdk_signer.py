import os
import logging
import subprocess
from pathlib import Path
from .helper import check_jdk_environ_variable

JARSIGNER_EXECUTABLE_NAME = "jarsigner.exe"
logger = logging.getLogger(__name__)


def validate_signing_input(input_dir, taco_name, alias, keystore):
    """
    Validate signing input
    """

    if not alias:
        logger.error("Signing Error: Private key's alias is missing or empty")
        return False

    if not keystore or not os.path.isfile(Path(keystore)):
        logger.error("Signing Error: Keystore path is missing or invalid")
        return False

    if not os.path.isfile(input_dir/taco_name):
        logger.error("Signing Error: Taco file to be signed has been deleted or doesn't exist")
        return False

    return True


def jdk_sign_jar(input_dir, taco_name, alias, keystore):
    """
    Sign a taco using JAVA JDK

    :param input_dir: source dir of taco file to be signed
    :type input_dir: str

    :param taco_name: taco file name
    :type taco_name: str

    :param alias: Private key's alias in keystore
    :type alias: str

    :param keystore: keystore path
    :type keystore: str

    :return: Boolean
    """

    if not check_jdk_environ_variable(JARSIGNER_EXECUTABLE_NAME):
        logger.error("Error: jdk_create_jar: no jdk set up in PATH environment variable, "
                     "please download JAVA JDK and add it to PATH")
        return False

    logging.debug("Start signing " + taco_name + " from " + str(os.path.abspath(input_dir)) + " using JDK jarsigner")

    args = ["jarsigner", "-keystore", keystore, "-signedjar", str(input_dir/("signed_" + taco_name)), str(input_dir/taco_name), alias]
    p = subprocess.Popen(args)
    p.wait()

    logging.info(taco_name + " was signed as " + "signed_" + taco_name + " at " + str(os.path.abspath(input_dir)))

    return True

