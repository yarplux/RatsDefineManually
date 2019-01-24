
TIME_AREA = [208, 0, 310, 24, 200, 50]

FILE_OPTIONS_FOLDER = './general_options.txt'
FILE_OPTIONS_DEFAULT = './options.txt'

DIALOG_TITLE_OPEN_VIDEO = 'Выберете файл видео'
DIALOG_TITLE_GENERAL = 'Обработка'
DIALOG_TITLE_WARNING = 'Уведомление'

DIALOG_TEXT_ERROR_OPEN_FILE = 'Для работа необходимо выбрать файл!'
DIALOG_TEXT_WARNING_TIME_AREA = 'Выберете область расположения времени в кадре'
DIALOG_TEXT_WARNING_TIME = 'Введите корректное время (формат: ЧАСЫ МИНУТЫ СЕКУНДЫ)'
DIALOG_TEXT_WARNING_ACTION = 'Выберете фиксируемое движение'

DIALOG_TEXT_EXIT = 'Вы действительно хотите выйти?'
DIALOG_TEXT_ANOTHER = 'Вы хотите выбрать другой файл?'

DIALOG_TEXT_SAVE_TRACK = 'Cохранить текущий трек?'
DIALOG_TEXT_SAVE_OPTIONS = 'Cохранить текущие настройки обработки видео?'
DIALOG_TEXT_SAVE_GENERAL = 'Cохранить текущие общие настройки ( + текущий список движений)?'
DIALOG_TEXT_SAVE_OPTIONS_DEFAULT = 'Сохранить как настройки обработки по-умолчанию?'

DIR_OPTIONS = './options'
DIR_TRACKS = './tracks'
DIR_RESULTS = './results'

# Options
EXCLUDE = {'delay', 'FrameDelta', 'k'}

OPT_LABELS = {
 'delay': 'Задержка кадров (в мс)',
 'FrameDelta': 'Следующий кадр',
 'x0': 'Обрезка слева',
 'width': 'Ширина',
 'y0': 'Обрезка сверху',
 'height': 'Высота'
}

OPT_PROC = {
 'delay': 1, 'delay_Max': 500,
 'FrameDelta': 10, 'FrameDelta_Max': 50,
 'k': 2
}

ACTIONS = [
# 'Движение без смещения',
# 'Смещение (сек.)',
# 'Вращение (шт.)',
# 'Перебежки (сек.)',
# 'Встаёт на задние лапы (шт.)',
# 'Пьёт (время, шт.)',
# 'Ест (время, шт.)'
]