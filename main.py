#!/usr/bin/python

import argparse
import sys
import requests
import os
import shutil
import hashlib
import glob
import time
from itertools import count
from urllib.parse import urlparse
from datetime import datetime

#versione del programma
VERSION = 1.5

#tempo di attesa per ogni controllo e quante volte ripetere (-1 = infinito)
STOP = 5
REPEAT = -1

#destinazioni cartelle
PATH_TEMP = 'temp/'
PATH_SAVE = 'save/'

#formattazione nomi
HOUR_FORMAT = '%Y_%m_%d_%H_%M_%S'
NAME_IMAGE_NOW = 'image.jpg'

debug_choice = False
none_choice = False

#presa dei parametri
def get_argv():
    parser = argparse.ArgumentParser(description="", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + str(VERSION), help="Versione del programma")
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Visualizza i comandi')
    parser.add_argument("-n", action="store_true", dest="none", help="Nessun testo di risposta")
    parser.add_argument("-d", action="store_true", dest="debug", help="attivazione del debug")
    parser.add_argument("-t", help="Ogni quanto controllare", default=STOP, dest="time", type=int)
    parser.add_argument("-r", help="Quante volte controllare", default=REPEAT, dest="repeat", type=int)
    parser.add_argument("url", help="Url da monitorare")
    args = parser.parse_args()
    return args

#controllo dei parametri
def check_argv(argv):
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

#controllo url
def is_url(url):
    try:
        result = urlparse(url)
        debug("Url valido", debug_choice)
        return all([result.scheme, result.netloc])
    except ValueError:
        debug("Url non valido", debug_choice)
        return False

#controlo con md5 del file
def get_hash(img_path):
    debug("Esecuzione dell'hash", debug_choice)
    with open(img_path, "rb") as f:
        img_hash = hashlib.md5()
        while chunk := f.read(8192):
            img_hash.update(chunk)
    return img_hash.hexdigest()

#download dell'immagine per il controllo
def download_image(image_url, folder, image_name):
    if not os.path.exists(folder):
        debug("Creazione della cartella " + folder, debug_choice)
        os.makedirs(folder)
    img_data = requests.get(image_url).content
    with open(folder + image_name, 'wb') as handler:
        handler.write(img_data)
    debug("immagine scaricata per il controllo", debug_choice)

#funzione di debug dei messaggi
def debug(string, status):
    if(status):
        print('[' + datetime.now().strftime('%H:%M:%S') + '] ' + string)

if __name__ == "__main__":
    save_name = ''
    #controllo argomenti
    argv = get_argv()
    check_argv(argv)
    #presa dei valori
    stop = int(argv.time)
    repeat = int(argv.repeat)
    url = argv.url
    debug_choice = argv.debug
    none_choice = not argv.none

    #esecuzione controllo immagine
    for i in count(0):

        try:
            exit() if i == repeat else 1
            #download immagine
            debug("Inizio analisi", debug_choice)
            temp_name = 'image_' + datetime.now().strftime(HOUR_FORMAT) + '.jpg'
            debug('analisi immagine ' + temp_name, debug_choice)
            if not os.path.exists(PATH_TEMP):
                os.makedirs(PATH_TEMP)
            download_image(url, PATH_TEMP, temp_name)

            if (save_name == ''):
                #se non è presente un immagine precedente nel programma
                shutil.copy2(PATH_TEMP + temp_name, NAME_IMAGE_NOW)
                debug("Copia dell'immagine scaricata nella directory principale", debug_choice)
                if not os.path.exists(PATH_SAVE):
                    debug("Creazione cartella " + PATH_SAVE, debug_choice)
                    os.makedirs(PATH_SAVE)
                    shutil.copy2(PATH_TEMP + temp_name, PATH_SAVE + temp_name)
                else:
                    debug("Controllo file presenti nella cartella " + PATH_SAVE, debug_choice)
                    list_of_files = glob.glob(PATH_SAVE + '*')
                    if (len(list_of_files)):
                        latest_file = max(list_of_files, key=os.path.getmtime)
                        if (get_hash(PATH_TEMP + temp_name) != get_hash(latest_file)):
                            debug("Nuova immagine trovata", none_choice)
                            shutil.copy2(PATH_TEMP + temp_name, PATH_SAVE + temp_name)
                save_name = temp_name
            else:
                #controllo se l'immagine è stata già salvatata
                if not os.path.exists(PATH_SAVE):
                    debug("Creazione cartella " + PATH_SAVE, debug_choice)
                    os.makedirs(PATH_SAVE)
                list_of_files = glob.glob(PATH_SAVE + '*')
                if (len(list_of_files)):
                    latest_file = max(list_of_files, key=os.path.getmtime)
                    if (get_hash(PATH_TEMP + temp_name) != get_hash(latest_file)):
                        shutil.copy2(PATH_TEMP + temp_name, PATH_SAVE + temp_name)
                        shutil.copy2(PATH_TEMP + temp_name, NAME_IMAGE_NOW)
                        debug("Nuova immagine trovata", none_choice)
                debug("Salvataggio immagine " + temp_name, debug_choice)
                save_name = temp_name

            #puliaizia file temporanei
            if os.path.exists(PATH_TEMP + temp_name):
                debug("Eliminazione file di lavoro", debug_choice)
                os.remove(PATH_TEMP + temp_name)

            #attesa
            time.sleep(stop)
        except ValueError:
            continue