#!/usr/bin/env python3
# import firebase_admin
# from firebase_admin import credentials,db
from logwriter import write_some_log
from datetime import datetime
from dotenv import load_dotenv
from playsound import playsound
from display import Display
import os
import json

# cache aside
CACHE = './db/students_cache.json'
# periodic attendance json
now = datetime.now()
formatted_time = now.strftime("%d-%m-%Y")
logger = write_some_log(f'./logs/{formatted_time}.log','db.py')
post_periodic_folder = f'./db/post_periodic'
periodic_post = f'./db/post_periodic/post_periodic{formatted_time}.json'
# Kredensial untuk realtime database dari firebase
# CRED_PATH = './db/credential.json'
# Limit transaksi untuk free tier firebase adalah 350 MB per hari
# Untuk sebulan free 10 GB
load_dotenv()
# Database exported from anshar.my.id users exported as json file
# DATABASE = os.environ.get('DATABASE')
display = Display()

class Db:
    def __init__(self):
        logger.Log_write('Starting')
        # self.cred = credentials.Certificate(CRED_PATH)
        # firebase_admin.initialize_app(self.cred,{
        #     'databaseURL':DATABASE
        # })
        # self.main_table = 'students/'
        # self.attendance_table = 'absensi/'
        # Local in-memory cache
        self.all_students = self._get_all_from_cache()
        self._redact_password()
        self.marked_students = []
        logger.Log_write('Setting audio .. ')
        self.success_sound = "./resources/ding.mp3"

    def get_student(self, id) -> list:
        if not f'stu-id-{id}' in self.all_students:
            print(f'ID {id} not found in database [please check users.json]')
            logger.Log_write(f'ID {id} not found in database [users.json not contain user]','error')
            return 'None in database'
        else:
            list_info = self.all_students[f'stu-id-{id}']
            return list_info

    def _get_all_from_cache(self):
        now = datetime.now()
        formatted_time = now.strftime("%d-%m-%Y %H:%M:%S")
        # status_cache_ref = db.reference('cache_sync_status/')
        # status_cache = status_cache_ref.get()
        
        # Jika status tidak sinkron, maka sinkronkan local cache
        # if status_cache["students_cache"] == False:
        #     info = self._get_all_from_db()
        #     info['fetched_date'] = formatted_time
        #     if os.path.exists(CACHE):
        #         os.remove(CACHE)
        #     with open(CACHE,'w') as f:
        #         json.dump(info,f)
        #         print('Local cache updated ')
        #         logger.Log_write('Local cache updated because database changed')
        #         status_cache_ref.update({'students_cache':True})
        #     return info
        
        # Jika tidak ditemukan status cache atau status tersinkron, maka cek juga kapan data di cache
        # else:
        if os.path.exists(CACHE):
            with open(CACHE,'r') as f:
                info = json.load(f)
            time_now = datetime.strptime(formatted_time,"%d-%m-%Y %H:%M:%S")
            time_cache = datetime.strptime(info['fetched_date'],"%d-%m-%Y %H:%M:%S")
            difference_time = time_now - time_cache
            # 1 day, 10:05:26 contoh jika di print
            # Jika umur cache masih belum lebih dari 10 menit
            total_detik = int(difference_time.total_seconds())
            if total_detik <= 600:
                print('Using cache .. ')
                logger.Log_write('Using cache ..')
                return info
            else:
                info = self._get_all_from_db()
                info['fetched_date'] = formatted_time
                with open(CACHE,'w') as f:
                    json.dump(info,f,indent=3)
                    print(f'Local cache updated ')
                    logger.Log_write('Local cache updated because more than 10 minutes old')
                    # status_cache_ref.update({'students_cache':True})
                return info
        else:
            info = self._get_all_from_db()
            info['fetched_date'] = formatted_time
            with open(CACHE,'w') as f:
                json.dump(info,f,indent=3)
                print('Local cache updated ')
                logger.Log_write('Local cache updated because first time running')
                # status_cache_ref.update({'students_cache':True})
            return info

    def _get_all_from_db(self):
        info = {}
        # info = db.reference(self.main_table).get()
        # print('Downloading data from database .. ')
        if not os.path.exists('./db/users.json'):
            print("users json not found [database notfound]")
            logger.Log_write("no users json found at ./db/users.json [no database found]")
            return None
        with open('./db/users.json','r') as f:
            data:list = json.load(f)

        table_name = data[2]['name']
        column_name = data[2]['data']
        if table_name != 'users':
            print('no users table at index[11]')
            logger.Log_write('no users table at index[11] possibly structure change')
            return None
        else:
            # print(table_name)
            info = {"stu-id-" + item["name"]: {"nama": item["full_name"].replace('\\','')} for item in column_name}
            logger.Log_write('fetching name and id from users.json to cache')
        # logger.Log_write('Downloading data from database ..')
        # Mendapatkan data semua siswa agar tidak terlalu sering meminta data dari database
        return info
    
    def _redact_password(self):
        if not os.path.exists('./db/users.json'):
            print("users json not found [database notfound]")
            logger.Log_write("no users json found at ./db/users.json [no database found]")
            return None
        with open('./db/users.json','r') as f:
            data:list = json.load(f)
        stat_pass = data[2].get('status_pass')
        if not stat_pass:
            logger.Log_write('Redacting password in users.json file')
            for item in data[2]['data']:
                item['password'] = "**REDACTED**"
            data[2]['status_pass'] = "REDACTED"
            with open('./db/users.json','w') as f:
                json.dump(data,f,indent=3)
            logger.Log_write('Password redacted ..')
        else:
            logger.Log_write('Password is safe and redacted')
            
    
    # def mark_as_present(self, id):
    #     return True
    
    def mark_attendance(self,date, stu_id):
        # stu_id berupa angka saja
        name = self.get_student(stu_id).get('nama')
        # format stu_id agar cocok dengan di dalam file cache students
        f_stu_id = f'stu-id-{stu_id}'
        lazy_upload = {}

        # Menggunakan total absen dari cache karena total sebelumnya seharusnya sudah tersedia di cache
        # Dimatikan karena migrasi ke database erina
        # if not 'total_masuk' in self.all_students[f_stu_id]:
        #     total_masuk = 0
        # else:
        #     total_masuk = self.get_student(stu_id).get('total_masuk')
        if name in self.marked_students:
            # Has already marked
            return
        if os.path.exists(periodic_post):
            with open(periodic_post,'r') as f:
                lazy_upload = json.load(f)
            if f_stu_id in lazy_upload:
                return
        # referensi ke table absensi
        # attendance_ref = db.reference(f'{self.attendance_table}{date}')
        # referensi ke table students
        # student_ref = db.reference(f'{self.main_table}{f_stu_id}')

        # if not attendance_ref.child(f_stu_id).get():
        display.show_checkmark(True)
        try:
            playsound(self.success_sound)
            logger.Log_write(f'Playing sound for {name} {f_stu_id}')
        except:
            print(f"Error playing sound")
            logger.Log_write(f'Error playing sound','error')
        # Tambahkan total masuk siswa
        # total_masuk+=1
        # Get the current time
        current_time = datetime.now().time()
        # Format the time as HH:MM:SS
        formatted_time = current_time.strftime("%H:%M:%S")
        # Update local cache
        # self.all_students[f_stu_id]['total_masuk'] = total_masuk
        # self.all_students[f_stu_id]['absensi_terakhir'] = f'{date} , {formatted_time}'
        
        # Update database
        # attendance_ref.update({f_stu_id: formatted_time})
        # student_ref.child('total_masuk').set(total_masuk)
        # student_ref.child('absensi_terakhir').set(f'{date} , {formatted_time}')
        print(f"Attendance marked for {name} on {date} [Updating post_periodic]")
        logger.Log_write(f'Attendance marked for {name} on {date} [Updating post_periodic]')
        # Update end point api lazyly
        if not os.path.exists(post_periodic_folder):
            os.mkdir(post_periodic_folder)
            logger.Log_write('Post periodic folder created')
        with open(periodic_post,'w') as f:
            lazy_upload[f'{f_stu_id}']={'id':stu_id,'tipe':'HADIR','time':formatted_time}
            json.dump(lazy_upload,f)
            logger.Log_write('Post_periodic updated')
            
            # payload = {'id':'12345','tipe':'HADIR','nama':'test API'}
            # r = requests.post(API_URL,payload)
            # print(r.text)
        # with open(CACHE,'w') as file_cache:
        #     json.dump(self.all_students,file_cache)
        #     logger.Log_write('Students_cache updated')
        # Beritahu jika siswa telah sukses terabsen
        # print(f"Attendance marked for {name} on {date} [Updating database]")
        # logger.Log_write(f'Attendance marked for {name} on {date} [Updating database]')
        self.marked_students.append(name)
        # else:
        #     # Jika aplikasi di restart atau di mulai ulang pada hari itu juga
        #     print("Already marked on database [Updating local in memory cache]")
        #     logger.Log_write("Already marked on database [Updating local in memory cache]")
        #     self.marked_students.append(name)

if __name__ == "__main__":
    # Jalankan file ini untuk merefresh local cache manual
    dxb = Db()
    now = datetime.now()
    formatted_time = now.strftime("%d-%m-%Y %H:%M:%S")
    # status_cache_ref = db.reference('cache_sync_status/')
    print('Refreshing local cache')
    info = dxb._get_all_from_db()
    info['fetched_date'] = formatted_time
    if os.path.exists(CACHE):
        os.remove(CACHE)
    with open(CACHE,'w') as f:
        json.dump(info,f)
        print('Local cache updated ')
        # status_cache_ref.update({'students_cache':True})