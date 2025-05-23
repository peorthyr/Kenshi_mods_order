import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime

# Configurazioni
MODS_PATH = r'D:\Steam\steamapps\workshop\content\233860'
MODS_CFG_PATH = r'D:\Steam\steamapps\common\Kenshi\data\mods.cfg'
MASTERLIST_PATH = r'masterlist.json'
LOG_PATH = r'kenshi_mod_sorter.log'

# Percorso locale per la scrittura
LOCAL_MODS_CFG_PATH = os.path.join(os.path.dirname(__file__), "mods_local.cfg")

# Caricamento masterlist
with open(MASTERLIST_PATH, 'r', encoding='utf-8') as file:
    masterlist = json.load(file)

# Inizializza logger
def log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_PATH, 'a', encoding='utf-8') as log_file:
        log_file.write(f'[{timestamp}] {message}\n')

# Leggi mods.cfg
with open(MODS_CFG_PATH, 'r', encoding='utf-8') as file:
    mods_cfg_lines = [line.strip() for line in file if line.strip()]

# Lettura mods
mods_info = {}
for mod_id in os.listdir(MODS_PATH):
    mod_folder = os.path.join(MODS_PATH, mod_id)
    
    # Cerca il file .mod nella cartella
    mod_file = next((f for f in os.listdir(mod_folder) if f.endswith('.mod')), None)
    if not mod_file:
        log(f'Nessun file .mod trovato nella cartella {mod_folder}')
        continue

    # Costruisci il percorso del file .info corrispondente
    info_file_name = f"_{os.path.splitext(mod_file)[0]}.info"
    info_path = os.path.join(mod_folder, info_file_name)

    try:
        # Leggi il file .info
        tree = ET.parse(info_path)
        root = tree.getroot()
        tags = [tag.text for tag in root.find('tags').findall('string')]
        mod_name = root.find('mod').text + '.mod'
        mods_info[mod_name] = tags
    except FileNotFoundError:
        log(f'File .info non trovato: {info_path}')
    except Exception as e:
        log(f'Errore lettura info per mod {mod_file}: {str(e)}')

# Ordina inizialmente i segnaposto
sorted_mods = [line for line in mods_cfg_lines if line.startswith('[')]

# Mappa categorie
categories_order = {line: i for i, line in enumerate(sorted_mods)}

# Gestione ordinamento mods
mods_final = sorted_mods.copy()

# Helper per trovare categoria
mod_to_category = {}

for mod in mods_info:
    # Masterlist check
    found_in_masterlist = False
    for category in masterlist:
        if mod in category['Mod']:
            category_tag = sorted_mods[category['Order']]
            mod_to_category[mod] = category_tag
            found_in_masterlist = True
            log(f'Mod: "{mod}" assegnato tramite masterlist a "{category_tag}"')
            break

    if found_in_masterlist:
        continue

    # Tags check
    tags = mods_info[mod]
    matched_categories = [cat for cat in sorted_mods if any(tag.lower() in cat.lower() for tag in tags)]

    if matched_categories:
        # Trova categoria con priorità massima
        category_tag = max(matched_categories, key=lambda c: categories_order[c])
        log(f'Mod: "{mod}" assegnato a "{category_tag}" (tag corrispondenti: {tags})')
    else:
        category_tag = '[11]----------[Miscellanious]----------.mod'
        mod_id = os.path.basename(os.path.dirname(mod))  # Estrai l'ID del mod dalla struttura del percorso
        log(f'Mod: "{mod}" (ID: {mod_id}) senza tag o info corrotto, assegnato a Miscellanious')

    mod_to_category[mod] = category_tag

# Costruisci lista finale
final_mod_list = []
for cat in sorted_mods:
    final_mod_list.append(cat)
    mods_in_cat = [mod for mod, cat_tag in mod_to_category.items() if cat_tag == cat]
    mods_in_cat.sort()  # ordinamento alfabetico
    final_mod_list.extend(mods_in_cat)

# Scrivi nuovo mods.cfg
with open(LOCAL_MODS_CFG_PATH, 'w', encoding='utf-8') as file:
    for mod in final_mod_list:
        file.write(f'{mod}\n')

log('Ordinamento completato con successo.')
