import tkinter as tk
from tkinter import messagebox
from collections import OrderedDict

import os

from PIL import Image, ImageTk, ImageDraw

import constants as cs
import config as cfg

from ui_wrapper_classes import Win, WinText, MySlider, MyText
from video_wrapper_class import MyVideo


class MainWindow(Win):
    sliders = {}            # settings sliders list
    lines = {}              # actions frames list

    paused = True           # state of catching new video frames in update function
    started = False         # state of started action

    ti = [None]*2           # time start/end image list
    si = None               # temp source image
    ca = None               # current action

    command_stack = []

    def __init__(self, window=tk.Tk(), window_title='Наблюдение за крысами'):
        Win.__init__(self, window, window_title, True)

        cfg.init_general()

        while not cfg.init_options():
            if not messagebox.askyesno(cs.DIALOG_TITLE_OPEN_VIDEO, cs.DIALOG_TEXT_ANOTHER):
                exit()

        self.ca = tk.StringVar()  # current action
        self.window.focus_force()

        # Init Settings
        self.frame_settings = tk.Frame(self.window, bd=1, relief=tk.SOLID)
        self.frame_settings.pack(fill=tk.Y, side=tk.RIGHT)

        # Init Video Frame
        self.vid = MyVideo(cfg.video_name)

        # Pack settings in frame after define real size of video:
        cfg.opt_process['width_Max'] = self.vid.width
        cfg.opt_process['height_Max'] = self.vid.height
        self.init_settings_sliders()

        tk.Frame(self.frame_settings, height=2, bg="black").pack(fill=tk.X, pady=5)

        tk.Label(self.frame_settings, text="Выбор положение разделителя:", font=("Helvetica", 12, 'bold')).pack()
        self.MODES = ['Горизонтально', 'Вертикально']
        self.divider = tk.StringVar()

        for text in self.MODES:
            b = tk.Radiobutton(
                self.frame_settings,
                text=text,
                variable=self.divider,
                value=self.MODES.index(text),
                command=self.ch_divider)
            b.pack(fill=tk.X, padx=10, pady=3)

        # Create a canvas that can fit the above video source size

        frame = tk.Frame(self.window)

        text = tk.Text(frame, bg=self.window.cget('bg'), width=55, wrap=tk.WORD)
        text.insert(1.0, cs.TEXT_HELP)
        text.pack(side=tk.LEFT, fill=tk.Y)

        self.frame_main = tk.Frame(frame, bd=1, relief=tk.SOLID)
        self.frame_main.pack()

        frame.pack(anchor=tk.N, fill=tk.X)

        self.canvas_source = tk.Canvas(self.frame_main, width=self.vid.width, height=self.vid.height)
        self.canvas_source.pack(side=tk.LEFT)

        self.slider = tk.Scale(self.window, label='Текущий кадр',
                               from_=1, to=self.vid.length, orient=tk.HORIZONTAL,
                               command=lambda x: self.ch_frame(x))
        self.slider.pack(fill=tk.X)

        self.divider.set(0)

        frame_time = tk.Frame(self.window)

        frame = tk.Frame(frame_time, bd=2, relief=tk.RAISED)
        self.text_journal = MyText(frame, '', '', 60, 6)
        frame.pack(anchor=tk.NE, side=tk.RIGHT)

        self.canvas_time = tk.Canvas(frame_time, bg='black', width=cs.TIME_AREA[4], height=cs.TIME_AREA[5])
        self.canvas_time.pack()

        frame = tk.Frame(frame_time)
        tk.Label(frame, text='Всего пересечений:', font="Helvetica 14").pack(side=tk.LEFT)
        self.counter1 = tk.Label(frame, text='0', font="Helvetica 14")
        self.counter1.pack(side=tk.RIGHT)
        frame.pack()

        frame = tk.Frame(frame_time)
        tk.Label(frame, text='Полных пересечений:', font="Helvetica 14").pack(side=tk.LEFT)
        self.counter2 = tk.Label(frame, text='0', font="Helvetica 14")
        self.counter2.pack(side=tk.RIGHT)
        frame.pack()

        frame = tk.Frame(frame_time)
        tk.Label(frame, text='Час (напр. 22):', font="Helvetica 14").pack(side=tk.LEFT)
        self.entry_time = tk.Entry(frame, font="Helvetica 14", width=4)
        self.entry_time.delete(0, tk.END)

        if 'hour' in cfg.opt_process:
            self.entry_time.insert(0, cfg.opt_process['hour'])

        else:
            self.entry_time.insert(0, 22)

        self.entry_time.pack(side=tk.RIGHT)

        frame.pack()
        tk.Button(frame_time, text='Сохранить', bd=1, font="Helvetica 14", command=lambda : self.save_journal()).pack(pady=3)
        frame_time.pack()

        #
        # Binding keys _________________________________________________________________________________________________
        #
        self.window.bind('<Escape>', self.my_exit)
        self.window.bind('<F1>', lambda event, c='<F1>': self.help(event, c))
        self.window.bind('<F2>', self.reload)

        self.window.bind('<space>', self.pause)

        self.window.bind('<Left>', self.left)
        self.window.bind('<Right>', self.right)
        self.slider.config(label=self.slider.cget('label') + ' (Left/Right)')

        self.window.bind('<Up>', self.up)
        self.window.bind('<Down>', self.down)
        self.sliders['FrameDelta'].set_label(self.sliders['FrameDelta'].get_label()+' (Up/Down)')

        self.window.bind('<Button-1>', self.unfocus)
        self.window.bind('<Button-3>', self.unfocus)

        # Bindings for counter 1
        self.window.bind('<minus>', lambda event, w=self.counter1, c='<minus>': self.minus(event, w, c))
        self.window.bind('<plus>', lambda event, w=self.counter1, c='<plus>': self.plus(event, w, c))
        self.window.bind('<equal>', lambda event, w=self.counter1, c='<plus>': self.plus(event, w, c))

        self.window.bind('<Delete>', lambda event, w=self.counter1, c='<Delete>': self.clear(event, w, c))
        self.window.bind('<period>', lambda event, w=self.counter1, c='<Delete>': self.clear(event, w, c))

        # Bindings for counter 2
        self.window.bind('1', lambda event, w=self.counter2, c='1': self.minus(event, w, c))
        self.window.bind('2', lambda event, w=self.counter2, c='2': self.plus(event, w, c))
        self.window.bind('3', lambda event, w=self.counter2, c='3': self.clear(event, w, c))

        self.window.bind('<Return>', self.enter)

        self.window.bind('<Control-z>', self.undo)
        self.init_settings_state()
        self.update()
        self.next_loop()
        self.window.mainloop()



