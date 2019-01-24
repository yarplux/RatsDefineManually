import tkinter as tk
from tkinter import messagebox

import cv2
import os
import PIL.Image
import PIL.ImageTk
import numpy as np

import constants as cs
import config as cfg

from panels_menu import Win, WinHelp


#
# Widget wrapper classes ===============================================================================================
#
class MySlider(object):
    init = False

    def __init__(self, my_parent, my_callback, name):
        self.name = name
        self.function = my_callback
        self.min = 1
        self.slider = tk.Scale(my_parent,
                               from_=self.min, to=cs.OPT_PROC[name + "_Max"], label=cs.OPT_LABELS[name],
                               orient=tk.HORIZONTAL, length=300,
                               command=self.callback)

        if type(cs.OPT_PROC[name+'_Max']) == float:
            self.slider.config(resolution=0.1)

        self.slider.pack()

        if cs.OPT_PROC[name] == self.min:
            self.init = True
        else:
            self.slider.set(cs.OPT_PROC[name])

    def callback(self, x):
        if self.init:
            self.function(self.slider.get(), self.name)
        self.init = True


class MyButton(object):
    def __init__(self, my_parent, my_text, my_callback, side):
        self.function = my_callback
        self.name = my_text
        self.button = tk.Button(my_parent, text=my_text, bd=1, relief=tk.FLAT, command=self.callback)
        self.button.pack(side=side, pady=3, padx=5)

    def callback(self):
        self.function(self.name, self.button)


#
# Video wrapper classes ================================================================================================
#
class MyVideo:
    vid = cv2.VideoCapture()
    counter = 0
    frame = np.zeros((0, 0, 3), np.uint8)

    def __init__(self, video_source=''):
        self.vid = cv2.VideoCapture(video_source)
        self.length = self.vid.get(cv2.CAP_PROP_FRAME_COUNT)

        self.current_width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.current_height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

        self.width = int(self.current_width*cs.OPT_PROC['k'])
        self.height = int(self.current_height*cs.OPT_PROC['k'])

        if self.vid.isOpened():
            ret, frame = self.vid.read()
            MyVideo.frame = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), (self.width, self.height))

        else:
            raise ValueError("Unable to open video source", video_source)


    def get_frame(self):
        if self.vid.isOpened():
            MyVideo.counter += cs.OPT_PROC['FrameDelta']
            if MyVideo.counter >= self.length:
                MyVideo.counter = 0

            self.vid.set(cv2.CAP_PROP_POS_FRAMES, MyVideo.counter)
            ret, frame = self.vid.read()
            if ret:
                self.width = int(self.current_width * cs.OPT_PROC['k'])
                self.height = int(self.current_height * cs.OPT_PROC['k'])

                MyVideo.frame = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), (int(self.width), int(self.height) ))

            return ret, MyVideo.frame
        else:
            return False, None

    def set_frame(self, x, flag):
        if flag:
            self.vid.set(cv2.CAP_PROP_POS_FRAMES, x)
            ret, frame = self.vid.read()
            if ret:
                self.width = int(self.current_width * cs.OPT_PROC['k'])
                self.height = int(self.current_height * cs.OPT_PROC['k'])

                MyVideo.frame = cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), (int(self.width), int(self.height)))
            MyVideo.counter = x

    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()


#
# MAIN WINDOW CLASS ====================================================================================================
#
class MainWindow(Win):
    sliders = {}            # settings sliders list
    lines = {}              # actions frames list

    active = True           # state of active update function
    paused = True           # state of catching new video frames in update function
    started = False         # state of started action

    tr = [0]*6              # list, defininng time zone rectangle
    ti = [None]*2           # time start/end image list

    si = None               # temp source image
    ca = None               # current action

