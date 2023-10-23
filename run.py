#!/usr/bin/env python3
from dotenv import load_dotenv
from datetime import datetime
import face_recognition
import numpy as np
import platform
import cv2
import os

from logwriter import write_some_log
from student import Student
from display import Display
from db import Db

def run_main():
    # This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
    # other example, but it includes some basic performance tweaks to make things run a lot faster:
    #   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
    #   2. Only detect faces in every other frame of video.

    # PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
    # OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
    # specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

    load_dotenv()
    # Supported os is Windows and Linux if you want to use another os maybe the timing not accurate
    HOST = platform.system()
    TOLERANCE = float(os.environ.get('TOLERANCE'))

    # Get the current date
    current_date = datetime.now()
    # Format the date as DD-MM-YYYY
    formatted_date = current_date.strftime("%d-%m-%Y")
    logger = write_some_log(f'./logs/{formatted_date}.log','run.py')
    logger.Log_write('--------- Starting ---------')
    logger.Log_write(f'Host : {HOST}')

    # Get a reference to webcam #0 (the default one)
    print('Getting video capture .. ')
    logger.Log_write('Getting video capture ..')
    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        print('Cannot access camera : 0 trying camera 1 .. ')
        logger.Log_write('Cannot access camera : 0 trying camera 1 ..','warning')
        video_capture = cv2.VideoCapture(1)
        if not video_capture.isOpened():
            print("Error: Cannot open any camera.")
            logger.Log_write(f'Cannot open any camera','critical')
            exit()
        else:
            logger.Log_write("Successfully opened camera at index 1.")
    else:
        logger.Log_write("Successfully opened camera at index 0.")

    db = Db()
    student = Student()
    display = Display(video_capture)
    known_face_encodings = student.face_encodings
    window_mode_resizeable = False # Jika ingin menggunakan window kecil set ke True
    window_name = 'Video'

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True
    check_encoding = student.check_images_to_encodings()

    counter = 0
    timeout_counter = 0
    unknown_id_in_database = False
    current_stu = ''
    mode_nama = 'Belum terdaftar'
    timing_icon = {'Windows':[4,6,60],'Linux':[0,10,100],'Darwin':[4,6,60],'Java':[4,6,60]}
    if HOST != 'Windows' and HOST != 'Linux':
        print('This os maybe have a different timing ...')
        logger.Log_write('Timing may have differ','warning')
    # Jika False maka memakai mode popup info.png jika True memakai marked.png
    mode_popup = True
    logger.Log_write('Preparing while loop ..')

    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()
        if not ret:
            print('[Warning] No signal ..')
            logger.Log_write('video_capture no signal','error')
            continue
        frame = display.write_header(frame)

        # Only process every other frame of video to save time
        if process_this_frame:
            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, TOLERANCE)
                name = mode_nama

                # # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = known_face_names[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                if not check_encoding:
                    continue
                # Jika encoding cocok dan dapat digunakan secara tepat, jika tidak maka continue atau skip iterasi ini
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    student_id = student.get_image_id(best_match_index)
                    student_info = db.get_student(student_id)
                    if student_info == 'None in database':
                        name = student_info
                        unknown_id_in_database = True
                    else:
                        name = student_info.get('nama')
                        unknown_id_in_database = False
                    if not name in face_names:
                        if not unknown_id_in_database:
                            db.mark_attendance(formatted_date,student_id)
                    # Jika orang yang terdeteksi merupakan orang selanjutnya maka langsung reset ceklist
                    if name != current_stu:
                        counter = 0
                        mode_popup = True
                        # print('New face inline')
                        try:
                            cv2.destroyWindow('Terabsen')
                        except:
                            pass
                    else:
                        # print('popup false')
                        mode_popup = False
                    current_stu = name
                    # Gunakan value <= 4 untuk di OS Window
                    if counter <= timing_icon[HOST][0]:
                    # if counter == 0:
                        # print(f'checkmark mode : {mode_popup}')
                        # if not unknown_id_in_database:
                        #     display.show_checkmark(mode_popup)
                        # else:
                        if mode_nama != "Ready":
                            display.show_checkmark(False)
                        counter += 1
                    counter += 1
                    # Gunakan value == 6 untuk OS Window
                    if counter == timing_icon[HOST][1]:
                    # if counter == 10:
                        # print('Destroyed window more than 6 iter')
                        try:
                            cv2.destroyWindow('Terabsen')
                        except:
                            pass
                        counter = 0
                face_names.append(name)
        if mode_popup == False:
            timeout_counter+=1
            # Gunakan value >= 60 untuk OS Window
            if timeout_counter >= timing_icon[HOST][2]:
            # if timeout_counter >= 100:
                timeout_counter = 0
                try:
                    cv2.destroyWindow('Terabsen')
                except:
                    pass
        else:
            timeout_counter = 0

        process_this_frame = not process_this_frame
        frame = display.resize_frame(frame)
        if window_mode_resizeable:
            cv2.namedWindow(window_name)
            cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.namedWindow(window_name,cv2.WINDOW_NORMAL)
            cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            display.draw_student_name(frame, top, right, bottom, left, name)

        # Display the resulting image
        cv2.imshow(window_name, frame)
        # print("faces : ",face_names)

        # Hit 'q' on the keyboard to quit!
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

        # Hit esc to quit
        key = cv2.waitKey(1) & 0xFF
        if key == ord('r') or key == ord('R'):
            logger.Log_write('Resetting mode_nama')
            mode_nama = 'Belum terdaftar'
        if key == ord('p') or key == ord('P'):
            logger.Log_write('Opening sign up')
            mode_nama = 'Ready'
        if key == 27:  # Press 'Esc' key to exit
            logger.Log_write('esc key pressed ...')
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()
    logger.Log_write('--------- Exited ---------')

if __name__ == '__main__':
    run_main()