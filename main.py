#!/usr/bin/python

try:
    import argparse
    import sys
    import requests
    import os
    import shutil
    import hashlib
    import glob
    import time
    import tempfile
    import urllib
    from itertools import count
    from urllib.parse import urlparse
    from datetime import datetime
    import atexit
    import urllib.parse
    import urllib.request

except Exception as e:
    print(e.args)
    sys.exit()

#versione del programma
VERSION = 1.5

#tempo di attesa per ogni controllo e quante volte ripetere (-1 = infinito)
STOP = 5
REPEAT = -1

#destinazioni cartelle
PATH_SAVE = 'save'

#formattazione nomi
HOUR_FORMAT = '%Y_%m_%d_%H_%M_%S'
NAME_IMAGE_NOW = 'image.jpg'
LOG_FILE = 'log.txt'

log_choice = False
none_choice = False

#presa dei parametri
def get_argv():
    try:
        parser = argparse.ArgumentParser(description="", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + str(VERSION), help="Versione del programma")
        parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Visualizza i comandi')
        parser.add_argument("-n", action="store_true", dest="none", help="Nessun testo di risposta")
        parser.add_argument("-l", action="store_true", dest="log", help="attivazione dei log")
        parser.add_argument("-t", help="Ogni quanto controllare 5 - 2592000", default=STOP, dest="time", type=int)
        parser.add_argument("-r", help="Quante volte controllare 0 - 999999999", default=REPEAT, dest="repeat", type=int)
        parser.add_argument("url", help="Url da monitorare")
        args = parser.parse_args()
        return args
    except Exception as e:
        log(e.args, log_choice)
        print("Chiusura inaspettata del programma")
        sys.exit()

#controllo dei parametri
def check_argv(argv):

    #controllo del tempo di attesa per ogni esecuzione
    try:
        if (int(argv.time) < 5 or int(argv.time) > 2592000):
            print("Valore tempo non valido") #messaggio di errore
            sys.exit()
        else:
            log("Valore del tempo di attesa per ogni ciclo valido", log_choice) #validazione del tempo eseguita con successo
    except Exception as e:
        log(e.args, log_choice)
        print("Chiusura inaspettata del programma")
        sys.exit()

    #controllo dei cicli da ripetere
    try:
        if (int(argv.repeat) < -1 or int(argv.repeat) > 999999999):
            print("Valore dei cicli non valido") #messaggio di errore
            sys.exit()
        else:
            log("Valore del numero di cicli di controllo valido", log_choice) #validazione numero di cicli di controllo
    except Exception as e:
        log(e.args, log_choice)
        print("Chiusura inaspettata del programma")
        sys.exit()

    #controllo della validità dell'url
    try:
        result = urlparse(argv.url)
        response = requests.get(argv.url)
        if (not all([result.scheme, result.netloc]) or response.status_code != 200):
            print("URL non valido")
        else:
            log("URL valido", log_choice)
    except Exception as e:
        log(e.args, log_choice)
        print("Chiusura inaspettata del programma")
        sys.exit()

#md5 di file
def get_md5(path_file):
    with open(path_file, "rb") as f:
        md5 = hashlib.md5()
        while chunk := f.read(8192):
            md5.update(chunk)
    return md5.hexdigest()

#download immagine
def get_file(url: str, folder: str, name: str):
    
    if (folder != ''):
        if not os.path.exists(folder):
            os.makedirs(folder)
        #os.chdir(folder)
    
    with urllib.request.urlopen(url) as response:
        parsed_url_path = urllib.parse.urlparse(response.url).path
        filename = os.path.basename(parsed_url_path)
        file_extension = os.path.splitext(filename)
        with open(folder + name + file_extension[1], 'w+b') as f:
            shutil.copyfileobj(response, f)
    #print(os.getcwd())
    #if (folder != ''):
        #for i in range(folder.count('/') + 1):
            #os.chdir('../')
    return file_extension[1]

#funzione di log dei messaggi
def log(string, status):
    if(status):
        if (os.path.exists(LOG_FILE)):
            with open(LOG_FILE, 'a') as f:
                f.write('[' + datetime.now().strftime('%H:%M:%S') + '] ' + string)
        else:
            with open(LOG_FILE, 'w') as f:
                f.write('[' + datetime.now().strftime('%H:%M:%S') + '] ' + string)


def main():
    #contorllo argomenti
    argv = get_argv()
    check_argv(argv)
    #associazioni variabili
    stop = int(argv.time)
    repeat = int(argv.repeat)
    url = argv.url
    log_choice = argv.log
    none_choice = not argv.none

    #creazione di una cartella temporanea
    PATH_TEMP = tempfile.mkdtemp()
  
    for i in count(0):
        try:
            exit() if i == repeat else 1 #se raggiunge il numero di cicli indicati

            #download del file temporaneo per il controllo
            temp_name = '/image_' + datetime.now().strftime(HOUR_FORMAT)
            temp_name = '' + temp_name + get_file(url, PATH_TEMP, temp_name)

            #verifica presenza della cartella per il salvataggio
            if not os.path.exists(PATH_SAVE):
                os.makedirs(PATH_SAVE)
            
            #controllo ultimo file salvato
            list_of_files = glob.glob(PATH_SAVE + '/*')
            if (len(list_of_files)):
                latest_file = max(list_of_files, key=os.path.getmtime)
                if (get_md5(PATH_TEMP + temp_name) != get_md5(latest_file)): #se è diverso da quello attuale
                    shutil.copy2(PATH_TEMP + temp_name, PATH_SAVE + temp_name)
                    shutil.copy2(PATH_TEMP + temp_name, NAME_IMAGE_NOW) 
                    if (none_choice):
                        print("Nuova immagine trovata")
            else:
                shutil.copy2(PATH_TEMP + temp_name, PATH_SAVE + temp_name)
                shutil.copy2(PATH_TEMP + temp_name, NAME_IMAGE_NOW)
                if (none_choice):
                    print("Nuova immagine trovata")
                 
            #eliminazione del file di controllo
            if os.path.exists(PATH_TEMP + temp_name):
                os.remove(PATH_TEMP + temp_name)

            #attesa
            time.sleep(stop)

        except Exception as e: #gestione errore
            log(e.args, log_choice)
            print("Chiusura inaspettata del programma")
            print(e.args)
            sys.exit()
        except KeyboardInterrupt: #ctrl + c
            print("Chiusura")
            shutil.rmtree(PATH_TEMP)
            sys.exit()

if __name__ == "__main__":
    main()