#
# Initialization________________________________________________________________________________________________________
#
    def __init__(self, window=tk.Tk(), window_title='Наблюдение за крысами 2.0'):
        Win.__init__(self, window, window_title, True)

        cfg.init_gen_options()
        while not cfg.init_options():
            if not messagebox.askyesno(cs.DIALOG_TITLE_OPEN_VIDEO, cs.DIALOG_TEXT_ANOTHER):
                exit()

        self.ca = tk.StringVar()  # current action
        self.window.focus_force()

        # Init Main Menu
        self.frame_menu = tk.Frame(self.window)
        self.frame_menu.pack(fill=tk.X, side=tk.TOP, pady=5)

        self.menu = ['Помощь', 'Открыть другое видео']
        self.menu_functions = [self.help, self.reload]

        for i in range(len(self.menu)):
            MyButton(self.frame_menu, self.menu[i], self.menu_functions[i], tk.LEFT)
            if self.menu[i].__contains__('Сохранить'):
                self.frame_menu.winfo_children()[i].config(state='disabled')

        # Init Settings
        self.frame_settings = tk.Frame(self.window, bd=1, relief=tk.SOLID)
        self.frame_settings.pack(fill=tk.Y, side=tk.RIGHT)

        # Init Video Frame
        self.vid = MyVideo(cfg.video_name)

        # Pack settings in frame after define real size of video:
        cs.OPT_PROC['width_Max'] = self.vid.width
        cs.OPT_PROC['height_Max'] = self.vid.height
        self.init_slider()

        tk.Frame(self.frame_settings, height=2, bg="black").pack(fill=tk.X, pady=5)

        tk.Label(self.frame_settings, text="Выбор положение разделителя:", font=("Helvetica", 12, 'bold')).pack()
        self.MODES = ['Горизонтально', 'Вертикально']
        self.divider = tk.StringVar()
        self.divider.set(0)

        for text in self.MODES:
            b = tk.Radiobutton(self.frame_settings, text=text, variable=self.divider, value=self.MODES.index(text))
            b.pack(fill=tk.X, padx=10, pady=3)

        # Create a canvas that can fit the above video source size

        self.frame_main = tk.Frame(self.window, bd=1, relief=tk.SOLID)
        self.frame_main.pack()

        self.canvas_source = tk.Canvas(self.frame_main, width=self.vid.width, height=self.vid.height)
        self.canvas_source.pack(side=tk.LEFT)

        self.slider = tk.Scale(self.window, label='Текущий кадр',
                               from_=1, to=self.vid.length, orient=tk.HORIZONTAL,
                               command=lambda x, flag=self.paused: self.vid.set_frame(int(x), flag))

        self.slider.pack(fill=tk.X)
        tk.Frame(self.window, bg="black").pack(fill=tk.X, pady=5)

        # Init Actions
        self.ca.set(-1)
        self.ca.trace("w", lambda name, k, mode, sv=self.ca: self.action_start(sv))

        self.frame_actions = tk.Frame(self.window)
        self.frame_actions.pack(anchor=tk.NW, side=tk.LEFT)

        frame = tk.Frame(self.frame_actions)
        frame.pack(anchor=tk.NW)
        tk.Button(frame, text='Stop (s)', font='Helvetica 16 bold', fg='red',
                  command=lambda sv=self.ca: self.action_stop(sv)).pack(side=tk.LEFT, padx=3, pady=3)

        for i in range(len(cs.ACTIONS)):
            self.lines[i] = tk.Frame(self.frame_actions, bd=1, relief=tk.SUNKEN)
            self.lines[i].pack()
            tk.Radiobutton(self.lines[i], text='Start', font="Helvetica 14", variable=self.ca, value=i, indicatoron=0) \
                .pack(side=tk.LEFT, padx=3, pady=3)
            tk.Label(self.lines[i], text=cs.ACTIONS[i], width=30, font='bold').pack(side=tk.LEFT)

        # flat, groove, raised, ridge, solid, or sunken
        self.frame_time = tk.Frame(self.window, bd=2, relief=tk.RAISED)

        # self.frame_time.pack()
        tk.Canvas(self.frame_time, bg='black').pack(anchor=tk.N)
        tk.Entry(self.frame_time, font="Helvetica 14").pack(anchor=tk.N)
        tk.Canvas(self.frame_time, bg='black').pack(anchor=tk.N)
        tk.Entry(self.frame_time, font="Helvetica 14").pack(anchor=tk.N)
        tk.Button(self.frame_time, text='В отчёт', font='Helvetica 16 bold', fg='red',
                  command=lambda sv=self.ca: self.action_write(sv)).pack(anchor=tk.N)

        # TEST
        self.tr = cs.TIME_AREA
        for i in [0, 2]:
            self.frame_time.winfo_children()[i].config(width=self.tr[4], height=self.tr[5])
        self.ti[0] = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(MyVideo.frame.copy())
                                            .crop(tuple(self.tr[0:4]))
                                            .resize(tuple(self.tr[4:])))
        self.frame_time.pack()

        self.window.bind('<space>', self.pause)
        self.window.bind('<Escape>', self.my_exit)
        self.window.bind('<s>', lambda event, sv=self.ca: self.action_stop(sv))
        self.window.bind('<Left>', self.left)
        self.window.bind('<Right>', self.right)
        self.window.bind('<Button-1>', self.unfocus)
        self.window.bind('<Button-3>', self.unfocus)
        self.window.bind('<Key>', self.action_start_but)
        self.window.bind('<Return>', self.enter)

        self.update()
        self.window.mainloop()

