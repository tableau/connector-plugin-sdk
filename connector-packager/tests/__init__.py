import logging

LOG_FILE = 'packager_tests_logs.txt'

print("Printing test logs to " + LOG_FILE)

# Create logger.
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, filemode='w', format='%(asctime)s %(message)s')
logger = logging.getLogger()
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
logger.addHandler(ch)
