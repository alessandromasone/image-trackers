#!/usr/bin/python

#librerie
try:
    import pickle
    import re
    import pathlib
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
except Exception as e:
    print(e.args)
    sys.exit()

#versione del programma
VERSION = 1.7

#tempo di attesa per ogni controllo e quante volte ripetere (-1 = infinito)
STOP = 5
REPEAT = -1

#destinazioni cartelle
PATH_SAVE = 'save'

#formattazione nomi
HOUR_FORMAT = '%Y_%m_%d_%H_%M_%S'
NAME_FILE = 'file'
LOG_FILE = 'log.txt'
SAVE_DATA = 'preference.data'
PATH_TEMP = 'temp'

#scelte utente
log_choice = False
none_choice = False

#controllo connessione ad internet
def connected_to_internet(url='http://www.google.com/', timeout=5):
    try:
        _ = requests.head(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        print("Controlla la connessione ad internet")
        sys.exit()

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
        parser.add_argument("-e", help="Tipologia di estensione personale", dest="ext", type=str)
        parser.add_argument("-f", help="Nome custom per il file", dest="name", type=str)
        parser.add_argument("url", help="Url da monitorare")
        args = parser.parse_args()
        return args
    except Exception as e:
        print(e.args)
        sys.exit()

#controllo dei parametri
def check_argv(argv):

    #controllo del tempo di attesa per ogni esecuzione
    try:
        if (int(argv.time) < 5 or int(argv.time) > 2592000):
            log("Valore tempo non valido", log_choice)
            print("Valore tempo non valido") #messaggio di errore
            sys.exit()
        log("Valore del tempo di attesa per ogni ciclo valido", log_choice) #validazione del tempo eseguita con successo
    except Exception as e:
        log(e.args, log_choice)
        print("Chiusura inaspettata del programma" + e.args)
        sys.exit()

    #controllo dei cicli da ripetere
    try:
        if (int(argv.repeat) < -1 or int(argv.repeat) > 999999999):
            log("Valore dei cicli non valido", log_choice)
            print("Valore dei cicli non valido") #messaggio di errore
            sys.exit()
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
            log("URL non valido", log_choice)
            print("URL non valido") #messaggio di errore
            sys.exit()
        log("URL valido", log_choice) #validazione url eseguita con successo
    except Exception as e:
        log(e.args, log_choice)
        print("Chiusura inaspettata del programma")
        sys.exit()

    #controllo dell'estensione
    try:
        if ((argv.ext != None) and ((argv.ext.count('.') != 1 or (len(argv.ext) > 3 and len(argv.ext) < 2)))):
            print("Estenzione non valida") #messaggio di errore
            sys.exit()
        log("Estenzione valida", log_choice) #validazione dell'estenzione eseguita con successo
    except Exception as e:
        log(e.args, log_choice)
        print("Chiusura inaspettata del programma")
        sys.exit() 

    #controllo del nome personalizzato
    try:
        if (argv.name != None):
            regexp = re.compile('[^0-9a-zA-Z]+')
            if regexp.search(argv.name):
                print("Il nome inserito non è valido") #messaggio di errore
                sys.exit() 
        log("Nome valido", log_choice) #validazione del nome personalizzato
    except Exception as e:
        log(e.args, log_choice)
        print("Chiusura inaspettata del programma")
        sys.exit() 

#md5 del file
def get_md5(path_file):
    try:
        with open(path_file, "rb") as f:
            md5 = hashlib.md5()
            while chunk := f.read(8192):
                md5.update(chunk)
        log("md5 eseguito con successo", log_choice) #md5 eseguito con successo
        return md5.hexdigest()
    except Exception as e:
        log(e.args, log_choice)
        print("Chiusura inaspettata del programma")
        sys.exit()

#download file
def get_file(url: str, folder: str, name: str, ext):
    try:
        if (folder != ''): #se la cartella non esiste
            if not os.path.exists(folder):
                os.makedirs(folder)
                log("Creazione della cartella " + folder, log_choice)
        with urllib.request.urlopen(url) as response: #download del file come richiesta
            parsed_url_path = urllib.parse.urlparse(response.url).path
            filename = os.path.basename(parsed_url_path)
            file_extension = os.path.splitext(filename)
            file_ext = ext if (ext != None) else file_extension[1]
            with open(folder + name + file_ext, 'w+b') as f: #salvataggio nella cartella di destinazione
                shutil.copyfileobj(response, f)
        log("File scaricato con successo", log_choice)
        return name + file_ext
    except Exception as e:
        log(e.args, log_choice)
        print("Chiusura inaspettata del programma")
        sys.exit()

#funzione di log dei messaggi
def log(string, status):
    try:
        if(status):
            mode = 'a' if (os.path.exists(LOG_FILE)) else 'w' #se non è creato provvede a creare il file
            with open(LOG_FILE, mode) as f:
                    f.write('[' + datetime.now().strftime('%H:%M:%S') + '] ' + string + '\n')
    except Exception as e:
        log(e.args, log_choice)
        print("Chiusura inaspettata del programa")
        sys.exit()

def main():
    #blocco connessione internet
    try:
        connected_to_internet() #controllo connessione ad internet
    except Exception as e:
        print(e.args)
        sys.exit()
    #blocco controllo preference
    try:
        #verifica delle preferenze
        if len(sys.argv) == 1 and os.path.exists(SAVE_DATA): #se è presente il file di preferenze
            with open(SAVE_DATA, 'rb') as f:
                argv = pickle.load(f)
        else: #se non è presente un file preferenze
            argv = get_argv()
        check_argv(argv) #controllo della valità dei parametri
        #salvataggio dei parametri
        with open(SAVE_DATA, 'wb') as f:
            pickle.dump(argv, f)
    except Exception as e:
        print(e.args)
        sys.exit()
    try:
        #associazioni variabili
        stop = int(argv.time)
        repeat = int(argv.repeat)
        url = argv.url
        log_choice = argv.log
        none_choice = not argv.none
        ext = argv.ext
        name_file = str(argv.name) if argv.name else NAME_FILE
        PATH_TEMP = tempfile.mkdtemp() #creazione cartella temporanea
        log("Variabili associate correttamente", log_choice)
    except Exception as e:
        log(e.args, log_choice)
        print("Chiusura inaspettata del programma")
        sys.exit()
    try:
        for i in count(0):
            try:
                #download del file temporaneo per il controllo
                temp_name = '/' + name_file + '_' + datetime.now().strftime(HOUR_FORMAT)
                temp_name = get_file(url, PATH_TEMP, temp_name, ext)
                log("Nome del file generato correttamente", log_choice)

                #verifica presenza della cartella per il salvataggio
                if not os.path.exists(PATH_SAVE):
                    os.makedirs(PATH_SAVE)
                    log("Cartella per il salvataggio dello storico dei file", log_choice)
                
                #avvio ciclo immagini
                list_of_files = glob.glob(PATH_SAVE + '/*')
                if (len(list_of_files)): #se è presente una cartella con i salvataggi precedenti
                    latest_file = max(list_of_files, key=os.path.getmtime)
                    if (get_md5(PATH_TEMP + temp_name) != get_md5(latest_file)): #se è diverso da quello attuale
                        shutil.copy2(PATH_TEMP + temp_name, PATH_SAVE + temp_name)
                        shutil.copy2(PATH_TEMP + temp_name, name_file + pathlib.Path(temp_name).suffix) 
                        if (none_choice):
                            print("Nuova immagine trovata (" + str(i + 1) + ")")
                            log("Nuova immagine trovata", log_choice)
                else: #primo avvio del programma
                    shutil.copy2(PATH_TEMP + temp_name, PATH_SAVE + temp_name)
                    shutil.copy2(PATH_TEMP + temp_name, name_file + pathlib.Path(temp_name).suffix) 
                    if (none_choice):
                        print("Nuova immagine trovata (" + str(i + 1) + ")")
                        log("Nuova immagine trovata", log_choice)
                    
                #eliminazione del file di controllo
                if os.path.exists(PATH_TEMP + temp_name):
                    os.remove(PATH_TEMP + temp_name)
                    log("Pulizia dei file temporanei", log_choice)

                exit() if i == repeat-1 else 1 #se raggiunge il numero di cicli indicati

                #attesa
                time.sleep(stop)
            except Exception as e: #gestione errore
                log(e.args, log_choice)
                shutil.rmtree(PATH_TEMP)
                print("Chiusura inaspettata del programma")
                sys.exit()
    except Exception as e: #gestione errore
        log(e.args, log_choice)
        shutil.rmtree(PATH_TEMP)
        print("Chiusura inaspettata del programma")
        print(e.args)
        sys.exit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(e.args, log_choice)
        print("Chiusura inaspettata del programma" + e.args)
        sys.exit()
    except KeyboardInterrupt: #ctrl + c
        shutil.rmtree(PATH_TEMP)
        sys.exit()