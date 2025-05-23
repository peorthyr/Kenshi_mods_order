# Kenshi Mods Order

Analisi dettagliata per sviluppare un programma Python che automatizza l'ordinamento dei mod di Kenshi, evitando conflitti.

## Premesse

Kenshi carica i mod in base a un ordine preciso. Errori nell'ordine causano conflitti.

## 1. Identificazione dei Mod

Il programma opererà su una cartella configurabile contenente i mod di Kenshi.

**Percorso predefinito:**

```
D:\Steam\steamapps\workshop\content\233860
```

Dove `233860` è l'ID Steam di Kenshi. Ogni sottocartella ha nome numerico (ID Steam del mod), ad esempio:

```
D:\Steam\steamapps\workshop\content\233860\705119823
D:\Steam\steamapps\workshop\content\233860\726254871
```

Ogni mod dovrebbe contenere un file `.info` strutturato così:

```xml
<?xml version="1.0"?>
<ModData xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <id>726254871</id>
  <mod>RecruitPrisoners</mod>
  <title>Recruitable Prisoners - with dialogue (pls read description)</title>
  <tags>
    <string>Characters</string>
    <string>Cheats</string>
    <string>Gameplay</string>
  </tags>
  <visibility>0</visibility>
  <lastUpdate>2022-01-25T14:15:04+11:00</lastUpdate>
</ModData>
```

Le `tags` definiscono la categoria.

## 2. File di Ordinamento

I mod vengono ordinati nel file:

```
D:\Steam\steamapps\common\Kenshi\data\mods.cfg
```

**Esempio di contenuto:**

```
Project -Ultimate Anim Patch-.mod
[1]----------[UI, Graphics, Performance]----------.mod
[1.2]--------------------(Graphics).mod
...
[11]----------[Miscellanious]----------.mod
```

## 3. Prerequisiti

Sono necessari:

* Kenshi Load Order Organizer.mod
* Mod "segnaposto" (placeholder) predefiniti:

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

Questi mod fungono da categorie per ordinare gli altri mod ed evitare conflitti. Le categorie principali hanno numeri interi; le sottocategorie hanno numeri decimali.

## 4. Regole di Ordinamento

* Se un mod possiede più tag che corrispondono a più categorie diverse, prevale sempre quella più in basso (numerazione maggiore). Ad esempio, categoria `[8]` prevale su `[2]`, categoria `[3.1]` prevale su `[3]`.
* Se un mod non ha tags (file `.info` mancante, corrotto, oppure elemento tags assente), verrà assegnato all'ultima categoria `[11] Miscellanious`.
* Quando un mod viene inserito in una categoria, sarà collocato immediatamente sotto il relativo segnaposto, spostando verso il basso i mod già presenti.

## 5. Masterlist aggiuntiva (masterlist.json)

* È presente un file aggiuntivo `masterlist.json` che fornisce indicazioni precise sull'ordinamento per alcuni mod identificati dal nome del file `.mod` (non dall'ID).
* La struttura del file `masterlist.json` contiene una lista di categorie numerate (Order) e il nome dei mod che vi appartengono.
* Se un mod è presente in `masterlist.json`, il suo ordinamento deve rispettare esclusivamente la categoria definita dal file. Non è necessario rispettare la posizione interna precisa, il mod deve soltanto apparire nella categoria specificata dal file masterlist.

## 6. Processo di Ordinamento

### Step 1 - Lettura configurazione attuale

* Leggere il contenuto originale di `mods.cfg` e salvare i nomi in un array denominato `nomiModsTestuali`.

### Step 2 - Lettura informazioni dai mod

* Scansionare la cartella dei mod e leggere il file `.info` per ciascun mod.
* Salvare ogni informazione in un oggetto `modInfo`, contenente: nome mod, ID, tags.
* In caso di errori (mancanza o file corrotto), loggare l'errore.

### Step 3 - Creazione lista ordinata

* Creare una lista `modsOrdinati` contenente inizialmente solo i mod segnaposto.
* Per ciascun mod in `nomiModsTestuali`:

  * Verificare se il mod è presente nella `masterlist.json`. Se sì, utilizzare la categoria definita nel file.
  * Altrimenti, verificare se il mod ha tags leggendo da `modInfo`:

    * Se sì, scegliere la categoria con priorità più alta (numerazione più alta).
    * Se no, inserire in `[11] Miscellanious`.
  * Inserire il mod subito sotto al segnaposto della categoria scelta, facendo scalare gli altri mod.
  * Loggare chiaramente l'operazione.

### Step 4 - Gestione aggiunte e rimozioni

* Se nella cartella mod ci sono mod nuovi, non presenti in `mods.cfg`, inserirli in fondo alla categoria di pertinenza (sempre secondo priorità tag o masterlist).
* Se mod sono stati rimossi dalla cartella, eliminarli automaticamente dalla nuova versione di `mods.cfg`.
* Loggare chiaramente ogni inserimento o rimozione.

### Step 5 - Scrittura file ordinato

* Scrivere la lista finale di `modsOrdinati` nel file `mods.cfg`.

## 7. Logging ed Error Handling

Ogni decisione presa (categoria scelta, mod inseriti, rimossi, problemi riscontrati) sarà chiaramente loggata con struttura dettagliata.

