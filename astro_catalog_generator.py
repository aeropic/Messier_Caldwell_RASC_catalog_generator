#=============================================================================
#                          (c) AEROPIC 2026
#           all in one Messier/Caldwell/RASC catalog generator
#  
# https://github.com/aeropic/Messier_Caldwell_RASC_catalog_generator
# http://www.messier.seds.org/xtra/similar/rasc-ngc.html
# https://www.catchersofthelight.com/astrophotography-hidden-treasures-list.aspx
# https://app.astrobin.com/u/GaryI?collection=677&i=esls3b#gallery
#
#   V4.0.1 : added fex comments all in english
#   V4.0 : added selection of todo objects (red heart) and export of TODO.txt
#   V3.1 : huge mod in hidden treasures!
#   V3.0 : added O'Meara lists (secret deep and hidden treasures)
#   V2.1 : season is displayed only when all seasons is selected
#   V2.0 : rolling menus for seasons and direction selection
#   V1.6 : display size for small object in orange (small means < 2'x2')
#   V1.5.1 : bug fix in size display
#   V1.5 : update of RASC objects usual name
#   V1.4 : image box points on telescopius when no image
#   V1.3.1 : tooltip border color light blue
#   V1.3 : logs in cmd window during thumbnails generation
#   V1.2 : .tif/tiff  is supported - dedicate view jpg files are created for display
#   V1.1.1 : .tif is partly supported (thumbnail OK, zoom KO)
#   V1.1 : syntax error in a comment fixed
#   V1.0 : first release
#============================================================================

import os
import re
import subprocess
import sys
import json
import importlib
from datetime import datetime


