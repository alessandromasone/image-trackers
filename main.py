#!/usr/bin/python

import argparse
import sys
import requests
from urllib.parse import urlparse

#versione del programma
VERSION = 1.0

#tempo di attesa per ogni controllo e quante volte ripetere (-1 = infinito)
TIME = 5
REPEAT = -1

#controllo dei parametri
def check_argv():
    parser = argparse.ArgumentParser(description="", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + str(VERSION), help="Versione del programma")
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Visualizza i comandi')
    parser.add_argument("-t", help="Ogni quanto controllare", default=TIME, dest="time", type=int)
    parser.add_argument("-r", help="Quante volte controllare", default=REPEAT, dest="repeat", type=int)
    parser.add_argument("url", help="Url da monitorare")
    args = parser.parse_args()
    return args

#controllo url
def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

if __name__ == "__main__":
    argv = check_argv()
    #controllo varoli inserti
    #tempo
    if (int(argv.time) < 5 or int(argv.time) > 2592000):
        print("Il tempo non deve essere minore di 5 o maggiore di 2592000")
        sys.exit()
    #cicli da ripetere
    if (int(argv.repeat) < -1 or int(argv.repeat) > 999999999):
        print("Il numero delle volte da ripete è troppo alto")
        sys.exit()
    #controllo formato dell'url
    if (not is_url(argv.url)):
        print("Il sito sembra non essere valido")
        sys.exit()
    #controllo eisstenza dell'url
    response = requests.get(argv.url)
    if (response.status_code != 200):
        print("Il sito sembra non essere raggiungibile")
        sys.exit()
    #presa dei valori
    time = int(argv.time)
    repeat = int(argv.repeat)
    url = argv.url

