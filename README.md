# Obsidian Vault Backup

Applicazione desktop per Windows che copia un Vault di Obsidian verso una cartella di backup e permette anche il ripristino nella direzione opposta.

È pensata soprattutto per backup su Dropbox, ma funziona con qualunque cartella locale, disco esterno, NAS montato come unità, OneDrive o altra cartella sincronizzata.

## Funzioni

- selezione del percorso del Vault locale
- selezione del percorso della cartella di backup
- copia Vault -> Backup
- ripristino Backup -> Vault
- include anche la cartella nascosta .obsidian
- copia solo file nuovi o modificati
- conserva date e metadati dei file quando possibile
- non elimina automaticamente i file presenti solo nella destinazione
- memorizza i due percorsi selezionati
- barra di avanzamento e log
- possibilità di annullare l'operazione
- conferma obbligatoria prima del ripristino
- blocco dei percorsi annidati per evitare copie ricorsive

## Sicurezza

L'app non esegue una sincronizzazione speculare.

- un file presente solo nella destinazione non viene cancellato
- un file presente sia nella sorgente sia nella destinazione può essere sovrascritto se la sorgente contiene una versione diversa
- nel ripristino Backup -> Vault viene sempre richiesta una conferma

Per maggiore sicurezza è consigliato chiudere Obsidian prima di eseguire un backup o un ripristino.

## Requisiti per l'avvio dal codice

- Windows 10 o Windows 11
- Python 3.9 o successivo
- Tkinter, normalmente incluso nell'installazione standard di Python per Windows

## Avvio

1. Scarica il repository.
2. Estrai i file.
3. Fai doppio clic su Avvia_Obsidian_Vault_Backup.bat.
4. Seleziona il Vault locale e la cartella di backup.

I percorsi vengono ricordati automaticamente.

## Esempio con Dropbox

Vault locale:

    C:\Users\NomeUtente\Documents\Obsidian\Mio Vault

Backup:

    C:\Users\NomeUtente\Dropbox\Backup Obsidian\Mio Vault

## Creare l'EXE

È incluso Build_EXE.bat. Facendo doppio clic, PyInstaller viene installato o aggiornato e viene creato:

    dist\Obsidian-Vault-Backup.exe

## Build automatica con GitHub Actions

Ad ogni push sul branch main, e anche manualmente dalla scheda Actions, GitHub:

1. prepara Python
2. installa PyInstaller
3. crea l'EXE Windows
4. carica l'eseguibile come artifact scaricabile

## Configurazione

I percorsi selezionati vengono salvati in:

    %APPDATA%\ObsidianVaultBackup\config.json

## Versione

1.0.0

## Note

Obsidian è un prodotto di Obsidian.md. Questo progetto è indipendente e non è affiliato o approvato da Obsidian.md.