#
# Menu other functions__________________________________________________________________________________________________
#
    def reload(self, name, button):
        self.active = False
        if cfg.init_options():
            self.init_slider(False)
            self.paused = True
            self.vid = MyVideo(cfg.video_name)
            self.slider.set(1)

        self.active = True

    def help(self, name, widget):
        WinHelp(tk.Toplevel(self.window), name, widget)

#
# Event keyboard and mouse functions____________________________________________________________________________________
#
    def enter(self, event):
        print(event.widget)
        if event.widget == self.frame_time.winfo_children()[1]:
            self.frame_time.winfo_children()[3].focus()
        elif event.widget == self.frame_time.winfo_children()[3]:
            self.action_write(self.ca)

    def action_start_but(self, event):
        if not isinstance(event.widget, tk.Entry):
            try:
                self.ca.set(int(event.char)-1)
            except:
                return

    def pause(self, event):
        if not isinstance(event.widget, tk.Entry) and not isinstance(event.widget, tk.Button):
            self.paused = not self.paused

    def unfocus(self, event):
        if not isinstance(event.widget, tk.Entry):
            self.window.focus()

    def left(self, event):
        if MyVideo.counter > 0:
            x = MyVideo.counter
            d = cs.OPT_PROC['FrameDelta']
            self.slider.set(x-d)

    def right(self, event):
        if MyVideo.counter < self.vid.length:
            x = MyVideo.counter
            d = cs.OPT_PROC['FrameDelta']
            self.slider.set(x+d)

    def my_exit(self, event):
        if messagebox.askokcancel(cs.DIALOG_TITLE_GENERAL, cs.DIALOG_TEXT_EXIT):
            if not os.path.exists(cfg.options_dir):
                os.makedirs(cfg.options_dir)
            options_name = cfg.options_dir + '/options_' + cfg.video_name[cfg.video_name.rfind('/') + 1:-4] + '.txt'

            f_options = open(options_name, 'w')
            for key in cs.OPT_PROC:
                if not cs.EXCLUDE.__contains__(key):
                    f_options.write('#\nsize ' + key + ' ' + str(cs.OPT_PROC[key]) + '\n\n')
            f_options.close()

            f_options = open('general_options.txt', 'w')
            for key in cfg.topt.keys():
                f_options.write('#\n' + key + " " + str(cfg.topt[key]) + '\n\n')
            f_options.close()
            Win.quit(self)

    def quit(self):
        self.my_exit(0)

