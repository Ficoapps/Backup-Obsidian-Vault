# Obsidian Vault Backup

Applicazione desktop gratuita e open source per Windows che copia un Vault di Obsidian verso una cartella di backup e permette il ripristino nella direzione opposta.

È pensata soprattutto per backup su Dropbox, ma funziona con qualunque cartella locale, disco esterno, NAS montato come unità, OneDrive o altra cartella sincronizzata.

## Versione corrente

**1.0.1**

Questa versione usa un pacchetto Windows portatile `onedir` invece del precedente EXE autoestraente `onefile`. La nuova struttura è più trasparente per Windows 11 e tende a generare meno falsi positivi da parte dei controlli euristici antivirus.

## Download consigliato per Windows 11

Scarica dalla sezione Releases:

    Obsidian-Vault-Backup-v1.0.1-Windows.zip

Release:

https://github.com/Ficoapps/Backup-Obsidian-Vault/releases/tag/v1.0.1

### Avvio

1. Scarica il file ZIP.
2. Fai clic destro sullo ZIP e scegli **Estrai tutto**.
3. Apri la cartella estratta.
4. Avvia `Obsidian-Vault-Backup.exe`.
5. Non spostare soltanto l'EXE: deve rimanere insieme alla cartella `_internal` e agli altri file generati.

Se Windows mostra un avviso SmartScreen perché l'app non è ancora firmata digitalmente, verifica che il file provenga dalla release ufficiale di questo repository. La release include anche `SHA256SUMS.txt` per controllare l'integrità del pacchetto.

## Funzioni

- selezione del percorso del Vault locale
- selezione del percorso della cartella di backup
- copia Vault -> Backup
- ripristino Backup -> Vault
- include anche la cartella nascosta `.obsidian`
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

## Esempio con Dropbox

Vault locale:

    C:\Users\NomeUtente\Documents\Obsidian\Mio Vault

Backup:

    C:\Users\NomeUtente\Dropbox\Backup Obsidian\Mio Vault

## Avvio dal codice

Requisiti:

- Windows 10 o Windows 11
- Python 3.9 o successivo
- Tkinter, normalmente incluso nell'installazione standard di Python per Windows

Per avviare dal codice fai doppio clic su:

    Avvia_Obsidian_Vault_Backup.bat

## Creare il pacchetto Windows

È incluso:

    Build_EXE.bat

Lo script genera:

    dist\Obsidian-Vault-Backup\Obsidian-Vault-Backup.exe

e il pacchetto distribuibile:

    dist\Obsidian-Vault-Backup-v1.0.1-Windows.zip

La build utilizza:

- PyInstaller `--onedir`
- modalità grafica `--windowed`
- UPX disabilitato
- manifest Windows 10/11
- metadati di prodotto e versione

## Build automatica con GitHub Actions

Ad ogni push sul branch `main`, GitHub:

1. prepara Python
2. installa PyInstaller
3. crea la build Windows `onedir`
4. genera il pacchetto ZIP
5. genera il checksum SHA-256
6. pubblica la release `v1.0.1` se non esiste

## SmartScreen e firma digitale

Il packaging più tradizionale riduce i falsi positivi, ma non può eliminare da solo gli avvisi di reputazione di Windows SmartScreen.

Per eliminare in modo affidabile l'avviso di editore sconosciuto è necessaria una firma digitale Code Signing attendibile o una distribuzione tramite un canale firmato, ad esempio Microsoft Store.

## Configurazione

I percorsi selezionati vengono salvati in:

    %APPDATA%\ObsidianVaultBackup\config.json

## Verifica del download

La release include `SHA256SUMS.txt`. È possibile verificare il pacchetto in PowerShell con:

    Get-FileHash .\Obsidian-Vault-Backup-v1.0.1-Windows.zip -Algorithm SHA256

Il valore deve coincidere con quello pubblicato in `SHA256SUMS.txt`.

## Note

Obsidian è un prodotto di Obsidian.md. Questo progetto è indipendente e non è affiliato o approvato da Obsidian.md.
