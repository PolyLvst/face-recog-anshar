#!/usr/bin/env python3
import json
import requests
from dotenv import load_dotenv
from datetime import datetime
from logwriter import write_some_log
import pickle
import time
import os

# run this file with cron with interval of 5 minutes
# atau windows task scheduler

# lazy upload periodic json file
now = datetime.now()
formatted_time = now.strftime("%d-%m-%Y")
logger = write_some_log(f'./logs/{formatted_time}.log','lazy_attend.py')
logger.Log_write('Starting')
periodic_post = f'./db/post_periodic/post_periodic{formatted_time}.json'
posted_ids = f'./db/post_periodic/posted{formatted_time}.checkpoint'
# Umur maksimal file post_periodic dan posted adalah 3 hari
max_age_seconds = 3 * 24 * 60 * 60

load_dotenv()
find_this = os.environ
# JAM_TERAKHIR_MASUK = find_this['JAM_TERAKHIR_MASUK']
API_URL = find_this['API_URL']
# time1 = datetime.strptime(JAM_TERAKHIR_MASUK, "%H:%M:%S")

def check_internet_connection():
    try:
        # Try to make a GET request to a well-known website, like Google
        response = requests.get("https://www.google.com", timeout=5)
        # If the request is successful, return True
        return True
    except requests.ConnectionError:
        # Connection error indicates no internet connection
        return False

if os.path.exists(periodic_post):
    if check_internet_connection():
        logger.Log_write('Internet available')
    else:
        logger.Log_write('No internet connection ..')
        print('No internet connection ..')
        exit()
    for file_path in os.listdir('./db/post_periodic'):
        file_path = os.path.join('./db/post_periodic',file_path)
        file_stat = os.stat(file_path)
        current_time = time.time()
        # Calculate the age of the file in seconds
        file_age_seconds = current_time - file_stat.st_mtime
        # Compare the age with the maximum allowed age
        if file_age_seconds > max_age_seconds:
            # File is older than 3 days, so delete it
            os.remove(file_path)
            print(f"{file_path} has been deleted as it's more than 3 days old.")
            logger.Log_write(f'deleted {file_path} - old post_periodic','warning')
    # print(f'Jam masuk : {JAM_TERAKHIR_MASUK}')
    with open(periodic_post,'r') as json_file :
        payloads:dict = json.load(json_file)
    if os.path.exists(posted_ids):
        with open(posted_ids,'rb') as f:
            marked_ids = pickle.load(f)
            logger.Log_write('Opening .checkpoint')
    else:
        marked_ids = []
        logger.Log_write('No checkpoint found')
    complete = False
    cur_marked_id = []
    while not complete:
        for key,value in payloads.items():
            if key in marked_ids:
                continue
            # id_stu = int(value.get("id"))
            id_stu = value.get("id")
            tipe = value.get("tipe")
            time_attend = value.get("time")
            
            # time_date_format = datetime.strptime(time_attend,'%H:%M:%S')
            # Jika waktu masuk siswa > waktu telat maka tipe = TELAT
            # if time_date_format > time1:
            #     print(f'id : {id_stu} tipe : TELAT time : {time_attend}')
            #     logger.Log_write(f'id : {id_stu} tipe : TELAT time : {time_attend}')
            #     tipe = 'TELAT'
            # else:
            print(f'id : {id_stu} tipe : {tipe} time : {time_attend}')
            logger.Log_write(f'id : {id_stu} tipe : {tipe} time : {time_attend}')
            # post the payload
            r = requests.post(API_URL,{'id':id_stu,'tipe':tipe,'time':time_attend})
            if r.status_code >= 200 and r.status_code <=299:                
                marked_ids.append(key)
                cur_marked_id.append(key)
            else:
                print(r.text)
                logger.Log_write(f'Key : {key} got {r.text}','error')
        # Pop id yang telah terkirim
        for xid in marked_ids:
            payloads.pop(xid)

        # Jika selesai semua maka mark complete
        if len(payloads) <= 0:
            complete=True
    if len(cur_marked_id) == 0:
        print('Listening .. [lazy_attend.py]')
        logger.Log_write('Listening ..')
        exit()
    print('All posted .. ')
    logger.Log_write('All posted, storing to .checkpoint')
    with open(posted_ids,'wb') as f:
        pickle.dump(marked_ids,f)

# Jika belum ada file post_periodic
else:
    print('Listening .. [lazy_attend.py]')
    logger.Log_write('Listening .. [No post periodic file generated yet]')
    # sleep(3)