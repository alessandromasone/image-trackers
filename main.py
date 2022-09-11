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
    try:
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
    except ValueError:
        print("Errore durante la sezione parametri")
        sys.exit()

#controllo dei parametri
def check_argv(argv):
    #controllo valori inserti

    #controllo del tempo di esecuzione
    try:
        if (int(argv.time) < 5 or int(argv.time) > 2592000):
            print("Il tempo non deve essere minore di 5 o maggiore di 2592000") #messaggio di errore
            debug("Valore del tempo non valido", debug_choice)
            sys.exit()
        else:
            debug("Valore del tempo valido", debug_choice) #validazione del tempo eseguita con successo
    except ValueError:
        print("Errore durante la sezione controllo del tempo di durata")
        sys.exit()



    #controllo dei cicli da ripetere
    try:
        if (int(argv.repeat) < -1 or int(argv.repeat) > 999999999):
            print("Il numero dei cicli di controllo immessi è maggiore di quello permesso") #messaggio di errore
            debug("Valore dei cicli non valido", debug_choice)
            sys.exit()
        else:
            debug("Valore del numero di cicli di controllo è valido", debug_choice) #validazione dell'input del numero di cicli di controllo
    except ValueError:
        print("Errore durante l'analisi dei cicli di controllo")
        sys.exit()



    #controllo formato testuale dell'url
    if (is_url(argv.url)):
        debug("l'Url inserito sembra essere in un formato valido", debug_choice)
    else:
        print("Il sito inserito non sembra essere un url")
        debug("l'Url inserito non sembra essere in un formato valido", debug_choice)
        sys.exit()



    #controllo se l'url è raggiungibile
    try:
        response = requests.get(argv.url)
        if (response.status_code != 200):
            print("Sito non raggiungibile inserirne uno raggiungibile") #messaggio di errore
            debug("Non è possibile stabilire una connessione con l'url inserito", debug_choice)
            sys.exit()
        else:
            debug("Url validato correttamente", debug_choice) #validazione dell'input dell'url
    except:
        print("L'url sembra non essere raggiungibile o non valido")
        sys.exit()

#controllo url
def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
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