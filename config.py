import os

from tkinter import filedialog
from tkinter import messagebox

import constants as cs


# Глобальные переменные (инициализация)
# ---------------------------------------------------------------------------------------------------------------
topt = {}
video_name = ''
options_name = ''
options_dir = ''
results_dir = ''


# Инициализация опций программы (подгрузка из файла)
# ---------------------------------------------------------------------------------------------------------------
def init_gen_options():
    global topt

    file_options = open(cs.FILE_OPTIONS_FOLDER, 'r')
    line = file_options.readline()
    while line:
        if line[0] != '#' and line != "\n":
            line = line.replace('\n', '')
            words = line.split(' ')
            topt[words[0]] = line[len(words[0])+1:]
        line = file_options.readline()
    file_options.close()


def init_options():
    global topt, video_name, options_name, options_dir, results_dir

    print('Last video folder:', topt['last_video'])
    video_name = filedialog.askopenfilename(initialdir=topt['last_video'],
                                            title=cs.DIALOG_TITLE_OPEN_VIDEO,
                                            filetypes=(("video files", "*.avi *.mp4"), ("all files", "*.*")))

    topt['last_video'] = video_name[:video_name.rfind('/')]

    if video_name == '':
        messagebox.showinfo(cs.DIALOG_TITLE_GENERAL, cs.DIALOG_TEXT_ERROR_OPEN_FILE)
        return False

    options_dir = video_name[:video_name.rfind('/')] + cs.DIR_OPTIONS[1:]
    results_dir = video_name[:video_name.rfind('/')] + cs.DIR_RESULTS[1:]

    options_name = options_dir + '/options_' + video_name[video_name.rfind('/') + 1:-4] + '.txt'
    if not (os.path.exists(options_dir) and os.path.isfile(options_name)):
        options_name = cs.FILE_OPTIONS_DEFAULT

    file_options = open(options_name, 'r')
    line = file_options.readline()
    while line:
        if line[0] != '#' and line != "\n":
            line = line.replace('\n', '')
            words = line.split(' ')
            if words[0] == "size":
                cs.OPT_PROC[words[1]] = int(words[2])
        line = file_options.readline()
    file_options.close()

    print(cs.OPT_PROC)
    return True
