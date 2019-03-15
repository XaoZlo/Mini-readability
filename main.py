import os
import sys
import argparse
import requests
import urllib.parse
from html.parser import HTMLParser


class Main:

    def __init__(self):

        self.cur_dir = os.getcwd()
        self.url = self.get_url_from_argv()
        self.raw_html = self.get_raw_html()
        parser = MyHTMLParser(self.url)
        parser.feed(self.raw_html)
        self.content = parser.article
        print(parser.article)
        pass

    def get_settings(self):
        settings_file = self.cur_dir + '/settings.json'
        if os.path.exists(settings_file):
            with open(settings_file, 'r', encoding='utf-8') as settings:
                print(settings.readline())
        else:
            print('Нет файла настроек!')

    def get_raw_html(self):
        """Юзер агент чтобы сайты не думали что мы робот"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0) Gecko/16.0 Firefox/16.0'
        }

        try:
            response = requests.get(self.url, headers=headers)
            if response.status_code is not 200:
                print("Что-то пошло не так...")
                sys.exit()
            return response.text
        except requests.exceptions.InvalidSchema:
            print('Неправильная ссылка')

    def get_argv(self):
        parser = self.create_argv_parser()
        args = parser.parse_args(sys.argv[1:])
        return args

    def create_argv_parser(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('url', type=str)

        return parser

    def get_url_from_argv(self):
        url = self.get_argv().url
        return url

    def write_to_file(self):

        """Вытаскиваем из ссылки строку после https://"""
        raw_url = urllib.parse.urlparse(self.url)

        raw_path = '%s%s' % (raw_url[1], raw_url[2])

        """Проверяем есть ли название файла"""
        file_batch = os.path.split(raw_path)
        if len(file_batch[1]) == 0:
            raw_path = '%s%s' % (file_batch[0], '.txt')
        else:
            raw_path = '%s%s%s' % (file_batch[0], file_batch[1].split('.')[0], '.txt')
        '''Меняем '/' на '\' '''
        raw_path = raw_path.replace('/', '\\')
        file_path = self.cur_dir + '\\' + raw_path
        dir_name = os.path.dirname(file_path)
        """Проверяем есть ли указанная директория"""
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        with open(file_path, 'w', encoding="utf-8") as file:
            file.write(self.content)


class MyHTMLParser(HTMLParser):

    def __init__(self, url):
        super().__init__()
        self.user = 'x'

        self.article = ''
        self.recording = 0
        self.exclude_flag = 0
        self.paragraph_flag = 0
        self.url_flag = 0
        self.url_to_write = ''
        self.hostname = urllib.parse.urlparse(url)[1]
        self.selectors = {
            'main_content_selector': 'p',
            'nested_selectors': ['p', 'i', 'span', 'a'],
            'title': 'h1',
            'article': 'article',
        }
        self.exclude_selectors = ['header', 'footer']
        pass

    def handle_starttag(self, tag, attrs):
        if tag in self.exclude_selectors:
            self.exclude_flag = 1
            return
        if tag == 'a' and self.recording:
            self.url_flag = 1
            self.url_to_write = attrs[0][1]
            if not urllib.parse.urlparse(self.url_to_write)[1]:
                self.url_to_write = '%s%s' % (self.hostname, self.url_to_write)

        if tag in self.selectors['main_content_selector']:
            self.recording = 1
        else:
            return

    def handle_endtag(self, tag):
        if tag in self.exclude_selectors and self.exclude_flag:
            self.exclude_flag = 0
            return
        if tag == self.selectors['main_content_selector'] and self.recording:
            self.recording -= 1
            self.paragraph_flag = 1

    def handle_data(self, data):
        if self.exclude_flag:
            return
        if self.recording:
            if self.paragraph_flag:
                self.article = '%s%s%s' % (self.article, '\n\n', data)
                self.paragraph_flag = 0
            else:
                self.article = '%s%s' % (self.article, data)
            if self.url_flag:
                self.article = '%s [%s]' % (self.article, self.url_to_write)
                self.url_flag = 0


if __name__ == '__main__':
    main = Main()

    main.write_to_file()