#
# Menu other functions__________________________________________________________________________________________________
#
    def reload(self, event):
        self.paused = True

        self.save_journal()
        self.save_options()

        if cfg.init_options():
            self.init_settings_sliders(False)
            self.init_settings_state()

            self.vid = MyVideo(cfg.video_name)
            self.slider.config(to=self.vid.length)

            self.update()

    def help(self, event, command):
        f = open(cs.FILE_HELP, 'r')
        text = f.read()
        f.close()
        WinText(tk.Toplevel(self.window), 'Помощь', self.window, command, self.help, text, 155)

#
# Event keyboard and mouse functions____________________________________________________________________________________
#
    def undo(self,event):
        if self.command_stack.__len__() > 0:
            last = self.command_stack.pop()
            if last[0] in ['<plus>', '<minus>']:
                value = int(self.counter1.cget('text'))+last[1]
                self.counter1.config(text=str(value))
            if last[0] == '<Delete>':
                self.counter1.config(text=str(last[1]))
            if last[0] in ['1', '2']:
                value = int(self.counter2.cget('text'))+last[1]
                self.counter2.config(text=str(value))
            if last[0] == '3':
                self.counter2.config(text=str(last[1]))
            if last[0] == '<Return>':
                self.entry_time.delete(0, tk.END)
                self.entry_time.insert(0, str(last[1]))
                self.counter1.config(text=str(last[2]))
                self.counter2.config(text=str(last[3]))
                self.text_journal.remove_last_line()


    def pause(self, event):
        if not isinstance(event.widget, tk.Entry) and not isinstance(event.widget, tk.Button):
            self.paused = not self.paused

    def unfocus(self, event):
        if not isinstance(event.widget, tk.Entry):
            self.window.focus()

    def left(self, event):
        if (event.state != 0) and not isinstance(event.widget, tk.Entry):
            if MyVideo.counter > 0:
                x = MyVideo.counter
                d = cfg.opt_process['FrameDelta']
                self.slider.set(x-d)

    def right(self, event):
        if (event.state != 0) and not isinstance(event.widget, tk.Entry):
            if MyVideo.counter < self.vid.length:
                x = MyVideo.counter
                d = cfg.opt_process['FrameDelta']
                self.slider.set(x+d)

    def plus(self, event, widget, command):
        if not isinstance(event.widget, tk.Entry):
            self.command_stack.append([command, -1])
            value = int(widget.cget('text')) + 1
            # if widget is self.counter2:
            #     self.counter1.config(text=str(int(self.counter1.cget('text'))+1))

            widget.config(text=str(value))

    def minus(self, event, widget, command):
        if not isinstance(event.widget, tk.Entry):
            self.command_stack.append([command, 1])
            value = int(widget.cget('text')) - 1
            if value >= 0:
                # if widget is self.counter2:
                #     self.counter1.config(text=str(int(self.counter1.cget('text')) - 1))

                widget.config(text=str(value))

    def clear(self, event, widget, command):
        if not isinstance(event.widget, tk.Entry):
            value = int(widget.cget('text'))
            self.command_stack.append([command, value])
            # if widget is self.counter2:
            #     value = int(self.counter1.cget('text'))-value
            #     self.counter1.config(text=str(value if value > 0 else 0))

            widget.config(text='0')

    def enter(self, event):
        if not isinstance(event.widget, tk.Entry):
            text = self.text_journal.T.get(1.0, tk.END)
            hour = int(self.entry_time.get())
            hour1 = '0' + str(hour) if hour < 10 else str(hour)
            hour2 = '0' + str(hour+1) if hour+1 < 10 else str(hour+1)

            if hour2 == '24':
                hour2 = '00'

            text = text \
                + hour1 + '; '\
                + hour2 + '; ' \
                + str(self.counter1.cget('text')) + '; ' \
                + str(self.counter2.cget('text')) + ';'

            self.entry_time.delete(0, tk.END)
            self.entry_time.insert(0, hour2)

            self.text_journal.add(text)

            self.command_stack.append(['<Return>',
                                       hour,
                                       self.counter1.cget('text'),
                                       self.counter2.cget('text')])

            self.counter1.config(text='0')
            self.counter2.config(text='0')

        else:
            self.window.focus()

    def up(self, event):
        if event.state != 0:
            self.sliders['FrameDelta'].set(self.sliders['FrameDelta'].get()+1)

    def down(self, event):
        if event.state != 0:
            self.sliders['FrameDelta'].set(self.sliders['FrameDelta'].get()-1)

    def save_journal(self, dir=None, name=None):
        if dir is None:
            dir = cfg.results_dir

        if name is None:
            name=cfg.video_name


        if not os.path.exists(dir):
            os.makedirs(dir)

        results_name = dir + '/results_' + name[name.rfind('/') + 1:-4] + '.csv'
        print(results_name)

        f = open(results_name, 'w')
        f.write(self.text_journal.T.get(1.0, tk.END).rstrip('\n'))
        f.close()

    def save_options(self, dir=None, name=None):
        if dir is None:
            dir = cfg.options_dir

        if name is None:
            name = cfg.video_name

        if not os.path.exists(dir):
            os.makedirs(dir)
        options_name = dir + '/options_' + name[name.rfind('/') + 1:-4] + '.txt'

        f_options = open(options_name, 'w')

        cfg.opt_process['counter'] = self.vid.counter
        cfg.opt_process['hour'] = self.entry_time.get()
        cfg.opt_process['divider'] = int(self.divider.get())
        cfg.opt_process['counter1'] = self.counter1.cget('text')
        cfg.opt_process['counter2'] = self.counter2.cget('text')

        for key in cfg.opt_process:
            if not cfg.EXCLUDE.__contains__(key):
                f_options.write('#\n' + key + ' ' + str(cfg.opt_process[key]) + '\n\n')
        f_options.close()

        f_options = open('general_options.txt', 'w')
        for key in cfg.topt.keys():
            f_options.write('#\n' + key + " " + str(cfg.topt[key]) + '\n\n')
        f_options.close()

    def my_exit(self, event):
        pause = self.paused
        self.paused = True
        if messagebox.askokcancel(cs.DIALOG_TITLE_GENERAL, cs.DIALOG_TEXT_EXIT):
            self.save_journal()
            self.save_options()
            Win.quit(self)

        else:
            self.paused = pause

    def quit(self):
        self.my_exit(0)