# --- DEPENDENCIES AUTO-INSTALL ---
def install_dependencies():
    try:
        importlib.import_module("PIL")
    except ImportError:
        print("Installation des dépendances manquantes...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
        importlib.invalidate_caches()

install_dependencies()
from PIL import Image, ImageOps
    
# --- CONFIGURATION & TRANSLATION ---
CONFIG = {
    "SOURCE_DIR": os.getcwd(),
    "SELECTED_CATALOG": "Messier",                #  selected catalog at startup: possible values : "Messier", "Caldwell", "RASC"
    "THUMB_DIR": "thumbnails",                    # name of the thumbnails directory
    "OUTPUT_HTML": "astro_catalog.html",          # name of the HTML page
    "THUMB_SIZE": 105,                            # size of the square thumbnail on the HTML page (max 200x200)
    "LATITUDE": 43.6,                             # your latitude
    "LIMIT_IMPOSSIBLE": 0,                        # degrees : change here if your horizon is masked
    "LIMIT_DIFFICILE": 20,
    "LIMIT_SMALL_OBJECT": 120                     # arcseconds ; paint small objects size in orange
}

LANG = {
    "CATALOG": "mon catalogue",                              # "my catalog"
    "PAGE_TITLE": "Mon Catalogue Astro",                     # "my astro catalog"
    "UNIT_LABEL": "objets",                                  # "objects"
    "ALL": "Toutes saisons",                                 # "All seasons"
    "ALL_DIR": "Nord et Sud",                                # "North and South"
    "NO_DATE": "Date inconnue",                              # "unknown date"
    "NORTH": "Nord",                                         # "North"
    "SOUTH": "Sud",                                          # "South"
    "TYPES": {
        "N": "Nébuleuse",                                    # "nebula"
        "NP": "Néb. Planétaire",                             # "planetary nebula"
        "AG": "Amas Globulaire",                             # "globular cluster"
        "AO": "Amas Ouvert",                                 # "open cluster"
        "G": "Galaxie",                                      # "galaxy
        "NS": "Nuage Stellaire",                             # "stellar cloud"
        "D": "Étoile Double",                                # "double star"
        "A": "Astérisme",                                    # "asterim"
        "SNR": "Rémanent Supernova",                         # "super nova remnant"
        "EN": "Néb. Émission",                               # "Emission Nebula"
        "RN": "Néb. Réflexion",                              # "reflection nebula "SNR": "Reste Supernova",
        "E/RN": "Néb. Ém./Réf.",                             # " emissin and reflexion nebula"
        "AN": "Amas + Néb."                                  # " Nebula and cluster"
    },
    "FAMILIES_LABELS": {
        "ALL": "Tous objets",                               # "all objects"
        "NEB": "Nébuleuses",                                # "nebula"
        "GAL": "Galaxies",
        "CLU": "Amas et divers"                             # "clusters and others"
    },
    "SEASONS": {"P": "Printemps", "E": "Été", "A": "Automne", "H": "Hiver"}      # {"P": "Spring", "E": "Summer", "A": "Automn", "H": "Winter"}
}



T, S = LANG["TYPES"], LANG["SEASONS"]

# --- DATABASES (MESSIER, CALDWELL, RASC) ---
# --- you can translate the constellation name and the usual name but keep the NGC reference as is ---
# --- replace the lists here after with the "English_databases.txt" content for the english translation
# --- Format: [Type, Season, Constellation, Mag, Size, Common Name, Dec, Tech_Ref]



MESSIER_DATA = {
    1: [T["SNR"], S["H"], "Taureau", "8.4", "6'x4'", "Nébuleuse du Crabe", 22.0, "NGC 1952"],
    2: [T["AG"], S["A"], "Verseau", "6.3", "16'", "Amas du Verseau", -0.8, "NGC 7089"],
    3: [T["AG"], S["P"], "Ch. de Chasse", "6.2", "18'", "Amas des Chiens de Chasse", 28.4, "NGC 5272"],
    4: [T["AG"], S["E"], "Scorpion", "5.9", "36'", "Amas du Scorpion", -26.5, "NGC 6121"],
    5: [T["AG"], S["P"], "Serpent", "5.7", "23'", "Amas du Serpent", 2.1, "NGC 5904"],
    6: [T["AO"], S["E"], "Scorpion", "4.2", "25'", "Amas du Papillon", -32.2, "NGC 6405"],
    7: [T["AO"], S["E"], "Scorpion", "3.3", "80'", "Amas de Ptolémée", -34.8, "NGC 6475"],
    8: [T["N"], S["E"], "Sagittaire", "6.0", "90'x40'", "Nébuleuse de la Lagune", -24.4, "NGC 6523"],
    9: [T["AG"], S["E"], "Ophiuchus", "7.7", "11'", "Amas d'Ophiuchus", -18.5, "NGC 6333"],
    10: [T["AG"], S["E"], "Ophiuchus", "6.6", "20'", "Amas d'Ophiuchus", -4.1, "NGC 6254"],
    11: [T["AO"], S["E"], "Écu", "5.8", "14'", "Amas du Canard Sauvage", -6.3, "NGC 6705"],
    12: [T["AG"], S["E"], "Ophiuchus", "6.7", "16'", "Amas d'Ophiuchus", -1.9, "NGC 6218"],
    13: [T["AG"], S["E"], "Hercule", "5.8", "20'", "Grand Amas d'Hercule", 36.5, "NGC 6205"],
    14: [T["AG"], S["E"], "Ophiuchus", "7.6", "11'", "Amas d'Ophiuchus", -3.3, "NGC 6402"],
    15: [T["AG"], S["A"], "Pégase", "6.2", "18'", "Amas de Pégase", 12.2, "NGC 7078"],
    16: [T["N"], S["E"], "Serpent", "6.0", "7'", "Nébuleuse de l'Aigle", -13.8, "NGC 6611"],
    17: [T["N"], S["E"], "Sagittaire", "6.0", "11'", "Nébuleuse Omega", -16.2, "NGC 6618"],
    18: [T["AO"], S["E"], "Sagittaire", "7.5", "9'", "Cygne Noir", -17.1, "NGC 6613"],
    19: [T["AG"], S["E"], "Ophiuchus", "6.8", "17'", "Amas d'Ophiuchus", -26.3, "NGC 6273"],
    20: [T["N"], S["E"], "Sagittaire", "6.3", "28'", "Nébuleuse Trifide", -23.0, "NGC 6514"],
    21: [T["AO"], S["E"], "Sagittaire", "6.5", "13'", "Amas du Sagittaire", -22.5, "NGC 6531"],
    22: [T["AG"], S["E"], "Sagittaire", "5.1", "32'", "Grand Amas du Sagittaire", -23.9, "NGC 6656"],
    23: [T["AO"], S["E"], "Sagittaire", "6.9", "27'", "Amas du Sagittaire", -19.0, "NGC 6494"],
    24: [T["NS"], S["E"], "Sagittaire", "4.6", "90'", "Petit Nuage Stellaire du Sagittaire", -18.4, "NGC 6603"],
    25: [T["AO"], S["E"], "Sagittaire", "4.6", "32'", "Amas du Sagittaire", -19.2, "IC 4725"],
    26: [T["AO"], S["E"], "Écu", "8.0", "15'", "Amas de l'Écu", -9.4, "NGC 6694"],
    27: [T["NP"], S["E"], "Petit Renard", "7.4", "8'x6'", "Nébuleuse Dumbbell", 22.7, "NGC 6853"],
    28: [T["AG"], S["E"], "Sagittaire", "6.8", "11'", "Amas du Sagittaire", -24.9, "NGC 6626"],
    29: [T["AO"], S["E"], "Cygne", "7.1", "7'", "Amas du Cygne", 38.5, "NGC 6913"],
    30: [T["AG"], S["A"], "Capricorne", "7.2", "12'", "Amas du Capricorne", -23.2, "NGC 7099"],
    31: [T["G"], S["A"], "Andromède", "3.4", "190'x60'", "Galaxie d'Andromède", 41.3, "NGC 224"],
    32: [T["G"], S["A"], "Andromède", "8.1", "8'x6'", "Le Gentil (M32)", 40.9, "NGC 221"],
    33: [T["G"], S["A"], "Triangle", "5.7", "70'x40'", "Galaxie du Triangle", 30.7, "NGC 598"],
    34: [T["AO"], S["H"], "Persée", "5.2", "35'", "Amas de Persée", 42.8, "NGC 1039"],
    35: [T["AO"], S["H"], "Gémeaux", "5.1", "28'", "Amas des Gémeaux", 24.3, "NGC 2168"],
    36: [T["AO"], S["H"], "Cocher", "6.0", "12'", "Amas du Cocher", 34.1, "NGC 1960"],
    37: [T["AO"], S["H"], "Cocher", "5.6", "24'", "Amas du Cocher", 32.5, "NGC 2099"],
    38: [T["AO"], S["H"], "Cocher", "6.4", "21'", "Amas de l'Étoile de Mer", 35.8, "NGC 1912"],
    39: [T["AO"], S["E"], "Cygne", "4.6", "32'", "Amas du Cygne", 48.4, "NGC 7092"],
    40: [T["D"], S["P"], "Grande Ourse", "8.4", "0.8'", "Winnecke 4", 58.1, "WNC 4"],
    41: [T["AO"], S["H"], "Grand Chien", "4.5", "38'", "Amas du Petit Rucher", -20.7, "NGC 2287"],
    42: [T["N"], S["H"], "Orion", "4.0", "85'x60'", "Nébuleuse d'Orion", -5.4, "NGC 1976"],
    43: [T["N"], S["H"], "Orion", "9.0", "20'x15'", "Nébuleuse de De Mairan", -5.2, "NGC 1982"],
    44: [T["AO"], S["H"], "Cancer", "3.1", "95'", "Amas de la Crèche", 19.7, "NGC 2632"],
    45: [T["AO"], S["H"], "Taureau", "1.6", "110'", "Les Pléiades", 24.1, "NGC 1432"],
    46: [T["AO"], S["H"], "Poupe", "6.1", "27'", "Amas de la Poupe", -14.8, "NGC 2437"],
    47: [T["AO"], S["H"], "Poupe", "4.4", "30'", "Amas de la Poupe", -14.4, "NGC 2422"],
    48: [T["AO"], S["H"], "Hydre", "5.8", "54'", "Amas de l'Hydre", -5.8, "NGC 2548"],
    49: [T["G"], S["P"], "Vierge", "8.4", "10'x9'", "Galaxie de la Vierge", 8.0, "NGC 4472"],
    50: [T["AO"], S["H"], "Licorne", "5.9", "16'", "Amas de la Licorne", -8.3, "NGC 2323"],
    51: [T["G"], S["P"], "Ch. de Chasse", "8.4", "11'x7'", "Galaxie du Tourbillon", 47.2, "NGC 5194"],
    52: [T["AO"], S["A"], "Cassiopée", "6.9", "13'", "Amas de Cassiopée", 61.6, "NGC 7654"],
    53: [T["AG"], S["P"], "Chevelure", "7.6", "13'", "Amas de la Chevelure", 18.2, "NGC 5024"],
    54: [T["AG"], S["E"], "Sagittaire", "7.6", "12'", "Amas du Sagittaire", -30.5, "NGC 6715"],
    55: [T["AG"], S["E"], "Sagittaire", "6.3", "19'", "Amas du Sagittaire", -30.9, "NGC 6809"],
    56: [T["AG"], S["E"], "Lyre", "8.3", "9'", "Amas de la Lyre", 33.0, "NGC 6779"],
    57: [T["NP"], S["E"], "Lyre", "8.8", "1.5'x1'", "Nébuleuse de l'Anneau", 33.0, "NGC 6720"],
    58: [T["G"], S["P"], "Vierge", "9.7", "6'x5'", "Galaxie de la Vierge", 11.8, "NGC 4579"],
    59: [T["G"], S["P"], "Vierge", "10.6", "5'x4'", "Galaxie de la Vierge", 11.6, "NGC 4621"],
    60: [T["G"], S["P"], "Vierge", "8.8", "7'x6'", "Galaxie de la Vierge", 11.6, "NGC 4649"],
    61: [T["G"], S["P"], "Vierge", "9.7", "6'x6'", "Galaxie de la Vierge", 4.5, "NGC 4303"],
    62: [T["AG"], S["E"], "Ophiuchus", "6.5", "15'", "Amas d'Ophiuchus", -30.1, "NGC 6266"],
    63: [T["G"], S["P"], "Ch. de Chasse", "8.6", "12'x8'", "Galaxie du Tournesol", 42.0, "NGC 5055"],
    64: [T["G"], S["P"], "Chevelure", "8.5", "10'x5'", "Galaxie de l'Œil Noir", 21.7, "NGC 4826"],
    65: [T["G"], S["P"], "Lion", "9.3", "10'x3'", "Galaxie du Lion", 13.1, "NGC 3623"],
    66: [T["G"], S["P"], "Lion", "8.9", "9'x4'", "Galaxie du Lion", 13.0, "NGC 3627"],
    67: [T["AO"], S["H"], "Cancer", "6.1", "30'", "Amas du Cobra Royal", 11.8, "NGC 2682"],
    68: [T["AG"], S["P"], "Hydre", "7.8", "11'", "Amas de l'Hydre", -26.7, "NGC 4590"],
    69: [T["AG"], S["E"], "Sagittaire", "7.6", "10'", "Amas du Sagittaire", -32.3, "NGC 6637"],
    70: [T["AG"], S["E"], "Sagittaire", "7.9", "9'", "Amas du Sagittaire", -32.3, "NGC 6681"],
    71: [T["AG"], S["E"], "Flèche", "8.2", "7'", "Amas de la Flèche", 18.8, "NGC 6838"],
    72: [T["AG"], S["A"], "Verseau", "9.3", "7'", "Amas du Verseau", -12.5, "NGC 6981"],
    73: [T["A"], S["A"], "Verseau", "9.0", "2.8'", "Astérisme du Verseau", -12.6, "NGC 6994"],
    74: [T["G"], S["A"], "Poissons", "9.4", "10'x10'", "Galaxie du Fantôme", 15.8, "NGC 628"],
    75: [T["AG"], S["E"], "Sagittaire", "8.5", "7'", "Amas du Sagittaire", -21.9, "NGC 6864"],
    76: [T["NP"], S["A"], "Persée", "10.1", "2.7'x1.8'", "Nébuleuse de la Petite Haltère", 51.6, "NGC 650"],
    77: [T["G"], S["A"], "Baleine", "8.9", "7'x6'", "Galaxie de la Baleine", -0.0, "NGC 1068"],
    78: [T["N"], S["H"], "Orion", "8.3", "8'x6'", "M78 (Nébuleuse)", 0.1, "NGC 2068"],
    79: [T["AG"], S["H"], "Lièvre", "7.7", "10'", "Amas du Lièvre", -24.5, "NGC 1904"],
    80: [T["AG"], S["E"], "Scorpion", "7.3", "10'", "Amas du Scorpion", -22.9, "NGC 6093"],
    81: [T["G"], S["P"], "Grande Ourse", "6.9", "26'x14'", "Galaxie de Bode", 69.1, "NGC 3031"],
    82: [T["G"], S["P"], "Grande Ourse", "8.4", "11'x4'", "Galaxie du Cigare", 69.7, "NGC 3034"],
    83: [T["G"], S["P"], "Hydre", "7.5", "13'x11'", "Galaxie du Moulinet Austral", -29.9, "NGC 5236"],
    84: [T["G"], S["P"], "Vierge", "9.1", "6'x6'", "Galaxie de la Vierge", 12.9, "NGC 4374"],
    85: [T["G"], S["P"], "Chevelure", "9.1", "7'x5'", "Galaxie de la Chevelure", 18.2, "NGC 4382"],
    86: [T["G"], S["P"], "Vierge", "8.9", "9'x6'", "Galaxie de la Vierge", 12.9, "NGC 4406"],
    87: [T["G"], S["P"], "Vierge", "8.6", "8'x8'", "Virgo A", 12.4, "NGC 4486"],
    88: [T["G"], S["P"], "Chevelure", "9.6", "7'x4'", "Galaxie de la Chevelure", 14.4, "NGC 4501"],
    89: [T["G"], S["P"], "Vierge", "9.8", "5'x5'", "Galaxie de la Vierge", 12.6, "NGC 4552"],
    90: [T["G"], S["P"], "Vierge", "9.5", "10'x4'", "Galaxie de la Vierge", 13.2, "NGC 4569"],
    91: [T["G"], S["P"], "Chevelure", "10.2", "5'x4'", "Galaxie de la Chevelure", 14.5, "NGC 4548"],
    92: [T["AG"], S["E"], "Hercule", "6.3", "14'", "Amas d'Hercule", 43.1, "NGC 6341"],
    93: [T["AO"], S["H"], "Poupe", "6.0", "22'", "Amas de la Poupe", -23.9, "NGC 2447"],
    94: [T["G"], S["P"], "Ch. de Chasse", "8.2", "11'x9'", "Galaxie de l'Œil de Crocodile", 41.1, "NGC 4736"],
    95: [T["G"], S["P"], "Lion", "9.7", "7'x5'", "Galaxie du Lion", 11.7, "NGC 3351"],
    96: [T["G"], S["P"], "Lion", "9.2", "8'x5'", "Galaxie du Lion", 11.8, "NGC 3368"],
    97: [T["NP"], S["P"], "Grande Ourse", "9.9", "3.4'", "Nébuleuse du Hibou", 55.0, "NGC 3587"],
    98: [T["G"], S["P"], "Chevelure", "10.1", "10'x3'", "Galaxie de la Chevelure", 14.9, "NGC 4192"],
    99: [T["G"], S["P"], "Chevelure", "9.9", "5'x5'", "Galaxie du Coma Pinwheel", 14.4, "NGC 4254"],
    100: [T["G"], S["P"], "Chevelure", "9.3", "7'x6'", "Galaxie de la Chevelure", 15.8, "NGC 4321"],
    101: [T["G"], S["P"], "Grande Ourse", "7.9", "28'x27'", "Galaxie du Moulinet", 54.4, "NGC 5457"],
    102: [T["G"], S["P"], "Dragon", "9.9", "6'x3'", "Galaxie du Fuseau", 55.8, "NGC 5866"],
    103: [T["AO"], S["A"], "Cassiopée", "7.4", "6'", "Amas de Cassiopée", 60.7, "NGC 581"],
    104: [T["G"], S["P"], "Vierge", "8.0", "9'x4'", "Galaxie du Sombrero", -11.6, "NGC 4594"],
    105: [T["G"], S["P"], "Lion", "9.3", "5'x5'", "Galaxie du Lion", 12.6, "NGC 3379"],
    106: [T["G"], S["P"], "Ch. de Chasse", "8.4", "18'x7'", "Galaxie des Chiens de Chasse", 47.3, "NGC 4258"],
    107: [T["AG"], S["E"], "Ophiuchus", "7.9", "13'", "Amas d'Ophiuchus", -13.1, "NGC 6171"],
    108: [T["G"], S["P"], "Grande Ourse", "10.0", "9'x2'", "Galaxie de la Planche à Surf", 53.4, "NGC 3556"],
    109: [T["G"], S["P"], "Grande Ourse", "9.8", "8'x5'", "Galaxie de la Grande Ourse", 53.4, "NGC 3992"],
    110: [T["G"], S["A"], "Andromède", "8.1", "17'x10'", "Galaxie d'Andromède (sat.)", 41.7, "NGC 205"]
}

CALDWELL_DATA = {
    1: [T["AO"], S["A"], "Céphée", "8.1", "13'", "NGC 188", 85.3, "NGC 188"],
    2: [T["NP"], S["A"], "Céphée", "10.2", "37''", "Nébuleuse du Nœud Coulant", 72.5, "NGC 40"],
    3: [T["G"], S["A"], "Dragon", "9.7", "18.6'x6.9'", "Galaxie du Dragon", 69.5, "NGC 4236"],
    4: [T["RN"], S["A"], "Céphée", "-", "18'x18'", "Nébuleuse de l'Iris", 68.2, "NGC 7023"],
    5: [T["G"], S["H"], "Girafe", "8.4", "21.1'x20.9'", "Galaxie de la Girafe", 68.1, "IC 342"],
    6: [T["NP"], S["P"], "Dragon", "8.1", "18''", "Nébuleuse de l'Œil de Chat", 66.6, "NGC 6543"],
    7: [T["G"], S["H"], "Girafe", "8.4", "24.9'x12'", "NGC 2403", 65.6, "NGC 2403"],
    8: [T["AO"], S["A"], "Cassiopée", "7.1", "5.8'", "NGC 559", 63.3, "NGC 559"],
    9: [T["EN"], S["A"], "Céphée", "-", "50'x40'", "Nébuleuse de la Grotte", 62.3, "Sh2-155"],
    10: [T["AO"], S["A"], "Cassiopée", "7.1", "16'", "NGC 663", 61.2, "NGC 663"],
    11: [T["EN"], S["A"], "Cassiopée", "-", "15'x8'", "Nébuleuse de la Bulle", 61.2, "NGC 7635"],
    12: [T["G"], S["A"], "Céphée", "8.9", "11.5'x11.5'", "Galaxie du Feu d'Artifice", 60.1, "NGC 6946"],
    13: [T["AO"], S["A"], "Cassiopée", "6.7", "13'", "Amas de la Chouette", 58.3, "NGC 457"],
    14: [T["AO"], S["A"], "Persée", "4.4", "30'", "Double Amas de Persée", 57.1, "NGC 869"],
    15: [T["NP"], S["E"], "Cygne", "9.8", "30''", "Nébuleuse de l'Œil Clignotant", 50.5, "NGC 6826"],
    16: [T["AO"], S["E"], "Lézard", "6.4", "20'", "NGC 7243", 49.9, "NGC 7243"],
    17: [T["G"], S["A"], "Cassiopée", "9.1", "13'x8'", "NGC 147", 48.5, "NGC 147"],
    18: [T["G"], S["A"], "Cassiopée", "9.2", "12'x10'", "NGC 185", 48.3, "NGC 185"],
    19: [T["EN"], S["A"], "Céphée", "-", "12'", "Nébuleuse du Cocon", 47.3, "IC 5146"],
    20: [T["EN"], S["E"], "Cygne", "-", "120'x100'", "Nébuleuse de l'Amérique du Nord", 44.3, "NGC 7000"],
    21: [T["G"], S["P"], "Chiens de Chasse", "9.4", "5'x4'", "NGC 4449", 44.1, "NGC 4449"],
    22: [T["NP"], S["A"], "Andromède", "8.3", "20''", "Nébuleuse de la Boule de Neige Bleue", 42.5, "NGC 7662"],
    23: [T["G"], S["A"], "Andromède", "10.0", "13'x3'", "Galaxie de l'Aiguille d'Argent", 42.3, "NGC 891"],
    24: [T["G"], S["H"], "Persée", "11.7", "2'x2'", "Perseus A", 41.5, "NGC 1275"],
    25: [T["AG"], S["H"], "Lynx", "10.4", "4'", "Amas de l'Errant Intergalactique", 38.9, "NGC 2419"],
    26: [T["G"], S["P"], "Chiens de Chasse", "10.2", "16'x2'", "NGC 4244", 37.8, "NGC 4244"],
    27: [T["EN"], S["E"], "Cygne", "-", "20'x10'", "Nébuleuse du Croissant", 38.4, "NGC 6888"],
    28: [T["AO"], S["A"], "Andromède", "5.2", "45'", "NGC 752", 37.8, "NGC 752"],
    29: [T["G"], S["P"], "Chiens de Chasse", "9.8", "5'x3'", "NGC 5005", 37.1, "NGC 5005"],
    30: [T["G"], S["A"], "Pégase", "9.5", "11'x4'", "Galaxie de Deer Lick", 34.4, "NGC 7331"],
    31: [T["EN"], S["H"], "Cocher", "-", "30'x20'", "Nébuleuse de l'Étoile Flamboyante", 34.3, "IC 405"],
    32: [T["G"], S["P"], "Chiens de Chasse", "9.3", "15'x3'", "Galaxie de la Baleine", 32.5, "NGC 4631"],
    33: [T["SNR"], S["E"], "Cygne", "-", "78'x8'", "Grande Dentelle du Cygne", 31.7, "NGC 6992"],
    34: [T["SNR"], S["E"], "Cygne", "-", "70'x6'", "Petite Dentelle du Cygne", 30.7, "NGC 6960"],
    35: [T["G"], S["P"], "Chevelure de Bérénice", "11.4", "1'x1'", "Amas de la Chevelure", 28.0, "NGC 4889"],
    36: [T["G"], S["P"], "Chevelure de Bérénice", "9.6", "11'x5'", "NGC 4559", 28.0, "NGC 4559"],
    37: [T["AO"], S["E"], "Petit Renard", "6.0", "14'", "NGC 6885", 26.5, "NGC 6885"],
    38: [T["G"], S["P"], "Chevelure de Bérénice", "9.6", "16'x3'", "Galaxie de l'Aiguille", 26.0, "NGC 4565"],
    39: [T["NP"], S["H"], "Gémeaux", "8.3", "13''", "Nébuleuse de l'Esquimau", 20.9, "NGC 2392"],
    40: [T["G"], S["P"], "Lion", "10.7", "3'x2'", "NGC 3626", 18.4, "NGC 3626"],
    41: [T["AO"], S["H"], "Taureau", "0.5", "330'", "Les Hyades", 15.9, "Mel 25"],
    42: [T["AG"], S["E"], "Dauphin", "10.6", "3'", "NGC 7006", 16.2, "NGC 7006"],
    43: [T["G"], S["A"], "Pégase", "10.0", "7'x2'", "NGC 7814", 16.1, "NGC 7814"],
    44: [T["G"], S["A"], "Pégase", "10.3", "5'x4'", "NGC 7479", 12.3, "NGC 7479"],
    45: [T["G"], S["P"], "Bouvier", "10.0", "5'x5'", "NGC 5248", 8.9, "NGC 5248"],
    46: [T["EN"], S["H"], "Licorne", "-", "2'x1'", "Nébuleuse Variable de Hubble", 8.7, "NGC 2261"],
    47: [T["AG"], S["E"], "Dauphin", "8.3", "7'", "NGC 6934", 7.4, "NGC 6934"],
    48: [T["G"], S["P"], "Hydre", "9.2", "5'x4'", "NGC 2775", 7.0, "NGC 2775"],
    49: [T["EN"], S["H"], "Licorne", "-", "80'x60'", "Nébuleuse de la Rosette", 5.0, "NGC 2237"],
    50: [T["AO"], S["H"], "Licorne", "4.8", "24'", "Amas de la Rosette", 4.9, "NGC 2244"],
    51: [T["G"], S["A"], "Baleine", "9.0", "16'x15'", "IC 1613", 2.1, "IC 1613"],
    52: [T["G"], S["P"], "Vierge", "9.4", "4'x3'", "NGC 4697", -5.8, "NGC 4697"],
    53: [T["G"], S["P"], "Sextant", "9.2", "8.3x3.2'", "Galaxie du Fuseau", -7.7, "NGC 3115"],
    54: [T["AO"], S["H"], "Licorne", "7.6", "14'", "NGC 2506", -10.8, "NGC 2506"],
    55: [T["NP"], S["E"], "Verseau", "8.0", "25''", "Nébuleuse Saturne", -11.4, "NGC 7009"],
    56: [T["NP"], S["A"], "Baleine", "8.0", "4'", "Nébuleuse du Crâne", -11.9, "NGC 246"],
    57: [T["G"], S["E"], "Sagittaire", "7.5", "15'x13'", "Galaxie de Barnard", -14.8, "NGC 6822"],
    58: [T["AO"], S["H"], "Grand Chien", "7.2", "20'", "Amas de Caroline", -15.6, "NGC 2360"],
    59: [T["NP"], S["P"], "Hydre", "8.3", "16''", "Le Fantôme de Jupiter", -18.6, "NGC 3242"],
    60: [T["G"], S["P"], "Corbeau", "10.3", "3'x2'", "Galaxies des Antennes A", -18.9, "NGC 4038"],
    61: [T["G"], S["P"], "Corbeau", "10.3", "3'x2'", "Galaxies des Antennes B", -19.0, "NGC 4039"],
    62: [T["G"], S["A"], "Baleine", "8.9", "12'x3'", "NGC 247", -20.8, "NGC 247"],
    63: [T["NP"], S["A"], "Verseau", "7.3", "13'", "Nébuleuse de l'Hélice", -20.8, "NGC 7293"],
    64: [T["AO"], S["H"], "Grand Chien", "4.1", "20'", "NGC 2362", -24.9, "NGC 2362"],
    65: [T["G"], S["A"], "Sculpteur", "7.1", "25'x7'", "Galaxie du Sculpteur", -25.3, "NGC 253"],
    66: [T["AG"], S["P"], "Hydre", "8.5", "2'", "NGC 5694", -26.5, "NGC 5694"],
    67: [T["G"], S["A"], "Fourneau", "9.3", "9'x6'", "NGC 1097", -30.3, "NGC 1097"],
    68: [T["EN"], S["E"], "Couronne Australe", "-", "1'", "NGC 6729", -36.9, "NGC 6729"],
    69: [T["NP"], S["E"], "Scorpion", "9.6", "2'", "Nébuleuse du Papillon", -37.1, "NGC 6302"],
    70: [T["G"], S["A"], "Sculpteur", "8.1", "12'x9'", "NGC 300", -37.7, "NGC 300"],
    71: [T["AO"], S["H"], "Poupe", "4.2", "27'", "NGC 2477", -38.5, "NGC 2477"],
    72: [T["G"], S["A"], "Sculpteur", "7.8", "31'x6'", "NGC 55", -39.2, "NGC 55"],
    73: [T["AG"], S["H"], "Colombe", "7.3", "11'", "NGC 1851", -40.1, "NGC 1851"],
    74: [T["NP"], S["H"], "Voiles", "8.2", "1'", "Nébuleuse du Huit Éclatant", -40.4, "NGC 3132"],
    75: [T["AO"], S["E"], "Loup", "5.8", "40'", "NGC 6124", -40.7, "NGC 6124"],
    76: [T["AO"], S["E"], "Scorpion", "2.6", "15'", "NGC 6231", -41.8, "NGC 6231"],
    77: [T["G"], S["P"], "Centaure", "6.8", "18'x14'", "Centaurus A", -43.0, "NGC 5128"],
    78: [T["AG"], S["P"], "Centaure", "3.7", "36'", "Omega Centauri", -47.5, "NGC 5139"],
    79: [T["AO"], S["P"], "Croix du Sud", "4.2", "10'", "La Boîte à Bijoux", -60.3, "NGC 4755"],
    80: [T["AG"], S["P"], "Centaure", "3.7", "36'", "Omega Centauri bis", -47.5, "NGC 5139"],
    81: [T["AG"], S["E"], "Autel", "8.1", "6'", "NGC 6352", -48.4, "NGC 6352"],
    82: [T["AG"], S["E"], "Autel", "8.1", "12'", "NGC 6362", -67.0, "NGC 6362"],
    83: [T["G"], S["P"], "Centaure", "8.6", "13'x4'", "NGC 4945", -49.5, "NGC 4945"],
    84: [T["AG"], S["P"], "Centaure", "7.4", "10'", "NGC 5286", -51.4, "NGC 5286"],
    85: [T["AO"], S["H"], "Voiles", "2.5", "50'", "IC 2391", -53.0, "IC 2391"],
    86: [T["AG"], S["E"], "Autel", "5.3", "30'", "NGC 6397", -53.7, "NGC 6397"],
    87: [T["AG"], S["H"], "Horloge", "8.4", "7'", "NGC 1261", -55.2, "NGC 1261"],
    88: [T["AO"], S["P"], "Compas", "9.1", "11'", "NGC 5823", -55.6, "NGC 5823"],
    89: [T["AO"], S["E"], "Règle", "5.1", "14'", "NGC 6067", -54.2, "NGC 6067"],
    90: [T["NP"], S["H"], "Carène", "10.9", "18''", "NGC 2867", -58.3, "NGC 2867"],
    91: [T["AO"], S["P"], "Carène", "3.9", "41'", "NGC 3532", -58.7, "NGC 3532"],
    92: [T["EN"], S["P"], "Carène", "-", "120'", "Nébuleuse d'Eta Carinae", -59.7, "NGC 3372"],
    93: [T["AG"], S["E"], "Paon", "5.4", "27'", "NGC 6752", -59.9, "NGC 6752"],
    94: [T["AO"], S["P"], "Croix du Sud", "4.2", "10'", "La Boîte à Bijoux", -60.3, "NGC 4755"],
    95: [T["AO"], S["E"], "Triangle Austral", "5.1", "12'", "NGC 6025", -60.5, "NGC 6025"],
    96: [T["AO"], S["H"], "Carène", "3.8", "30'", "NGC 2516", -60.8, "NGC 2516"],
    97: [T["AO"], S["P"], "Centaure", "3.9", "12'", "NGC 3766", -61.5, "NGC 3766"],
    98: [T["AO"], S["P"], "Croix du Sud", "4.1", "5'", "NGC 4609", -61.0, "NGC 4609"],
    99: [T["EN"], S["P"], "Croix du Sud", "-", "420'x300'", "Nébuleuse du Sac à Charbon", -62.5, "C99"],
    100: [T["EN"], S["P"], "Centaure", "-", "60'", "Nébuleuse du Poulet qui Court", -63.0, "IC 2944"],
    101: [T["G"], S["E"], "Paon", "8.3", "16'x11'", "NGC 6744", -63.9, "NGC 6744"],
    102: [T["AO"], S["P"], "Carène", "1.9", "100'", "Pléiades du Sud", -64.4, "IC 2602"],
    103: [T["EN"], S["H"], "Dorade", "-", "40'", "Nébuleuse de la Tarentule", -69.1, "NGC 2070"],
    104: [T["AG"], S["A"], "Toucan", "4.0", "31'", "NGC 47", -72.1, "NGC 47"],
    105: [T["AG"], S["P"], "Mouche", "7.8", "14'", "NGC 4833", -70.9, "NGC 4833"],
    106: [T["AG"], S["A"], "Toucan", "4.0", "31'", "47 Tucanae", -72.1, "NGC 104"],
    107: [T["AG"], S["P"], "Oiseau de Paradis", "9.2", "10'", "NGC 6101", -72.2, "NGC 6101"],
    108: [T["AG"], S["P"], "Mouche", "7.2", "20'", "NGC 4372", -73.0, "NGC 4372"],
    109: [T["NP"], S["P"], "Caméléon", "10.6", "15''", "NGC 3195", -81.2, "NGC 3195"]
}

RASC_DATA = {
    1: [T["NP"], S["A"], "Verseau", "8.3", "25''", "Nébuleuse Saturne", -11.4, "NGC 7009"],
    2: [T["NP"], S["A"], "Verseau", "6.5", "12'50''", "Nébuleuse de l'Hélice", -20.8, "NGC 7293"],
    3: [T["G"], S["A"], "Pégase", "9.5", "10.7x4.0'", "Galaxie de Deer Lick", 34.4, "NGC 7331"],
    4: [T["EN"], S["A"], "Cassiopée", "-", "15x8'", "Nébuleuse de la Bulle", 61.2, "NGC 7635"],
    5: [T["AO"], S["A"], "Cassiopée", "6.7", "16'", "Amas de la Rose Blanche", 56.7, "NGC 7789"],
    6: [T["G"], S["A"], "Cassiopée", "11.7", "2x2'", "Galaxie naine de Cassiopée", 48.3, "NGC 185"],
    7: [T["EN"], S["A"], "Cassiopée", "-", "35x30'", "Nébuleuse Pacman", 56.6, "NGC 281"],
    8: [T["AO"], S["A"], "Cassiopée", "6.4", "13'", "Amas de la Chouette", 58.3, "NGC 457"],
    9: [T["AO"], S["A"], "Cassiopée", "7.1", "16'", "Amas de l'Écharpe (Scarf Cluster)", 61.2, "NGC 663"],
    10: [T["NP"], S["A"], "Cassiopée", "12.3", "34''", "Phantom Streak Nebula", 61.3, "NGC 1289"],
    11: [T["NP"], S["A"], "Andromède", "9.2", "20''", "Nébuleuse de la Boule de Neige Bleue", 42.5, "NGC 7662"],
    12: [T["G"], S["A"], "Andromède", "10", "13.5x2.8'", "Galaxie de l'Aiguille d'Argent", 42.3, "NGC 891"],
    13: [T["G"], S["A"], "Sculpteur", "7.1", "25.1x7.4'", "Galaxie du Sculpteur", -25.3, "NGC 253"],
    14: [T["G"], S["A"], "Bélier", "10.3", "7.1x4.5'", "Galaxie Spirale", 19.0, "NGC 772"],
    15: [T["NP"], S["A"], "Baleine", "8.0", "3'45''", "Nébuleuse du Crâne", -11.9, "NGC 246"],
    16: [T["G"], S["A"], "Baleine", "10.1", "5.2x4.4'", "Galaxie lenticulaire", -1.1, "NGC 936"],
    17: [T["AO"], S["A"], "Persée", "4.4", "30'/30'", "Double Amas de Persée", 57.1, "NGC 869"],
    18: [T["G"], S["A"], "Persée", "9.5", "8.7x4.3'", "Galaxie lenticulaire", 39.0, "NGC 1023"],
    19: [T["EN"], S["A"], "Persée", "-", "3.0x3.0'", "Fossil Footprint Nebula", 51.3, "NGC 1491"],
    20: [T["NP"], S["A"], "Girafe", "12.0", "52''", "Nébuleuse de l'Huître", 60.9, "NGC 1501"],
    21: [T["G"], S["A"], "Eridan", "9.9", "7.8x6.9'", "Galaxie NGC 1232", -20.6, "NGC 1232"],
    22: [T["NP"], S["A"], "Eridan", "10.4", "18''", "Nébuleuse de l'Œil de Cléopâtre", -12.7, "NGC 1535"],
    23: [T["NP"], S["H"], "Taureau", "10.8", "1'54''", "Crystal Ball Nebula", 30.8, "NGC 1514"],
    24: [T["E/RN"], S["H"], "Cocher", "-", "3.0x3.0'", "Fly Nebula", 34.2, "NGC 1931"],
    25: [T["RN"], S["H"], "Orion", "-", "8.0x5.0'", "Nébuleuse de la Tête de Renard", -3.3, "NGC 1788"],
    26: [T["E/RN"], S["H"], "Orion", "-", "40x25'", "Nébuleuse Courante", -4.7, "NGC 1973"],
    27: [T["NP"], S["H"], "Orion", "12.4", "18''", "Nébuleuse planétaire", 9.1, "NGC 2022"],
    28: [T["EN"], S["H"], "Orion", "-", "30x30'", "Nébuleuse de la Flamme", -1.9, "NGC 2024"],
    29: [T["AO"], S["H"], "Orion", "8.5", "10'", "Amas ouvert", 12.8, "NGC 2194"],
    30: [T["NP"], S["H"], "Gémeaux", "13.0", "55''", "Nébuleuse de la Cacahuète", 29.5, "NGC 2371"],
    31: [T["NP"], S["H"], "Gémeaux", "8.3", "13''", "Nébuleuse de l'Esquimau", 20.9, "NGC 2392"],
    32: [T["EN"], S["H"], "Licorne", "-", "80x60'", "Nébuleuse de la Rosette", 5.0, "NGC 2237"],
    33: [T["E/RN"], S["H"], "Licorne", "var", "2x1'", "Nébuleuse Variable de Hubble", 8.7, "NGC 2261"],
    34: [T["EN"], S["H"], "Grand Chien", "-", "8.0x6.0'", "Nébuleuse du Casque de Thor", -13.2, "NGC 2359"],
    35: [T["NP"], S["H"], "Poupe", "10.3", "14''", "Nébuleuse de l'Insecte", -18.2, "NGC 2440"],
    36: [T["AO"], S["H"], "Poupe", "6.5", "22'", "Amas ouvert", -12.8, "NGC 2539"],
    37: [T["G"], S["H"], "Girafe", "8.4", "17.8x11.0'", "Galaxie spirale", 65.6, "NGC 2403"],
    38: [T["G"], S["H"], "Girafe", "10.1", "5.1x4.4'", "Galaxie lenticulaire", 78.2, "NGC 2655"],
    39: [T["G"], S["P"], "Lynx", "9.7", "9.3x2.5'", "Galaxie de la Soucoupe volante", 33.4, "NGC 2683"],
    40: [T["G"], S["P"], "Grande Ourse", "9.3", "8.1x3.8'", "Galaxie spirale", 51.0, "NGC 2841"],
    41: [T["G"], S["P"], "Grande Ourse", "10.6", "7.6x1.7'", "Galaxie spirale", 55.7, "NGC 3079"],
    42: [T["G"], S["P"], "Grande Ourse", "9.7", "6.9x6.8'", "Galaxie spirale", 41.4, "NGC 3184"],
    43: [T["G"], S["P"], "Grande Ourse", "10.9", "5.4x1.5'", "Galaxie spirale", 47.5, "NGC 3877"],
    44: [T["G"], S["P"], "Grande Ourse", "9.8", "3.8x2.5'", "Galaxie lenticulaire", 45.0, "NGC 3941"],
    45: [T["G"], S["P"], "Grande Ourse", "10.7", "5.1x1.4'", "Galaxie lenticulaire", 50.9, "NGC 4026"],
    46: [T["G"], S["P"], "Grande Ourse", "10.5", "5.8x2.5'", "Galaxie spirale", 50.5, "NGC 4088"],
    47: [T["G"], S["P"], "Grande Ourse", "11.9", "6.9x1.7'", "Galaxie spirale", 50.5, "NGC 4157"],
    48: [T["G"], S["P"], "Grande Ourse", "9.6", "5.5x2.3'", "Galaxie spirale", 61.6, "NGC 4605"],
    49: [T["G"], S["P"], "Sextant", "9.2", "8.3x3.2'", "Galaxie du Fuseau", -7.7, "NGC 3115"],
    50: [T["NP"], S["P"], "Hydre", "8.6", "16''", "Le Fantôme de Jupiter", -18.6, "NGC 3242"],
    51: [T["G"], S["P"], "Petit Lion", "11.7", "5.9x1.7'", "Galaxie spirale", 33.4, "NGC 3003"],
    52: [T["G"], S["P"], "Petit Lion", "9.9", "6.9x6.5'", "Galaxie du Petit Moulinet", 25.0, "NGC 3344"],
    53: [T["G"], S["P"], "Petit Lion", "11.3", "6.2x1.5'", "Galaxie spirale", 36.6, "NGC 3432"],
    54: [T["G"], S["P"], "Lion", "8.9", "12.6x6.6'", "Galaxie spirale", 21.5, "NGC 2903"],
    55: [T["G"], S["P"], "Lion", "9.9", "5.9x2.6'", "Galaxie lenticulaire", 12.6, "NGC 3384"],
    56: [T["G"], S["P"], "Lion", "8.7", "9.5x5.0'", "Galaxie spirale", -0.0, "NGC 3521"],
    57: [T["G"], S["P"], "Lion", "10.0", "3.7x3.2'", "Galaxie elliptique", 18.0, "NGC 3607"],
    58: [T["G"], S["P"], "Lion", "9.5", "14.8x3.6'", "Galaxie de l'Arête", 13.6, "NGC 3628"],
    59: [T["G"], S["P"], "Chiens de Chasse", "10.8", "4.8x1.1'", "Galaxie lenticulaire", 43.1, "NGC 4111"],
    60: [T["G"], S["P"], "Chiens de Chasse", "9.7", "7.9x6.3'", "Galaxie irrégulière", 36.3, "NGC 4214"],
    61: [T["G"], S["P"], "Chiens de Chasse", "10.2", "16.2x2.5'", "Galaxie de la Lame d'Argent", 37.8, "NGC 4244"],
    62: [T["G"], S["P"], "Chiens de Chasse", "9.4", "5.1x3.7'", "Galaxie irrégulière", 44.1, "NGC 4449"],
    63: [T["G"], S["P"], "Chiens de Chasse", "9.8", "5.9x3.1'", "Galaxies des Cocons", 41.6, "NGC 4490"],
    64: [T["G"], S["P"], "Chiens de Chasse", "9.3", "15.1x3.3'", "Galaxie de la Baleine", 32.5, "NGC 4631"],
    65: [T["G"], S["P"], "Chiens de Chasse", "10.4", "13.8x3.3'", "La Crosse de Hockey", 32.2, "NGC 4656"],
    66: [T["G"], S["P"], "Chiens de Chasse", "9.8", "5.9x3.1'", "Galaxie spirale", 37.1, "NGC 5005"],
    67: [T["G"], S["P"], "Chiens de Chasse", "10.1", "10.5x5.6'", "Galaxie spirale", 36.6, "NGC 5033"],
    68: [T["G"], S["P"], "Chevelure de Bérénice", "10.4", "6.9x2.8'", "Galaxie spirale", 29.6, "NGC 4274"],
    69: [T["G"], S["P"], "Chevelure de Bérénice", "10.2", "3.6x2.2'", "Galaxie spirale", 31.2, "NGC 4414"],
    70: [T["G"], S["P"], "Chevelure de Bérénice", "9.8", "4.8x3.8'", "Galaxie elliptique", 25.8, "NGC 4494"],
    71: [T["G"], S["P"], "Chevelure de Bérénice", "9.8", "10.5x4.9'", "Galaxie spirale", 28.0, "NGC 4559"],
    72: [T["G"], S["P"], "Chevelure de Bérénice", "9.6", "16.2x2.8'", "Galaxie de l'Aiguille", 26.0, "NGC 4565"],
    73: [T["G"], S["P"], "Chevelure de Bérénice", "9.2", "11.0x7.9'", "Galaxie spirale", 25.5, "NGC 4725"],
    74: [T["G"], S["P"], "Corbeau", "10.7", "~3x2'", "Galaxies des Antennes", -18.9, "NGC 4038"],
    75: [T["NP"], S["P"], "Corbeau", "10.3", "45''", "Galaxie de l'Atome pour la Paix", -18.8, "NGC 4361"],
    76: [T["G"], S["P"], "Vierge", "9.9", "8.3x2.2'", "Galaxie spirale", 13.1, "NGC 4216"],
    77: [T["G"], S["P"], "Vierge", "11.0", "5.1x1.4'", "Galaxie spirale", 12.7, "NGC 4388"],
    78: [T["G"], S["P"], "Vierge", "10.1", "9.3x3.9'", "Les Yeux", 13.0, "NGC 4438"],
    79: [T["G"], S["P"], "Vierge", "10.5", "10.2x1.9'", "Galaxie spirale", 0.1, "NGC 4517"],
    80: [T["G"], S["P"], "Vierge", "9.6", "7.6x2.3'", "Galaxie spirale", 7.7, "NGC 4526"],
    81: [T["G"], S["P"], "Vierge", "9.8", "6.8x5.0'", "Galaxie spirale", 8.2, "NGC 4535"],
    82: [T["G"], S["P"], "Vierge", "~11", "4.6x2.1'", "Les Jumeaux Siamois", 11.3, "NGC 4567"],
    83: [T["G"], S["P"], "Vierge", "9.6", "3.5x2.7'", "Galaxie spirale", -8.7, "NGC 4699"],
    84: [T["G"], S["P"], "Vierge", "10.2", "8.7x1.6'", "Galaxie de l'Équerre", 11.2, "NGC 4762"],
    85: [T["G"], S["P"], "Vierge", "10.6", "7.9x1.7'", "Galaxie spirale", 1.9, "NGC 5746"],
    86: [T["AG"], S["P"], "Bouvier", "9.1", "11.0'", "Amas globulaire", 28.5, "NGC 5466"],
    87: [T["G"], S["P"], "Dragon", "10.4", "12.3x1.8'", "Galaxie de l'Éclat", 56.3, "NGC 5907"],
    88: [T["G"], S["P"], "Dragon", "10.2", "6.2x2.3'", "Galaxie spirale", 70.1, "NGC 6503"],
    89: [T["NP"], S["P"], "Dragon", "8.8", "18''", "Nébuleuse de l'Œil de Chat", 66.6, "NGC 6543"],
    90: [T["NP"], S["E"], "Hercule", "9.3", "14''", "Nébuleuse de la Tortue", 23.8, "NGC 6210"],
    91: [T["NP"], S["E"], "Ophiuchus", "10.4", "30''", "Nébuleuse du Petit Fantôme", -17.8, "NGC 6369"],
    92: [T["NP"], S["E"], "Ophiuchus", "9.0", "8''", "Emerald Nebula", 6.8, "NGC 6572"],
    93: [T["AO"], S["E"], "Ophiuchus", "4.6", "27'", "Amas de Tweedledum", 6.5, "NGC 6633"],
    94: [T["AG"], S["E"], "Ecu de Sobieski", "8.2", "7.2'", "Amas globulaire", -8.7, "NGC 6712"],
    95: [T["NP"], S["E"], "Aigle", "11.8", "1'49''", "Phantom Feather Nebula", 6.5, "NGC 6781"],
    96: [T["AO"], S["E"], "Cygne", "7.3", "5'", "Amas de la Tête de Renard (Foxhead)", 40.2, "NGC 6819"],
    97: [T["NP"], S["E"], "Cygne", "9.8", "30''", "Nébuleuse de l'Œil Clignotant", 50.5, "NGC 6826"],
    98: [T["SNR"], S["E"], "Cygne", "-", "20x10'", "Nébuleuse du Croissant", 38.4, "NGC 6888"],
    "99a": [T["SNR"], S["E"], "Cygne", "-", "70x6'", "Petite Dentelle du Cygne", 30.7, "NGC 6960"],
    "99b": [T["SNR"], S["E"], "Cygne", "-", "78x8'", "Grande Dentelle du Cygne", 31.7, "NGC 6992"],
    100: [T["EN"], S["E"], "Cygne", "-", "120x100'", "Nébuleuse de l'Amérique du Nord", 44.3, "NGC 7000"],
    101: [T["NP"], S["E"], "Cygne", "10.4", "15''", "Nébuleuse planétaire", 42.2, "NGC 7027"],
    102: [T["NP"], S["E"], "Sagittaire", "11.8", "34''", "Little Gem Nebula", -16.2, "NGC 6445"],
    103: [T["AO"], S["E"], "Sagittaire", "8.1", "6'", "Amas ouvert", -27.9, "NGC 6520"],
    104: [T["NP"], S["E"], "Sagittaire", "9.9", "17''", "Little Gem Nebula", -16.2, "NGC 6818"],
    105: [T["AO"], S["E"], "Petit Renard", "8.8", "3.2'", "Amas ouvert", 20.3, "NGC 6802"],
    106: [T["AO"], S["E"], "Petit Renard", "6.3", "31'", "Amas ouvert", 28.3, "NGC 6940"],
    107: [T["AO"], S["E"], "Céphée", "7.8", "8'", "Amas ouvert", 60.6, "NGC 6939"],
    108: [T["G"], S["E"], "Céphée", "8.9", "11.0x9.8'", "Galaxie du Feu d'Artifice", 60.1, "NGC 6946"],
    109: [T["RN"], S["E"], "Céphée", "-", "8x7'", "Nébuleuse par réflexion", 66.1, "NGC 7129"],
    110: [T["NP"], S["E"], "Céphée", "10.2", "37''", "Nébuleuse du Nœud Coulant", 72.5, "NGC 40"]
}

O_MEARA_DATA = {
    # hidden treasures
    1: [T["AO"], S["A"], "Cassiopée", "8.8", "5'", "NGC 189", 61.1, "NGC 189"],
    2: [T["AO"], S["A"], "Cassiopée", "7.0", "15'", "Amas du Voilier", 61.8, "NGC 225"],
    3: [T["N"], S["A"], "Cassiopée", "7.8", "30'x35'", "Nébuleuse Pacman", 56.6, "NGC 281"],
    4: [T["AG"], S["A"], "Sculpteur", "8.1", "13'", "NGC 288", -26.6, "NGC 288"],
    5: [T["G"], S["A"], "Andromède", "10.0", "3.5'", "Galaxie de la Perle Perdue", 35.7, "NGC 404"],
    6: [T["G"], S["A"], "Céto", "10.5", "4'x2'", "Galaxie du Petit Fuseau", -6.9, "NGC 584"],
    7: [T["AO"], S["A"], "Cassiopée", "7.9", "6'", "Amas Ying Yang", 60.7, "NGC 659"],
    8: [T["G"], S["A"], "Bélier", "10.3", "7'x4'", "Galaxie Fiddlehead", 19.0, "NGC 772"],
    9: [T["G"], S["A"], "Céto", "10.2", "6'x3'", "NGC 908", -21.2, "NGC 908"],
    10: [T["G"], S["A"], "Persée", "9.5", "7'x3'", "Galaxie Lenticulaire de Persée", 39.1, "NGC 1023"],
    11: [T["G"], S["H"], "Éridan", "9.8", "7'x7'", "Galaxie de l'Œil de Dieu", -20.6, "NGC 1232"],
    12: [T["G"], S["H"], "Éridan", "8.5", "11'x10'", "Galaxie au Col de Neige", -41.1, "NGC 1291"],
    13: [T["G"], S["H"], "Fourneau", "9.4", "12'x9'", "Fornax A", -37.2, "NGC 1316"],
    14: [T["AO"], S["H"], "Persée", "1.2", "185'", "Amas d'Alpha Persei", 49.0, "Alpha Per"],
    15: [T["N"], S["H"], "Persée", "5.7", "3'", "nuage de Persée (NGC 1333)", 31.4, "NGC 1333"],
    16: [T["NP"], S["H"], "Fourneau", "9.4", "6'", "Nébuleuse de l'Embryon", -25.9, "NGC 1360"],
    17: [T["G"], S["H"], "Fourneau", "9.5", "11'x6'", "NGC 1365", -36.1, "NGC 1365"],
    18: [T["G"], S["H"], "Fourneau", "9.4", "7'x7'", "NGC 1399", -35.4, "NGC 1399"],
    19: [T["G"], S["H"], "Fourneau", "9.5", "8'x5'", "NGC 1398", -26.3, "NGC 1398"],
    20: [T["G"], S["H"], "Fourneau", "10.0", "3'x3'", "NGC 1404", -35.6, "NGC 1404"],
    21: [T["A"], S["H"], "Girafe", "5.0", "150'", "Cascade de Kemble", 63.0, "Kemble 1"],
    22: [T["NP"], S["H"], "Girafe", "11.5", "0.9'", "Nébuleuse de l'Huître", 61.0, "NGC 1501"],
    23: [T["AO"], S["H"], "Girafe", "6.0", "20'", "Amas du Jolly Roger", 62.3, "NGC 1502"],
    24: [T["NP"], S["H"], "Éridan", "9.6", "0.9'", "Œil de Cléopâtre", -12.7, "NGC 1535"],
    25: [T["AO"], S["H"], "Persée", "6.4", "18'", "Amas m & m", 51.2, "NGC 1528"],
    26: [T["AO"], S["H"], "Persée", "6.2", "12'", "Amas m & m", 50.3, "NGC 1545"],
    27: [T["AO"], S["H"], "Taureau", "6.4", "40'", "Amas de la Lune Pirate", 19.1, "NGC 1647"],
    28: [T["NP"], S["H"], "Lièvre", "9.6", "0.5'", "Nébuleuse de la Framboise", -12.7, "IC 418"],
    29: [T["AO"], S["H"], "Orion", "5.0", "50'", "Amas de Lambda Orionis", 9.9, "Cr 69"],
    30: [T["AO"], S["H"], "Orion", "4.2", "28'", "Amas du Wagon de Charbon", -4.4, "NGC 1981"],
    31: [T["AO"], S["H"], "Orion", "5.0", "30'", "Le Joyau Perdu d'Orion", -4.9, "NGC 1980"],
    32: [T["N"], S["H"], "Orion", "6.3", "20'", "Nébuleuse de l'Homme qui Court", -4.8, "NGC 1977"],
    33: [T["N"], S["H"], "Orion", "9.5", "2'", "Nébuleuse du Tampon en Caoutchouc", -6.7, "NGC 1999"],
    34: [T["N"], S["H"], "Orion", "7.2", "30'", "Nébuleuse de la Flamme", 1.9, "NGC 2024"],
    35: [T["N"], S["H"], "Orion", "10.0", "3'", "NGC 2163", 18.7, "NGC 2163"],
    36: [T["AO"], S["H"], "Orion", "5.9", "6'", "Amas des Petites Pléiades", 14.0, "NGC 2169"],
    37: [T["N"], S["H"], "Orion", "6.9", "18'", "NGC 2175", 20.5, "NGC 2175"],
    38: [T["AO"], S["H"], "Licorne", "4.1", "40'", "Amas de l'Arbre de Noël", 9.9, "NGC 2264"],
    39: [T["AO"], S["H"], "Licorne", "6.0", "15'", "Le Dragon d'Hagrid", 0.5, "NGC 2301"],
    40: [T["AO"], S["H"], "Licorne", "7.1", "18'", "Avery's Island", -10.3, "NGC 2353"],
    41: [T["NP"], S["H"], "Poupe", "9.4", "1.3'", "Nébuleuse du Papillon Albinos", -18.2, "NGC 2440"],
    42: [T["AO"], S["H"], "Poupe", "2.8", "50'", "Amas du Scorpion Piquant", -38.0, "NGC 2451"],
    43: [T["N"], S["H"], "Poupe", "7.1", "15'", "NGC 2467", -26.4, "NGC 2467"],
    44: [T["AO"], S["H"], "Voiles", "4.7", "25'", "Amas de la Boucle d'Oreille d'Or", -49.2, "NGC 2547"],
    45: [T["AO"], S["H"], "Poupe", "6.5", "15'", "Amas de l'Assiette", -12.8, "NGC 2539"],
    46: [T["AO"], S["H"], "Poupe", "6.3", "70'", "Amas du Cœur et de la Dague", -37.6, "NGC 2546"],
    47: [T["G"], S["P"], "Lynx", "9.7", "9'x2'", "Galaxie de l'OVNI", 33.4, "NGC 2683"],
    48: [T["G"], S["P"], "Girafe", "10.1", "5'x4'", "NGC 2655", 78.2, "NGC 2655"],
    49: [T["G"], S["P"], "Grande Ourse", "9.3", "8'x4'", "Galaxie de l'Œil de Tigre", 51.0, "NGC 2841"],
    50: [T["AO"], S["P"], "Voiles", "7.0", "15'", "Amas du Collier de Perles", -57.0, "IC 2488"],
    51: [T["G"], S["P"], "Lion", "8.8", "13'x6'", "NGC 2903", 21.5, "NGC 2903"],
    52: [T["G"], S["P"], "Grande Ourse", "9.6", "7'x7'", "Petite Galaxie du Moulinet", 41.4, "NGC 3184"],
    53: [T["AO"], S["P"], "Voiles", "6.0", "5'", "Amas du Trésor de la Reine", -51.7, "NGC 3228"],
    54: [T["AO"], S["P"], "Carène", "4.7", "5'", "Petite Boîte à Bijoux", -58.2, "NGC 3293"],
    55: [T["G"], S["P"], "Petit Lion", "9.7", "7'x7'", "NGC 3344", 24.9, "NGC 3344"],
    56: [T["G"], S["P"], "Lion", "9.2", "11'x5'", "NGC 3521", 0.0, "NGC 3521"],
    57: [T["G"], S["P"], "Hydre", "9.4", "12'x7'", "Galaxie Cadre", -32.8, "NGC 3621"],
    58: [T["G"], S["P"], "Lion", "9.6", "13'x3'", "Galaxie du Fantôme du Roi Hamlet", 13.6, "NGC 3628"],
    59: [T["G"], S["P"], "Chiens de Chasse", "9.6", "8'x7'", "NGC 4214", 36.3, "NGC 4214"],
    60: [T["G"], S["P"], "Vierge", "10.3", "8'x2'", "Galaxie Silver Streak", 13.1, "NGC 4216"],
    61: [T["NP"], S["P"], "Corbeau", "10.9", "2.1'", "NGC 4361", -18.8, "NGC 4361"],
    62: [T["AO"], S["P"], "Chevelure de Bérénice", "1.8", "300'", "Amas de Coma", 25.9, "Mel 111"],
    63: [T["G"], S["P"], "Chiens de Chasse", "9.5", "6'x3'", "Galaxie du Cocon", 41.6, "NGC 4490"],
    64: [T["NP"], S["P"], "Girafe", "10.6", "0.3'", "Nébuleuse du Citron Vert", 82.6, "IC 3568"],
    65: [T["G"], S["P"], "Vierge", "9.6", "7'x3'", "Galaxie du Sourcil Poilu", 7.7, "NGC 4526"],
    66: [T["G"], S["P"], "Grande Ourse", "10.1", "6'x2'", "Galaxie de l'Œuf de Fabergé", 61.6, "NGC 4605"],
    67: [T["G"], S["P"], "Chiens de Chasse", "10.1", "15'x2'", "Galaxie du Crochet", 32.2, "NGC 4656"],
    68: [T["G"], S["P"], "Vierge", "9.6", "4'x3'", "NGC 4699", -8.7, "NGC 4699"],
    69: [T["G"], S["P"], "Chevelure de Bérénice", "9.3", "11'x8'", "NGC 4725", 25.5, "NGC 4725"],
    70: [T["G"], S["P"], "Centaure", "9.5", "9'x3'", "Le Fantôme d'Iota", -36.6, "NGC 5102"],
    71: [T["AO"], S["P"], "Centaure", "5.9", "8'", "Amas du Petit Scorpion", -62.9, "NGC 5281"],
    72: [T["G"], S["P"], "Vierge", "10.5", "4'x3'", "NGC 5363", 5.3, "NGC 5363"],
    73: [T["AO"], S["P"], "Centaure", "5.5", "30'", "NGC 5662", -56.7, "NGC 5662"],
    74: [T["G"], S["P"], "Vierge", "10.5", "7'x1'", "Galaxie de la Lame et la Perle", 2.0, "NGC 5746"],
    75: [T["G"], S["P"], "Dragon", "9.9", "7'x3'", "Galaxie de l'Or des Fous", 55.8, "NGC 5866"],
    76: [T["AG"], S["P"], "Balance", "8.4", "11'", "Amas Globulaire Fantôme", -21.0, "NGC 5897"],
    77: [T["AG"], S["E"], "Loup", "7.6", "10'", "NGC 5986", -37.8, "NGC 5986"],
    78: [T["NP"], S["E"], "Hercule", "8.8", "0.4'", "Nébuleuse de la Tortue", 23.8, "NGC 6210"],
    79: [T["AO"], S["E"], "Scorpion", "6.4", "9'", "NGC 6242", -39.5, "NGC 6242"],
    80: [T["AO"], S["E"], "Scorpion", "5.4", "8'", "Amas de l'Aile de Papillon de Nuit", -37.9, "NGC 6281"],
    81: [T["NP"], S["E"], "Ophiuchus", "11.4", "0.6'", "Nébuleuse du Petit Fantôme", -23.8, "NGC 6369"],
    82: [T["AO"], S["E"], "Scorpion", "8.8", "12'", "Amas Fantôme", -37.0, "NGC 6400"],
    83: [T["AO"], S["E"], "Ophiuchus", "8.3", "45'", "La Ruche d'Été", 5.7, "NGC 4665"],
    84: [T["NP"], S["E"], "Sagittaire", "11.2", "0.7'", "Nébuleuse de la Boîte", -20.0, "NGC 6445"],
    85: [T["G"], S["E"], "Dragon", "10.2", "7'x3'", "Galaxie Perdue dans l'Espace", 70.1, "NGC 6503"],
    86: [T["AG"], S["E"], "Scorpion", "7.2", "10'", "Amas de la Pépite d'Argent", -37.1, "NGC 6441"],
    87: [T["D"], S["E"], "Ophiuchus", "9.5", "n/a", "Étoile de Barnard", 4.7, "Barnard"],
    88: [T["AO"], S["E"], "Sagittaire", "7.6", "5'", "Le Coffre du Mort", -27.9, "NGC 6520"],
    89: [T["AG"], S["E"], "Sagittaire", "7.5", "9'", "Amas de l'Étoile de Mer", -25.0, "NGC 6544"],
    90: [T["NP"], S["E"], "Ophiuchus", "8.1", "0.3'", "Nébuleuse de l'Œil d'Émeraude", 6.9, "NGC 6572"],
    91: [T["AG"], S["E"], "Sagittaire", "7.6", "9'", "NGC 6624", -30.4, "NGC 6624"],
    92: [T["AO"], S["E"], "Ophiuchus", "4.6", "20'", "Amas de Tweedledum", 6.5, "NGC 6633"],
    93: [T["AO"], S["E"], "Serpent", "5.0", "52'", "Amas de Graff", 5.4, "IC 4756"],
    94: [T["AO"], S["E"], "Aigle", "6.7", "15'", "Amas de la Licorne Volante", 10.3, "NGC 6709"],
    95: [T["AG"], S["E"], "Écu", "8.1", "10'", "NGC 6712", -8.7, "NGC 6712"],
    96: [T["AG"], S["E"], "Sagittaire", "6.8", "13'", "NGC 6723", -36.6, "NGC 6723"],
    97: [T["A"], S["E"], "Petit Renard", "3.6", "60'", "Le Cintre", 20.2, "Cr 399"],
    98: [T["AO"], S["E"], "Cygne", "7.3", "5'", "Amas de la Tête de Renard", 40.2, "NGC 6819"],
    99: [T["NP"], S["E"], "Sagittaire", "9.3", "0.8'", "Nébuleuse du Petit Joyau", -14.2, "NGC 6818"],
    100: [T["AO"], S["E"], "Cygne", "7.6", "7'", "Amas de la Frégate Pirate", 44.2, "NGC 6866"],
    101: [T["AO"], S["E"], "Petit Renard", "6.3", "25'", "Amas de Mothra", 28.3, "NGC 6940"],
    102: [T["N"], S["E"], "Cygne", "n/a", "480'", "Sac à Charbon du Nord", 41.0, "LDN 906"],
    103: [T["NP"], S["E"], "Cygne", "10.7", "1.4'", "Nébuleuse du Bouton de Manteau", 54.5, "NGC 7008"],
    104: [T["NP"], S["E"], "Cygne", "8.5", "0.3'", "NGC 7027", 42.2, "NGC 7027"],
    105: [T["AN"], S["E"], "Céphée", "3.5", "154'", "Amas de l'Éléphant / Trèfle", 57.8, "IC 1396"],
    106: [T["AO"], S["A"], "Céphée", "7.2", "20'", "Vif d'Or de Harry Potter", 58.1, "NGC 7380"],
    107: [T["A"], S["A"], "Poissons", "8.0", "12'", "Petite Louche", 8.0, "Asterism"],
    108: [T["AO"], S["A"], "Cassiopée", "6.7", "25'", "Amas de la Rose Rose (O'Meara)", 56.7, "NGC 7789"],
    109: [T["G"], S["A"], "Sculpteur", "9.0", "9'", "Galaxie de Bond", -32.6, "NGC 7793"],
# secret deep
    1001: [T["RN"], S["A"], "Cassiopée", "10.1", "8.6'", "vdB 1", 58.7, "vdB 1"],
    1002: [T["G"], S["A"], "Sculpteur", "10.4", "8.1'", "Galaxie du Calmar Géant", -33.2, "NGC 134"],
    1003: [T["G"], S["A"], "Poissons", "10.4", "5.2'", "Galaxie du Tourbillon", 5.2, "NGC 488"],
    1004: [T["AO"], S["A"], "Cassiopée", "7.9", "40'", "Amas ouvert avec nébulosité", 61.8, "NGC 654"],
    1005: [T["AO"], S["A"], "Cassiopée", "9.1", "57'", "Lund 57 / Loch Ness monster", 71.9, "Collinder 463"],
    1006: [T["AO"], S["A"], "Cassiopée", "4.4", "130'", "Strong Man Cluster", 59.4, "Stock 2"],
    1007: [T["G"], S["A"], "Céto", "10.1", "5.2'", "Galaxie de la Soucoupe", -1.1, "NGC 936"],
    1008: [T["G"], S["A"], "Éridan", "10.6", "2.9'", "Galaxie de la Truffe", -7.5, "NGC 1084"],
    1009: [T["AO"], S["A"], "Persée", "7.6", "10'", "Amas de l'Étoile de Mer", 47.2, "NGC 1245"],
    1010: [T["G"], S["A"], "Éridan", "10.4", "6.5'", "Galaxie spirale barrée", -19.4, "NGC 1300"],
    1011: [T["AO"], S["H"], "Persée", "8.1", "30'", "Amas de la Raie / Petit Scorpion", 37.3, "NGC 1342"],
    1012: [T["N"], S["H"], "Orion", "10.0", "90'", "La Tête de Cheval (dans Barnard's Loop)", 0.7, "Barnard 33"], 
    1013: [T["G"], S["H"], "Éridan", "10.8", "1.9'", "Galaxie avec NGC 1407", -18.6, "NGC 1400"],
    1014: [T["G"], S["H"], "Éridan", "9.7", "2.5'", "Galaxie avec NGC 1400", -18.5, "NGC 1407"],
    1015: [T["EN"], S["H"], "Persée", "10.0", "12'", "Nébuleuse de l'Empreinte Fossile", 51.3, "NGC 1491"],
    1016: [T["NP"], S["H"], "Taureau", "10.0", "2'", "Nébuleuse de la Boule de Cristal", 30.7, "NGC 1514"],
    1017: [T["EN"], S["H"], "Persée", "10.0", "12'", "Trifide du Nord", 35.2, "NGC 1579"],
    1018: [T["AO"], S["H"], "Taureau", "7.0", "60'", "Amas ouvert", 23.6, "NGC 1750"],
    1019: [T["AO"], S["H"], "Taureau", "7.0", "90'", "Amas ouvert", 23.7, "NGC 1758"],
    1020: [T["EN"], S["H"], "Orion", "10.0", "8'", "Chauve-Souris Cosmique / Foxface", -3.3, "NGC 1788"],
    1021: [T["AO"], S["H"], "Taureau", "7.0", "17'", "Amas ouvert", 16.5, "NGC 1807"],
    1022: [T["AO"], S["H"], "Taureau", "7.7", "16'", "Amas ouvert", 16.6, "NGC 1817"],
    1023: [T["EN"], S["H"], "Cocher", "10.0", "13'", "Nébuleuse de l'Araignée", 34.4, "IC 417"],
    1024: [T["AO"], S["H"], "Cocher", "8.3", "3'", "La Mouche (avec IC 417)", 34.2, "NGC 1931"],
    1025: [T["AO"], S["H"], "Orion", "0.4", "150'", "Ceinture d'Orion", -1.0, "Collinder 70"],
    1026: [T["NP"], S["H"], "Orion", "11.6", "0.5'", "Nébuleuse des Baisers", 9.1, "NGC 2022"],
    1027: [T["NP"], S["H"], "Cocher", "11.5", "0.25'", "Nébuleuse planétaire", 46.1, "IC 2149"],
    1028: [T["EN"], S["H"], "Licorne", "10.0", "3'", "Nébuleuse par émission", -9.7, "NGC 2149"],
    1029: [T["RN"], S["H"], "Licorne", "10.0", "110'", "Nébuleuse de l'Ange", -6.3, "NGC 2170"],
    1030: [T["AO"], S["H"], "Cocher", "7.2", "15'", "Amas du Cœur Brisé", 41.1, "NGC 2281"],
    1031: [T["AG"], S["H"], "Poupe", "7.3", "6.8'", "Amas Globulaire de la Poupe", -36.0, "NGC 2298"],
    1032: [T["EN"], S["H"], "Licorne", "10.0", "4'", "Nébuleuse par émission", -7.7, "NGC 2316"],
    1033: [T["AO"], S["H"], "Licorne", "5.5", "7'", "Amas ouvert", -10.6, "NGC 2343"],
    1034: [T["NP"], S["H"], "Licorne", "10.3", "2'", "Nébuleuse du Papillon", -0.8, "NGC 2346"],
    1035: [T["EN"], S["H"], "Grand Chien", "10.0", "10'", "Casque de Thor / Canard", -13.2, "NGC 2359"],
    1036: [T["NP"], S["H"], "Gémeaux", "9.1", "2.1'", "Nébuleuse de la Double Bulle", 29.4, "NGC 2371"],
    1037: [T["AO"], S["H"], "Gémeaux", "9.1", "10'", "Amas de la Comète Scintillante", 21.5, "NGC 2420"],
    1038: [T["G"], S["P"], "Grande Ourse", "10.1", "7.6'", "Galaxie du Frisbee Fantôme", 55.6, "NGC 3079"],
    1039: [T["G"], S["P"], "Grande Ourse", "10.0", "4.6'", "Galaxie irrégulière", 68.7, "NGC 3077"],
    1040: [T["G"], S["P"], "Sextant", "10.5", "30'", "Galaxie Impétueuse", 3.4, "NGC 3166"],
    1041: [T["G"], S["P"], "Sextant", "10.3", "4.8'", "Galaxie spirale", 3.4, "NGC 3169"],
    1042: [T["G"], S["P"], "Grande Ourse", "10.7", "8.3'", "Galaxie spirale", 45.5, "NGC 3198"],
    1043: [T["G"], S["P"], "Lion", "10.3", "2.8'", "Arp 94 (avec NGC 3227)", 19.8, "NGC 3226"],
    1044: [T["G"], S["P"], "Lion", "10.3", "5.6'", "Arp 94 (avec NGC 3226)", 19.8, "NGC 3227"],
    1045: [T["G"], S["P"], "Petit Lion", "10.5", "6.2'", "Arp 206 / Aiguille à tricoter", 36.6, "NGC 3432"],
    1046: [T["G"], S["P"], "Grande Ourse", "10.1", "5.9'", "Galaxie spirale", 43.5, "NGC 3675"],
    1047: [T["G"], S["P"], "Grande Ourse", "10.6", "4.4'", "Galaxie spirale", 48.7, "NGC 3893"],
    1048: [T["G"], S["P"], "Grande Ourse", "10.3", "6.6'", "Galaxie spirale", 52.3, "NGC 3953"],
    1049: [T["G"], S["P"], "Grande Ourse", "10.5", "4.5'", "Galaxie avec NGC 4041", 61.9, "NGC 4036"],
    1050: [T["G"], S["P"], "Grande Ourse", "10.1", "5'", "Galaxie spirale", 44.5, "NGC 4051"],
    1051: [T["G"], S["P"], "Chiens de Chasse", "10.7", "4.8'", "Galaxie spirale", 43.0, "NGC 4111"],
    1052: [T["AG"], S["P"], "Chevelure de Bérénice", "10.3", "4'", "Amas Kick the Can", 18.5, "NGC 4147"],
    1053: [T["G"], S["P"], "Chevelure de Bérénice", "10.1", "6'", "Galaxie de l'Oeil Noir", 18.3, "NGC 4293"],
    1054: [T["G"], S["P"], "Chevelure de Bérénice", "10.3", "3.6'", "Galaxie en troupeau", 31.2, "NGC 4414"],
    1055: [T["G"], S["P"], "Vierge", "11.0", "3'", "Arp 120 (les yeux avec NGC 4438)", 13.0, "NGC 4435"],
    1056: [T["G"], S["P"], "Vierge", "10.1", "9.3'", "Les Yeux (Arp 120)", 13.0, "NGC 4438"],
    1057: [T["G"], S["P"], "Chevelure de Bérénice", "10.1", "4.8'", "Galaxie spirale", 17.0, "NGC 4450"],
    1058: [T["G"], S["P"], "Vierge", "10.3", "3.7'", "Galaxie proche des Yeux", 13.1, "NGC 4461"],
    1059: [T["G"], S["P"], "Chevelure de Bérénice", "10.2", "4.5'", "Galaxie elliptique", 13.4, "NGC 4473"],
    1060: [T["G"], S["P"], "Chevelure de Bérénice", "10.4", "4'", "Galaxie spirale", 13.6, "NGC 4477"],
    1061: [T["G"], S["P"], "Vierge", "9.5", "6.2'", "Galaxie elliptique", 2.6, "NGC 4636"],
    1062: [T["G"], S["P"], "Vierge", "10.5", "4.2'", "Galaxie spirale", 3.0, "NGC 4665"],
    1063: [T["G"], S["P"], "Vierge", "10.5", "5.4'", "Galaxie lenticulaire", -1.2, "NGC 4753"],
    1064: [T["G"], S["P"], "Vierge", "10.1", "8.7'", "Galaxie avec NGC 4754", 11.2, "NGC 4762"],
    1065: [T["G"], S["P"], "Chiens de Chasse", "10.0", "11'", "Galaxie spirale", 36.5, "NGC 5033"],
    1066: [T["G"], S["P"], "Chiens de Chasse", "10.0", "5.4'", "Compagne de M51 (Arp 85)", 47.2, "NGC 5195"],
    1067: [T["AG"], S["P"], "Bouvier", "10.3", "11'", "Amas Globulaire Fantôme", 28.5, "NGC 5466"],
    1068: [T["G"], S["P"], "Vierge", "10.5", "3.4'", "Galaxie spirale", 1.6, "NGC 5846"],
    1069: [T["G"], S["P"], "Dragon", "10.1", "12'", "Galaxie de l'Éclat", 56.3, "NGC 5907"],
    1070: [T["NP"], S["E"], "Hercule", "11.4", "0.25'", "Nébuleuse du Petit Pois", 12.0, "IC 4593"],
    1071: [T["AG"], S["E"], "Scorpion", "9.0", "9.3'", "Amas Globulaire", -26.0, "NGC 6144"],
    1072: [T["G"], S["E"], "Hercule", "11.5", "3'", "Galaxie proche de M13", 36.8, "NGC 6207"],
    1073: [T["AG"], S["E"], "Hercule", "9.4", "4.5'", "Amas Globulaire d'Hercule", 47.5, "NGC 6229"],
    1074: [T["AG"], S["E"], "Ophiuchus", "9.0", "7.9'", "Amas Globulaire", -26.5, "NGC 6293"],
    1075: [T["NP"], S["E"], "Ophiuchus", "10.5", "0.75'", "Nébuleuse de la Boîte", -12.9, "NGC 6309"],
    1076: [T["AG"], S["E"], "Ophiuchus", "9.5", "7.2'", "Amas Globulaire", -17.8, "NGC 6356"],
    1077: [T["AG"], S["E"], "Sagittaire", "10.3", "90'", "Fenêtre de Baade", -30.0, "NGC 6522"],
    1078: [T["AG"], S["E"], "Sagittaire", "10.0", "3.7'", "Amas Globulaire", -30.0, "NGC 6528"],
    1079: [T["NP"], S["E"], "Sagittaire", "11.0", "1.5'", "Anneau Austral", -33.8, "NGC 6563"],
    1080: [T["RN"], S["E"], "Sagittaire", "10.0", "5'", "Nébuleuse par réflexion", -19.7, "NGC 6589"],
    1081: [T["RN"], S["E"], "Sagittaire", "10.0", "11'", "Nébuleuse par réflexion", -19.8, "NGC 6595"],
    1082: [T["AG"], S["E"], "Sagittaire", "9.0", "5'", "Amas Globulaire", -25.5, "NGC 6638"],
    1083: [T["AO"], S["E"], "Écu de Sobieski", "7.2", "16'", "Amas du Traîneau", -8.2, "NGC 6664"],
    1084: [T["AG"], S["E"], "Sagittaire", "9.1", "3.9'", "Amas Globulaire (Palomar 9)", -22.7, "NGC 6717"],
    1085: [T["NP"], S["E"], "Aigle", "11.5", "0.25'", "Nébuleuse de la Fleur de Pissenlit", -5.9, "NGC 6751"],
    1086: [T["AO"], S["E"], "Aigle", "7.0", "90'", "Amas avec NGC 6756", 4.2, "NGC 6755"],
    1087: [T["AO"], S["E"], "Aigle", "10.0", "4'", "Amas avec NGC 6755", 4.7, "NGC 6756"],
    1088: [T["NP"], S["E"], "Aigle", "11.5", "1'", "Mini Dumbbell / Fils de M76", -1.5, "NGC 6778"],
    1089: [T["NP"], S["E"], "Aigle", "11.5", "2'", "Nébuleuse de la Boule de Neige", 6.5, "NGC 6781"],
    1090: [T["NP"], S["E"], "Aigle", "11.5", "1'", "Nébuleuse du Rétrécissement", 9.2, "NGC 6804"],
    1091: [T["AO"], S["E"], "Cygne", "8.1", "13'", "Smoke Ring / Hole in a Cluster", 46.3, "NGC 6811"],
    1092: [T["A"], S["E"], "Cygne", "10.0", "12'", "Astérisme du Cerf-Volant", 47.5, "Cygnus Kite Asterism"],
    1093: [T["NP"], S["E"], "Dauphin", "11.5", "0.3'", "Nébuleuse planétaire", 12.7, "NGC 6891"],
    1094: [T["NP"], S["E"], "Cygne", "10.0", "1'", "Petite Nébuleuse de l'Anneau", 30.5, "NGC 6894"],
    1095: [T["EN"], S["E"], "Cygne", "10.0", "0.1'", "Nébuleuse Gamma Cygni", 40.2, "IC 1318"],
    1096: [T["NP"], S["E"], "Dauphin", "10.9", "1'", "Nébuleuse de l'Éclair Bleu", 20.1, "NGC 6905"],
    1097: [T["AO"], S["E"], "Cygne", "5.9", "8'", "Amas de l'Arpenteur (Inchworm)", 40.7, "NGC 6910"],
    1098: [T["AO"], S["A"], "Céphée", "8.8", "8'", "Astérisme de l'Oie en vol", 60.6, "NGC 6939"],
    1099: [T["NP"], S["A"], "Cygne", "10.7", "0.5'", "Nébuleuse du Cheeseburger", 47.8, "NGC 7026"],
    1100: [T["NP"], S["A"], "Cygne", "10.0", "1'", "Nébuleuse du Disque Fantôme", 46.2, "NGC 7048"],
    1101: [T["RN"], S["A"], "Céphée", "10.0", "8'", "Rose Cosmique", 66.1, "NGC 7129"],
    1102: [T["AO"], S["A"], "Céphée", "6.1", "7'", "Alligator Nageur", 62.6, "NGC 7160"],
    1103: [T["AO"], S["A"], "Lézard", "8.4", "40'", "Amas ouvert", 46.4, "NGC 7209"],
    1104: [T["NP"], S["A"], "Céphée", "11.0", "0.7'", "Nébuleuse planétaire", 61.2, "NGC 7354"],
    1105: [T["AO"], S["A"], "Céphée", "7.3", "4'", "Amas du Loir (Dormouse)", 60.5, "NGC 7510"],
    1106: [T["EN"], S["A"], "Céphée", "10.0", "10'", "Nébuleuse de la Lagune Nord", 61.5, "NGC 7538"],
    1107: [T["AO"], S["A"], "Cassiopée", "8.5", "17'", "Amas avec NGC 7788", 61.2, "NGC 7790"],
}



CATALOGS = {
    "Messier": {"prefix": "M", "data": MESSIER_DATA},          # the prefix is used in the HTML page
    "Caldwell": {"prefix": "C", "data": CALDWELL_DATA},
    "RASC": {"prefix": "R", "data": RASC_DATA},
    "O'Meara": {"prefix": "X", "data": O_MEARA_DATA}
}

TODO_FILE = "TODO.txt"


# --- SCRIPT ---

import os
import re
import json
from datetime import datetime
from PIL import Image, ImageOps

def find_image(prefix, obj_id, tech_ref):
    """Search for a matching image in the source directory based on technical references or IDs"""
    valid_exts = ('.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff', '.lnk')
    if not os.path.exists(CONFIG["SOURCE_DIR"]): return None
    
    # Pre-filter files with valid extensions and exclude thumbnails
    files = [f for f in os.listdir(CONFIG["SOURCE_DIR"]) 
             if f.lower().endswith(valid_exts) and "_thumb" not in f]

    if tech_ref:
        # Search by technical designation (e.g., NGC 7000, IC 434)
        # Captures the catalog type and the object number
        match = re.search(r"(NGC|IC|SH2|Mel|WNC|M|Barnard|vdB)\s?(\d+)", tech_ref, re.IGNORECASE)
        if match:
            a_type, a_num = match.group(1), match.group(2)
            # Regex handles various separators between type and number
            # Negative lookahead (?!\d) ensures we don't match NGC 1 if the file is NGC 12
            pattern = rf"{a_type}[_ \-\s]?{a_num}(?!\d)"
            for filename in files:
                if re.search(pattern, filename, re.IGNORECASE):
                    return filename

    # Fallback search: match using catalog prefix + object ID
    pattern_id = rf"(^|[_ \-\.]){prefix}[_ \-\s]?{obj_id}(?!\d)"
    for filename in files:
        if re.search(pattern_id, filename, re.IGNORECASE):
            return filename
                
    return None
    
def get_exif_date(path):
    """Extract capture date from EXIF or fallback to file modification date"""
    try:
        with Image.open(path) as img:
            exif = img._getexif()
            # Tag 306 corresponds to DateTime
            if exif and 306 in exif:
                return datetime.strptime(exif[306], "%Y:%m:%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
    except: pass
    # Default to filesystem modification time if EXIF is missing or unreadable
    return datetime.fromtimestamp(os.path.getmtime(path)).strftime("%d/%m/%Y %H:%M")

def make_thumbnail(src):
    """Generate a square thumbnail and convert TIF files for web display"""
    if not os.path.exists(CONFIG["THUMB_DIR"]): os.makedirs(CONFIG["THUMB_DIR"])
    dest = os.path.join(CONFIG["THUMB_DIR"], f"thumb_{src}")
    
    # Handle heavy TIF files: generate a lightweight JPG 'view' version for the lightbox
    if src.lower().endswith(('.tif', '.tiff')):
        view_dest = os.path.join(CONFIG["THUMB_DIR"], f"view_{os.path.splitext(src)[0]}.jpg")
        if not os.path.exists(view_dest):
            try:
                with Image.open(src) as img_view:
                    # Auto-rotate based on EXIF and convert to RGB (strips Alpha/CMYK)
                    img_view = ImageOps.exif_transpose(img_view).convert("RGB")
                    view_size = CONFIG.get("VIEW_SIZE", 1200)
                    img_view.thumbnail((view_size, view_size), Image.Resampling.LANCZOS)
                    img_view.save(view_dest, "JPEG", quality=85)
            except Exception:
                pass

    if os.path.exists(dest): return dest
    
    try:
        # Generate the square thumbnail using a center-crop approach
        with Image.open(src) as img:
            img = ImageOps.exif_transpose(img).convert("RGB")
            w, h = img.size
            min_dim = min(w, h)
            left, top = (w - min_dim) / 2, (h - min_dim) / 2
            right, bottom = (w + min_dim) / 2, (h + min_dim) / 2
            img = img.crop((left, top, right, bottom))
            size = CONFIG["THUMB_SIZE"]
            img = img.resize((size, size), Image.Resampling.LANCZOS)
            img.save(dest, "JPEG", quality=85)
            print(src)
            return dest
    except: return src
    
def load_todo_list():
    """Load the list of marked objects from TODO.txt (JSON format)"""
    if not os.path.exists(TODO_FILE): return {}
    try:
        with open(TODO_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return json.loads(content) if content else {}
    except Exception as e:
        print(f"Error reading TODO.txt : {e}")
        return {}
        
def generate():
    """Main function to process data and generate the HTML gallery"""
    final_json = {}
    stats = {}
    
    # Load marked objects at the start to flag them in the UI
    todo_list = load_todo_list() 
    
    # Extract prefixes for JS to ensure synchronization between Python logic and Frontend
    prefixes_js = {k: v["prefix"] for k, v in CATALOGS.items()}
    
    for name, data_dict in CATALOGS.items():
        # Get marked IDs for this specific catalog (e.g., "Messier")
        marked_ids = todo_list.get(name, [])
        
        objs = []
        found_count = 0
        prefix = data_dict["prefix"]
        # Natural sort for IDs (handles numeric strings correctly: 1, 2, 10 instead of 1, 10, 2)
        keys = sorted(data_dict["data"].keys(), key=lambda x: (int(re.sub(r'\D', '', str(x))), str(x)))
        
        print(" ")
        print("==============")
        print("   " + name)
        print("==============")
        
        for k in keys:
            info = data_dict["data"][k]
            tech_ref = info[7]
            img_file = find_image(prefix, k, tech_ref)
            thumb, date = "", ""
            if img_file:
                found_count += 1
                thumb, date = make_thumbnail(img_file), get_exif_date(img_file)
            
            # Visibility calculation: max altitude based on observer latitude and object declination
            dec = info[6]
            h_max = 90 - abs(CONFIG["LATITUDE"] - dec)
            
            # Determine color coding based on observation difficulty
            color = "#c9d1d9" # Default
            if h_max <= CONFIG["LIMIT_IMPOSSIBLE"]: color = "#da3633" # Red
            elif h_max <= CONFIG["LIMIT_DIFFICILE"]: color = "#ff9f43" # Orange

            objs.append({
                "id": k, 
                "prefix": prefix, 
                "info": info, 
                "tech_ref": tech_ref,
                "img": img_file or "", 
                "thumb": thumb, 
                "date": date,
                "h_max": round(h_max, 1),
                "label_color": color,
                "todo": str(k) in [str(i) for i in marked_ids]
            })
            
        final_json[name] = objs
        stats[name] = f"{found_count}/{len(data_dict['data'])}"

    
    # --- UI Component Preparation (Dropdown menus) ---
    select_options = "".join([f'<option value="{c}" {"selected" if c == CONFIG["SELECTED_CATALOG"] else ""}>{c}</option>' for c in CATALOGS.keys()])
    season_options = "".join([f'<option value="{val}">{val}</option>' for val in LANG["SEASONS"].values()])
    dir_options = f'<option value="Tous">{LANG["ALL_DIR"]}</option><option value="{LANG["NORTH"]}">{LANG["NORTH"]}</option><option value="{LANG["SOUTH"]}">{LANG["SOUTH"]}</option>'

    # Dynamic family construction from LANG dictionary
    family_options = f"""
        <option value="Tous">{LANG['FAMILIES_LABELS']['ALL']}</option>
        <option value="Nébuleuse">{LANG['FAMILIES_LABELS']['NEB']}</option>
        <option value="Galaxie">{LANG['FAMILIES_LABELS']['GAL']}</option>
        <option value="Amas">{LANG['FAMILIES_LABELS']['CLU']}</option>
    """

    limit_small = CONFIG.get("LIMIT_SMALL_OBJECT", 60)
    
    html_template = fr"""<!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <style>
            :root {{ --case-size: {CONFIG["THUMB_SIZE"]}px; }}
            body {{ background: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', sans-serif; text-align: center; padding: 20px; overflow-x: hidden; }}
            h1 {{ font-size: 2.2em; margin-bottom: 5px; color: #fff; }}
            .stats-header {{ color: #8b949e; font-size: 1.1em; margin-bottom: 20px; }}
            
            /* Unified filter bar style with custom arrow */
            .filter-bar {{ margin-bottom: 30px; display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; }}
            .filter-select {{ 
                background: #21262d; 
                color: #fff; 
                border: 1px solid #388bfd; /* Fixed blue border */
                padding: 8px 35px 8px 15px; 
                border-radius: 20px; 
                cursor: pointer; 
                font-family: inherit;
                font-size: 14px;
                outline: none;
                transition: 0.2s;
                appearance: none; 
                -webkit-appearance: none;
                -moz-appearance: none;
                background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23ffffff%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E');
                background-repeat: no-repeat;
                background-position: right 12px top 50%; 
                background-size: 10px auto;
            }}
            
            .filter-select:hover, .filter-select:focus {{ 
                border-color: #388bfd; 
                background-color: #2a3039; 
                box-shadow: 0 0 0 2px rgba(56, 139, 253, 0.3);
            }}

            /* Export button - Fixed top right */
            .btn-export {{ 
                position: fixed; top: 10px; right: 10px; z-index: 1000;
                background: #161b22; border: 1px solid #30363d; color: #8b949e;
                padding: 6px 12px; border-radius: 6px; font-size: 11px;
                cursor: pointer; transition: 0.2s; background-image: none;
            }}
            .btn-export:hover {{ background: #21262d; border-color: #8b949e; color: #fff; }}

            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(var(--case-size), 1fr)); gap: 15px; width: 100%; margin: 0 auto; }}
            .case {{ background: #161b22; border-radius: 8px; border: 1px solid #30363d; overflow: hidden; position: relative; display: flex; flex-direction: column; }}
            
            /* Heart icon for TODO items */
            .todo-heart {{ 
                position: absolute; top: 5px; right: 8px; 
                color: #ff4d4d; font-size: 22px; cursor: pointer; 
                z-index: 10; text-shadow: 0 0 4px #000;
                user-select: none;
            }}

            .img-box {{ width: 100%; aspect-ratio: 1 / 1; display: flex; align-items: center; justify-content: center; background: #000; cursor: pointer; overflow: hidden; }}
            .img-box img {{ width: 100%; height: 100%; object-fit: cover; }}
            .empty-info {{ color: #484f58; font-size: 11px; font-weight: bold; text-align: center; padding: 5px; line-height: 1.2; }}
            .label {{ background: #21262d; padding: 8px 5px; font-weight: bold; font-size: 12px; border-top: 1px solid #30363d; cursor: pointer; transition: 0.2s; }}
            
            #tooltip {{ position: fixed; display: none; background: #0d1117; border: 1px solid #3498db; border-radius: 8px; padding: 12px; z-index: 2000; text-align: left; min-width: 220px; box-shadow: 0 8px 24px #000; pointer-events: none; }}
            #overlay {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 9999; justify-content: center; align-items: center; overflow: hidden; }}
            #fullImg {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); cursor: grab; user-select: none; max-width: 95%; max-height: 95%; transition: transform 0.05s linear; }}
        </style>
    </head>
    <body>
        <h1 id="catTitle">{LANG['CATALOG']}</h1>
        <div class="stats-header" id="statsText"></div>
        
        <div class="filter-bar">
            <select id="catSelect" class="filter-select" onchange="update()">
                {select_options}
            </select>
            <select id="familySelect" class="filter-select" onchange="filterF(this.value)">
                {family_options}
            </select>
            <select id="seasonSelect" class="filter-select" onchange="filterS(this.value)">
                <option value="Tous">{LANG['ALL']}</option>
                {season_options}
            </select>
            <select id="dirSelect" class="filter-select" onchange="filterD(this.value)">
                {dir_options}
            </select>
            <button onclick="exportTodo()" class="filter-select btn-export">💾 TODO.txt</button>
        </div>

        <div class="grid" id="grid"></div>
        <div id="tooltip"></div>
        <div id="overlay" onclick="if(event.target===this) closeM()"><img id="fullImg"></div>

        <script>
            const data = {json.dumps(final_json)};
            const stats = {json.dumps(stats)};
            const prefixes = {json.dumps(prefixes_js)};
            const thumbDir = "{CONFIG['THUMB_DIR']}";
            const userLat = {CONFIG['LATITUDE']}; 
            
            // INITIALIZATION: Sync TODO.txt (Python) with localStorage (Browser)
            let localTodo = JSON.parse(localStorage.getItem('astro_todo')) || {{}};
            for (let cat in data) {{
                if (!localTodo[cat]) localTodo[cat] = [];
                data[cat].forEach(obj => {{
                    // If marked in the file but missing from browser cache, add it
                    if (obj.todo && !localTodo[cat].includes(obj.id)) {{
                        localTodo[cat].push(obj.id);
                    }}
                }});
            }}
            localStorage.setItem('astro_todo', JSON.stringify(localTodo));

            // Family mapping using abbreviated types from LANG
            const FAMILIES = {{
                "Nébuleuse": [
                    "{LANG['TYPES']['N']}", "{LANG['TYPES']['NP']}", "{LANG['TYPES']['NS']}", 
                    "{LANG['TYPES']['SNR']}", "{LANG['TYPES']['EN']}", "{LANG['TYPES']['RN']}", 
                    "{LANG['TYPES']['E/RN']}", "{LANG['TYPES']['AN']}"
                ],
                "Galaxie": ["{LANG['TYPES']['G']}"],
                "Amas": [
                    "{LANG['TYPES']['AG']}", "{LANG['TYPES']['AO']}", 
                    "{LANG['TYPES']['D']}", "{LANG['TYPES']['A']}", "{LANG['TYPES']['AN']}"
                ]
            }};
            
            let currentSeason = 'Tous';
            let currentDir = 'Tous'; 
            let currentFamily = 'Tous';
            
            let scale = 1, posX = 0, posY = 0, isDragging = false, startX, startY;
            const m = document.getElementById("overlay"), mi = document.getElementById("fullImg"), t = document.getElementById('tooltip');

            function filterS(s) {{ currentSeason = s; update(); }}
            function filterD(d) {{ currentDir = d; update(); }}
            function filterF(f) {{ currentFamily = f; update(); }}

            // Trigger download of the TODO state as a text file
            function exportTodo() {{
                const blob = new Blob([JSON.stringify(localTodo, null, 4)], {{type: 'text/plain'}});
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'TODO.txt';
                a.click();
                window.URL.revokeObjectURL(url);
            }}

            // Toggle Heart status via Right Click
            function toggleHeart(e, catName, objId) {{
                e.preventDefault(); 
                if (!localTodo[catName]) localTodo[catName] = [];
                const idx = localTodo[catName].indexOf(objId);
                if (idx > -1) localTodo[catName].splice(idx, 1);
                else localTodo[catName].push(objId);
                localStorage.setItem('astro_todo', JSON.stringify(localTodo));
                update();
                return false;
            }}

            function update() {{
                const cat = document.getElementById('catSelect').value;
                const g = document.getElementById('grid'); 
                g.innerHTML = '';
                document.getElementById('catTitle').innerText = "{LANG['CATALOG']} " + cat;
                document.getElementById('statsText').innerText = "(" + stats[cat] + ")";
                
                data[cat].forEach(obj => {{
                    if (!obj.info || obj.info.length < 7) return;
                    const objType = obj.info[0].trim();
                    const objSeason = obj.info[1].trim();
                    const declin = parseFloat(obj.info[6]);
                    const objDir = declin > userLat ? "{LANG['NORTH']}" : "{LANG['SOUTH']}";
                    
                    // Apply filters: Family, Season, and Direction
                    if (currentFamily !== 'Tous' && !(FAMILIES[currentFamily] && FAMILIES[currentFamily].includes(objType))) return;
                    if (currentSeason !== 'Tous' && objSeason !== currentSeason) return;
                    if (currentDir !== 'Tous' && objDir !== currentDir) return;
                    
                    const d = document.createElement('div'); d.className = 'case';
                    d.onmousemove = (e) => showT(e, obj);
                    d.onmouseleave = () => t.style.display='none';
                    d.oncontextmenu = (e) => toggleHeart(e, cat, obj.id);
                    
                    const isTodo = localTodo[cat] && localTodo[cat].includes(obj.id);
                    const heart = isTodo ? '<div class="todo-heart">❤</div>' : '';

                    let displaySeason = currentSeason === 'Tous' ? `<br>(${{objSeason}})` : '';
                    let content = obj.thumb ? `<img src="${{obj.thumb}}">` : `<div class="empty-info">${{objType}}${{displaySeason}}</div>`;
                    
                    // Redirect to the generated high-quality JPG 'view' for TIF/TIFF images
                    let clickImg = obj.img;
                    if (obj.img && (obj.img.toLowerCase().endsWith('.tif') || obj.img.toLowerCase().endsWith('.tiff'))) {{
                        let baseName = obj.img.substring(0, obj.img.lastIndexOf('.'));
                        if (baseName.startsWith('thumb_')) baseName = baseName.substring(6);
                        clickImg = thumbDir + "/view_" + baseName + ".jpg";
                    }}
                    
                    // --- URL TELESCOPIUS logic ---
                    let tUrl = "https://telescopius.com/deep-sky-objects/";
                    if (obj.prefix === prefixes.Messier) {{
                        tUrl += "m-" + obj.id;
                    }} else if (obj.prefix === prefixes.Caldwell) {{
                        tUrl += "c-" + obj.id;
                    }} else if (obj.prefix === prefixes.RASC || obj.prefix === prefixes["O'Meara"]) {{
                        // Regex specific to extraction of the object number within catalogs like RASC
                        const regex = /(?:NGC|IC|SH2|BARNARD|VDB)[_ \-]?(\d+)/i;
                        const match = obj.tech_ref.match(regex);
                        const idNum = match ? match[1] : ""; 
                        if (obj.tech_ref.toUpperCase().includes("IC")) tUrl += "ic-" + idNum;
                        else if (obj.tech_ref.toUpperCase().includes("SH2")) tUrl += "sh2-" + idNum;
                        else if (obj.tech_ref.toUpperCase().includes("BARNARD")) tUrl += "barnard-" + idNum;
                        else if (obj.tech_ref.toUpperCase().includes("VDB")) tUrl += "vdb-" + idNum;
                        else tUrl += "ngc-" + idNum;
                    }}
                
                    const labelText = obj.tech_ref ? `${{obj.prefix}}${{obj.id}} - ${{obj.tech_ref}}` : `${{obj.prefix}}${{obj.id}}`;
                    const imgAction = obj.img ? `openM('${{clickImg}}')` : `window.open('${{tUrl}}', '_blank')`;

                    d.innerHTML = `${{heart}}
                                    <div class="img-box" onclick="${{imgAction}}">${{content}}</div>
                                    <div class="label" style="color:${{obj.label_color}}" onclick="window.open('${{tUrl}}', '_blank')">${{labelText}}</div>`;
                    g.appendChild(d);
                }});
            }}

            // Lightbox functionality: Open, Zoom (Wheel), and Pan (Drag)
            function openM(s) {{ if(!s) return; scale = 1; posX = 0; posY = 0; mi.src = s; m.style.display = "flex"; updateTransform(); }}
            function closeM() {{ m.style.display = "none"; }}
            function updateTransform() {{ mi.style.transform = `translate(calc(-50% + ${{posX}}px), calc(-50% + ${{posY}}px)) scale(${{scale}})`; }}
            
            m.addEventListener('wheel', e => {{ e.preventDefault(); scale = Math.min(Math.max(0.5, scale * (e.deltaY > 0 ? 0.9 : 1.1)), 10); updateTransform(); }}, {{passive: false}});
            mi.addEventListener('mousedown', e => {{ isDragging = true; startX = e.clientX - posX; startY = e.clientY - posY; e.preventDefault(); }});
            window.addEventListener('mousemove', e => {{ if (isDragging) {{ posX = e.clientX - startX; posY = e.clientY - startY; updateTransform(); }} }});
            window.addEventListener('mouseup', () => isDragging = false);

            // Display Tooltip with detailed object data
            function showT(e, obj) {{
                let html = "";
                if (obj.img) {{
                    html += `<div style="color:#4a9eff; font-weight:bold; font-size:12px; margin-bottom:2px;">${{obj.img}}</div>`;
                    html += `<div style="color:#888; font-size:11px; margin-bottom:8px;">Date: ${{obj.date}}</div>`;
                    html += `<hr style="border:0; border-top:1px solid #444; margin:8px 0;">`;
                }}
                
                let s = obj.info[4] || "";
                let c = "";
                let threshold = {limit_small}; 
                let dims = s.split(/[x×]/);
                let isSmall = dims.length > 0;

                // Detect small objects for visual highlighting (Orange color if below threshold)
                for (let i = 0; i < dims.length; i++) {{
                    let d = dims[i].trim();
                    let tm = 0, ts = 0;
                    let mMatch = d.match(/([0-9.]+)'($|[^'])/);
                    let sMatch = d.match(/([0-9.]+)(?:''|["])/);
                    if (mMatch) tm = parseFloat(mMatch[1]);
                    if (sMatch) ts = parseFloat(sMatch[1]);
                    if (!mMatch && !sMatch) {{
                        let v = parseFloat(d);
                        if (!isNaN(v)) tm = v;
                    }}
                    if ((tm * 60) + ts >= threshold || (tm * 60) + ts === 0) {{ isSmall = false; break; }}
                }}
                if (isSmall) c = ' style="color:orange;"';

                const declin = parseFloat(obj.info[6]);
                const isNorth = declin > userLat;
                const direction = isNorth ? "{LANG['NORTH']}" : "{LANG['SOUTH']}";
                const badgeColor = isNorth ? "#3498db" : "#f1c40f";

                html += `<div><strong>Type:</strong> ${{obj.info[0]}}</div>`;
                html += `<div><strong>Saison:</strong> ${{obj.info[1]}}</div>`;
                html += `<div><strong>Constellation:</strong> ${{obj.info[2]}}</div>`;
                html += `<div><strong>Magnitude:</strong> ${{obj.info[3]}}</div>`;
                html += `<div${{c}}><strong>Taille:</strong> ${{s}}</div>`;
                html += `<div><strong>Déclinaison:</strong> <span style="font-weight:bold; color:#c9d1d9;">${{obj.info[6]}}°</span> `;
                html += `<span style="font-size:9px; background:#21262d; color:${{badgeColor}}; padding:1px 4px; border-radius:3px; border:1px solid ${{badgeColor}}; margin-left:5px; vertical-align:middle; font-weight:bold;">${{direction}}</span></div>`;
                html += `<div><strong>Élévation Max:</strong> ${{obj.h_max}}°</div>`;
                html += `<hr style="border:0; border-top:1px solid #444; margin:8px 0;">`;
                html += `<div style="font-style:italic; color:#3498db; margin-top:5px;"><strong>${{obj.info[5]}}</strong></div>`;
                
                t.innerHTML = html; t.style.display = 'block';
                let x = e.clientX + 15, y = e.clientY + 15;
                // Collision detection with window edges for the tooltip
                if (x + 250 > window.innerWidth) x = e.clientX - t.offsetWidth - 15;
                if (y + t.offsetHeight > window.innerHeight) y = e.clientY - t.offsetHeight - 15;
                t.style.left = x + 'px'; t.style.top = y + 'px';
            }}
            update();
        </script>
    </body>
    </html>"""
    
    with open(CONFIG["OUTPUT_HTML"], "w", encoding="utf-8") as f: f.write(html_template)

if __name__ == "__main__": generate()
