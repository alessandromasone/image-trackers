# Import delle librerie necessarie
import os
import sys
import shutil
import hashlib
import argparse
import requests
import json
import re
import glob
import time
import tempfile
import urllib
from urllib.parse import urlparse
from datetime import datetime
from itertools import count

LOG_FILE = 'log.txt'  # File di log per scrivere gli eventi
SAVE_DATA = 'preference.json'  # File per salvare le preferenze dell'utente

# Funzione per verificare la connessione a Internet
def connected_to_internet(url='http://www.google.com/', timeout=5):
    try:
        requests.head(url, timeout=timeout)  # Esegui una richiesta head al sito per verificare la connessione
        return True
    except requests.ConnectionError:
        print("Controlla la connessione ad internet")  # Messaggio di errore in caso di fallimento
        sys.exit()  # Termina il programma

# Funzione per ottenere i parametri da linea di comando
def get_argv():
    parser = argparse.ArgumentParser(description="Monitor a URL for file changes", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # Aggiunta dei vari argomenti da linea di comando
    parser.add_argument("-l", action="store_true", dest="log", help="Attivazione dei log")
    parser.add_argument("-t", help="Ogni quanto controllare 5 - 2592000", default=5, dest="time", type=int)
    parser.add_argument("-r", help="Quante volte controllare 0 - 999999999", default=-1, dest="repeat", type=int)
    parser.add_argument("-e", help="Tipologia di estensione personale", dest="ext", type=str)
    parser.add_argument("-f", help="Nome custom per il file", default="img", dest="name", type=str)
    parser.add_argument("-p", help="Nome custom per la cartella di salvataggio", default="save", dest="path", type=str)
    parser.add_argument("-n", action="store_true", dest="none", help="Disabilita la stampa dei messaggi (modalità silenziosa)")
    parser.add_argument("url", help="Url da monitorare")
    return parser.parse_args()  # Restituisce gli argomenti passati dall'utente

# Funzione per validare gli argomenti passati
def validate_argv(args):
    if not 5 <= args.time <= 2592000:
        print("Valore tempo non valido")  # Controlla se il tempo è nel range valido
        sys.exit()
    if not -1 <= args.repeat <= 999999999:
        print("Valore dei cicli non valido")  # Controlla se il numero di ripetizioni è valido
        sys.exit()

    parsed_url = urlparse(args.url)
    # Verifica se l'URL è valido
    if not all([parsed_url.scheme, parsed_url.netloc]) or requests.get(args.url).status_code != 200:
        print("URL non valido")  # Se l'URL è non valido o la richiesta non è andata a buon fine
        sys.exit()

    # Verifica la validità dell'estensione, se presente
    if args.ext and (args.ext.count('.') != 1 or not 2 <= len(args.ext) <= 4):
        print("Estensione non valida")
        sys.exit()

    # Verifica che il nome del file non contenga caratteri non validi
    if args.name and re.search(r'[^0-9a-zA-Z]+', args.name):
        print("Il nome inserito non è valido")
        sys.exit()

# Funzione per calcolare l'MD5 di un file
def get_md5(path_file):
    try:
        with open(path_file, "rb") as f:
            md5 = hashlib.md5()
            for chunk in iter(lambda: f.read(8192), b""):
                md5.update(chunk)
        return md5.hexdigest()
    except Exception as e:
        print(f"Errore durante la generazione dell'MD5: {e}")  # Gestione degli errori
        sys.exit()

# Funzione per scaricare un file da un URL
def get_file(url, folder, name, ext=None):
    try:
        os.makedirs(folder, exist_ok=True)  # Crea la cartella di destinazione, se non esiste
        with urllib.request.urlopen(url) as response:
            file_ext = ext or os.path.splitext(os.path.basename(urllib.parse.urlparse(response.url).path))[1]  # Estrai l'estensione del file
            full_path = os.path.join(folder, f"{name}{file_ext}")  # Crea il percorso completo per il file
            with open(full_path, 'wb') as f:
                shutil.copyfileobj(response, f)  # Copia il contenuto del file
        return full_path
    except Exception as e:
        print(f"Errore durante il download del file: {e}")
        sys.exit()

# Funzione per registrare i log, se attivato
def log(message, log_choice):
    if log_choice:
        with open(LOG_FILE, 'a') as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")  # Scrive il messaggio di log

# Funzione per aggiornare il file (copiare il file scaricato nella cartella di destinazione)
def update_file(source, destination, log_choice, none_choice):
    try:
        shutil.copy2(source, destination)  # Copia il file
        if not none_choice:  # Se la modalità silenziosa non è attiva
            print("Nuova immagine trovata")
            log("Nuova immagine trovata", log_choice)  # Log dell'evento
    except Exception as e:
        print(f"Errore durante l'aggiornamento del file: {e}")
        sys.exit()

# Funzione per caricare le preferenze salvate o ottenere i parametri da linea di comando
def load_preferences():
    if os.path.exists(SAVE_DATA):
        with open(SAVE_DATA, 'r') as f:
            data = json.load(f)  # Carica i dati dal file JSON
        data.setdefault("none", False)
        data.setdefault("log", False)
        return argparse.Namespace(**data)  # Restituisce gli argomenti come Namespace
    else:
        args = get_argv()  # Ottieni gli argomenti dalla linea di comando
        with open(SAVE_DATA, 'w') as f:
            json.dump(vars(args), f, indent=4)  # Salva i parametri in un file JSON
        return args

# Funzione principale
def main():
    connected_to_internet()  # Verifica la connessione a Internet

    try:
        args = load_preferences()  # Carica o imposta le preferenze
        validate_argv(args)  # Valida gli argomenti passati

        # Estrai le preferenze per variabili locali
        log_choice, none_choice = args.log, args.none
        ext, name_file = args.ext, args.name
        path_save = args.path
        stop, repeat = args.time, args.repeat

        # Creazione di una cartella temporanea per scaricare i file
        with tempfile.TemporaryDirectory() as temp_dir:
            for i in count():  # Ciclo infinito fino al numero di ripetizioni
                temp_name = os.path.join(temp_dir, f"{name_file}_{datetime.now().strftime('%Y_%m_%d_%H_%M_%S')}")
                downloaded_file = get_file(args.url, temp_dir, temp_name, ext)

                os.makedirs(path_save, exist_ok=True)  # Crea la cartella di salvataggio se non esiste

                # Controlla se ci sono file salvati precedentemente
                saved_files = glob.glob(f"{path_save}/*")
                if saved_files:
                    latest_file = max(saved_files, key=os.path.getmtime)  # Ottieni l'ultimo file modificato
                    if get_md5(downloaded_file) != get_md5(latest_file):  # Confronta l'MD5
                        update_file(downloaded_file, os.path.join(path_save, os.path.basename(downloaded_file)), log_choice, none_choice)
                else:
                    update_file(downloaded_file, os.path.join(path_save, os.path.basename(downloaded_file)), log_choice, none_choice)

                if i == repeat - 1:
                    break  # Esci se il numero di ripetizioni è stato raggiunto
                time.sleep(stop)  # Pausa prima del prossimo controllo
    except KeyboardInterrupt:
        pass  # Gestione dell'interruzione da tastiera
    except Exception as e:
        print(f"Errore: {e}")

# Esegui la funzione principale se il file viene eseguito direttamente
if __name__ == "__main__":
    main()
