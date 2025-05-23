import os
import json
import xml.etree.ElementTree as ET
import logging

# Configurazione logging
logging.basicConfig(
    filename="auto_order_1.log",
    level=logging.DEBUG,  # Cambiato a DEBUG per log più dettagliati
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Percorsi predefiniti
MODS_FOLDER = r"D:\Steam\steamapps\workshop\content\233860"
MODS_CFG = r"D:\Steam\steamapps\common\Kenshi\data\mods.cfg"
MASTERLIST_FILE = "masterlist.json"
DB_FILE = "mods_db.json"
LOCAL_MODS_CFG_PATH = os.path.join(os.path.dirname(__file__), "mods_local_auto_1.cfg")

# Categorie segnaposto
CATEGORIES = [
    "[1]----------[UI, Graphics, Performance]----------.mod",
    "[1.2]--------------------(Graphics).mod",
    "[1.3]--------------------(Performance).mod",
    "[2]----------[Animations]----------.mod",
    "[3]----------[New Races, Race edit, Cosmetics]----------.mod",
    "[4]----------[Game Starts, Minor NPC, Animals]----------.mod",
    "[5]----------[Faction edits, Minor Faction, Bounties]----------.mod",
    "[6]----------[Buildings]----------.mod",
    "[7]----------[Armor & Weapons]----------.mod",
    "[8]----------[Overhauls & World Changes]----------.mod",
    "[8.1]--------------------(Combat).mod",
    "[9]----------[Patches]----------.mod",
    "[9.2]--------------------(Animation Patches).mod",
    "[10]----------[Economy]----------.mod",
    "[11]----------[Miscellanious]----------.mod"
]

# Mappatura tra tag e categorie
TAG_TO_CATEGORY = {
    "Buildings": "[6]----------[Buildings]----------.mod",
    "Characters": "[3]----------[New Races, Race edit, Cosmetics]----------.mod",
    "Cheats": "[11]----------[Miscellanious]----------.mod",
    "Clothing/Armour": "[7]----------[Armor & Weapons]----------.mod",
    "Environment/Map": "[8]----------[Overhauls & World Changes]----------.mod",
    "Factions": "[5]----------[Faction edits, Minor Faction, Bounties]----------.mod",
    "GUI": "[1]----------[UI, Graphics, Performance]----------.mod",
    "Gameplay": "[8.1]--------------------(Combat).mod",
    "Graphical": "[1.2]--------------------(Graphics).mod",
    "Items/Weapons": "[7]----------[Armor & Weapons]----------.mod",
    "Races": "[3]----------[New Races, Race edit, Cosmetics]----------.mod",
    "Research": "[10]----------[Economy]----------.mod",
    "Total Overhaul": "[8]----------[Overhauls & World Changes]----------.mod"
}

def load_masterlist():
    """Carica il file masterlist.json."""
    logging.debug("Caricamento del file masterlist.json...")
    if os.path.exists(MASTERLIST_FILE):
        with open(MASTERLIST_FILE, "r", encoding="utf-8") as f:
            masterlist = json.load(f)
            logging.info(f"Masterlist caricata con successo: {len(masterlist)} mod trovati.")
            return masterlist
    logging.warning("Masterlist non trovata. Procedo senza di essa.")
    return {}

def load_database():
    """Carica il database locale dei mod."""
    logging.debug("Caricamento del database locale mods_db.json...")
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            database = json.load(f)
            logging.info(f"Database locale caricato con successo: {len(database)} mod trovati.")
            return database
    logging.warning("Database locale non trovato. Creazione di un nuovo database.")
    return {}

def save_database(database):
    """Salva il database locale dei mod."""
    logging.debug("Salvataggio del database locale mods_db.json...")
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(database, f, indent=4)
    logging.info("Database locale salvato con successo.")

def read_mod_info(mod_folder):
    """Legge il file .info di un mod e restituisce un dizionario con i dati."""
    # Cerca il file .mod nella cartella
    mod_files = [f for f in os.listdir(mod_folder) if f.endswith(".mod")]
    if not mod_files:
        logging.warning(f"Nessun file .mod trovato nella cartella: {mod_folder}")
        return None

    # Costruisce il nome del file .info corrispondente
    mod_file_name = mod_files[0]  # Assume che ci sia un solo file .mod
    info_file_name = f"_{os.path.splitext(mod_file_name)[0]}.info"
    info_file = os.path.join(mod_folder, info_file_name)

    if not os.path.exists(info_file):
        logging.warning(f"File .info non trovato: {info_file}")
        return None

    try:
        # Legge il file .info
        tree = ET.parse(info_file)
        root = tree.getroot()

        # Cerca i tag richiesti
        mod_id = root.find("id").text if root.find("id") is not None else None
        mod_name = (
            root.find("mod").text if root.find("mod") is not None else
            root.find("name").text if root.find("name") is not None else
            root.find("title").text if root.find("title") is not None else None
        )
        tags = [tag.text for tag in root.findall("tags/string")] if root.find("tags") else []

        if not mod_id or not mod_name:
            logging.warning(f"File .info incompleto o non valido: {info_file}")
            return None

        # Aggiunge l'estensione .mod al nome del mod
        mod_name_with_extension = f"{mod_name}.mod"

        mod_info = {
            "id": mod_id,
            "name": mod_name_with_extension,
            "tags": tags
        }
        logging.debug(f"Informazioni lette dal file .info: {mod_info}")
        return mod_info
    except ET.ParseError as e:
        logging.error(f"Errore di parsing XML nel file .info: {info_file} - {e}")
    except Exception as e:
        logging.error(f"Errore nella lettura del file .info: {info_file} - {e}")
    return None

def categorize_mod(mod_info, masterlist):
    """Determina la categoria di un mod."""
    logging.debug(f"Determinazione della categoria per il mod: {mod_info['name']}")
    
    # Controlla se il mod è nella masterlist
    if mod_info["name"] in masterlist:
        category = masterlist[mod_info["name"]]
        logging.info(f"Mod {mod_info['name']} trovato nella masterlist. Categoria: {category}")
        return category
    
    # Cerca la categoria basandosi sui tag
    for tag in mod_info["tags"]:
        if tag in TAG_TO_CATEGORY:
            category = TAG_TO_CATEGORY[tag]
            logging.info(f"Mod {mod_info['name']} categorizzato come: {category} (tag: {tag})")
            return category
    
    # Categoria predefinita se nessun tag corrisponde
    logging.warning(f"Mod {mod_info['name']} non categorizzato. Assegnato a [11] Miscellanious.")
    return "[11]----------[Miscellanious]----------.mod"

def read_current_mods_cfg():
    """Legge il file mods.cfg e restituisce una lista di mod."""
    logging.debug("Lettura del file mods.cfg...")
    if os.path.exists(MODS_CFG):
        with open(MODS_CFG, "r", encoding="utf-8") as f:
            mods = [line.strip() for line in f.readlines()]
            logging.info(f"File mods.cfg letto con successo: {len(mods)} mod trovati.")
            return mods
    logging.warning("File mods.cfg non trovato. Procedo con una lista vuota.")
    return []

def write_new_mods_cfg(mods_ordered):
    """Scrive il nuovo file mods.cfg."""
    logging.debug("Scrittura del nuovo file mods.cfg...")
    with open(LOCAL_MODS_CFG_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(mods_ordered))
    logging.info(f"Nuovo file mods.cfg scritto con successo: {LOCAL_MODS_CFG_PATH}")

def main():
    logging.info("Inizio del processo di ordinamento dei mod...")
    
    # Caricamento dati
    masterlist = load_masterlist()
    database = load_database()
    current_mods = read_current_mods_cfg()

    # Scansione cartella mod
    logging.debug("Scansione della cartella dei mod...")
    mods_info = []
    for mod_id in os.listdir(MODS_FOLDER):
        mod_folder = os.path.join(MODS_FOLDER, mod_id)
        if os.path.isdir(mod_folder):
            mod_info = read_mod_info(mod_folder)
            if mod_info:
                mods_info.append(mod_info)
    logging.info(f"Scansione completata: {len(mods_info)} mod trovati.")

    # Aggiornamento database locale
    logging.debug("Aggiornamento del database locale...")
    for mod_info in mods_info:
        if mod_info["name"] not in database:
            category = categorize_mod(mod_info, masterlist)
            database[mod_info["name"]] = {
                "id": mod_info["id"],
                "name": mod_info["name"],  # Salva il nome del mod
                "tags": mod_info["tags"],
                "category": category,
                "in_masterlist": mod_info["name"] in masterlist
            }
            logging.info(f"Mod aggiunto al database: {mod_info['name']} - Categoria: {category}")

    # Debug: verifica se i mod di mods_local.cfg sono nel database
    for mod_name in current_mods:
        if mod_name not in database:
            logging.warning(f"Mod '{mod_name}' non trovato nel database.")
        else:
            logging.debug(f"Mod '{mod_name}' trovato nel database con categoria: {database[mod_name]['category']}")

    # Creazione lista ordinata
    logging.debug("Creazione della lista ordinata dei mod...")
    mods_ordered = []
    category_to_mods = {category: [] for category in CATEGORIES}

    # Raggruppa i mod per categoria, escludendo i mod segnaposto
    for mod_name in current_mods:
        if mod_name in CATEGORIES:
            logging.debug(f"Mod segnaposto '{mod_name}' ignorato durante il raggruppamento.")
            continue  # Ignora i mod segnaposto
        if mod_name in database:
            category = database[mod_name]["category"]
            if category in category_to_mods:
                category_to_mods[category].append(mod_name)
                logging.debug(f"Mod '{mod_name}' aggiunto alla categoria '{category}'.")
            else:
                logging.warning(f"Categoria '{category}' non trovata per il mod '{mod_name}'.")
        else:
            logging.warning(f"Mod '{mod_name}' non trovato nel database.")

    # Costruisce la lista ordinata
    for category in CATEGORIES:
        mods_ordered.append(category)  # Aggiunge il segnaposto della categoria
        mods_ordered.extend(category_to_mods[category])  # Aggiunge i mod della categoria
        # Output al terminale per verificare il contenuto
        print(f"Categoria: {category}")
        print(f"Mods sotto questa categoria: {category_to_mods[category]}")
        print(f"Lista attuale mods_ordered:\n{mods_ordered}\n")
        logging.debug(f"Categoria: {category} - Mods: {category_to_mods[category]}")

    # Scrittura del file mods.cfg
    write_new_mods_cfg(mods_ordered)

    # Salvataggio database aggiornato
    save_database(database)
    logging.info("Processo completato con successo.")

if __name__ == "__main__":
    main()