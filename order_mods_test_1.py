import json
import re

# Percorsi dei file
mods_file = r"d:\lavorini\io\Kenshi\KMO\Kenshi_mods_order\raw\mods.txt"
masterlist_file = r"d:\lavorini\io\Kenshi\KMO\Kenshi_mods_order\raw\masterlist.json"
output_file = r"d:\lavorini\io\Kenshi\KMO\Kenshi_mods_order\raw\mods_ordered.txt"

# Leggi il file masterlist.json
with open(masterlist_file, "r", encoding="utf-8") as f:
    masterlist = json.load(f)

# Crea un dizionario per mappare i mod alle loro categorie
mod_to_category = {}
for category in masterlist:
    for mod in category["Mod"]:
        mod_to_category[mod.strip().lower()] = category["Order"]

# Leggi il file mods.txt
with open(mods_file, "r", encoding="utf-8") as f:
    mods_lines = f.readlines()

# Inizializza le categorie con i separatori
categories = {}
separator_pattern = re.compile(r"^\[(\d+(\.\d+)?)\]")  # Pattern per separatori come [1], [1.2], ecc.

for line in mods_lines:
    line = line.strip()
    match = separator_pattern.match(line)
    if match:
        categories[match.group(1)] = {"separator": line, "mods": []}

# Aggiungi una categoria "Miscellanious (11)" per i mod non trovati
categories["11"] = {"separator": "[11]----------[Miscellanious]----------.mod", "mods": []}

# Assegna i mod alle categorie
for line in mods_lines:
    mod_name = line.strip()
    if separator_pattern.match(mod_name) or not mod_name.endswith(".mod"):
        continue  # Salta i separatori o righe non valide
    mod_key = mod_name.lower()
    if mod_key in mod_to_category:
        category_order = str(mod_to_category[mod_key])
        if category_order in categories:
            categories[category_order]["mods"].append(mod_name)
    else:
        categories["11"]["mods"].append(mod_name)  # Mod non trovato nella masterlist

# Ordina le categorie numericamente
sorted_categories = sorted(categories.items(), key=lambda x: float(x[0]))

# Scrivi il file mods_ordered.txt
with open(output_file, "w", encoding="utf-8") as f:
    for _, category in sorted_categories:
        # Scrivi il separatore
        f.write(f"{category['separator']}\n")
        # Scrivi i mod della categoria
        for mod in category["mods"]:
            f.write(f"{mod}\n")