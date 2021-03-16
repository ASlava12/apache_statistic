import re
import logging
import gzip

from os.path import getsize
from math import floor
from datetime import datetime

DATE_FORMAT_LOG = r'[%d/%b/%Y:%H:%M:%S %z]'
COMPRESS_RATIO_GZ = 5.4

def parse(part):
    """
        Получает на вход файл (file) и какую его часть анализировать (part). Вернет генератор для обхода файла.

        Вызов генератора вернет структуру.

        Структура, представлена в виде словаря:

            **domain** (String) - доменное имя
            **remoteIP** (String) -  IP адрес обратившегося к контенту сайта
            **userAuth** (String) - (%u) имя пользователя при HTTP аутентификация
            **time** (unix timestamp) - время обращения, смотри [https://linux-notes.org/rabota-s-unix-timestamp-time-na-python/](https://linux-notes.org/rabota-s-unix-timestamp-time-na-python/)
            **method** (String) - [метод HTTP](https://ru.wikipedia.org/wiki/HTTP#Методы), используемый при обращении к серверу
            [**URI**](https://ru.wikipedia.org/wiki/URI) (String)
            **protocol** (String) - [HTTP протокол](https://ru.wikipedia.org/wiki/HTTP)
            **response_status** (int) - [код ответа сервера](https://ru.wikipedia.org/wiki/Список_кодов_состояния_HTTP)
            **response_size** (int) - Размер ответа в байтах, 0 - не было данных (в логах "-"
            **referer** (String) - [Источник запроса](https://ru.wikipedia.org/wiki/HTTP_referer)
            **user_agent** (String) - [описание клиентского приложения](https://ru.wikipedia.org/wiki/User_agent)
            **request_service_time** (int) - Время, затраченное на обслуживание запроса, в микросекундах (10  ^ -6).
            **user_time** (int) - Пользовательское время (модуль mod_log_rusage)
            **kernel_time** (int) - Время ядра (модуль mod_log_rusage).
    """
    file = part[0]
    logging.debug('Enter File: {file} in part {part}'.format(file=file, part=part[1:]))

    if file[-3:] == '.gz':
        f = gzip.open(file, 'rb')
        isgzip = True
    else:
        f = open(file)
        isgzip = False

    f.seek(part[1])
    # Исключаем дублирование
    row = '-'
    if part[1] != 0:
        if isgzip:
            row = f.readline().decode()
        else:
            row = f.readline()

    while part[2] != -1 and f.tell() <= part[2] or part[2] == -1 and row != '':
        if isgzip: # без символа \n
            row = f.readline().decode()[:-1]
        else:
            row = f.readline()[:-1]
        
        try:
            split1 = row.split('\"')
            split2 = split1[0].split(' ')
            split3 = split1[1].split(' ')
            split4 = split1[2].split(' ')
            split5 = re.split(' |:',split1[6])
            uri = ' '.join(split3[1:-1])
            uri_pos = uri.find('?')
            yield {
                'domain': split2[0],
                'remoteIP': split2[1],
                'userAuth': split2[-4] if split2[-4] != '-' else None,
                'time': datetime.strptime(' '.join(split2[-3:-1]), DATE_FORMAT_LOG).timestamp(), # В секундах
                'method': split3[0],
                'URI': uri[:uri_pos if uri_pos != -1 else len(uri)],
                'protocol': split3[-1],
                'response_status': split4[1],
                'response_size': int(split4[2]) if split4[2] != '-' else 0,
                'referer': split1[3],
                'user_agent': split1[5],
                'request_service_time': int(split5[1]),
                'user_time': int(split5[2]),
                'kernel_time': int(split5[3]),
            }
        except Exception as e:
            logging.warning('String not processed in {file} / {part}. String content: \"{row}\". Exception: {exc}'.format(file=file, part=part[1:], row=row, exc=e))

    f.close()

def split_parts(file: str, parts) -> list:
    """
        Разбивает файл на части для дальнейшего использования в анализе. Часть представляет собой кортеж из двух чисел: 
            (from, to):
                from - начальный байт строки
                to - конечный
        Некоторые условности: 
             0 - обозначает начало файла
            -1 - обозначает конец файла
    """
    # Выставляем коэффициент сжатия
    if len(file) > 3 and file[-3:] == '.gz':
        compress_ratio = COMPRESS_RATIO_GZ
    else:
        compress_ratio = 1
    # Размер части
    part_size = floor(getsize(file) * compress_ratio / parts)
    # Список, содержащий кортежы частей для анализа
    return [(file, x*part_size, (x+1)*part_size if x+1 != parts else -1) for x in range(parts)]