#
# Mainframe functions___________________________________________________________________________________________________
#
    def next_loop(self):
        if not self.paused:
            self.update()
        self.window.after(cfg.opt_process['delay'], self.next_loop)

    def update(self):
        if not self.paused:
            ret, frame = self.vid.get_frame()
            self.slider.set(MyVideo.counter)
        else:
            ret = True
            frame = self.vid.frame

        if MyVideo.counter == 0:
            self.paused = True

        if ret:
            im = Image.fromarray(frame[
                                 cfg.opt_process['y0']:cfg.opt_process['y0'] + cfg.opt_process['height'],
                                 cfg.opt_process['x0']:cfg.opt_process['x0'] + cfg.opt_process['width']])

            image = ImageDraw.Draw(im)

            if int(self.divider.get()) == 1:
                image.line((im.size[0]/2, 0, im.size[0]/2, im.size[1]), fill=(0, 255, 0, 255), width=2)
            else:
                image.line((0, im.size[1] / 2, im.size[0], im.size[1] / 2), fill=(0, 255, 0, 255), width=2)

            self.si = ImageTk.PhotoImage(image=im)
            self.canvas_source.create_image(
                int(self.vid.width/2),
                int(self.vid.height/2),
                image=self.si, anchor=tk.CENTER)

            self.ti = ImageTk.PhotoImage(image=Image.fromarray(MyVideo.frame.copy())
                                                    .crop(tuple(cs.TIME_AREA[0:4]))
                                                    .resize(tuple(cs.TIME_AREA[4:])))

            self.canvas_time.create_image(0, 0, image=self.ti, anchor=tk.NW)

        else:
            # TODO уведомление пользователя в GUI
            print('Something error. ret = False')
            self.paused = True
            return

