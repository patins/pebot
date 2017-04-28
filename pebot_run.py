from pebot import *

import sys
import logging
import time
import json
from datetime import datetime
logging.basicConfig(filename='the_log.log',level=logging.DEBUG,format='%(asctime)s %(message)s')
logging.info('waiting')
while datetime.now() < datetime(2016, 3, 2, 7, 58):
    time.sleep(1)
logging.info('starting')

bot = PEBot()
MIT_ID = ''

while True:
    try:
        section_list, date = bot.get_section_list()
    except:
        time.sleep(3)
        continue
    if date == '03/02/2016':
        for section in section_list:
            if 'archery' in section['title'].lower() and 'T' in section['days'] and 'R' in section['days'] and '1:00 PM' in section['time']:
                section_id = section['section_id']
                logging.info('Found section %s' % section)
                logging.info(bot.register_for_section(section_id, MIT_ID))
                sys.exit(0)
        logging.error('No appropriate section found %s' % json.dumps(section_list))
        sys.exit(0)
    else:
        logging.info('Got date %s' % date)
    if datetime.now() > datetime(2016,3,2,8,5):
        logging.error('Date time past')
        sys.exit(0)
    time.sleep(5)
