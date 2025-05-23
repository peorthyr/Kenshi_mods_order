# Kenshi Mods Order 

Analisi completa per sviluppare un programma Python che automatizzi l'ordinamento dei mod di Kenshi, evitando conflitti.

## Premesse 
Kenshi carica i mod seguendo un ordine definito in un file specifico. Un ordine scorretto genera conflitti e problemi di compatibilità.

## Identificazione e Raccolta dati dei Mod 
Il programma lavora su una cartella configurabile contenente tutti i mod di Kenshi scaricati da Steam Workshop.
Percorso predefinito della cartella Steam:

D:\Steam\steamapps\workshop\content\233860 
In questa cartella ci sono sottocartelle numerate con l’ID del mod, ad esempio:

D:\Steam\steamapps\workshop\content\233860\705119823 D:\Steam\steamapps\workshop\content\233860\726254871 All'interno di ogni sottocartella (ID del mod) ci sono due file di interesse:

nomeDelMod.mod

_nomeDelMod.info

Dove nomeDelMod.mod è esattamente lo stesso nome presente nel file mods.cfg.

Struttura del file .info:

```xml
<mod>
    <id>726254871</id>
    <name>RecruitPrisoners</name>
    <tags>
        <tag>Characters</tag>
        <tag>Gameplay</tag>
    </tags>
    <version>0</version>
    <date>2022-01-25T14:15:04+11:00</date>
</mod>
```
Le tags definiscono le categorie di appartenenza.

File di Ordinamento L'ordine di caricamento mod è definito nel file:
D:\Steam\steamapps\common\Kenshi\data\mods.cfg 

Esempio contenuto di mods.cfg:

```
Project -Ultimate Anim Patch-.mod
[1]----------[UI, Graphics, Performance]----------.mod
[1.2]--------------------(Graphics).mod
Nightvision+.mod
...
[11]----------[Miscellanious]----------.mod

## 3. Prerequisiti Necessari per funzionare:

Kenshi Load Order Organizer.mod

Mod "segnaposto" (placeholder), che identificano le categorie e sotto-categorie di ordinamento.

Elenco placeholder:

```
[1]----------[UI, Graphics, Performance]----------.mod
[1.2]--------------------(Graphics).mod
[1.3]--------------------(Performance).mod
[2]----------[Animations]----------.mod
[3]----------[New Races, Race edit, Cosmetics]----------.mod
[4]----------[Game Starts, Minor NPC, Animals]----------.mod
[5]----------[Faction edits, Minor Faction, Bounties]----------.mod
[6]----------[Buildings]----------.mod
[7]----------[Armor & Weapons]----------.mod
[8]----------[Overhauls & World Changes]----------.mod
[8.1]--------------------(Combat).mod
[9]----------[Patches]----------.mod
[9.2]--------------------(Animation Patches).mod
[10]----------[Economy]----------.mod
[11]----------[Miscellanious]----------.mod
```
Questi mod segnaposto servono da riferimenti per ordinare gli altri mod ed evitare conflitti.

## Priorità di Ordinamento

Se un mod ha più tags appartenenti a categorie differenti, prevale sempre la categoria più "in basso" (numero maggiore). Ad esempio:
[8] prevale su [2]

[3.1] prevale su [3]

Se non è possibile leggere le tags (file .info corrotto o assente), il mod sarà inserito automaticamente nell'ultima categoria [11] Miscellanious.

Ogni mod viene inserito immediatamente sotto al segnaposto della categoria selezionata, facendo scalare di posizione i mod già presenti.

Masterlist (masterlist.json) Esiste un file aggiuntivo masterlist.json contenente ulteriori informazioni di ordinamento per alcuni mod identificati dal nome del file .mod.
Il file masterlist.json contiene una lista di categorie numerate (Order) e i nomi esatti dei mod che devono appartenere a quella categoria.

Se un mod è presente nella masterlist.json, l'ordinamento rispetta esclusivamente la categoria specificata in questo file. Non è necessario rispettare la posizione precisa all'interno della categoria, solo la categoria stessa.

Processo dettagliato di Ordinamento 
## Step 1 – Lettura mods.cfg Leggere mods.cfg salvando i nomi originali in un array nomiModsTestuali.

## Step 2 – Lettura informazioni mod e creazione database locale Scansionare le sottocartelle dei mod.

Per ogni cartella, leggere il file .mod e _*.info.

Creare un oggetto dati per ogni mod contenente:

id: ID Steam (dalla cartella)
nome_mod: Nome del file .mod
file_info: Nome file .info
cartella: Percorso completo della cartella mod
tags: Tags ottenute dal file .info
in_masterlist: booleano che indica presenza in masterlist.json

Salvare queste informazioni in un "database" locale (ad esempio un file mods_db.json) per accesso rapido nei successivi riavvii.

## Step 3 – Creazione lista ordinata finale (con uso DB locale)
Per ogni mod presente nell'array nomiModsTestuali:

Controlla il Database Locale:

Se il mod non è presente nel database locale:

Controlla la masterlist.json.

Se è nella masterlist:

inserisci il mod sotto la categoria indicata dalla masterlist.

salva questa informazione (categoria della masterlist e flag in_masterlist = True) nel DB locale.

Se non è nemmeno nella masterlist:

leggi il file .info se disponibile per ricavare le tags, altrimenti assegnalo alla categoria [11] Miscellanious.

Salva tutte queste informazioni (tags, categoria selezionata, flag in_masterlist = False) nel DB locale.

Se il mod è già presente nel database locale:

Controlla se ha il flag in_masterlist impostato su True:

Se sì, utilizza direttamente la categoria salvata nel database locale.

Se in_masterlist è False:

Utilizza le informazioni sulle tags presenti nel database locale per determinare la categoria.

Inserisci il mod immediatamente sotto il segnaposto della categoria selezionata, spostando gli altri mod verso il basso.

Logga chiaramente ogni decisione, evidenziando se la scelta è stata fatta usando il DB locale, masterlist o nuova lettura del file .info.

## Step 4 – Gestione aggiunte e rimozioni
Mod nuovi: Se ci sono mod nella cartella Steam assenti in mods.cfg, inserirli alla fine della categoria corretta (seguendo sempre le regole precedenti).

Mod rimossi: Mod rimossi dalla cartella Steam vanno automaticamente eliminati da mods.cfg.

Loggare ogni aggiunta e rimozione chiaramente.

## Step 5 – Scrittura mods.cfg
Salvare la lista finale ordinata modsOrdinati nel file mods.cfg.

Logging ed Error Handling Tutte le operazioni (letture, inserimenti, rimozioni, errori) devono essere chiaramente loggate in un file o console per facilitare manutenzione e debug.