import os
import xml.etree.ElementTree as ET
import json
import logging

# Configurazione logging
logging.basicConfig(
    filename="auto_order.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Percorsi
MODS_FOLDER = r"D:\Steam\steamapps\workshop\content\233860"
MODS_CFG = r"D:\Steam\steamapps\common\Kenshi\data\mods.cfg"
MASTERLIST_FILE = "masterlist.json"
# Percorso locale per la scrittura
LOCAL_MODS_CFG_PATH = os.path.join(os.path.dirname(__file__), "mods_local_auto.cfg")

# Categorie predefinite
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

def read_masterlist():
    """Legge il file masterlist.json."""
    if not os.path.exists(MASTERLIST_FILE):
        logging.warning(f"Masterlist non trovata: {MASTERLIST_FILE}")
        return {}
    with open(MASTERLIST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def read_mod_info(mod_folder):
    """Legge il file .info di un mod e restituisce un dizionario con i dati."""
    info_file = os.path.join(mod_folder, "mod.info")
    if not os.path.exists(info_file):
        logging.warning(f"File .info mancante per il mod: {mod_folder}")
        return None
    try:
        tree = ET.parse(info_file)
        root = tree.getroot()
        tags = [tag.text for tag in root.find("tags")] if root.find("tags") else []
        return {
            "id": root.find("id").text,
            "name": root.find("mod").text,
            "tags": tags
        }
    except Exception as e:
        logging.error(f"Errore nella lettura del file .info: {info_file} - {e}")
        return None

def categorize_mod(mod_info, masterlist):
    """Determina la categoria di un mod."""
    if mod_info["name"] in masterlist:
        return masterlist[mod_info["name"]]
    for category in reversed(CATEGORIES):
        if any(tag in category for tag in mod_info["tags"]):
            return category
    return "[11]----------[Miscellanious]----------.mod"

def read_current_mods_cfg():
    """Legge il file mods.cfg e restituisce una lista di mod."""
    if not os.path.exists(MODS_CFG):
        logging.warning(f"File mods.cfg non trovato: {MODS_CFG}")
        return []
    with open(MODS_CFG, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines()]

def write_new_mods_cfg(mods_ordered):
    """Scrive il nuovo file mods.cfg."""
    with open(LOCAL_MODS_CFG_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(mods_ordered))
    logging.info(f"File mods.cfg aggiornato con successo.")

def main():
    # Lettura configurazioni attuali
    current_mods = read_current_mods_cfg()
    masterlist = read_masterlist()

    # Lettura informazioni mod
    mods_info = []
    for mod_id in os.listdir(MODS_FOLDER):
        mod_folder = os.path.join(MODS_FOLDER, mod_id)
        if os.path.isdir(mod_folder):
            mod_info = read_mod_info(mod_folder)
            if mod_info:
                mods_info.append(mod_info)

    # Creazione lista ordinata
    mods_ordered = CATEGORIES.copy()
    for mod_info in mods_info:
        category = categorize_mod(mod_info, masterlist)
        index = mods_ordered.index(category) + 1
        mods_ordered.insert(index, mod_info["name"] + ".mod")

    # Rimozione duplicati e scrittura file
    mods_ordered = list(dict.fromkeys(mods_ordered))  # Rimuove duplicati mantenendo l'ordine
    write_new_mods_cfg(mods_ordered)

if __name__ == "__main__":
    main()