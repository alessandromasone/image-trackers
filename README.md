# Image Trackers

Questo repository contiene uno script Python che permette di monitorare un URL specificato per rilevare cambiamenti in un file (ad esempio, un'immagine) e scaricare la nuova versione quando viene rilevato un cambiamento. Il programma è configurabile tramite la riga di comando e può essere eseguito con diverse opzioni per personalizzare il comportamento.

## Funzionalità

- **Monitoraggio continuo**: Lo script monitorizza un URL specifico per modifiche a un file.
- **Controllo periodico**: È possibile configurare la frequenza con cui il programma controlla l'URL per nuove versioni del file.
- **Supporto per log**: Le attività possono essere registrate in un file di log per tracciare gli eventi.
- **Modalità silenziosa**: È possibile disabilitare la stampa dei messaggi sulla console per l'esecuzione silenziosa.

## Requisiti

- Python 3.x

## Installazione

1. Clona il repository:

```bash
git clone https://github.com/alessandromasone/image-trackers.git
cd image-trackers
```

2. Assicurati di avere Python 3.x installato nel tuo sistema.
3. Installa le librerie necessarie con:

```bash
pip install -r requirements.txt
```

## Uso

### Sintassi della riga di comando

Lo script accetta diversi argomenti tramite la riga di comando:

```bash
python tracker.py [options] <URL>
```

### Opzioni disponibili:

- `-l` : Attiva la registrazione dei log nel file `log.txt`.
- `-t` : Intervallo di tempo tra i controlli (in secondi). Default: `5`. Deve essere compreso tra `5` e `2592000` secondi (30 giorni).
- `-r` : Numero di volte per ripetere il controllo (default: `-1`, che indica un controllo infinito).
- `-e` : Estensione del file da monitorare (opzionale).
- `-f` : Nome personalizzato per il file scaricato (default: `img`).
- `-p` : Nome della cartella di salvataggio (default: `save`).
- `-n` : Disabilita la stampa dei messaggi (modalità silenziosa).
- `<URL>` : L'URL da monitorare per i cambiamenti del file.

### Esempio di uso

```bash
python tracker.py -l -t 10 -r 5 -f "immagine" -p "download" https://picsum.photos/200/200
```

In questo esempio:

- L'URL `https://picsum.photos/200/200` viene monitorato.
- I controlli vengono eseguiti ogni 10 secondi.
- Il file verrà scaricato al massimo 5 volte.
- I file scaricati verranno salvati nella cartella `download` e avranno il nome personalizzato `immagine`.
- I messaggi di log vengono registrati nel file `log.txt`.

### Modalità silenziosa

Per eseguire lo script in modalità silenziosa (senza messaggi nella console), puoi usare l'opzione `-n`:

```bash
python tracker.py -n https://picsum.photos/200/200
```

## Log

Il programma registra gli eventi, come il rilevamento di un nuovo file, nel file `log.txt`. Questo file viene aggiornato ad ogni esecuzione del programma se l'opzione `-l` è attivata.

### Esempio di log

```txt
[12:30:15] Nuova immagine trovata
[12:40:30] Nuova immagine trovata
```

## Preferenze

Le preferenze impostate tramite la riga di comando vengono salvate nel file `preference.json` per consentire la persistenza tra le esecuzioni. Il programma cercherà questo file all'avvio e caricherà le preferenze salvate.

## Funzionamento

1. Lo script verifica la connessione a Internet.
2. Carica le preferenze salvate (se esistono) o ottiene i parametri dalla riga di comando.
3. Monitora l'URL specificato per rilevare cambiamenti nel file.
4. Se un file viene modificato, lo script lo scarica e lo salva nella cartella configurata.
5. Se l'opzione di log è attivata, viene registrato un evento nel file di log.
6. Lo script continua a controllare l'URL secondo l'intervallo di tempo specificato fino a raggiungere il numero di ripetizioni configurato o fino a quando non viene interrotto.

## Licenza

Questo progetto è rilasciato sotto la licenza MIT. Vedi il file [LICENSE](LICENSE) per ulteriori dettagli.