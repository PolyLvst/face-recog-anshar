#!/usr/bin/env python3
import pickle
from logwriter import write_some_log
from datetime import datetime
# import glob
import os 

WORK_DIR = os.getcwd() + "/images"
current_date = datetime.now()
# Format the date as DD-MM-YYYY
formatted_date = current_date.strftime("%d-%m-%Y")
logger = write_some_log(f'./logs/{formatted_date}.log','student.py')

class Student:
    
    def __init__(self) -> None:
        self.images = self._get_images()
        self.face_encodings = self._get_face_encodings()
        self.image_ids = self._get_image_ids()
        self.known_face_encodings

    def _get_images(self):
        # images = glob.glob(F"{WORK_DIR}/*.jpg")
        # images.sort()
        logger.Log_write('Getting all images in images folder')
        images = [os.path.join(WORK_DIR, filename) for filename in os.listdir(WORK_DIR) if filename.endswith(('.jpg', '.png'))]
        return images

    def _get_face_encodings(self):
        # encodings = []
        # for image in self.images:
        #     print(f"converting .. {image}")
        #     encoding = face_recognition.face_encodings(face_recognition.load_image_file(image))[0]
        #     encodings.append(encoding)
        bin_path = "./bin/known_face_encodings.pkl"
        if os.path.exists(bin_path):
            logger.Log_write('Opening bin of known face encodings')
            with open(bin_path, 'rb') as file:
                known_face_encodings = pickle.load(file)
        else:
            print('No binary found [Please run multi_encode.py]')
            logger.Log_write('No binary found [Please run multi_encode.py]','critical')
            known_face_encodings = []
        self.known_face_encodings = known_face_encodings
        return known_face_encodings

    def _get_image_ids(self):
        image_ids = []
        for image in self.images:
            image_id = os.path.splitext(os.path.basename(image))[0]
            image_ids.append(image_id)
        
        return image_ids

    def get_image_id(self, idx):
        return self.image_ids[idx]
    
    def check_images_to_encodings(self):
        logger.Log_write('Checking encodings ..')
        encodings_len = len(self.known_face_encodings)
        images_len = len(os.listdir(WORK_DIR))
        if encodings_len == images_len:
            logger.Log_write('Images are fully compatible with encodings')
            return True
        if encodings_len > images_len:
            print('Images are not compatible with total of encodings [Missing images]')
            print(f'encodings : {encodings_len}')
            print(f'images : {images_len}')
            logger.Log_write(f'Images are not compatible with total of encodings [Missing images] len --> encodings : {encodings_len} images : {images_len}','error')
            return False
        if encodings_len < images_len:
            print('Encodings not enough [Images too much]')
            print(f'encodings : {encodings_len}')
            print(f'images : {images_len}')
            logger.Log_write(f'Encodings not enough [Images too much] len --> encodings : {encodings_len} images : {images_len}','error')
            return False
        

# if __name__ == '__main__':
#     student = Student()
#     no = 0
#     for name in student.images:
#         no+=1
#         print(f'{no} {name}')
