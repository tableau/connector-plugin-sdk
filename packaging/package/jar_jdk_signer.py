import os
import logging
import subprocess
from pathlib import Path
from .helper import check_jdk_environ_variable
import getpass

JARSIGNER_EXECUTABLE_NAME = "jarsigner.exe"
logger = logging.getLogger(__name__)

KEYSTORE_PWD_PROMPT_LENGTH = len("Enter Passphrase for keystore: ")
ALIAS_PWD_PROMPT_LENGTH = len("Enter key password for : ")


def validate_signing_input(input_dir, taco_name, alias, keystore):
    """
    Validate signing input

    :return: Boolean
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


def get_user_pwd(alias):
    """
    Let user input password for keystore and alias, which will be used as jarsigner subprocess input
    """

    ks_pwd = getpass.getpass(prompt='Enter keystore password: ', stream=None)
    alias_pwd = getpass.getpass(prompt='Enter password for alias ' + alias + ":(RETURN if same as keystore password)",
                                stream=None)

    if alias_pwd == "" or alias_pwd == ks_pwd:
        return str.encode(ks_pwd + "\n"), str.encode(ks_pwd + "\n")
    else:
        return str.encode(ks_pwd + "\n"), str.encode(alias_pwd + "\n")


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
        return False

    logger.debug("Start signing " + taco_name + " from " +
                 str(os.path.abspath(input_dir)) + " using JDK jarsigner")

    # Get user's keystore and alias password input from console
    pwd_input = get_user_pwd(alias)
    ks_pwd_bytes = pwd_input[0]
    alias_pwd_bytes = None
    if pwd_input[1] != pwd_input[0]:
        alias_pwd_bytes = pwd_input[1]

    # Start jarsigner subprocess
    args = ["jarsigner", "-keystore", keystore, str(input_dir/taco_name), alias]
    p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Pass keystore and alias password to jarsigner subprocess
    p.stdin.write(ks_pwd_bytes)
    p.stdin.flush()
    p.stdout.read(KEYSTORE_PWD_PROMPT_LENGTH)
    if alias_pwd_bytes:
        p.stdin.write(alias_pwd_bytes)
        p.stdin.flush()
        p.stdout.read(ALIAS_PWD_PROMPT_LENGTH + len(alias))

    # log jarsigner output
    while True:
        line = p.stdout.readline()
        if not line:
            break
        str_to_log = str(line, 'utf-8').rstrip('\r\n')
        if str_to_log:
            logger.info(str_to_log)

    p.stdout.close()
    p.stdin.close()
    p.terminate()
    p.wait()

    if p.returncode == 0:
        logger.info("taco was signed as " + taco_name + " at " + str(os.path.abspath(input_dir)))
        return True
    else:
        return False
