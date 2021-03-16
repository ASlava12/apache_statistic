date_desc = "\n\tYYYY - Год, например 2020.\n\tMM - месяц от 01 до 12,\n\tDD - день от 01 до 31,\n\thh - час от 00 до 23,\n\tmm - минута от 00 до 59,\n\tss - секунда от 00 до 59."

reference = (
    (
        ['-lf','--log-file'], 
        {
            'type': str, 
            'metavar': 'file', 
            'action': 'append',
            'help': 'Файл с логами Apache',
            'required': True
        }
    ),
    (
        ['-f', '--from'], 
        {
            'type': str, 
            'dest': 'from_date', 
            'help': 'Начать анализ с указанного времени и даты: [YYYY-MM-DD hh:mm:ss] {}'.format(date_desc),
            'metavar': 'YYYY-MM-DD[ hh][:mm]:[ss]'
        }
    ),
    (
        ['-t', '--to'], 
        {
            'type': str, 
            'dest': 'to_date', 
            'help': 'Закончить анализ указанным временем и датой: [YYYY-MM-DD hh:mm:ss] {}'.format(date_desc),
            'metavar': 'YYYY-MM-DD[ hh][:mm]:[ss]'
        }
    ),
    (
        ['--count'], 
        {
            'type': int, 
            'dest': 'count', 
            'help': 'Количество записей.',
            'metavar': 'COUNT',
            'default': 10
        }
    ),
    (
        ['-d', '--domain'], 
        {
            'type': str, 
            'dest': 'domains', 
            'action': 'append', 
            'help': 'Учитывать в статистике указанные домены.'
        }
    ),
    (
        ['-ua', '--user-agent'], 
        {
            'type': str, 
            'dest': 'user_agents', 
            'action': 'append', 
            'help': 'Учитывать в статистике указанные User-Agent.'
        }
    ),
    (
        ['-i', '--ip'], 
        {
            'type': str, 
            'dest': 'ips', 
            'action': 'append', 
            'help': 'Учитывать в статистике указанные IP отправителя.'
        }
    ),
    (
        ['-m', '--method'], 
        {
            'type': str, 
            'dest': 'methods', 
            'action': 'append', 
            'help': 'Учитывать в статистике указанные методы (GET|POST|HEAD|PUT|DELETE|OPTIONS|PATCH).'
        }
    ),
    (
        ['-w', '--workers'], 
        {
            'type': int, 
            'dest': 'workers', 
            'help': 'Указывает количество воркеров (потоков), которое будет использоваться приложением.',
            'default': 6
        }
    ),
    (
        ['--json'], 
        {
            'action': "store_true", 
            'dest': "as_json", 
            'help': "Вывод результата в формате JSON",
            'default': False
        }
    ),
    (
        ['--no-hour-statistic'], 
        {
            'action': "store_true", 
            'dest': "no_hour_statistic", 
            'help': "Запрещает вывод статистики в виде почасового графика.",
            'default': False
        }
    ),
    (
        ['--no-tops-statistic'], 
        {
            'action': "store_true", 
            'dest': "no_tops_statistic", 
            'help': "Запрещает вывод топ COUNT результатов.",
            'default': False
        }
    ),
    (
        ['--no-common'], 
        {
            'action': "store_true", 
            'dest': "no_common", 
            'help': "Запрещает вывод обобщенных данных.",
            'default': False
        }
    ),
    (
        ['--disable'], 
        {
            'type': str, 
            'metavar': 'parameter', 
            'action': 'append', 
            'dest': 'parameter',
            'help': 'Исключить параметр при подсчете статистики. Возможные параметры: (domains, ip, user-agents, methods, statuses, requests_uri, requests_url) - отвечают за вывод топ COUNT, (total) - общая информация, (hour_statistic) - почасовая статистика, (requests, cp, generation_time, answer_size) - параметры, для рассчета топ значений. ',
        }
    )
)