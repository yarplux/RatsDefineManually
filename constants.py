TIME_AREA = [208, 0, 310, 24, 200, 50]

VERSION = 'simple_2.1'

TEXT_HELP = 'ESC - выход\n\n' + \
            'F1 - Помощь\n\n' + \
            'F2 - Открыть видео\n\n' + \
            'Пробел - пауза\n\n' + \
            '↑ (↓) - увеличить(уменьшить) скорость\n\n' + \
            '← (→) - перемотка\n\t(работает на паузе)\n\n' + \
            '-/+/del - уменьшить/увеличить/сбросить\n\tобщий счётчик пересечений\n\n' + \
            '1/2/3 - уменьшить/увеличить/сбросить\n\tсчётчик полных пересечений\n\n' + \
            'При выделенном текстовом работают не все клавиши управления!\n' + \
            'ПКМ в любой точке - сбросить фокус с текстового поля\n\n' + \
            'Enter - записать текущее время и состояние счётчиков на отправку в файл\n' + \
            '\t(сохраняется в файл по кнопке сохранить, ' + \
            'открытии нового видео или корректном выходе из программы)\n\n' + \
            'Ctrl+z - отмена последнего изменения счётчика / формы для журнала'


FILE_OPTIONS_FOLDER = './general_options.txt'
FILE_OPTIONS_DEFAULT = './options.txt'
FILE_HELP = './README.txt'

DIALOG_TITLE_OPEN_VIDEO = 'Выберете файл видео'
DIALOG_TITLE_GENERAL = 'Обработка'
DIALOG_TITLE_WARNING = 'Уведомление'

DIALOG_TEXT_WARNING_TIME_AREA = 'Выберете область расположения времени в кадре'
DIALOG_TEXT_WARNING_TIME = 'Введите корректное время (формат: ЧАСЫ МИНУТЫ СЕКУНДЫ)'
DIALOG_TEXT_WARNING_ACTION = 'Выберете фиксируемое движение'

DIALOG_TEXT_EXIT = 'Вы действительно хотите выйти?'
DIALOG_TEXT_ANOTHER = 'Вы хотите выбрать другой файл?'

DIALOG_TEXT_SAVE_TRACK = 'Cохранить текущий трек?'
DIALOG_TEXT_SAVE_OPTIONS = 'Cохранить текущие настройки обработки видео?'
DIALOG_TEXT_SAVE_GENERAL = 'Cохранить текущие общие настройки ( + текущий список движений)?'
DIALOG_TEXT_SAVE_OPTIONS_DEFAULT = 'Сохранить как настройки обработки по-умолчанию?'

DIALOG_TEXT_ERROR_VERSION = 'Файл опций старой версии. Загружены настройки по-умолчанию'

DIR_OPTIONS = './options'
DIR_TRACKS = './tracks'
DIR_RESULTS = './results'

