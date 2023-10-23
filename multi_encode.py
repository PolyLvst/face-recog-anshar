#!/usr/bin/env python3
from logwriter import write_some_log
from datetime import datetime
import face_recognition
import multiprocessing
import argparse
import pickle
import shutil
import time
import os

current_date = datetime.now()
# Format the date as DD-MM-YYYY
formatted_date = current_date.strftime("%d-%m-%Y")
logger = write_some_log(f'./logs/{formatted_date}.log','multi_encode.py')

class MultEncode():
    def __init__(self) -> None:
        self.bin_path = "./bin/known_face_encodings.pkl"
        self.image_paths = []
        self.num_processes = 0

    def refresh_bin(self,mode:str):
        mode = mode.lower()
        if mode == 'n':
            with open(self.bin_path, 'rb') as file:
                known_face_encodings = pickle.load(file)
            return known_face_encodings,False

        image_folder = './images'
        destination_folder = './new_images'
        files = os.listdir(image_folder)
        for file in files:
            print(f'Moving image .. {file}')
            logger.Log_write(f'Moving image .. {file}')
            source_path = os.path.join(image_folder, file)
            destination_path = os.path.join(destination_folder, file)
            shutil.move(source_path, destination_path)
        try:
            os.remove(self.bin_path)
            print(f"File '{self.bin_path}' has been deleted.")
            logger.Log_write(f"File '{self.bin_path}' has been deleted.")
        except FileNotFoundError:
            print(f"File '{self.bin_path}' not found.")
            logger.Log_write(f"File '{self.bin_path}' not found.","error")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            logger.Log_write(f"An error occurred: {str(e)}")
        return [],True

    # Function to process an image
    def encode_image(self,images):
        encodings = []
        destination_folder = "./images"
        for image in images:
            print(f"Processing ---------> {image} ..")
            load_image = face_recognition.load_image_file(image)
            try:
                face_locations = face_recognition.face_locations(load_image)
                if len(face_locations) > 0:
                    encoding = face_recognition.face_encodings(load_image)[0]
                    if '\\' in image:
                        file = image.replace('./new_images\\','')
                    else:
                        file = image.replace('./new_images/','')
                    destination_path = os.path.join(destination_folder, file)
                    shutil.move(image, destination_path)
                else:
                    print(f'No face detected at image : {image} skipping')
                    logger.Log_write(f'No face detected at image : {image}','error')
                    continue
            except Exception as e:
                print(f'Error encountered when processing [{image}]')
                logger.Log_write(f'Error encountered when processing [{image}] e : {e}','error')
                continue
            encodings.append(encoding)
        return encodings

    def get_elapsed_time(self,start_time,end_time):
        elapsed_time = end_time - start_time  # Calculate the elapsed time in seconds
        # Convert elapsed time to hours, minutes, and seconds
        hours = int(elapsed_time // 3600)
        elapsed_time %= 3600
        minutes = int(elapsed_time // 60)
        seconds = elapsed_time % 60
        print(f"Elapsed time : {hours} hours, {minutes} minutes, {seconds:.3f} seconds")
        logger.Log_write(f"Elapsed time : {hours} hours, {minutes} minutes, {seconds:.3f} seconds")
    
    def mult_proc_encode(self):
        size_define = self.num_processes
        # Jika foto yang di proses terlalu sedikit
        if len(self.image_paths) < self.num_processes:
            size_define = len(self.image_paths)
        # Split the list of image paths into chunks for parallel processing
        chunk_size = len(self.image_paths) // size_define
        image_path_chunks = [self.image_paths[i:i+chunk_size] for i in range(0, len(self.image_paths), chunk_size)]
        start_time = time.time()
        # Create a pool of worker processes
        with multiprocessing.Pool(processes=self.num_processes) as pool:
            encodings_list = pool.map(self.encode_image, image_path_chunks)
        end_time = time.time()
        # Flatten the list of list di dalam encodings
        encodings = [encoding for sublist in encodings_list for encoding in sublist]
        return start_time,end_time,encodings

    def encode_now(self,choose='Y',mode_input='input'):
        """ choose [Y/N] Y - Refresh bin N - Extend bin \n mode_input [input/args] """
        # Directory containing your images
        image_folder = "./new_images"
        destination_folder = "./images"

        # Loading binary file
        known_face_encodings = []
        mode_ = choose
        refresh_mode = False
        if os.path.exists(self.bin_path):
            if mode_input == 'input':
                mode_ = input('Do you want to refresh existing bin? [Y/N] ')
                known_face_encodings,refresh_mode = self.refresh_bin(mode_)
            else:
                known_face_encodings,refresh_mode = self.refresh_bin(mode_)
        else:
            print('First time run [Creating bin]')
            logger.Log_write('First time run [Creating bin]')
            known_face_encodings,refresh_mode = self.refresh_bin(mode_)
        if refresh_mode == False:
            if len(os.listdir(image_folder))==0:
                print('New image not found, Updated')
                logger.Log_write('New image not found, Updated')
                exit()
            if mode_.lower() == 'n':
                print('Extending current bin .. ')
                logger.Log_write('Extending current bin ..')
        else:
            print('Loading .. ')

        # List all image file paths in the folder
        self.image_paths = [os.path.join(image_folder, filename) for filename in os.listdir(image_folder) if filename.endswith(('.jpg', '.png'))]
        found_folder = []
        for path_check in os.listdir(image_folder):
            folder_path = os.path.join(image_folder, path_check)
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                found_folder.append(folder_path)
        if len(found_folder)>=1:
            print(f"The folders '{found_folder}' exists inside '{image_folder}'.")
            logger.Log_write(f"The folders '{found_folder}' exists inside '{image_folder}'.")
            print('Found folders .. [Make sure only images exist]')
            return

        # Number of processes to run concurrently
        self.num_processes = multiprocessing.cpu_count()  # You can adjust this number
        print(f'Number of available processor : {self.num_processes}')
        logger.Log_write(f'Number of available processor : {self.num_processes}')

        # Encodings list
        encodings = []
        print(f'Total image to process [{len(self.image_paths)}]')
        logger.Log_write(f'Total image to process [{len(self.image_paths)}]')
        if __name__ == '__main__':
            print('Using multiprocess .. ')
            logger.Log_write('Using multiprocess ..')
            start_time,end_time,encodings=self.mult_proc_encode()
        else:
            print('Using non multiprocess .. [run multi_encode.py directly for faster encoding]')
            logger.Log_write('Using non multiprocess .. [run multi_encode.py directly for faster encoding]','warning')
            start_time = time.time()
            for image in self.image_paths:
                print(f"Processing ---------> {image} ..")
                logger.Log_write(f"Processing ---------> {image} .. [non multiprocess]")
                load_image = face_recognition.load_image_file(image)
                try:
                    face_locations = face_recognition.face_locations(load_image)
                    if len(face_locations) > 0:
                        encoding = face_recognition.face_encodings(load_image)[0]
                        file = image.replace('./new_images\\','')
                        destination_path = os.path.join(destination_folder, file)
                        shutil.move(image, destination_path)
                    else:
                        print(f'No face detected at image : {image} skipping')
                        logger.Log_write(f'No face detected at image : {image} [non multiprocess]','error')
                        continue
                except Exception as e:
                    print(f'Error encountered when processing [{image}]')
                    logger.Log_write(f'Error encountered when processing [{image}] [non multiprocess] e : {e}','error')
                    continue
                encodings.append(encoding)
            end_time = time.time()
        self.get_elapsed_time(start_time,end_time)
        # Saving binary file
        known_face_encodings.extend(encodings)
        with open(self.bin_path, 'wb') as file:
            pickle.dump(known_face_encodings, file)

        # # List all files in the source folder
        skipped = os.listdir(image_folder)

        # Jika ada foto tanpa wajah terdeteksi maka
        print(f'\nTotal : {len(self.image_paths)} Skipped : {len(skipped)}, Bin saved at ->> {self.bin_path}')
        logger.Log_write(f'\nTotal : {len(self.image_paths)}, Bin saved at ->> {self.bin_path}')
        logger.Log_write(f'Some images skipped : {skipped}','warning')

        print('Done .. ')
        logger.Log_write('Done ..')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Use all your hardware potential to speed up encoding process")
    parser.add_argument('--refresh', '-r', action='store_true', help='Enable refresh mode')
    args = parser.parse_args()
    MultEncd = MultEncode()
    if args.refresh:
        print("Refresh mode is enabled.")
        MultEncd.encode_now('Y','args')
    else:
        MultEncd.encode_now()