import sys
import glob
import argparse
import time
import requests
import logging

formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S:%f')
logging.basicConfig(filename='mission.log',level=logging.DEBUG, format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S')
logging.debug('This message should go to the log file')
time.sleep(1)
logging.info('So should this')
logging.warning('And this, too')