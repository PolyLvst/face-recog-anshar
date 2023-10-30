#!/usr/bin/env python3
from screeninfo import get_monitors
from datetime import datetime
from logwriter import write_some_log
import ttkbootstrap as ttk
import cv2

current_date = datetime.now()
# Format the date as DD-MM-YYYY
formatted_date = current_date.strftime("%d-%m-%Y")
logger = write_some_log(f'./logs/{formatted_date}.log','display.py')
class Display:
    CAPTION1 = "SISTEM ABSENSI"
    CAPTION2 = "SD ISLAM TERPADU "
    CAPTION3 = "NURUL ANSHAR"
    
    FONT = cv2.FONT_HERSHEY_DUPLEX
    FONT_SCALE = 1.0
    FONT_THICKNESS = 80
    LABEL_COlOR = (0, 0, 0)
    # LOGO_FILE =  "/Users/zefri/Working/nurul-anshar/face-recognition/logo.png"
    LOGO_FILE =  "./resources/logo.png"
    LOGO_FILE_K =  "./resources/logokanan.png"

    def __init__(self, vcap = None) -> None:
        # Video Capture
        if vcap:
            self.vcap = vcap
            self.width  = self.vcap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float `width`
            self.height = self.vcap.get(cv2.CAP_PROP_FRAME_HEIGHT)  # float `height`
            self.display_width,self.display_height = self._get_monitor_size()
        self.scr_width,self.scr_height = self._get_ori_monitor_size()
        self.marked_students = []

    def write_caption(self, frame, header, ypos):
        (label_width, label_height), baseline = cv2.getTextSize(header, self.FONT, self.FONT_SCALE, self.FONT_THICKNESS)
        x_pos = int((self.width - label_width)/2) + 50
        cv2.putText(frame, header, (x_pos, ypos), self.FONT, self.FONT_SCALE, self.LABEL_COlOR, 1)

    def draw_overlay(self, frame):
        overlay = frame.copy()
        # Rectangle parameters
        x, y, w, h = 0, 0, int(self.width), 100  
        # A filled rectangle
        cv2.rectangle(overlay, (x, y), (x+w, y+h), (255, 255, 255), -1)  
    
        alpha = 0.4  # Transparency factor.    
        # Following line overlays transparent rectangle
        # over the image
        return cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

    def write_header(self, frame):
        new_image = self.draw_overlay(frame)
        new_image = self.draw_logo(new_image)

        self.write_caption(new_image, self.CAPTION1, 30)
        self.write_caption(new_image, self.CAPTION2, 60)
        self.write_caption(new_image, self.CAPTION3, 90)
        return new_image

    def draw_logo(self, background):
        ori = cv2.imread(self.LOGO_FILE, -1)
        ori2 = cv2.imread(self.LOGO_FILE_K, -1)

        scale_percent = (80/ori.shape[0]) * 100
        width = int(ori.shape[1] * scale_percent / 100)
        height = int(ori.shape[0] * scale_percent / 100)
        dim = (width, height)

        scale_percent_k = (80/ori2.shape[0]) * 100
        width_k = int(ori2.shape[1] * scale_percent_k / 100)
        height_k = int(ori2.shape[0] * scale_percent_k / 100)
        dim_k = (width_k, height_k)
        
        # resize image
        logo = cv2.resize(ori, dim, interpolation = cv2.INTER_AREA)
        logo_k = cv2.resize(ori2, dim_k, interpolation = cv2.INTER_AREA)

        (label_width, label_height), baseline = cv2.getTextSize(self.CAPTION2, self.FONT, self.FONT_SCALE, self.FONT_THICKNESS)

        y_offset = 10
        x_offset = int((self.width - label_width ) / 2) - 50

        y_offset_k = 10
        x_offset_k = int(self.width / 2) + 175

        y1, y2 = y_offset, y_offset + logo.shape[0]
        x1, x2 = x_offset, x_offset + logo.shape[1]

        y1_k, y2_k = y_offset_k, y_offset_k + logo_k.shape[0]
        x1_k, x2_k = x_offset_k, x_offset_k + logo_k.shape[1]

        alpha_s = logo[:, :, 3] / 255.0
        alpha_l = 1.0 - alpha_s

        alpha_s_k = logo_k[:, :, 3] / 255.0
        alpha_l_k = 1.0 - alpha_s_k

        for c in range(0, 3):
            background[y1:y2, x1:x2, c] = (alpha_s * logo[:, :, c] +
                                    alpha_l * background[y1:y2, x1:x2, c])
        for c in range(0, 3):
            background[y1_k:y2_k, x1_k:x2_k, c] = (alpha_s_k * logo_k[:, :, c] +
                                    alpha_l_k * background[y1_k:y2_k, x1_k:x2_k, c])
        
        return background
            

    def draw_student_name(self, frame, top, right, bottom, left, name):
        top *= 6#4
        right *= 7#4
        bottom *= 7#4
        left *= 6#4
        if name == "Belum terdaftar":
            color = (0, 0, 255)
        elif name == "None in database":
            color = (0, 130, 255)
        elif name in self.marked_students:
            # print('Already marked')
            color = (255, 130, 0)
        elif name == "Ready":
            color = (0, 225, 55)
        else:
            # print('Okay marked')
            color = (0, 100, 0)
            self.marked_students.append(name)
        # print(self.marked_students)
        
        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), color, 3)
        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    def resize_frame(self,frame):
        resized_frame = cv2.resize(frame, (self.display_width, self.display_height))
        return resized_frame
    
    def _get_monitor_size(self):
        # Get the screen's resolution
        monitors = get_monitors()
        if monitors:
            primary_monitor = monitors[0]
            screen_width = primary_monitor.width
            screen_height = primary_monitor.height
            # print("Screen Width:", screen_width, "Screen Height:", screen_height)
        else:
            print("No monitors found.")
            logger.Log_write('No monitors found','error')
        screen_aspect_ratio = screen_width / screen_height
        frame_width = self.width
        frame_height = self.height
        # Calculate the aspect ratio of the video frame
        frame_aspect_ratio = frame_width / frame_height
        # Calculate the dimensions to display the video frame without stretching
        if frame_aspect_ratio > screen_aspect_ratio:
            display_width = screen_width
            display_height = int(screen_width / frame_aspect_ratio)
        else:
            display_height = screen_height
            display_width = int(screen_height * frame_aspect_ratio)
        return display_width,display_height
    
    def _get_ori_monitor_size(self):
        # Get the screen's resolution
        monitors = get_monitors()
        if monitors:
            primary_monitor = monitors[0]
            screen_width = primary_monitor.width
            screen_height = primary_monitor.height
        else:
            print('No monitor .. ')
            logger.Log_write('No monitor','error')
        return screen_width,screen_height

    def show_checkmark(self,marked:bool):
        # Read the image file
        if marked == True:
            # Jika sudah terabsen
            # print('Marked')
            png = cv2.imread('./resources/marked.png')
        else:
            # Jika siswa kembali lagi maka akan muncul logo info saja
            # print('info')
            png = cv2.imread('./resources/info.png')
        screen_width,screen_height = self.scr_width,self.scr_height
        # Check if the image was loaded successfully
        if png is not None:
            # Create a borderless window
            cv2.namedWindow('Terabsen', cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty('Terabsen', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            # Resize the borderless window to your desired dimensions
            prefer_ratio = 100
            offset_y = 30
            cv2.resizeWindow('Terabsen', prefer_ratio, prefer_ratio)
            # Calculate the position to move the window to the center bottom
            move_x = (screen_width - prefer_ratio) // 2
            move_y = screen_height - prefer_ratio - offset_y
            # Move the window to the calculated position
            cv2.moveWindow('Terabsen', move_x, move_y)
            # Display the image in the borderless window
            cv2.imshow('Terabsen', png)
        else:
            # If the image was not loaded successfully, print an error message
            print("Error: Unable to load the image.")
            logger.Log_write('Unable to load the image of checkmark / info','error')

    def user_register(self):
        # theme_list -> "darkly" "solar" "superhero" "cyborg" "vapor" "flatly" dan lebih lengkap ada di ttk bootstrap
        window = ttk.Window(title="Form pendaftaran",themename="darkly")
        w = 400 # width for the Tk window
        h = 200 # height for the Tk window

        # get screen width and height
        ws = self.scr_width # width of the screen
        hs = self.scr_height # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = int((ws/2) - (w/2))
        y = int(hs - h -50)

        # print(ws,hs)
        # print(x,y)
        window.geometry(f'{w}x{h}+{x}+{y}')

        header_label = ttk.Label(master=window,
                                 text="SDIT Nurul Anshar"
                                 ,font=("Calibri",18,"bold")
                                 ,justify="center")

        frame_id_field = ttk.Frame(master=window)
        frame_name_field = ttk.Frame(master=window)
        frame_button = ttk.Frame(master=window)

        id_field = ttk.Entry(master=frame_id_field)
        id_label = ttk.Label(master=frame_id_field,text="NIS")
        name_field = ttk.Entry(master=frame_name_field)
        name_label = ttk.Label(master=frame_name_field,text="Nama")

        regis_button = ttk.Button(master=frame_button,text="Send")
        take_photo = ttk.Button(master=frame_button,text="Ambil foto",bootstyle="success")

        # Pack semua widget agar ditampilkan
        header_label.pack(pady=17)

        id_label.pack(side="left",padx=7)
        id_field.pack(side="left",pady=5,padx=5)
        frame_id_field.pack()

        name_label.pack(side="left")
        name_field.pack(side="left",pady=5,padx=5)
        frame_name_field.pack()

        take_photo.pack(side="left",padx=5)
        regis_button.pack(side="left",padx=5)
        frame_button.pack(pady=5)

        window.mainloop()

if __name__ == "__main__":
    dp = Display()
    dp.user_register()