# Справка
```
slava@slava-Modern-15-A10M:~/MEGA/projects/llll/log_parser$ ./parse 
usage: parse [-h] -lf file [-f YYYY-MM-DD[hh][:mm]:[ss]] [-t YYYY-MM-DD[hh][:mm]:[ss]] [--count COUNT] [-d DOMAINS] [-ua USER_AGENTS] [-i IPS] [-m METHODS] [-w WORKERS] [--json] [--no-hour-statistic] [--no-tops-statistic] [--no-common]
             [--disable parameter]
parse: error: the following arguments are required: -lf/--log-file
```

```
slava@slava-Modern-15-A10M:~/MEGA/projects/llll/log_parser$ ./parse -h
usage: parse [-h] -lf file [-f YYYY-MM-DD[hh][:mm]:[ss]] [-t YYYY-MM-DD[hh][:mm]:[ss]] [--count COUNT] [-d DOMAINS] [-ua USER_AGENTS] [-i IPS] [-m METHODS] [-w WORKERS] [--json] [--no-hour-statistic] [--no-tops-statistic] [--no-common]
             [--disable parameter]

Скрипт для парсинга логов.

optional arguments:
  -h, --help            show this help message and exit
  -lf file, --log-file file
                        Файл с логами Apache
  -f YYYY-MM-DD[ hh][:mm]:[ss], --from YYYY-MM-DD[ hh][:mm]:[ss]
                        Начать анализ с указанного времени и даты: [YYYY-MM-DD hh:mm:ss] YYYY - Год, например 2020. MM - месяц от 01 до 12, DD - день от 01 до 31, hh - час от 00 до 23, mm - минута от 00 до 59, ss - секунда от 00 до 59.
  -t YYYY-MM-DD[ hh][:mm]:[ss], --to YYYY-MM-DD[ hh][:mm]:[ss]
                        Закончить анализ указанным временем и датой: [YYYY-MM-DD hh:mm:ss] YYYY - Год, например 2020. MM - месяц от 01 до 12, DD - день от 01 до 31, hh - час от 00 до 23, mm - минута от 00 до 59, ss - секунда от 00 до
                        59.
  --count COUNT         Количество записей.
  -d DOMAINS, --domain DOMAINS
                        Учитывать в статистике указанные домены.
  -ua USER_AGENTS, --user-agent USER_AGENTS
                        Учитывать в статистике указанные User-Agent.
  -i IPS, --ip IPS      Учитывать в статистике указанные IP отправителя.
  -m METHODS, --method METHODS
                        Учитывать в статистике указанные методы (GET|POST|HEAD|PUT|DELETE|OPTIONS|PATCH).
  -w WORKERS, --workers WORKERS
                        Указывает количество воркеров (потоков), которое будет использоваться приложением.
  --json                Вывод результата в формате JSON
  --no-hour-statistic   Запрещает вывод статистики в виде почасового графика.
  --no-tops-statistic   Запрещает вывод топ COUNT результатов.
  --no-common           Запрещает вывод обобщенных данных.
  --disable parameter   Исключить параметр при подсчете статистики. Возможные параметры: (domains, ip, user-agents, methods, statuses, requests_uri, requests_url) - отвечают за вывод топ COUNT, (total) - общая информация,
                        (hour_statistic) - почасовая статистика, (requests, cp, generation_time, answer_size) - параметры, для рассчета топ значений.
```

# Пример запуска
```
slava@slava-Modern-15-A10M:~/MEGA/projects/llll/log_parser$ python3.8 src/apache-parser.py -lf ~/Нужное/10324.2020-12-20-2020-12-22-bruma-apache-access.log --json > test.txt 2>/dev/null 
```
# Или
```
slava@slava-Modern-15-A10M:~/MEGA/projects/llll/log_parser$ python3.8 src/apache-parser.py -lf ~/Нужное/10324.2020-12-20-2020-12-22-bruma-apache-access.log | less 
```


# Потребление памяти
4 ГБ на 9.1 ГБ лога (24.5 млн записей)

# Проблемы
немного накосячил с обращением к диску (каждая строка = 1 обращение), нужно буферизовать ввод данных.


Установка компилятора и python
```
llll-support@logstorage:~/vart [0] $ for var in $(cat depends.txt); do wget https://mirror.yandex.ru/ubuntu/$var; done
llll-support@logstorage:~/vart [0] $ for var in $(find -name '*deb'); do ar -p $var data.tar.gz | tar zx -C . ;  done
llll-support@logstorage:~/vart [0] $ rm *.deb
llll-support@logstorage:~/vart/usr/bin [0] $ ln -s gcc-4.6 gcc



cd ~/python3
wget ftp://sourceware.org/pub/libffi/libffi-3.2.1.tar.gz
tar -xf libffi-3.2.1.tar.gz && rm libffi-3.2.1.tar.gz && cd libffi-3.2.1/
mkdir ../.local
export PATH=$HOME/vart/usr/bin:$PATH

llll-support@logstorage:~/python3/libffi-3.2.1 [0] $ ./configure --prefix $HOME/python3/.local LDFLAGS="-L/usr/local/lib"
llll-support@logstorage:~/python3/libffi-3.2.1 [0] $ make -j6 && make install
llll-support@logstorage:~/python3/libffi-3.2.1 [0] $ mkdir -p ~/python3/.local/include
llll-support@logstorage:~/python3/libffi-3.2.1 [0] $ cp x86_64-unknown-linux-gnu/include/ffi.h ../.local/include/
llll-support@logstorage:~/python3/libffi-3.2.1 [0] $ cp x86_64-unknown-linux-gnu/include/ffitarget.h ../.local/include/
llll-support@logstorage:~/python3 [0] $ wget https://www.python.org/ftp/python/3.8.8/Python-3.8.8.tgz
llll-support@logstorage:~/python3 [0] $ tar -xf Python-3.8.8.tgz 
llll-support@logstorage:~/python3 [0] $ rm Python-3.8.8.tgz 
llll-support@logstorage:~/python3/Python-3.8.8 [0] $ ./configure --prefix=$HOME/python3/.local LDFLAGS="-L/usr/local/lib"
llll-support@logstorage:~/python3/Python-3.8.8 [0] $ make -j6 && make install


```
