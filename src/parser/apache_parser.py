import logging
import plot
import json

from time import time
from multiprocessing import Pool
from prettytable import PrettyTable
from dateutil import parser

from .apache_parser_row import parse,split_parts

SEP1 = '========================================================================================================================'

DATE_ARGS_FORMAT = r'[%Y-%m-%d:%H:%M:%S]'

# Размер окна графика
SIZE_GRAPH = 0.5
try:
    tsz = plot.terminal_size()
except:
    tsz = [200, 50]


class ApacheLog:
    def __init__(self, logfiles: list, workers: int = 6):
        """
        logfiles - список файлов, которые нужно проанализировать.

            workers - указание количества используемых потоков.
        """
        # Фильтрация логов
        self._filter = {
            'domains': [],
            'dest_ip': [],
            'from_date': -1,
            'to_date': -1,
            'methods': [],
            'useragents': [],
        }
        # Список файлов
        self._file_list = logfiles
        # Количество воркеров
        self._workers = workers
        # Что собирать
        self._allowed={
            'domains': True, # Топ доменов
            'ip': True, # Топ IP
            'user-agents': True, # Топ User-Agents
            'methods': True, # Топ методов HTTP
            'statuses': True, # Топ статусов ответа
            'requests_uri': True, # Топ URI
            'requests_url': True, # Топ URL

            'total': True, # Отвечает за подсчет общей статистики

            'hour_statistic': True, # Почасовая статистика

            'requests': True, # Количество запросов всего
            'cp': True, # Нагрузка в минутах процессорного времени
            'generation_time': True, # Время генерации страниц (суммарно)
            'answer_size': True, # Размер ответа в байтах (суммарно)
        }

        self._tops = [
            'domains',
            'ip',
            'user-agents',
            'methods',
            'statuses',
            'requests_uri',
            'requests_url',
        ]

        self._sub_tops = [
            'requests',
            'cp',
            'generation_time',
            'answer_size',
        ]

        self.clear_cache()

    def disable(self, allowed):
        self._allowed[allowed] = False
        return self
    
    def enable(self, allowed):
        self._allowed[allowed] = True
        return self

    def __create_stat(self):
        return {
                'requests': {},
                'cp': {},
                'generation_time': {},
                'answer_size': {},
        }

    def __add_stat(self, name, subname, cp, generation_time, answer_size, requests = 1):
        """
        Добавляет данные в статистику
        """
        if self._allowed[name]:
            if self._allowed['requests']:
                if subname in self._result[name]['requests']:
                    self._result[name]['requests'][subname] += requests
                else:
                    self._result[name]['requests'][subname] = requests
            if self._allowed['cp']:
                if subname in self._result[name]['cp']:
                    self._result[name]['cp'][subname] += cp
                else:
                    self._result[name]['cp'][subname] = cp
            if self._allowed['generation_time']:
                if subname in self._result[name]['generation_time']:
                    self._result[name]['generation_time'][subname] += generation_time
                else:
                    self._result[name]['generation_time'][subname] = generation_time
            if self._allowed['answer_size']:
                if subname in self._result[name]['answer_size']:
                    self._result[name]['answer_size'][subname] += answer_size
                else:
                    self._result[name]['answer_size'][subname] = answer_size
        return self

    def __merge_stat(self, another: dict):
        """
        Объединчяет результаты двух статистик
        """
        for name in another.keys():
            for key in another[name]['requests'].keys():
                self.__add_stat(name, key, another[name]['cp'][key], another[name]['generation_time'][key], another[name]['answer_size'][key], another[name]['requests'][key])
        return self

    def clear_cache(self):
        self._result = {
            'domains': self.__create_stat(),
            'ip': self.__create_stat(),
            'user-agents': self.__create_stat(),
            'methods': self.__create_stat(),
            'statuses': self.__create_stat(),
            'requests_uri': self.__create_stat(),
            'requests_url': self.__create_stat(),
            'hour_statistic': self.__create_stat(),
            'total': self.__create_stat(),
        }
        return self

    def set_statistic(self, statistic: str, status: bool = True):
        """
        Устанавливает вывод статистики (statistic) в значение (status)
        """
        self._allowed[statistic] = status
        return self

    def get_statistic(self, statistic: str) -> bool:
        """
        Выводит значение, установленное для статистики. 
            False - означает, что статистик не будет собираться.
        """
        return self._allowed[statistic]

    def set_filter(self, name, filter):
        """
        Устанавливает фильтру (name) для анализа статистики значение (filter)
        """
        self._filter[name] = filter
        return self

    def get_filter(self, name):
        """
        Выводит значение фильтра (name)
        """
        return self._filter[name]

    def __match_user_agent(self, user_agent: str) -> str:
        for ua in self._filter['useragents']:
            if ua in user_agent:
                return True
        return False

    def _filter_match(self, record):
        """
        Проверка на соответствие фильтру.

        Filters:
            domains
            dest_ip
            from_date
            to_date
            methods
            useragents

            self._filter[]
        """
        return  (self._filter['domains'] == [] or record['domain'] in self._filter['domains']) and \
                (self._filter['dest_ip'] == [] or record['remoteIP'] in self._filter['dest_ip']) and \
                (self._filter['methods'] == [] or record['method'] in self._filter['methods']) and \
                (self._filter['useragents'] == [] or self.__match_user_agent(record['user_agent'])) and \
                (self._filter['from_date'] == -1 or record['time'] >= self._filter['from_date']) and \
                (self._filter['to_date'] == -1 or record['time'] <= self._filter['to_date'])

    def _thread(self, item):
        """
        Поток для подсчета статистики
        item - (path_to_log, from_byte, to_byte)
        """
        for rec in parse(item):
            """
            rec: 
                domain
                remoteIP
                userAuth
                time
                method
                URI
                protocol
                response_status
                response_size
                referer
                user_agent
                request_service_time
                user_time
                kernel_time
            """
            # Нагрузка CP (минуты процессорного времени)
            load = (rec['user_time'] + rec['kernel_time']) / 60000000
            self.__add_stat('total', 'total', load, rec['request_service_time'], rec['response_size'])

            if self._filter_match(rec):
                hh = int((rec['time'] // 3600 ) * 3600)
                self.__add_stat('domains', rec['domain'], load, rec['request_service_time'], rec['response_size'])
                self.__add_stat('ip', rec['remoteIP'], load, rec['request_service_time'], rec['response_size'])
                self.__add_stat('user-agents', rec['user_agent'], load, rec['request_service_time'], rec['response_size'])
                self.__add_stat('methods', rec['method'], load, rec['request_service_time'], rec['response_size'])
                self.__add_stat('statuses', rec['response_status'], load, rec['request_service_time'], rec['response_size'])
                self.__add_stat('requests_uri', rec['URI'], load, rec['request_service_time'], rec['response_size'])
                self.__add_stat('requests_url', rec['domain'] + rec['URI'], load, rec['request_service_time'], rec['response_size'])
                self.__add_stat('hour_statistic', hh, load, rec['request_service_time'], rec['response_size'])

        return self._result

    def calculate(self):
        """
        Запускает подсчет статистики в нескольких потоках. 
        """
        for logfile in self._file_list:
            logging.debug('Open file: {file}'.format(file=logfile))
            # Разбиваем файл на части
            parts = split_parts(logfile, self._workers)

            # self._thread((logfile, 0, -1)) # В одном потоке

            with Pool(self._workers) as pool:
                medium_result = pool.map(self._thread, parts)
                while medium_result != []:
                    self.__merge_stat(medium_result.pop(0))

        return self

    def get_top(self, name, subname, count = 10):
        """
        Получить топ count записей из статистики.

        name - один из self._tops
            domains
            ip
            user-agents
            methods
            statuses
            requests_uri
            requests_url

        subname - один из self._sub_tops
            requests
            cp
            generation_time
            answer_size
        """
        mask = '{:.3f}'
        result = []
        cnt = 0
        for key, val in sorted(self._result[name][subname].items(), key=lambda item: item[1], reverse=True):
            if subname in ['requests']:
                result.append(['{}'.format(val), key])
            elif subname in ['cp']:
                result.append([mask.format(val), key])
            elif subname in ['generation_time']:
                result.append([mask.format(val / self._result[name]['requests'][key] / 1000000), key])
            elif subname in ['answer_size']:
                result.append(['{:.0f}'.format(val / self._result[name]['requests'][key]), key])
            cnt += 1
            if cnt >= count:
                break
        return result

    def get_json(self, count = 10):
        result = {}
        for top in self._tops:
            if self._allowed[top]:
                result[top] = {}
                for sub in self._sub_tops:
                    if self._allowed[sub]:
                        result[top][sub] = self.get_top(top, sub, count)
        return json.dumps(dict(list(result.items()) + list(self._result['hour_statistic'].items())))

    def print_tops(self, count = 10):
        for top in self._tops:
            if self._allowed[top]:
                print('\nTop {} {}\n{}'.format(count, top, SEP1))
                for sub in self._sub_tops:
                    if self._allowed[sub]:
                        table = PrettyTable()
                        table.field_names = [sub, top]
                        table.add_rows(self.get_top(top, sub, count))
                        print('{table}\n\n'.format(table=table))

    def print_common(self):
        if self._allowed['requests']:
            print("Requests count: {}".format(self._result['total']['requests']['total']))
        if self._allowed['cp']:
            print("Total CP: {:.2f}".format(self._result['total']['cp']['total']))
        if self._allowed['generation_time']:
            print("Total generation time {} microseconds".format(self._result['total']['generation_time']['total']))
        if self._allowed['answer_size'] and self._allowed['requests']:
            print("Traffic per request (bytes): {:.0f}, Total: {:.2f} Mb".format(self._result['total']['answer_size']['total'] / self._result['total']['requests']['total'], self._result['total']['answer_size']['total'] / 1024 / 1024))

    def plot(self, subname, per_request = False):
        plot.clear_plot()
        if per_request:
            plot.plot(
                [self._result['hour_statistic'][subname][x] / self._result['hour_statistic']['requests'][x] for x in sorted(self._result['hour_statistic'][subname].keys())],
                #fill=True
                )
        else:
            plot.plot(
                [self._result['hour_statistic'][subname][x] for x in sorted(self._result['hour_statistic'][subname].keys())],
                #fill=True
                )

        plot.width(int(tsz[0] * SIZE_GRAPH))
        plot.height(int(tsz[1] * SIZE_GRAPH))

        plot.nocolor()
        plot.xlabel('hours')
        plot.axes(True, False)
        
        plot.show(tsz)

    def print_hour(self):
        if self._allowed['requests']:
            print("Request statistic:")
            self.plot('requests')
        if self._allowed['cp']:
            print('CP load statistic:')
            self.plot('cp')
        if self._allowed['generation_time']:
            print('Total generation time:')
            self.plot('generation_time')
        if self._allowed['generation_time']:
            print('Generation time per request:')
            self.plot('generation_time', True)
        if self._allowed['answer_size'] and self._allowed['requests']:
            print('Request size:')
            self.plot('answer_size')            
        if self._allowed['answer_size'] and self._allowed['requests']:
            print('Average request size:')
            self.plot('answer_size', True)


class CLIParse(ApacheLog):
    def __init__(self, args):
        super().__init__(args.log_file, args.workers)

        """
        Filters:
            domains
            dest_ip
            from_date
            to_date
            methods
            useragents
        """

        if args.domains is not None:
            for d in args.domains:
                self.set_filter('domains', d)
        
        if args.ips is not None:
            for ip in args.ips:
                self.set_filter('dest_ip', ip)

        if args.methods is not None:
            for m in args.methods:
                self.set_filter('methods', m)

        if args.user_agents is not None:
            for ua in args.user_agents:
                self.set_filter('useragents', ua)

        if args.from_date is not None:
            self.set_filter('from_date', parser.parse(args.from_date).timestamp())

        if args.to_date is not None:
            self.set_filter('to_date', parser.parse(args.to_date).timestamp())

        if args.parameter is not None:
            for param in args.parameter:
                self.disable(param)

        time_start = time()
        self.calculate()
        time_end = time()

        logging.info('Time parse: {:.3f}'.format(time_end - time_start))

        if args.as_json:
            print(self.get_json(args.count))
        else:
            if not args.no_common:
                self.print_common()
            if not args.no_tops_statistic:
                self.print_tops(args.count)
            if not args.no_hour_statistic:
                self.print_hour()