#
# Mainframe functions___________________________________________________________________________________________________
#
    # TODO how to save frame
    # cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

    def update(self):
        if not self.active:
            self.window.after(1, self.update)
            return

        if self.paused:
            frame = MyVideo.frame
            ret = True
            delay = 1
        else:
            ret, frame = self.vid.get_frame()
            if not ret:
                print('Something error. ret = False')
            if MyVideo.counter == 0:
                self.paused = True
            self.slider.set(MyVideo.counter)
            delay = cs.OPT_PROC['delay']

        if ret:
            frame1 = frame.copy()[
                     cs.OPT_PROC['y0']:cs.OPT_PROC['y0'] + cs.OPT_PROC['height'],
                     cs.OPT_PROC['x0']:cs.OPT_PROC['x0'] + cs.OPT_PROC['width']]

            if int(self.divider.get()) == 1:
                cv2.line(frame1, (int(np.size(frame1, 0) / 2), 0), (int(np.size(frame1, 0) / 2), int(self.vid.height)),
                         (0, 255, 0), 2)
            else:
                cv2.line(frame1, (0, int(np.size(frame1, 1) / 2)), (int(self.vid.width), int(np.size(frame1, 1) / 2)),
                         (0, 255, 0), 2)

            self.si = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame1))
            self.canvas_source.create_image(
                int(self.vid.width/2),
                int(self.vid.height/2),
                image=self.si, anchor=tk.CENTER)


            # TODO отображение времени
            if self.ti[0] is not None:
                self.ti[1] = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(MyVideo.frame.copy())
                                                    .crop(tuple(self.tr[0:4]))
                                                    .resize(tuple(self.tr[4:])))
                for i in [0, 1]:
                    self.frame_time.winfo_children()[i*2].create_image(0, 0, image=self.ti[i], anchor=tk.NW)

        self.window.after(delay, self.update)

#
# Settings functions____________________________________________________________________________________________________
#

    def init_slider(self, is_new=True):
        for option in cs.OPT_LABELS.keys():
            if is_new:
                self.sliders[option] = MySlider(self.frame_settings, self.ch_proc, option)
            else:
                self.sliders[option].init = False
                self.sliders[option].slider.set(cs.OPT_PROC[option])

    def ch_proc(self, x, name):
        cs.OPT_PROC[name] = x

#
# Action functions______________________________________________________________________________________________________
#
    def action_start(self, var):
        i = int(var.get())

        if not self.tr[4]*self.tr[5] == 0 and 0 <= i < len(cs.ACTIONS):
            print("Actions: " + cs.ACTIONS[i])

            self.ti[0] = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(MyVideo.frame.copy())
                                                .crop(tuple(self.tr[0:4]))
                                                .resize(tuple(self.tr[4:])))
        elif self.tr[4]*self.tr[5] == 0:
            var.set(-1)
            tk.messagebox.showwarning(cs.DIALOG_TITLE_WARNING, cs.DIALOG_TEXT_WARNING_TIME_AREA)

    def action_write(self, var):

        i = int(var.get())

        if 0 <= i < len(cs.ACTIONS):
            widgets = self.frame_time.winfo_children()

            if not os.path.exists(cfg.results_dir):
                os.makedirs(cfg.results_dir)

            results = cfg.results_dir + '/results_' + cfg.video_name[cfg.video_name.rfind('/') + 1:-4] + '.csv'

            if os.path.isfile(results):
                f_options = open(results, 'a')
            else:
                f_options = open(results, 'w')
                f_options.write('Время начала; Время конца; Движение;\n')

            for entry in [widgets[1], widgets[3]]:
                t = entry.get()
                t = t.replace(',', ' ')
                t = t.replace(':', ' ')
                words = t.split(' ')
                print(words)
                if not len(words) == 3 or not words[0].isnumeric() or not words[1].isnumeric or not words[2].isnumeric:
                    tk.messagebox.showwarning(cs.DIALOG_TITLE_WARNING, cs.DIALOG_TEXT_WARNING_TIME)
                    f_options.close()
                    return

                if not 0 <= all(words) <= 59:
                    tk.messagebox.showwarning(cs.DIALOG_TITLE_WARNING, cs.DIALOG_TEXT_WARNING_TIME)
                    f_options.close()
                    return

                f_options.write(words[0]+':'+words[1]+':'+words[2]+';')

            f_options.write(cs.ACTIONS[i]+';\n')
            f_options.close()
            widgets[1].delete(0, tk.END)
            widgets[3].delete(0, tk.END)
            var.set(-1)
            self.window.focus()

        else:
            tk.messagebox.showwarning(cs.DIALOG_TITLE_WARNING, cs.DIALOG_TEXT_WARNING_ACTION)

    def action_stop(self, var):
        if not int(var.get()) == -1:
            self.paused = not self.paused
            self.frame_time.winfo_children()[1].focus()

# Старт программы
MainWindow()