# Settings functions____________________________________________________________________________________________________
#
    def ch_frame(self, x):
        if self.paused:
            self.vid.set_frame(int(x))
            self .update()

    def init_settings_sliders(self, is_new=True):
        for option in cfg.opt_labels.keys():
            if is_new:
                self.sliders[option] = MySlider(self.frame_settings, self.ch_proc, option)
            else:
                self.sliders[option].init = False
                self.sliders[option].slider.set(cfg.opt_process[option])

    def init_settings_state(self):

        self.counter1.config(text=cfg.opt_process['counter1'] if 'counter1' in cfg.opt_process else '0')
        self.counter2.config(text=cfg.opt_process['counter2'] if 'counter2' in cfg.opt_process else '0')

        self.divider.set(cfg.opt_process['divider'] if 'divider' in cfg.opt_process else 0)

        self.slider.set(cfg.opt_process['counter'] if 'counter' in cfg.opt_process else 1)

        self.entry_time.delete(0, tk.END)
        self.entry_time.insert(0, str(cfg.opt_process['hour'] if 'hour' in cfg.opt_process else 22))

        results_name = cfg.results_dir + '/results_' + cfg.video_name[cfg.video_name.rfind('/') + 1:-4] + '.csv'
        if not os.path.exists(results_name):
            text = 'Журнал:\n'
            text += 'Файл; ' + cfg.video_name[cfg.video_name.rfind('/') + 1:] + '\n'
            path = cfg.video_name[:cfg.video_name.rfind('/')]
            text += 'Папка; ' + cfg.video_name[path.rfind('/') + 1:cfg.video_name.rfind('/')] + '\n'
            text += '\nОт; До; Пересечений; Полных пересечений;\n---'
        else:
            f = open(results_name, 'r')
            text = f.read()
            f.close()

        self.text_journal.add(text)

    def ch_proc(self, x, name):
        cfg.opt_process[name] = x
        if self.paused and (name != 'delay' and name != 'FrameDelta'):
            self.update()

    def ch_divider(self):
        self.update()


# Старт программы
MainWindow()
