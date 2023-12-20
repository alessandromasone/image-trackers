# Image trackers

Image-trackers è un programma scritto in Python per monitorare e rilevare modifiche in un'immagine accessibile da remoto. Il programma offre funzionalità per il download delle immagini, il calcolo dell'MD5, il controllo delle preferenze, la gestione dei log e altro ancora.

## Utilizzo

È possibile utilizzare il programma tramite riga di comando. Ecco come eseguire il programma:

```
python main.py "url da monitorare"
```

Ad esempio:

```
python main.py "https://source.unsplash.com/random/200x200?sig=1"
```

## Opzioni

Il programma supporta diverse opzioni che possono essere specificate come argomenti sulla riga di comando:

- `-n`: Non mostrare alcun testo di risposta.
- `-l`: Attiva la registrazione dei log.
- `-t <tempo>`: Specifica l'intervallo di tempo in secondi tra ogni controllo (valori validi: da 5 a 2592000).
- `-r <ripetizioni>`: Specifica il numero di volte che il controllo deve essere ripetuto (valori validi: da 0 a 999999999).
- `-e <estensione>`: Specifica un'estensione personalizzata per il file scaricato.
- `-f <nome>`: Specifica un nome personalizzato per il file scaricato.

## Contributi

Sono benvenuti i contributi a questo progetto. Se desideri contribuire, apri una nuova issue o invia una pull request.

## Licenza

Questo progetto è concesso in licenza secondo i termini della licenza [MIT](https://opensource.org/licenses/MIT).

## Note

Questo programma è stato sviluppato come progetto personale e non è affiliato o supportato da alcuna organizzazione o azienda.
