import os

from tkinter import filedialog
from collections import OrderedDict

import constants as cs

# Глобальные переменные (инициализация)
# ---------------------------------------------------------------------------------------------------------------
topt = {}
video_name = ''
options_name = ''
options_dir = ''
results_dir = ''

# Options
EXCLUDE = {'delay', 'FrameDelta', 'k'}

opt_labels = {}
opt_process = {}


def init_const():
    global opt_process, opt_labels

    opt_labels = OrderedDict({
        'delay': 'Задержка кадров (в мс)',
        'FrameDelta': 'Следующий кадр',
        'x0': 'Обрезка слева',
        'width': 'Ширина',
        'y0': 'Обрезка сверху',
        'height': 'Высота'
    })

    opt_process = {
        'delay': 1,
        'delay_Max': 500,
        'FrameDelta': 10,
        'FrameDelta_Max': 50,
        'k': 2
}


# Инициализация опций программы (подгрузка из файла)
# ---------------------------------------------------------------------------------------------------------------
def init_general():
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
    global topt, video_name, options_name, options_dir, results_dir, opt_process, opt_labels

    init_const()

    print('Last video folder:', topt['last_video'])
    video_name = filedialog.askopenfilename(initialdir=topt['last_video'],
                                            title=cs.DIALOG_TITLE_OPEN_VIDEO,
                                            filetypes=(("video files", "*.avi *.mp4"), ("all files", "*.*")))

    topt['last_video'] = video_name[:video_name.rfind('/')]

    if video_name == '':
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

            # TODO Для совместимости с предыдущей версией
            if words[0] == "size":
                opt_process[words[1]] = int(words[2])
            else:
                try:
                    opt_process[words[0]] = int(words[1])
                except ValueError:
                    pass
                # except Exception:
                #     pass

        line = file_options.readline()
    file_options.close()

    print(opt_process)
    return True
