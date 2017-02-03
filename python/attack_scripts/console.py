from time import sleep
import os


class Console(object):

    @staticmethod
    def color(s, color):
        colors = {
            'blue': '\033[94m',
            'green': '\033[92m',
            'warn': '\033[93m',
            'fail': '\033[91m',
            'end': '\033[0m',
            'bold': '\033[1m',
            'underline': '\033[4m',
        }
        return '%s%s%s' % (colors[color], s, colors['end'])

    @staticmethod
    def prompt(s=''):
        r = raw_input('[?] %s' % s)
        sleep(.1)
        return r

    @staticmethod
    def warn(s):
        print '[!] %s' % s

    @staticmethod
    def inform(s):
        print '[-] %s' % s

    @staticmethod
    def add(s):
        print '[+] %s' % s

    @staticmethod
    def run(s):
        print '[#] %s' % s


@staticmethod
def prompt_folder_name():
    pa = Console.prompt('Enter the project folder: ')
    print ''
    return os.path.abspath(pa)