# coding: utf-8
import ConfigParser
import requests
import json
import schedule
from expiringdict import ExpiringDict
import sys
import time

config_file = sys.argv[1]
print "config_file is %s" % config_file

config = ConfigParser.RawConfigParser()
config.read(config_file)

SECTION_NAME="DEFAULT"

sent_number = ExpiringDict(max_len=100, max_age_seconds=3600*24)
sent_max_size_map = ExpiringDict(max_len=10, max_age_seconds=3600*24)
# count num, every 24 hours, we can only sent sent_max_size sms message
sent_max_size = 200
# every send num, every url, every 24 hour can only use sent_max size sms message
sent_max = 3

hint_url = config.get(SECTION_NAME, "hint_url")
frequency_rate = json.loads(config.get(SECTION_NAME, "frequency_rate"))
hint_code = config.get(SECTION_NAME, "hint_code")
sms_send_status = json.loads(config.get(SECTION_NAME, "sms_send_status"))
args = config.get(SECTION_NAME, "args")
use_arg = config.get(SECTION_NAME, "use_arg")
method = config.get(SECTION_NAME, "method")
phone_number = json.loads(config.get(SECTION_NAME, "phone_number"))

# method to sent boring warning message
def do_job(params, check_url):
    print "I'm working!"

def send_message(code, url):
    message = "url:%s code:%s" % (url, code)
    for phone in phone_number:
        params = {
              "phone":phone,
            "message":message
             }
        do_job(params, url)

def check_request(index, url):
    print "now do check request:%s" % url
    param = json.loads(args)[index]
    print "param:%s" % param
    err_codes = json.loads(hint_code)[index]
    if json.loads(method)[index] == 'GET':
        r = requests.get(url, data=param)
        if (r.status_code not in err_codes) and sms_send_status[index] == "1":
            send_message(r.status_code, url)
        elif sms_send_status[index] != "1":
            print "he tells me to shut up my mouse"
    elif json.loads(method)[index] == 'POST':
        r = requests.post(url, data=json.dumps(param))
        print r.text
        if (r.status_code not in err_codes) and sms_send_status[index] == "1":
            send_message(r.status_code, url)
        elif sms_send_status[index] != "1":
            print "he tells me to shut up my mouse"

def __main__():
    hus = json.loads(hint_url)
    for (index, url) in enumerate(hus):
        schedule.every(int(frequency_rate[index])).seconds.do(check_request, index, url)
    while True:
        schedule.run_pending()
        time.sleep(1)

__main__()

