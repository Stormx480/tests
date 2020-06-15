import logging
import argparse
import sys
import os
import json


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--folder', '--folder_path', type=str, required=True)
parser.add_argument('-t', '--token', type=str, required=True)

args = parser.parse_args(sys.argv[1:])

base_url = 'https://dev-100-api.huntflow.ru'

default_headers = {
    'User-Agent': 'App/1.0 (eeeee@eeeee.ru)',
    'Authorization': 'Bearer {personal_token}'.format(personal_token=args.token)
}


logging.basicConfig(level='DEBUG',
                    filename='log_screen.log',
                    format="%(asctime)s %(levelname)s %(filename)s %(funcName)s %(message)s",
                    datefmt='%Y-%m-%d %H-%M')
logger = logging.getLogger('App')


status_dict = {
    'отправлено письмо': 'Submitted',
    'интервью с hr': 'HR Interview',
    'выставлен оффер': 'Offered',
    'отказ': 'Declined'
}

if not os.path.exists('checker.json'):
    json_file = open('checker.json', 'w')
    json_file.close()

if os.stat("checker.json").st_size == 0:
    json_file = open('checker.json', 'w')
    json.dump(
        {
            'processed': 0
        },
        json_file,
        ensure_ascii=False
    )
    json_file.close()

checker = open('checker.json', 'r+', encoding='utf-8')

