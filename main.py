#Masone Alessandro
import requests
import hashlib
import shutil
import os
import time
import sys
from datetime import datetime


#controllo del parametro di avvio
if (sys.argv[1] == 'help' or sys.argv[1] == '-h'):
    print('Utilizzo: ' + sys.argv[0] + " <link dell'immagine>")
    exit(0)

#passaggio del link attraverso il passaggio si parametri
link = sys.argv[1]

#nome temporaneo per il controllo
name_temp = ''
path_temp = 'temp/'

#nome dell'immagine da salvare
name_save = ''
path_save = 'save/'

#nome dell'immagine nella home
image_view_name = 'image.jpg'

#tempo di attesa per il contorllo
time_check = 5


#funzione di debug dei messaggi
def debug(string, status = True):
    if(status):
        print('[' + datetime.now().strftime('%H:%M:%S') + '] ' + string)

#controlo con md5 del file
def get_hash(img_path):
    with open(img_path, "rb") as f:
        img_hash = hashlib.md5()
        while chunk := f.read(8192):
            img_hash.update(chunk)
    debug('Hash ' + img_path + ' = ' + img_hash.hexdigest())
    return img_hash.hexdigest()

#download dell'immagine per il controllo
def get_image(image_url, path):
    img_data = requests.get(image_url).content
    with open(path, 'wb') as handler:
        handler.write(img_data)
    debug('Download immagine dal link ' + image_url)

#loop del programma
while True:
    #controllo esistenza cartella temp
    if not os.path.exists(path_temp):
        os.makedirs(path_temp)
        debug('Creazione cartella ' + path_temp)

    #creazione del nome dell'immagine temporanea per il controllo e download
    name_temp = 'image_' + datetime.now().strftime('%Y_%m_%d_%H_%M_%S') + '.jpg'
    get_image(link, path_temp + name_temp)

    #se non esiste un immagine
    if (name_save == ''):
        name_save = name_temp
        shutil.copy2(path_temp + name_temp, image_view_name)
        debug('Copia ' + path_temp + name_temp + ' in ' + image_view_name)
    #controllo se è una nuova immagine
    elif (get_hash(path_temp + name_temp) != get_hash(image_view_name)):
        #salvataggio nell'immagine
        debug('Nuova immagine trovata')
        name_save = name_temp
        #controllo esistenza cartella save
        if not os.path.exists(path_save):
            os.makedirs(path_save)
            debug('Creazione cartella save')
        shutil.copy2(image_view_name, path_save + name_save)
        debug('Copia ' + image_view_name + ' in ' + path_save + name_save)
        shutil.copy2(path_temp + name_temp, image_view_name)
        debug('Copia ' + path_temp + name_temp + ' in ' + image_view_name)

    #pulizia file temporanei
    if os.path.exists(path_temp + name_temp):
        os.remove(path_temp + name_temp)

    #attesa ciclo
    time.sleep(time_check)
