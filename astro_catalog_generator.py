#=============================================================================
#                          (c) AEROPIC 2026
#           all in one Messier/Caldwell/RASC catalog generator
#  
# https://github.com/aeropic/Messier_Caldwell_RASC_catalog_generator
# http://www.messier.seds.org/xtra/similar/rasc-ngc.html
#
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
    "LIMIT_DIFFICILE": 20
}

LANG = {
    "PAGE_TITLE": "Mon Catalogue Astro",                     # "my astro catalog"
    "UNIT_LABEL": "objets",                                  # "objects"
    "ALL": "Tous",                                           # "All"
    "NO_DATE": "Date inconnue",                              # "unknown date"
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
    "SEASONS": {"P": "Printemps", "E": "Été", "A": "Automne", "H": "Hiver"}      # {"P": "Spring", "E": "Summer", "A": "Automn", "H": "Winter"}
}



T, S = LANG["TYPES"], LANG["SEASONS"]

# --- DATABASES (MESSIER, CALDWELL, RASC) ---
# --- you can translate the constellation name and the usual name but keep the NGC reference as is ---
# --- see below for the english translation
# Format: [Type, Season, Constellation, Mag, Size, Common Name, Dec, Tech_Ref]



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
    45: [T["AO"], S["H"], "Taureau", "1.6", "110'", "Les Pléiades", 24.1, "M45"],
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
    6: [T["G"], S["A"], "Cassiopée", "11.7", "2x2'", "NGC 185", 48.3, "NGC 185"],
    7: [T["EN"], S["A"], "Cassiopée", "-", "35x30'", "Nébuleuse Pacman", 56.6, "NGC 281"],
    8: [T["AO"], S["A"], "Cassiopée", "6.4", "13'", "Amas de la Chouette", 58.3, "NGC 457"],
    9: [T["AO"], S["A"], "Cassiopée", "7.1", "16'", "NGC 663", 61.2, "NGC 663"],
    10: [T["NP"], S["A"], "Cassiopée", "12.3", "34''", "NGC 1289", 61.3, "NGC 1289"],
    11: [T["NP"], S["A"], "Andromède", "9.2", "20''", "Nébuleuse de la Boule de Neige Bleue", 42.5, "NGC 7662"],
    12: [T["G"], S["A"], "Andromède", "10", "13.5x2.8'", "Galaxie de l'Aiguille d'Argent", 42.3, "NGC 891"],
    13: [T["G"], S["A"], "Sculpteur", "7.1", "25.1x7.4'", "Galaxie du Sculpteur", -25.3, "NGC 253"],
    14: [T["G"], S["A"], "Bélier", "10.3", "7.1x4.5'", "Galaxie Spirale", 19.0, "NGC 772"],
    15: [T["NP"], S["A"], "Baleine", "8.0", "3'45''", "Nébuleuse du Crâne", -11.9, "NGC 246"],
    16: [T["G"], S["A"], "Baleine", "10.1", "5.2x4.4'", "NGC 936", -1.1, "NGC 936"],
    17: [T["AO"], S["A"], "Persée", "4.4", "30'/30'", "Double Amas de Persée", 57.1, "NGC 869"],
    18: [T["G"], S["A"], "Persée", "9.5", "8.7x4.3'", "NGC 1023", 39.0, "NGC 1023"],
    19: [T["EN"], S["A"], "Persée", "-", "3.0x3.0'", "NGC 1491", 51.3, "NGC 1491"],
    20: [T["NP"], S["A"], "Girafe", "12.0", "52''", "NGC 1501", 60.9, "NGC 1501"],
    21: [T["G"], S["A"], "Eridan", "9.9", "7.8x6.9'", "Galaxie NGC 1232", -20.6, "NGC 1232"],
    22: [T["NP"], S["A"], "Eridan", "10.4", "18''", "NGC 1535", -12.7, "NGC 1535"],
    23: [T["NP"], S["H"], "Taureau", "10.8", "1'54''", "NGC 1514", 30.8, "NGC 1514"],
    24: [T["E/RN"], S["H"], "Cocher", "-", "3.0x3.0'", "NGC 1931", 34.2, "NGC 1931"],
    25: [T["RN"], S["H"], "Orion", "-", "8.0x5.0'", "NGC 1788", -3.3, "NGC 1788"],
    26: [T["E/RN"], S["H"], "Orion", "-", "40x25'", "Nébuleuse Courante", -4.7, "NGC 1973"],
    27: [T["NP"], S["H"], "Orion", "12.4", "18''", "NGC 2022", 9.1, "NGC 2022"],
    28: [T["EN"], S["H"], "Orion", "-", "30x30'", "Nébuleuse de la Flamme", -1.9, "NGC 2024"],
    29: [T["AO"], S["H"], "Orion", "8.5", "10'", "NGC 2194", 12.8, "NGC 2194"],
    30: [T["NP"], S["H"], "Gémeaux", "13.0", "55''", "NGC 2371", 29.5, "NGC 2371"],
    31: [T["NP"], S["H"], "Gémeaux", "8.3", "13''", "Nébuleuse de l'Esquimau", 20.9, "NGC 2392"],
    32: [T["EN"], S["H"], "Licorne", "-", "80x60'", "Nébuleuse de la Rosette", 5.0, "NGC 2237"],
    33: [T["E/RN"], S["H"], "Licorne", "var", "2x1'", "Nébuleuse Variable de Hubble", 8.7, "NGC 2261"],
    34: [T["EN"], S["H"], "Grand Chien", "-", "8.0x6.0'", "Nébuleuse du Casque de Thor", -13.2, "NGC 2359"],
    35: [T["NP"], S["H"], "Poupe", "10.3", "14''", "NGC 2440", -18.2, "NGC 2440"],
    36: [T["AO"], S["H"], "Poupe", "6.5", "22'", "NGC 2539", -12.8, "NGC 2539"],
    37: [T["G"], S["H"], "Girafe", "8.4", "17.8x11.0'", "NGC 2403", 65.6, "NGC 2403"],
    38: [T["G"], S["H"], "Girafe", "10.1", "5.1x4.4'", "NGC 2655", 78.2, "NGC 2655"],
    39: [T["G"], S["P"], "Lynx", "9.7", "9.3x2.5'", "NGC 2683", 33.4, "NGC 2683"],
    40: [T["G"], S["P"], "Grande Ourse", "9.3", "8.1x3.8'", "NGC 2841", 51.0, "NGC 2841"],
    41: [T["G"], S["P"], "Grande Ourse", "10.6", "7.6x1.7'", "NGC 3079", 55.7, "NGC 3079"],
    42: [T["G"], S["P"], "Grande Ourse", "9.7", "6.9x6.8'", "NGC 3184", 41.4, "NGC 3184"],
    43: [T["G"], S["P"], "Grande Ourse", "10.9", "5.4x1.5'", "NGC 3877", 47.5, "NGC 3877"],
    44: [T["G"], S["P"], "Grande Ourse", "9.8", "3.8x2.5'", "NGC 3941", 45.0, "NGC 3941"],
    45: [T["G"], S["P"], "Grande Ourse", "10.7", "5.1x1.4'", "NGC 4026", 50.9, "NGC 4026"],
    46: [T["G"], S["P"], "Grande Ourse", "10.5", "5.8x2.5'", "NGC 4088", 50.5, "NGC 4088"],
    47: [T["G"], S["P"], "Grande Ourse", "11.9", "6.9x1.7'", "NGC 4157", 50.5, "NGC 4157"],
    48: [T["G"], S["P"], "Grande Ourse", "9.6", "5.5x2.3'", "NGC 4605", 61.6, "NGC 4605"],
    49: [T["G"], S["P"], "Sextant", "9.2", "8.3x3.2'", "Galaxie du Fuseau", -7.7, "NGC 3115"],
    50: [T["NP"], S["P"], "Hydre", "8.6", "16''", "Le Fantôme de Jupiter", -18.6, "NGC 3242"],
    51: [T["G"], S["P"], "Petit Lion", "11.7", "5.9x1.7'", "NGC 3003", 33.4, "NGC 3003"],
    52: [T["G"], S["P"], "Petit Lion", "9.9", "6.9x6.5'", "NGC 3344", 25.0, "NGC 3344"],
    53: [T["G"], S["P"], "Petit Lion", "11.3", "6.2x1.5'", "NGC 3432", 36.6, "NGC 3432"],
    54: [T["G"], S["P"], "Lion", "8.9", "12.6x6.6'", "NGC 2903", 21.5, "NGC 2903"],
    55: [T["G"], S["P"], "Lion", "9.9", "5.9x2.6'", "NGC 3384", 12.6, "NGC 3384"],
    56: [T["G"], S["P"], "Lion", "8.7", "9.5x5.0'", "NGC 3521", -0.0, "NGC 3521"],
    57: [T["G"], S["P"], "Lion", "10.0", "3.7x3.2'", "NGC 3607", 18.0, "NGC 3607"],
    58: [T["G"], S["P"], "Lion", "9.5", "14.8x3.6'", "Galaxie de l'Arête", 13.6, "NGC 3628"],
    59: [T["G"], S["P"], "Chiens de Chasse", "10.8", "4.8x1.1'", "NGC 4111", 43.1, "NGC 4111"],
    60: [T["G"], S["P"], "Chiens de Chasse", "9.7", "7.9x6.3'", "NGC 4214", 36.3, "NGC 4214"],
    61: [T["G"], S["P"], "Chiens de Chasse", "10.2", "16.2x2.5'", "NGC 4244", 37.8, "NGC 4244"],
    62: [T["G"], S["P"], "Chiens de Chasse", "9.4", "5.1x3.7'", "NGC 4449", 44.1, "NGC 4449"],
    63: [T["G"], S["P"], "Chiens de Chasse", "9.8", "5.9x3.1'", "NGC 4490", 41.6, "NGC 4490"],
    64: [T["G"], S["P"], "Chiens de Chasse", "9.3", "15.1x3.3'", "Galaxie de la Baleine", 32.5, "NGC 4631"],
    65: [T["G"], S["P"], "Chiens de Chasse", "10.4", "13.8x3.3'", "La Crosse de Hockey", 32.2, "NGC 4656"],
    66: [T["G"], S["P"], "Chiens de Chasse", "9.8", "5.9x3.1'", "NGC 5005", 37.1, "NGC 5005"],
    67: [T["G"], S["P"], "Chiens de Chasse", "10.1", "10.5x5.6'", "NGC 5033", 36.6, "NGC 5033"],
    68: [T["G"], S["P"], "Chevelure de Bérénice", "10.4", "6.9x2.8'", "NGC 4274", 29.6, "NGC 4274"],
    69: [T["G"], S["P"], "Chevelure de Bérénice", "10.2", "3.6x2.2'", "NGC 4414", 31.2, "NGC 4414"],
    70: [T["G"], S["P"], "Chevelure de Bérénice", "9.8", "4.8x3.8'", "NGC 4494", 25.8, "NGC 4494"],
    71: [T["G"], S["P"], "Chevelure de Bérénice", "9.8", "10.5x4.9'", "NGC 4559", 28.0, "NGC 4559"],
    72: [T["G"], S["P"], "Chevelure de Bérénice", "9.6", "16.2x2.8'", "Galaxie de l'Aiguille", 26.0, "NGC 4565"],
    73: [T["G"], S["P"], "Chevelure de Bérénice", "9.2", "11.0x7.9'", "NGC 4725", 25.5, "NGC 4725"],
    74: [T["G"], S["P"], "Corbeau", "10.7", "~3x2'", "Galaxies des Antennes", -18.9, "NGC 4038"],
    75: [T["NP"], S["P"], "Corbeau", "10.3", "45''", "NGC 4361", -18.8, "NGC 4361"],
    76: [T["G"], S["P"], "Vierge", "9.9", "8.3x2.2'", "NGC 4216", 13.1, "NGC 4216"],
    77: [T["G"], S["P"], "Vierge", "11.0", "5.1x1.4'", "NGC 4388", 12.7, "NGC 4388"],
    78: [T["G"], S["P"], "Vierge", "10.1", "9.3x3.9'", "Les Yeux", 13.0, "NGC 4438"],
    79: [T["G"], S["P"], "Vierge", "10.5", "10.2x1.9'", "NGC 4517", 0.1, "NGC 4517"],
    80: [T["G"], S["P"], "Vierge", "9.6", "7.6x2.3'", "NGC 4526", 7.7, "NGC 4526"],
    81: [T["G"], S["P"], "Vierge", "9.8", "6.8x5.0'", "NGC 4535", 8.2, "NGC 4535"],
    82: [T["G"], S["P"], "Vierge", "~11", "4.6x2.1'", "Les Jumeaux Siamois", 11.3, "NGC 4567"],
    83: [T["G"], S["P"], "Vierge", "9.6", "3.5x2.7'", "NGC 4699", -8.7, "NGC 4699"],
    84: [T["G"], S["P"], "Vierge", "10.2", "8.7x1.6'", "NGC 4762", 11.2, "NGC 4762"],
    85: [T["G"], S["P"], "Vierge", "10.6", "7.9x1.7'", "NGC 5746", 1.9, "NGC 5746"],
    86: [T["AG"], S["P"], "Bouvier", "9.1", "11.0'", "NGC 5466", 28.5, "NGC 5466"],
    87: [T["G"], S["P"], "Dragon", "10.4", "12.3x1.8'", "Galaxie de l'Éclat", 56.3, "NGC 5907"],
    88: [T["G"], S["P"], "Dragon", "10.2", "6.2x2.3'", "NGC 6503", 70.1, "NGC 6503"],
    89: [T["NP"], S["P"], "Dragon", "8.8", "18''", "Nébuleuse de l'Œil de Chat", 66.6, "NGC 6543"],
    90: [T["NP"], S["E"], "Hercule", "9.3", "14''", "NGC 6210", 23.8, "NGC 6210"],
    91: [T["NP"], S["E"], "Ophiuchus", "10.4", "30''", "Nébuleuse du Petit Fantôme", -17.8, "NGC 6369"],
    92: [T["NP"], S["E"], "Ophiuchus", "9.0", "8''", "NGC 6572", 6.8, "NGC 6572"],
    93: [T["AO"], S["E"], "Ophiuchus", "4.6", "27'", "NGC 6633", 6.5, "NGC 6633"],
    94: [T["AG"], S["E"], "Ecu de Sobieski", "8.2", "7.2'", "NGC 6712", -8.7, "NGC 6712"],
    95: [T["NP"], S["E"], "Aigle", "11.8", "1'49''", "NGC 6781", 6.5, "NGC 6781"],
    96: [T["AO"], S["E"], "Cygne", "7.3", "5'", "NGC 6819", 40.2, "NGC 6819"],
    97: [T["NP"], S["E"], "Cygne", "9.8", "30''", "Nébuleuse de l'Œil Clignotant", 50.5, "NGC 6826"],
    98: [T["SNR"], S["E"], "Cygne", "-", "20x10'", "Nébuleuse du Croissant", 38.4, "NGC 6888"],
    "99a": [T["SNR"], S["E"], "Cygne", "-", "70x6'", "Petite Dentelle du Cygne", 30.7, "NGC 6960"],
    "99b": [T["SNR"], S["E"], "Cygne", "-", "78x8'", "Grande Dentelle du Cygne", 31.7, "NGC 6992"],
    100: [T["EN"], S["E"], "Cygne", "-", "120x100'", "Nébuleuse de l'Amérique du Nord", 44.3, "NGC 7000"],
    101: [T["NP"], S["E"], "Cygne", "10.4", "15''", "NGC 7027", 42.2, "NGC 7027"],
    102: [T["NP"], S["E"], "Sagittaire", "11.8", "34''", "NGC 6445", -16.2, "NGC 6445"],
    103: [T["AO"], S["E"], "Sagittaire", "8.1", "6'", "NGC 6520", -27.9, "NGC 6520"],
    104: [T["NP"], S["E"], "Sagittaire", "9.9", "17''", "NGC 6818", -16.2, "NGC 6818"],
    105: [T["AO"], S["E"], "Petit Renard", "8.8", "3.2'", "NGC 6802", 20.3, "NGC 6802"],
    106: [T["AO"], S["E"], "Petit Renard", "6.3", "31'", "NGC 6940", 28.3, "NGC 6940"],
    107: [T["AO"], S["E"], "Céphée", "7.8", "8'", "NGC 6939", 60.6, "NGC 6939"],
    108: [T["G"], S["E"], "Céphée", "8.9", "11.0x9.8'", "Galaxie du Feu d'Artifice", 60.1, "NGC 6946"],
    109: [T["RN"], S["E"], "Céphée", "-", "8x7'", "NGC 7129", 66.1, "NGC 7129"],
    110: [T["NP"], S["E"], "Céphée", "10.2", "37''", "Nébuleuse du Nœud Coulant", 72.5, "NGC 40"]
}

"""
# --- ENGLISH TRANSLATED DATABASES (MESSIER, CALDWELL, RASC) ---
# remove the triple quote above and at the end of the database (python bloc comment)
# and bloc comment the french database



# --- MESSIER CATALOG (English) ---
MESSIER_DATA = {
    1: [T["SNR"], S["H"], "Taurus", "8.4", "6'x4'", "Crab Nebula", 22.0, "NGC 1952"],
    2: [T["AG"], S["A"], "Aquarius", "6.3", "16'", "Aquarius Cluster", -0.8, "NGC 7089"],
    3: [T["AG"], S["P"], "Canes Venatici", "6.2", "18'", "Canes Venatici Cluster", 28.4, "NGC 5272"],
    4: [T["AG"], S["E"], "Scorpius", "5.9", "36'", "Scorpius Cluster", -26.5, "NGC 6121"],
    5: [T["AG"], S["P"], "Serpens", "5.7", "23'", "Serpens Cluster", 2.1, "NGC 5904"],
    6: [T["AO"], S["E"], "Scorpius", "4.2", "25'", "Butterfly Cluster", -32.2, "NGC 6405"],
    7: [T["AO"], S["E"], "Scorpius", "3.3", "80'", "Ptolemy's Cluster", -34.8, "NGC 6475"],
    8: [T["N"], S["E"], "Sagittarius", "6.0", "90'x40'", "Lagoon Nebula", -24.4, "NGC 6523"],
    9: [T["AG"], S["E"], "Ophiuchus", "7.7", "11'", "Ophiuchus Cluster", -18.5, "NGC 6333"],
    10: [T["AG"], S["E"], "Ophiuchus", "6.6", "20'", "Ophiuchus Cluster", -4.1, "NGC 6254"],
    11: [T["AO"], S["E"], "Scutum", "5.8", "14'", "Wild Duck Cluster", -6.3, "NGC 6705"],
    12: [T["AG"], S["E"], "Ophiuchus", "6.7", "16'", "Ophiuchus Cluster", -1.9, "NGC 6218"],
    13: [T["AG"], S["E"], "Hercules", "5.8", "20'", "Great Hercules Cluster", 36.5, "NGC 6205"],
    14: [T["AG"], S["E"], "Ophiuchus", "7.6", "11'", "Ophiuchus Cluster", -3.3, "NGC 6402"],
    15: [T["AG"], S["A"], "Pegasus", "6.2", "18'", "Pegasus Cluster", 12.2, "NGC 7078"],
    16: [T["N"], S["E"], "Serpens", "6.0", "7'", "Eagle Nebula", -13.8, "NGC 6611"],
    17: [T["N"], S["E"], "Sagittarius", "6.0", "11'", "Omega Nebula", -16.2, "NGC 6618"],
    18: [T["AO"], S["E"], "Sagittarius", "7.5", "9'", "Black Swan", -17.1, "NGC 6613"],
    19: [T["AG"], S["E"], "Ophiuchus", "6.8", "17'", "Ophiuchus Cluster", -26.3, "NGC 6273"],
    20: [T["N"], S["E"], "Sagittarius", "6.3", "28'", "Trifid Nebula", -23.0, "NGC 6514"],
    21: [T["AO"], S["E"], "Sagittarius", "6.5", "13'", "Sagittarius Cluster", -22.5, "NGC 6531"],
    22: [T["AG"], S["E"], "Sagittarius", "5.1", "32'", "Great Sagittarius Cluster", -23.9, "NGC 6656"],
    23: [T["AO"], S["E"], "Sagittarius", "6.9", "27'", "Sagittarius Cluster", -19.0, "NGC 6494"],
    24: [T["NS"], S["E"], "Sagittarius", "4.6", "90'", "Small Sagittarius Star Cloud", -18.4, "NGC 6603"],
    25: [T["AO"], S["E"], "Sagittarius", "4.6", "32'", "Sagittarius Cluster", -19.2, "IC 4725"],
    26: [T["AO"], S["E"], "Scutum", "8.0", "15'", "Scutum Cluster", -9.4, "NGC 6694"],
    27: [T["NP"], S["E"], "Vulpecula", "7.4", "8'x6'", "Dumbbell Nebula", 22.7, "NGC 6853"],
    28: [T["AG"], S["E"], "Sagittarius", "6.8", "11'", "Sagittarius Cluster", -24.9, "NGC 6626"],
    29: [T["AO"], S["E"], "Cygnus", "7.1", "7'", "Cygnus Cluster", 38.5, "NGC 6913"],
    30: [T["AG"], S["A"], "Capricornus", "7.2", "12'", "Capricornus Cluster", -23.2, "NGC 7099"],
    31: [T["G"], S["A"], "Andromeda", "3.4", "190'x60'", "Andromeda Galaxy", 41.3, "NGC 224"],
    32: [T["G"], S["A"], "Andromeda", "8.1", "8'x6'", "Le Gentil (M32)", 40.9, "NGC 221"],
    33: [T["G"], S["A"], "Triangulum", "5.7", "70'x40'", "Triangulum Galaxy", 30.7, "NGC 598"],
    34: [T["AO"], S["H"], "Perseus", "5.2", "35'", "Perseus Cluster", 42.8, "NGC 1039"],
    35: [T["AO"], S["H"], "Gemini", "5.1", "28'", "Gemini Cluster", 24.3, "NGC 2168"],
    36: [T["AO"], S["H"], "Auriga", "6.0", "12'", "Auriga Cluster", 34.1, "NGC 1960"],
    37: [T["AO"], S["H"], "Auriga", "5.6", "24'", "Auriga Cluster", 32.5, "NGC 2099"],
    38: [T["AO"], S["H"], "Auriga", "6.4", "21'", "Starfish Cluster", 35.8, "NGC 1912"],
    39: [T["AO"], S["E"], "Cygnus", "4.6", "32'", "Cygnus Cluster", 48.4, "NGC 7092"],
    40: [T["D"], S["P"], "Ursa Major", "8.4", "0.8'", "Winnecke 4", 58.1, "WNC 4"],
    41: [T["AO"], S["H"], "Canis Major", "4.5", "38'", "Little Beehive Cluster", -20.7, "NGC 2287"],
    42: [T["N"], S["H"], "Orion", "4.0", "85'x60'", "Orion Nebula", -5.4, "NGC 1976"],
    43: [T["N"], S["H"], "Orion", "9.0", "20'x15'", "De Mairan's Nebula", -5.2, "NGC 1982"],
    44: [T["AO"], S["H"], "Cancer", "3.1", "95'", "Beehive Cluster", 19.7, "NGC 2632"],
    45: [T["AO"], S["H"], "Taurus", "1.6", "110'", "The Pleiades", 24.1, "M45"],
    46: [T["AO"], S["H"], "Puppis", "6.1", "27'", "Puppis Cluster", -14.8, "NGC 2437"],
    47: [T["AO"], S["H"], "Puppis", "4.4", "30'", "Puppis Cluster", -14.4, "NGC 2422"],
    48: [T["AO"], S["H"], "Hydra", "5.8", "54'", "Hydra Cluster", -5.8, "NGC 2548"],
    49: [T["G"], S["P"], "Virgo", "8.4", "10'x9'", "Virgo Galaxy", 8.0, "NGC 4472"],
    50: [T["AO"], S["H"], "Monoceros", "5.9", "16'", "Monoceros Cluster", -8.3, "NGC 2323"],
    51: [T["G"], S["P"], "Canes Venatici", "8.4", "11'x7'", "Whirlpool Galaxy", 47.2, "NGC 5194"],
    52: [T["AO"], S["A"], "Cassiopeia", "6.9", "13'", "Cassiopeia Cluster", 61.6, "NGC 7654"],
    53: [T["AG"], S["P"], "Coma Berenices", "7.6", "13'", "Coma Cluster", 18.2, "NGC 5024"],
    54: [T["AG"], S["E"], "Sagittarius", "7.6", "12'", "Sagittarius Cluster", -30.5, "NGC 6715"],
    55: [T["AG"], S["E"], "Sagittarius", "6.3", "19'", "Sagittarius Cluster", -30.9, "NGC 6809"],
    56: [T["AG"], S["E"], "Lyra", "8.3", "9'", "Lyra Cluster", 33.0, "NGC 6779"],
    57: [T["NP"], S["E"], "Lyra", "8.8", "1.5'x1'", "Ring Nebula", 33.0, "NGC 6720"],
    58: [T["G"], S["P"], "Virgo", "9.7", "6'x5'", "Virgo Galaxy", 11.8, "NGC 4579"],
    59: [T["G"], S["P"], "Virgo", "10.6", "5'x4'", "Virgo Galaxy", 11.6, "NGC 4621"],
    60: [T["G"], S["P"], "Virgo", "8.8", "7'x6'", "Virgo Galaxy", 11.6, "NGC 4649"],
    61: [T["G"], S["P"], "Virgo", "9.7", "6'x6'", "Virgo Galaxy", 4.5, "NGC 4303"],
    62: [T["AG"], S["E"], "Ophiuchus", "6.5", "15'", "Ophiuchus Cluster", -30.1, "NGC 6266"],
    63: [T["G"], S["P"], "Canes Venatici", "8.6", "12'x8'", "Sunflower Galaxy", 42.0, "NGC 5055"],
    64: [T["G"], S["P"], "Coma Berenices", "8.5", "10'x5'", "Black Eye Galaxy", 21.7, "NGC 4826"],
    65: [T["G"], S["P"], "Leo", "9.3", "10'x3'", "Leo Galaxy", 13.1, "NGC 3623"],
    66: [T["G"], S["P"], "Leo", "8.9", "9'x4'", "Leo Galaxy", 13.0, "NGC 3627"],
    67: [T["AO"], S["H"], "Cancer", "6.1", "30'", "King Cobra Cluster", 11.8, "NGC 2682"],
    68: [T["AG"], S["P"], "Hydra", "7.8", "11'", "Hydra Cluster", -26.7, "NGC 4590"],
    69: [T["AG"], S["E"], "Sagittarius", "7.6", "10'", "Sagittarius Cluster", -32.3, "NGC 6637"],
    70: [T["AG"], S["E"], "Sagittarius", "7.9", "9'", "Sagittarius Cluster", -32.3, "NGC 6681"],
    71: [T["AG"], S["E"], "Sagitta", "8.2", "7'", "Sagitta Cluster", 18.8, "NGC 6838"],
    72: [T["AG"], S["A"], "Aquarius", "9.3", "7'", "Aquarius Cluster", -12.5, "NGC 6981"],
    73: [T["A"], S["A"], "Aquarius", "9.0", "2.8'", "Aquarius Asterism", -12.6, "NGC 6994"],
    74: [T["G"], S["A"], "Pisces", "9.4", "10'x10'", "Phantom Galaxy", 15.8, "NGC 628"],
    75: [T["AG"], S["E"], "Sagittarius", "8.5", "7'", "Sagittarius Cluster", -21.9, "NGC 6864"],
    76: [T["NP"], S["A"], "Perseus", "10.1", "2.7'x1.8'", "Little Dumbbell Nebula", 51.6, "NGC 650"],
    77: [T["G"], S["A"], "Cetus", "8.9", "7'x6'", "Cetus Galaxy", -0.0, "NGC 1068"],
    78: [T["N"], S["H"], "Orion", "8.3", "8'x6'", "M78 (Nebula)", 0.1, "NGC 2068"],
    79: [T["AG"], S["H"], "Lepus", "7.7", "10'", "Lepus Cluster", -24.5, "NGC 1904"],
    80: [T["AG"], S["E"], "Scorpius", "7.3", "10'", "Scorpius Cluster", -22.9, "NGC 6093"],
    81: [T["G"], S["P"], "Ursa Major", "6.9", "26'x14'", "Bode's Galaxy", 69.1, "NGC 3031"],
    82: [T["G"], S["P"], "Ursa Major", "8.4", "11'x4'", "Cigar Galaxy", 69.7, "NGC 3034"],
    83: [T["G"], S["P"], "Hydra", "7.5", "13'x11'", "Southern Pinwheel Galaxy", -29.9, "NGC 5236"],
    84: [T["G"], S["P"], "Virgo", "9.1", "6'x6'", "Virgo Galaxy", 12.9, "NGC 4374"],
    85: [T["G"], S["P"], "Coma Berenices", "9.1", "7'x5'", "Coma Galaxy", 18.2, "NGC 4382"],
    86: [T["G"], S["P"], "Virgo", "8.9", "9'x6'", "Virgo Galaxy", 12.9, "NGC 4406"],
    87: [T["G"], S["P"], "Virgo", "8.6", "8'x8'", "Virgo A", 12.4, "NGC 4486"],
    88: [T["G"], S["P"], "Coma Berenices", "9.6", "7'x4'", "Coma Galaxy", 14.4, "NGC 4501"],
    89: [T["G"], S["P"], "Virgo", "9.8", "5'x5'", "Virgo Galaxy", 12.6, "NGC 4552"],
    90: [T["G"], S["P"], "Virgo", "9.5", "10'x4'", "Virgo Galaxy", 13.2, "NGC 4569"],
    91: [T["G"], S["P"], "Coma Berenices", "10.2", "5'x4'", "Coma Galaxy", 14.5, "NGC 4548"],
    92: [T["AG"], S["E"], "Hercules", "6.3", "14'", "Hercules Cluster", 43.1, "NGC 6341"],
    93: [T["AO"], S["H"], "Puppis", "6.0", "22'", "Puppis Cluster", -23.9, "NGC 2447"],
    94: [T["G"], S["P"], "Canes Venatici", "8.2", "11'x9'", "Croc's Eye Galaxy", 41.1, "NGC 4736"],
    95: [T["G"], S["P"], "Leo", "9.7", "7'x5'", "Leo Galaxy", 11.7, "NGC 3351"],
    96: [T["G"], S["P"], "Leo", "9.2", "8'x5'", "Leo Galaxy", 11.8, "NGC 3368"],
    97: [T["NP"], S["P"], "Ursa Major", "9.9", "3.4'", "Owl Nebula", 55.0, "NGC 3587"],
    98: [T["G"], S["P"], "Coma Berenices", "10.1", "10'x3'", "Coma Galaxy", 14.9, "NGC 4192"],
    99: [T["G"], S["P"], "Coma Berenices", "9.9", "5'x5'", "Coma Pinwheel Galaxy", 14.4, "NGC 4254"],
    100: [T["G"], S["P"], "Coma Berenices", "9.3", "7'x6'", "Coma Galaxy", 15.8, "NGC 4321"],
    101: [T["G"], S["P"], "Ursa Major", "7.9", "28'x27'", "Pinwheel Galaxy", 54.4, "NGC 5457"],
    102: [T["G"], S["P"], "Draco", "9.9", "6'x3'", "Spindle Galaxy", 55.8, "NGC 5866"],
    103: [T["AO"], S["A"], "Cassiopeia", "7.4", "6'", "Cassiopeia Cluster", 60.7, "NGC 581"],
    104: [T["G"], S["P"], "Virgo", "8.0", "9'x4'", "Sombrero Galaxy", -11.6, "NGC 4594"],
    105: [T["G"], S["P"], "Leo", "9.3", "5'x5'", "Leo Galaxy", 12.6, "NGC 3379"],
    106: [T["G"], S["P"], "Canes Venatici", "8.4", "18'x7'", "Canes Venatici Galaxy", 47.3, "NGC 4258"],
    107: [T["AG"], S["E"], "Ophiuchus", "7.9", "13'", "Ophiuchus Cluster", -13.1, "NGC 6171"],
    108: [T["G"], S["P"], "Ursa Major", "10.0", "9'x2'", "Surfboard Galaxy", 53.4, "NGC 3556"],
    109: [T["G"], S["P"], "Ursa Major", "9.8", "8'x5'", "Ursa Major Galaxy", 53.4, "NGC 3992"],
    110: [T["G"], S["A"], "Andromeda", "8.1", "17'x10'", "Andromeda Galaxy (sat.)", 41.7, "NGC 205"]
}

# --- CALDWELL CATALOG (English) ---
CALDWELL_DATA = {
    1: [T["AO"], S["A"], "Cepheus", "8.1", "13'", "NGC 188", 85.3, "NGC 188"],
    2: [T["NP"], S["A"], "Cepheus", "10.2", "37''", "Bow-Tie Nebula", 72.5, "NGC 40"],
    3: [T["G"], S["A"], "Draco", "9.7", "18.6'x6.9'", "Draco Galaxy", 69.5, "NGC 4236"],
    4: [T["RN"], S["A"], "Cepheus", "-", "18'x18'", "Iris Nebula", 68.2, "NGC 7023"],
    5: [T["G"], S["H"], "Camelopardalis", "8.4", "21.1'x20.9'", "Camelopardalis Galaxy", 68.1, "IC 342"],
    6: [T["NP"], S["P"], "Draco", "8.1", "18''", "Cat's Eye Nebula", 66.6, "NGC 6543"],
    7: [T["G"], S["H"], "Camelopardalis", "8.4", "24.9'x12'", "NGC 2403", 65.6, "NGC 2403"],
    8: [T["AO"], S["A"], "Cassiopeia", "7.1", "5.8'", "NGC 559", 63.3, "NGC 559"],
    9: [T["EN"], S["A"], "Cepheus", "-", "50'x40'", "Cave Nebula", 62.3, "Sh2-155"],
    10: [T["AO"], S["A"], "Cassiopeia", "7.1", "16'", "NGC 663", 61.2, "NGC 663"],
    11: [T["EN"], S["A"], "Cassiopeia", "-", "15'x8'", "Bubble Nebula", 61.2, "NGC 7635"],
    12: [T["G"], S["A"], "Cepheus", "8.9", "11.5'x11.5'", "Fireworks Galaxy", 60.1, "NGC 6946"],
    13: [T["AO"], S["A"], "Cassiopeia", "6.7", "13'", "Owl Cluster", 58.3, "NGC 457"],
    14: [T["AO"], S["A"], "Perseus", "4.4", "30'", "Double Cluster", 57.1, "NGC 869"],
    15: [T["NP"], S["E"], "Cygnus", "9.8", "30''", "Blinking Planetary Nebula", 50.5, "NGC 6826"],
    16: [T["AO"], S["E"], "Lacerta", "6.4", "20'", "NGC 7243", 49.9, "NGC 7243"],
    17: [T["G"], S["A"], "Cassiopeia", "9.1", "13'x8'", "NGC 147", 48.5, "NGC 147"],
    18: [T["G"], S["A"], "Cassiopeia", "9.2", "12'x10'", "NGC 185", 48.3, "NGC 185"],
    19: [T["EN"], S["A"], "Cepheus", "-", "12'", "Cocoon Nebula", 47.3, "IC 5146"],
    20: [T["EN"], S["E"], "Cygnus", "-", "120'x100'", "North America Nebula", 44.3, "NGC 7000"],
    21: [T["G"], S["P"], "Canes Venatici", "9.4", "5'x4'", "NGC 4449", 44.1, "NGC 4449"],
    22: [T["NP"], S["A"], "Andromeda", "8.3", "20''", "Blue Snowball Nebula", 42.5, "NGC 7662"],
    23: [T["G"], S["A"], "Andromeda", "10.0", "13'x3'", "Silver Needle Galaxy", 42.3, "NGC 891"],
    24: [T["G"], S["H"], "Perseus", "11.7", "2'x2'", "Perseus A", 41.5, "NGC 1275"],
    25: [T["AG"], S["H"], "Lynx", "10.4", "4'", "Intergalactic Wanderer", 38.9, "NGC 2419"],
    26: [T["G"], S["P"], "Canes Venatici", "10.2", "16'x2'", "NGC 4244", 37.8, "NGC 4244"],
    27: [T["EN"], S["E"], "Cygnus", "-", "20'x10'", "Crescent Nebula", 38.4, "NGC 6888"],
    28: [T["AO"], S["A"], "Andromeda", "5.2", "45'", "NGC 752", 37.8, "NGC 752"],
    29: [T["G"], S["P"], "Canes Venatici", "9.8", "5'x3'", "NGC 5005", 37.1, "NGC 5005"],
    30: [T["G"], S["A"], "Pegasus", "9.5", "11'x4'", "Deer Lick Galaxy", 34.4, "NGC 7331"],
    31: [T["EN"], S["H"], "Auriga", "-", "30'x20'", "Flaming Star Nebula", 34.3, "IC 405"],
    32: [T["G"], S["P"], "Canes Venatici", "9.3", "15'x3'", "Whale Galaxy", 32.5, "NGC 4631"],
    33: [T["SNR"], S["E"], "Cygnus", "-", "78'x8'", "Eastern Veil Nebula", 31.7, "NGC 6992"],
    34: [T["SNR"], S["E"], "Cygnus", "-", "70'x6'", "Western Veil Nebula", 30.7, "NGC 6960"],
    35: [T["G"], S["P"], "Coma Berenices", "11.4", "1'x1'", "Coma Cluster", 28.0, "NGC 4889"],
    36: [T["G"], S["P"], "Coma Berenices", "9.6", "11'x5'", "NGC 4559", 28.0, "NGC 4559"],
    37: [T["AO"], S["E"], "Vulpecula", "6.0", "14'", "NGC 6885", 26.5, "NGC 6885"],
    38: [T["G"], S["P"], "Coma Berenices", "9.6", "16'x3'", "Needle Galaxy", 26.0, "NGC 4565"],
    39: [T["NP"], S["H"], "Gemini", "8.3", "13''", "Eskimo Nebula", 20.9, "NGC 2392"],
    40: [T["G"], S["P"], "Leo", "10.7", "3'x2'", "NGC 3626", 18.4, "NGC 3626"],
    41: [T["AO"], S["H"], "Taurus", "0.5", "330'", "The Hyades", 15.9, "Mel 25"],
    42: [T["AG"], S["E"], "Delphinus", "10.6", "3'", "NGC 7006", 16.2, "NGC 7006"],
    43: [T["G"], S["A"], "Pegasus", "10.0", "7'x2'", "NGC 7814", 16.1, "NGC 7814"],
    44: [T["G"], S["A"], "Pegasus", "10.3", "5'x4'", "NGC 7479", 12.3, "NGC 7479"],
    45: [T["G"], S["P"], "Boötes", "10.0", "5'x5'", "NGC 5248", 8.9, "NGC 5248"],
    46: [T["EN"], S["H"], "Monoceros", "-", "2'x1'", "Hubble's Variable Nebula", 8.7, "NGC 2261"],
    47: [T["AG"], S["E"], "Delphinus", "8.3", "7'", "NGC 6934", 7.4, "NGC 6934"],
    48: [T["G"], S["P"], "Hydra", "9.2", "5'x4'", "NGC 2775", 7.0, "NGC 2775"],
    49: [T["EN"], S["H"], "Monoceros", "-", "80'x60'", "Rosette Nebula", 5.0, "NGC 2237"],
    50: [T["AO"], S["H"], "Monoceros", "4.8", "24'", "Rosette Cluster", 4.9, "NGC 2244"],
    51: [T["G"], S["A"], "Cetus", "9.0", "16'x15'", "IC 1613", 2.1, "IC 1613"],
    52: [T["G"], S["P"], "Virgo", "9.4", "4'x3'", "NGC 4697", -5.8, "NGC 4697"],
    53: [T["G"], S["P"], "Sextans", "9.2", "8.3x3.2'", "Spindle Galaxy", -7.7, "NGC 3115"],
    54: [T["AO"], S["H"], "Monoceros", "7.6", "14'", "NGC 2506", -10.8, "NGC 2506"],
    55: [T["NP"], S["E"], "Aquarius", "8.0", "25''", "Saturn Nebula", -11.4, "NGC 7009"],
    56: [T["NP"], S["A"], "Cetus", "8.0", "4'", "Skull Nebula", -11.9, "NGC 246"],
    57: [T["G"], S["E"], "Sagittarius", "7.5", "15'x13'", "Barnard's Galaxy", -14.8, "NGC 6822"],
    58: [T["AO"], S["H"], "Canis Major", "7.2", "20'", "Caroline's Cluster", -15.6, "NGC 2360"],
    59: [T["NP"], S["P"], "Hydra", "8.3", "16''", "Ghost of Jupiter", -18.6, "NGC 3242"],
    60: [T["G"], S["P"], "Corvus", "10.3", "3'x2'", "Antennae Galaxies A", -18.9, "NGC 4038"],
    61: [T["G"], S["P"], "Corvus", "10.3", "3'x2'", "Antennae Galaxies B", -19.0, "NGC 4039"],
    62: [T["G"], S["A"], "Cetus", "8.9", "12'x3'", "NGC 247", -20.8, "NGC 247"],
    63: [T["NP"], S["A"], "Aquarius", "7.3", "13'", "Helix Nebula", -20.8, "NGC 7293"],
    64: [T["AO"], S["H"], "Canis Major", "4.1", "20'", "NGC 2362", -24.9, "NGC 2362"],
    65: [T["G"], S["A"], "Sculptor", "7.1", "25'x7'", "Sculptor Galaxy", -25.3, "NGC 253"],
    66: [T["AG"], S["P"], "Hydra", "8.5", "2'", "NGC 5694", -26.5, "NGC 5694"],
    67: [T["G"], S["A"], "Fornax", "9.3", "9'x6'", "NGC 1097", -30.3, "NGC 1097"],
    68: [T["EN"], S["E"], "Corona Australis", "-", "1'", "NGC 6729", -36.9, "NGC 6729"],
    69: [T["NP"], S["E"], "Scorpius", "9.6", "2'", "Butterfly Nebula", -37.1, "NGC 6302"],
    70: [T["G"], S["A"], "Sculptor", "8.1", "12'x9'", "NGC 300", -37.7, "NGC 300"],
    71: [T["AO"], S["H"], "Puppis", "4.2", "27'", "NGC 2477", -38.5, "NGC 2477"],
    72: [T["G"], S["A"], "Sculptor", "7.8", "31'x6'", "NGC 55", -39.2, "NGC 55"],
    73: [T["AG"], S["H"], "Columba", "7.3", "11'", "NGC 1851", -40.1, "NGC 1851"],
    74: [T["NP"], S["H"], "Vela", "8.2", "1'", "Eight-Burst Nebula", -40.4, "NGC 3132"],
    75: [T["AO"], S["E"], "Lupus", "5.8", "40'", "NGC 6124", -40.7, "NGC 6124"],
    76: [T["AO"], S["E"], "Scorpius", "2.6", "15'", "NGC 6231", -41.8, "NGC 6231"],
    77: [T["G"], S["P"], "Centaurus", "6.8", "18'x14'", "Centaurus A", -43.0, "NGC 5128"],
    78: [T["AG"], S["P"], "Centaurus", "3.7", "36'", "Omega Centauri", -47.5, "NGC 5139"],
    79: [T["AO"], S["P"], "Crux", "4.2", "10'", "The Jewel Box", -60.3, "NGC 4755"],
    80: [T["AG"], S["P"], "Centaurus", "3.7", "36'", "Omega Centauri bis", -47.5, "NGC 5139"],
    81: [T["AG"], S["E"], "Ara", "8.1", "6'", "NGC 6352", -48.4, "NGC 6352"],
    82: [T["AG"], S["E"], "Ara", "8.1", "12'", "NGC 6362", -67.0, "NGC 6362"],
    83: [T["G"], S["P"], "Centaurus", "8.6", "13'x4'", "NGC 4945", -49.5, "NGC 4945"],
    84: [T["AG"], S["P"], "Centaurus", "7.4", "10'", "NGC 5286", -51.4, "NGC 5286"],
    85: [T["AO"], S["H"], "Vela", "2.5", "50'", "IC 2391", -53.0, "IC 2391"],
    86: [T["AG"], S["E"], "Ara", "5.3", "30'", "NGC 6397", -53.7, "NGC 6397"],
    87: [T["AG"], S["H"], "Horologium", "8.4", "7'", "NGC 1261", -55.2, "NGC 1261"],
    88: [T["AO"], S["P"], "Pyxis", "9.1", "11'", "NGC 5823", -55.6, "NGC 5823"],
    89: [T["AO"], S["E"], "Norma", "5.1", "14'", "NGC 6067", -54.2, "NGC 6067"],
    90: [T["NP"], S["H"], "Carina", "10.9", "18''", "NGC 2867", -58.3, "NGC 2867"],
    91: [T["AO"], S["P"], "Carina", "3.9", "41'", "NGC 3532", -58.7, "NGC 3532"],
    92: [T["EN"], S["P"], "Carina", "-", "120'", "Eta Carinae Nebula", -59.7, "NGC 3372"],
    93: [T["AG"], S["E"], "Pavo", "5.4", "27'", "NGC 6752", -59.9, "NGC 6752"],
    94: [T["AO"], S["P"], "Crux", "4.2", "10'", "The Jewel Box", -60.3, "NGC 4755"],
    95: [T["AO"], S["E"], "Triangulum Australe", "5.1", "12'", "NGC 6025", -60.5, "NGC 6025"],
    96: [T["AO"], S["H"], "Carina", "3.8", "30'", "NGC 2516", -60.8, "NGC 2516"],
    97: [T["AO"], S["P"], "Centaurus", "3.9", "12'", "NGC 3766", -61.5, "NGC 3766"],
    98: [T["AO"], S["P"], "Crux", "4.1", "5'", "NGC 4609", -61.0, "NGC 4609"],
    99: [T["EN"], S["P"], "Crux", "-", "420'x300'", "Coalsack Nebula", -62.5, "C99"],
    100: [T["EN"], S["P"], "Centaurus", "-", "60'", "Running Chicken Nebula", -63.0, "IC 2944"],
    101: [T["G"], S["E"], "Pavo", "8.3", "16'x11'", "NGC 6744", -63.9, "NGC 6744"],
    102: [T["AO"], S["P"], "Carina", "1.9", "100'", "Southern Pleiades", -64.4, "IC 2602"],
    103: [T["EN"], S["H"], "Dorado", "-", "40'", "Tarantula Nebula", -69.1, "NGC 2070"],
    104: [T["AG"], S["A"], "Tucana", "4.0", "31'", "NGC 47", -72.1, "NGC 47"],
    105: [T["AG"], S["P"], "Musca", "7.8", "14'", "NGC 4833", -70.9, "NGC 4833"],
    106: [T["AG"], S["A"], "Tucana", "4.0", "31'", "47 Tucanae", -72.1, "NGC 104"],
    107: [T["AG"], S["P"], "Apus", "9.2", "10'", "NGC 6101", -72.2, "NGC 6101"],
    108: [T["AG"], S["P"], "Musca", "7.2", "20'", "NGC 4372", -73.0, "NGC 4372"],
    109: [T["NP"], S["P"], "Chamaeleon", "10.6", "15''", "NGC 3195", -81.2, "NGC 3195"]
}

# --- RASC CATALOG (English) ---
RASC_DATA = {
    1: [T["NP"], S["A"], "Aquarius", "8.3", "25''", "Saturn Nebula", -11.4, "NGC 7009"],
    2: [T["NP"], S["A"], "Aquarius", "6.5", "12'50''", "Helix Nebula", -20.8, "NGC 7293"],
    3: [T["G"], S["A"], "Pegasus", "9.5", "10.7x4.0'", "Deer Lick Galaxy", 34.4, "NGC 7331"],
    4: [T["EN"], S["A"], "Cassiopeia", "-", "15x8'", "Bubble Nebula", 61.2, "NGC 7635"],
    5: [T["AO"], S["A"], "Cassiopeia", "6.7", "16'", "White Rose Cluster", 56.7, "NGC 7789"],
    6: [T["G"], S["A"], "Cassiopeia", "11.7", "2x2'", "NGC 185", 48.3, "NGC 185"],
    7: [T["EN"], S["A"], "Cassiopeia", "-", "35x30'", "Pacman Nebula", 56.6, "NGC 281"],
    8: [T["AO"], S["A"], "Cassiopeia", "6.4", "13'", "Owl Cluster", 58.3, "NGC 457"],
    9: [T["AO"], S["A"], "Cassiopeia", "7.1", "16'", "NGC 663", 61.2, "NGC 663"],
    10: [T["NP"], S["A"], "Cassiopeia", "12.3", "34''", "NGC 1289", 61.3, "NGC 1289"],
    11: [T["NP"], S["A"], "Andromeda", "9.2", "20''", "Blue Snowball Nebula", 42.5, "NGC 7662"],
    12: [T["G"], S["A"], "Andromeda", "10", "13.5x2.8'", "Silver Needle Galaxy", 42.3, "NGC 891"],
    13: [T["G"], S["A"], "Sculptor", "7.1", "25.1x7.4'", "Sculptor Galaxy", -25.3, "NGC 253"],
    14: [T["G"], S["A"], "Aries", "10.3", "7.1x4.5'", "Spiral Galaxy", 19.0, "NGC 772"],
    15: [T["NP"], S["A"], "Cetus", "8.0", "3'45''", "Skull Nebula", -11.9, "NGC 246"],
    16: [T["G"], S["A"], "Cetus", "10.1", "5.2x4.4'", "NGC 936", -1.1, "NGC 936"],
    17: [T["AO"], S["A"], "Perseus", "4.4", "30'/30'", "Double Cluster", 57.1, "NGC 869"],
    18: [T["G"], S["A"], "Perseus", "9.5", "8.7x4.3'", "NGC 1023", 39.0, "NGC 1023"],
    19: [T["EN"], S["A"], "Perseus", "-", "3.0x3.0'", "NGC 1491", 51.3, "NGC 1491"],
    20: [T["NP"], S["A"], "Draco", "12.0", "52''", "NGC 1501", 60.9, "NGC 1501"],
    21: [T["G"], S["A"], "Eridanus", "9.9", "7.8x6.9'", "Galaxy NGC 1232", -20.6, "NGC 1232"],
    22: [T["NP"], S["A"], "Eridanus", "10.4", "18''", "NGC 1535", -12.7, "NGC 1535"],
    23: [T["NP"], S["H"], "Taurus", "10.8", "1'54''", "NGC 1514", 30.8, "NGC 1514"],
    24: [T["E/RN"], S["H"], "Auriga", "-", "3.0x3.0'", "NGC 1931", 34.2, "NGC 1931"],
    25: [T["RN"], S["H"], "Orion", "-", "8.0x5.0'", "NGC 1788", -3.3, "NGC 1788"],
    26: [T["E/RN"], S["H"], "Orion", "-", "40x25'", "Running Nebula", -4.7, "NGC 1973"],
    27: [T["NP"], S["H"], "Orion", "12.4", "18''", "NGC 2022", 9.1, "NGC 2022"],
    28: [T["EN"], S["H"], "Orion", "-", "30x30'", "Flame Nebula", -1.9, "NGC 2024"],
    29: [T["AO"], S["H"], "Orion", "8.5", "10'", "NGC 2194", 12.8, "NGC 2194"],
    30: [T["NP"], S["H"], "Gemini", "13.0", "55''", "NGC 2371", 29.5, "NGC 2371"],
    31: [T["NP"], S["H"], "Gemini", "8.3", "13''", "Eskimo Nebula", 20.9, "NGC 2392"],
    32: [T["EN"], S["H"], "Monoceros", "-", "80x60'", "Rosette Nebula", 5.0, "NGC 2237"],
    33: [T["E/RN"], S["H"], "Monoceros", "var", "2x1'", "Hubble's Variable Nebula", 8.7, "NGC 2261"],
    34: [T["EN"], S["H"], "Canis Major", "-", "8.0x6.0'", "Thor's Helmet Nebula", -13.2, "NGC 2359"],
    35: [T["NP"], S["H"], "Puppis", "10.3", "14''", "NGC 2440", -18.2, "NGC 2440"],
    36: [T["AO"], S["H"], "Puppis", "6.5", "22'", "NGC 2539", -12.8, "NGC 2539"],
    37: [T["G"], S["H"], "Camelopardalis", "8.4", "17.8x11.0'", "NGC 2403", 65.6, "NGC 2403"],
    38: [T["G"], S["H"], "Camelopardalis", "10.1", "5.1x4.4'", "NGC 2655", 78.2, "NGC 2655"],
    39: [T["G"], S["P"], "Lynx", "9.7", "9.3x2.5'", "NGC 2683", 33.4, "NGC 2683"],
    40: [T["G"], S["P"], "Ursa Major", "9.3", "8.1x3.8'", "NGC 2841", 51.0, "NGC 2841"],
    41: [T["G"], S["P"], "Ursa Major", "10.6", "7.6x1.7'", "NGC 3079", 55.7, "NGC 3079"],
    42: [T["G"], S["P"], "Ursa Major", "9.7", "6.9x6.8'", "NGC 3184", 41.4, "NGC 3184"],
    43: [T["G"], S["P"], "Ursa Major", "10.9", "5.4x1.5'", "NGC 3877", 47.5, "NGC 3877"],
    44: [T["G"], S["P"], "Ursa Major", "9.8", "3.8x2.5'", "NGC 3941", 45.0, "NGC 3941"],
    45: [T["G"], S["P"], "Ursa Major", "10.7", "5.1x1.4'", "NGC 4026", 50.9, "NGC 4026"],
    46: [T["G"], S["P"], "Ursa Major", "10.5", "5.8x2.5'", "NGC 4088", 50.5, "NGC 4088"],
    47: [T["G"], S["P"], "Ursa Major", "11.9", "6.9x1.7'", "NGC 4157", 50.5, "NGC 4157"],
    48: [T["G"], S["P"], "Ursa Major", "9.6", "5.5x2.3'", "NGC 4605", 61.6, "NGC 4605"],
    49: [T["G"], S["P"], "Sextans", "9.2", "8.3x3.2'", "Spindle Galaxy", -7.7, "NGC 3115"],
    50: [T["NP"], S["P"], "Hydra", "8.6", "16''", "Ghost of Jupiter", -18.6, "NGC 3242"],
    51: [T["G"], S["P"], "Leo Minor", "11.7", "5.9x1.7'", "NGC 3003", 33.4, "NGC 3003"],
    52: [T["G"], S["P"], "Leo Minor", "9.9", "6.9x6.5'", "NGC 3344", 25.0, "NGC 3344"],
    53: [T["G"], S["P"], "Leo Minor", "11.3", "6.2x1.5'", "NGC 3432", 36.6, "NGC 3432"],
    54: [T["G"], S["P"], "Leo", "8.9", "12.6x6.6'", "NGC 2903", 21.5, "NGC 2903"],
    55: [T["G"], S["P"], "Leo", "9.9", "5.9x2.6'", "NGC 3384", 12.6, "NGC 3384"],
    56: [T["G"], S["P"], "Leo", "8.7", "9.5x5.0'", "NGC 3521", -0.0, "NGC 3521"],
    57: [T["G"], S["P"], "Leo", "10.0", "3.7x3.2'", "NGC 3607", 18.0, "NGC 3607"],
    58: [T["G"], S["P"], "Leo", "9.5", "14.8x3.6'", "Ridge Galaxy", 13.6, "NGC 3628"],
    59: [T["G"], S["P"], "Canes Venatici", "10.8", "4.8x1.1'", "NGC 4111", 43.1, "NGC 4111"],
    60: [T["G"], S["P"], "Canes Venatici", "9.7", "7.9x6.3'", "NGC 4214", 36.3, "NGC 4214"],
    61: [T["G"], S["P"], "Canes Venatici", "10.2", "16.2x2.5'", "NGC 4244", 37.8, "NGC 4244"],
    62: [T["G"], S["P"], "Canes Venatici", "9.4", "5.1x3.7'", "NGC 4449", 44.1, "NGC 4449"],
    63: [T["G"], S["P"], "Canes Venatici", "9.8", "5.9x3.1'", "NGC 4490", 41.6, "NGC 4490"],
    64: [T["G"], S["P"], "Canes Venatici", "9.3", "15.1x3.3'", "Whale Galaxy", 32.5, "NGC 4631"],
    65: [T["G"], S["P"], "Canes Venatici", "10.4", "13.8x3.3'", "Hockey Stick Galaxy", 32.2, "NGC 4656"],
    66: [T["G"], S["P"], "Canes Venatici", "9.8", "5.9x3.1'", "NGC 5005", 37.1, "NGC 5005"],
    67: [T["G"], S["P"], "Canes Venatici", "10.1", "10.5x5.6'", "NGC 5033", 36.6, "NGC 5033"],
    68: [T["G"], S["P"], "Coma Berenices", "10.4", "6.9x2.8'", "NGC 4274", 29.6, "NGC 4274"],
    69: [T["G"], S["P"], "Coma Berenices", "10.2", "3.6x2.2'", "NGC 4414", 31.2, "NGC 4414"],
    70: [T["G"], S["P"], "Coma Berenices", "9.8", "4.8x3.8'", "NGC 4494", 25.8, "NGC 4494"],
    71: [T["G"], S["P"], "Coma Berenices", "9.8", "10.5x4.9'", "NGC 4559", 28.0, "NGC 4559"],
    72: [T["G"], S["P"], "Coma Berenices", "9.6", "16.2x2.8'", "Needle Galaxy", 26.0, "NGC 4565"],
    73: [T["G"], S["P"], "Coma Berenices", "9.2", "11.0x7.9'", "NGC 4725", 25.5, "NGC 4725"],
    74: [T["G"], S["P"], "Corvus", "10.7", "~3x2'", "Antennae Galaxies", -18.9, "NGC 4038"],
    75: [T["NP"], S["P"], "Corvus", "10.3", "45''", "NGC 4361", -18.8, "NGC 4361"],
    76: [T["G"], S["P"], "Virgo", "9.9", "8.3x2.2'", "NGC 4216", 13.1, "NGC 4216"],
    77: [T["G"], S["P"], "Virgo", "11.0", "5.1x1.4'", "NGC 4388", 12.7, "NGC 4388"],
    78: [T["G"], S["P"], "Virgo", "10.1", "9.3x3.9'", "The Eyes", 13.0, "NGC 4438"],
    79: [T["G"], S["P"], "Virgo", "10.5", "10.2x1.9'", "NGC 4517", 0.1, "NGC 4517"],
    80: [T["G"], S["P"], "Virgo", "9.6", "7.6x2.3'", "NGC 4526", 7.7, "NGC 4526"],
    81: [T["G"], S["P"], "Virgo", "9.8", "6.8x5.0'", "NGC 4535", 8.2, "NGC 4535"],
    82: [T["G"], S["P"], "Virgo", "~11", "4.6x2.1'", "Siamese Twins", 11.3, "NGC 4567"],
    83: [T["G"], S["P"], "Virgo", "9.6", "3.5x2.7'", "NGC 4699", -8.7, "NGC 4699"],
    84: [T["G"], S["P"], "Virgo", "10.2", "8.7x1.6'", "NGC 4762", 11.2, "NGC 4762"],
    85: [T["G"], S["P"], "Virgo", "10.6", "7.9x1.7'", "NGC 5746", 1.9, "NGC 5746"],
    86: [T["AG"], S["P"], "Boötes", "9.1", "11.0'", "NGC 5466", 28.5, "NGC 5466"],
    87: [T["G"], S["P"], "Draco", "10.4", "12.3x1.8'", "Splinter Galaxy", 56.3, "NGC 5907"],
    88: [T["G"], S["P"], "Draco", "10.2", "6.2x2.3'", "NGC 6503", 70.1, "NGC 6503"],
    89: [T["NP"], S["P"], "Draco", "8.8", "18''", "Cat's Eye Nebula", 66.6, "NGC 6543"],
    90: [T["NP"], S["E"], "Hercules", "9.3", "14''", "NGC 6210", 23.8, "NGC 6210"],
    91: [T["NP"], S["E"], "Ophiuchus", "10.4", "30''", "Little Ghost Nebula", -17.8, "NGC 6369"],
    92: [T["NP"], S["E"], "Ophiuchus", "9.0", "8''", "NGC 6572", 6.8, "NGC 6572"],
    93: [T["AO"], S["E"], "Ophiuchus", "4.6", "27'", "NGC 6633", 6.5, "NGC 6633"],
    94: [T["AG"], S["E"], "Scutum", "8.2", "7.2'", "NGC 6712", -8.7, "NGC 6712"],
    95: [T["NP"], S["E"], "Aquila", "11.8", "1'49''", "NGC 6781", 6.5, "NGC 6781"],
    96: [T["AO"], S["E"], "Cygnus", "7.3", "5'", "NGC 6819", 40.2, "NGC 6819"],
    97: [T["NP"], S["E"], "Cygnus", "9.8", "30''", "Blinking Planetary Nebula", 50.5, "NGC 6826"],
    98: [T["SNR"], S["E"], "Cygnus", "-", "20x10'", "Crescent Nebula", 38.4, "NGC 6888"],
    "99a": [T["SNR"], S["E"], "Cygnus", "-", "70x6'", "Western Veil Nebula", 30.7, "NGC 6960"],
    "99b": [T["SNR"], S["E"], "Cygnus", "-", "78x8'", "Eastern Veil Nebula", 31.7, "NGC 6992"],
    100: [T["EN"], S["E"], "Cygnus", "-", "120x100'", "North America Nebula", 44.3, "NGC 7000"],
    101: [T["NP"], S["E"], "Cygnus", "10.4", "15''", "NGC 7027", 42.2, "NGC 7027"],
    102: [T["NP"], S["E"], "Sagittarius", "11.8", "34''", "NGC 6445", -16.2, "NGC 6445"],
    103: [T["AO"], S["E"], "Sagittarius", "8.1", "6'", "NGC 6520", -27.9, "NGC 6520"],
    104: [T["NP"], S["E"], "Sagittarius", "9.9", "17''", "NGC 6818", -16.2, "NGC 6818"],
    105: [T["AO"], S["E"], "Vulpecula", "8.8", "3.2'", "NGC 6802", 20.3, "NGC 6802"],
    106: [T["AO"], S["E"], "Vulpecula", "6.3", "31'", "NGC 6940", 28.3, "NGC 6940"],
    107: [T["AO"], S["E"], "Cepheus", "7.8", "8'", "NGC 6939", 60.6, "NGC 6939"],
    108: [T["G"], S["E"], "Cepheus", "8.9", "11.0x9.8'", "Fireworks Galaxy", 60.1, "NGC 6946"],
    109: [T["RN"], S["E"], "Cepheus", "-", "8x7'", "NGC 7129", 66.1, "NGC 7129"],
    110: [T["NP"], S["E"], "Cepheus", "10.2", "37''", "Bow-Tie Nebula", 72.5, "NGC 40"]
}
 """

CATALOGS = {
    "Messier": {"prefix": "M", "data": MESSIER_DATA},          # the prefix is used in the HTML page
    "Caldwell": {"prefix": "C", "data": CALDWELL_DATA},
    "RASC": {"prefix": "R", "data": RASC_DATA}
}

# --- SCRIPT ---

def find_image(prefix, obj_id, tech_ref):
    valid_exts = ('.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff', '.lnk')
    if not os.path.exists(CONFIG["SOURCE_DIR"]): return None
    
    files = [f for f in os.listdir(CONFIG["SOURCE_DIR"]) 
             if f.lower().endswith(valid_exts) and "_thumb" not in f]

    if tech_ref:
        match = re.search(r"(NGC|IC|Sh2|Mel|WNC|M)\s?(\d+)", tech_ref, re.IGNORECASE)
        if match:
            
            a_type, a_num = match.group(1), match.group(2)
            pattern = rf"{a_type}\s?{a_num}(?!\d)"
            for filename in files:
                if re.search(pattern, filename, re.IGNORECASE):
                    return filename

    pattern_id = rf"(^|[_ \-\.]){prefix}[_ \-\s]?{obj_id}(?!\d)"
    for filename in files:
        if re.search(pattern_id, filename, re.IGNORECASE):
            return filename
                
    return None
    
def get_exif_date(path):
    try:
        with Image.open(path) as img:
            exif = img._getexif()
            if exif and 306 in exif:
                return datetime.strptime(exif[306], "%Y:%m:%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
    except: pass
    return datetime.fromtimestamp(os.path.getmtime(path)).strftime("%d/%m/%Y %H:%M")

def make_thumbnail(src):
    
    if not os.path.exists(CONFIG["THUMB_DIR"]): os.makedirs(CONFIG["THUMB_DIR"])
    dest = os.path.join(CONFIG["THUMB_DIR"], f"thumb_{src}")
    
    # if  .tif file then generate view_file.jpg in the thumbnails dir that will be used for display
    if src.lower().endswith(('.tif', '.tiff')):
        view_dest = os.path.join(CONFIG["THUMB_DIR"], f"view_{os.path.splitext(src)[0]}.jpg")
        if not os.path.exists(view_dest):
            try:
                with Image.open(src) as img_view:
                    img_view = ImageOps.exif_transpose(img_view).convert("RGB")
                    view_size = CONFIG.get("VIEW_SIZE", 1200)
                    img_view.thumbnail((view_size, view_size), Image.Resampling.LANCZOS)
                    img_view.save(view_dest, "JPEG", quality=85)
            except Exception:
                pass

    if os.path.exists(dest): return dest
    
    try:
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

def generate():
    final_json = {}
    stats = {}
    
    # On extrait les préfixes pour le JS afin de rester synchro avec Python
    prefixes_js = {k: v["prefix"] for k, v in CATALOGS.items()}
    
    for name, data_dict in CATALOGS.items():
        objs = []
        found_count = 0
        prefix = data_dict["prefix"]
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
            
            dec = info[6]
            h_max = 90 - abs(CONFIG["LATITUDE"] - dec)
            
            color = "#c9d1d9" 
            if h_max <= CONFIG["LIMIT_IMPOSSIBLE"]: color = "#da3633"  #"#ff4d4d""#ff4d4d" 
            elif h_max <= CONFIG["LIMIT_DIFFICILE"]: color = "#ff9f43" 

            objs.append({
                "id": k, 
                "prefix": prefix, 
                "info": info, 
                "tech_ref": tech_ref,
                "img": img_file or "", 
                "thumb": thumb, 
                "date": date,
                "h_max": round(h_max, 1),
                "label_color": color
            })
            
        final_json[name] = objs
        stats[name] = f"{found_count}/{len(data_dict['data'])}"

    select_options = "".join([f'<option value="{c}" {"selected" if c == CONFIG["SELECTED_CATALOG"] else ""}>{c}</option>' for c in CATALOGS.keys()])

    html_template = f"""<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8">
    <style>
        :root {{ --case-size: {CONFIG["THUMB_SIZE"]}px; }}
        body {{ background: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', sans-serif; text-align: center; padding: 20px; overflow-x: hidden; }}
        h1 {{ font-size: 2.2em; margin-bottom: 5px; color: #fff; }}
        .stats-header {{ color: #8b949e; font-size: 1.1em; margin-bottom: 20px; }}
        .filter-bar {{ margin-bottom: 30px; display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; }}
        .filter-btn {{ background: #21262d; border: 1px solid #30363d; color: #c9d1d9; padding: 8px 20px; border-radius: 20px; cursor: pointer; transition: 0.2s; }}
        .filter-btn.active {{ background: #238636; border-color: #2ea043; color: #fff; }}
        .filter-btn.active-blue {{ background: #1f6feb; border-color: #388bfd; color: #fff; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(var(--case-size), 1fr)); gap: 15px; width: 100%; margin: 0 auto; }}
        .case {{ background: #161b22; border-radius: 8px; border: 1px solid #30363d; overflow: hidden; position: relative; display: flex; flex-direction: column; }}
        .img-box {{ width: 100%; aspect-ratio: 1 / 1; display: flex; align-items: center; justify-content: center; background: #000; cursor: pointer; overflow: hidden; }}
        .img-box img {{ width: 100%; height: 100%; object-fit: cover; }}
        .empty-info {{ color: #484f58; font-size: 11px; font-weight: bold; text-align: center; padding: 5px; line-height: 1.2; }}
        .label {{ background: #21262d; padding: 8px 5px; font-weight: bold; font-size: 12px; border-top: 1px solid #30363d; cursor: pointer; transition: 0.2s; }}
        #tooltip {{ position: fixed; display: none; background: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 12px; z-index: 2000; text-align: left; min-width: 220px; box-shadow: 0 8px 24px #000; pointer-events: none; }}
        #overlay {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 9999; justify-content: center; align-items: center; overflow: hidden; }}
        #fullImg {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); cursor: grab; user-select: none; max-width: 95%; max-height: 95%; transition: transform 0.05s linear; }}
    </style></head><body>
    <h1 id="catTitle">Catalogue</h1>
    <div class="stats-header" id="statsText"></div>
    <div class="filter-bar">
        <select id="catSelect" onchange="update()" style="background:#21262d; color:#fff; border-radius:20px; padding:8px 15px; border:1px solid #30363d;">{select_options}</select>
        <button class="filter-btn active-blue" onclick="filterS('Tous', this)">Tous</button>
        <button class="filter-btn" onclick="filterS('Printemps', this)">Printemps</button>
        <button class="filter-btn" onclick="filterS('Été', this)">Été</button>
        <button class="filter-btn" onclick="filterS('Automne', this)">Automne</button>
        <button class="filter-btn" onclick="filterS('Hiver', this)">Hiver</button>
    </div>
    <div class="grid" id="grid"></div>
    <div id="tooltip"></div>
    <div id="overlay" onclick="if(event.target===this) closeM()"><img id="fullImg"></div>
    <script>
        const data = {json.dumps(final_json)};
        const stats = {json.dumps(stats)};
        const prefixes = {json.dumps(prefixes_js)}; // Récupération des préfixes définis en Python
        
        // Extraction de la config Python vers JS
        const thumbDir = "{CONFIG['THUMB_DIR']}";
        
        
        let currentSeason = 'Tous';
        let scale = 1, posX = 0, posY = 0, isDragging = false, startX, startY;
        const m = document.getElementById("overlay"), mi = document.getElementById("fullImg"), t = document.getElementById('tooltip');

        function filterS(s, btn) {{
            currentSeason = s;
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active', 'active-blue'));
            btn.classList.add(s === 'Tous' ? 'active-blue' : 'active');
            update();
        }}

        function update() {{
            const cat = document.getElementById('catSelect').value;
            document.getElementById('catTitle').innerText = "Catalogue " + cat;
            document.getElementById('statsText').innerText = "(" + stats[cat] + ")";
            const g = document.getElementById('grid'); g.innerHTML = '';
            
            data[cat].forEach(obj => {{
                if (currentSeason !== 'Tous' && obj.info[1] !== currentSeason) return;
                const d = document.createElement('div'); d.className = 'case';
                d.onmousemove = (e) => showT(e, obj);
                d.onmouseleave = () => t.style.display='none';
                
                let content = obj.thumb ? `<img src="${{obj.thumb}}">` : `<div class="empty-info">${{obj.info[0]}}<br>${{obj.info[1]}}</div>`;
                
                // ---  REDIRECT VIEW POUR TIF OU TIFF ---
                let clickImg = obj.img;
                if (obj.img && (obj.img.toLowerCase().endsWith('.tif') || obj.img.toLowerCase().endsWith('.tiff'))) {{
                    // 1. Récupérer le nom de fichier sans l'extension
                    let baseName = obj.img.substring(0, obj.img.lastIndexOf('.'));
    
                    // 2. Supprimer le préfixe "thumb_" s'il existe au début du nom
                    if (baseName.startsWith('thumb_')) {{
                        baseName = baseName.substring(6); // 6 est la longueur de "thumb_"
                    }}
    
                    // 3. Concaténer avec le nouveau préfixe view_
                    clickImg = thumbDir + "/view_" + baseName + ".jpg";
                    // --- DEBUG ---
                    console.log("Source originale (obj.img):", obj.img);
                    console.log("Base extraite (baseName):", baseName);
                    console.log("Chemin final généré (clickImg):", clickImg);
                }}
                
                // ---  URL TELESCOPIUS RASC <==> NGC from database field(tech_ref) ---
                let tUrl = "https://telescopius.com/deep-sky-objects/";
                if (obj.prefix === prefixes.Messier) {{
                    tUrl += "m-" + obj.id;
                }} else if (obj.prefix === prefixes.Caldwell) {{
                    tUrl += "c-" + obj.id;
                }} else if (obj.prefix === prefixes.RASC) {{
                    const numMatch = obj.tech_ref.match(/\\d+/);
                    tUrl += "ngc-" + (numMatch ? numMatch[0] : "");
                }}

                const labelText = obj.tech_ref ? `${{obj.prefix}}${{obj.id}} - ${{obj.tech_ref}}` : `${{obj.prefix}}${{obj.id}}`;

                d.innerHTML = `<div class="img-box" onclick="openM('${{clickImg}}')">${{content}}</div>
                               <div class="label" style="color:${{obj.label_color}}" onclick="window.open('${{tUrl}}', '_blank')">${{labelText}}</div>`;
                g.appendChild(d);
            }});
        }}

        function openM(s) {{ if(!s) return; scale = 1; posX = 0; posY = 0; mi.src = s; m.style.display = "block"; updateTransform(); }}
        function closeM() {{ m.style.display = "none"; }}
        function updateTransform() {{ mi.style.transform = `translate(calc(-50% + ${{posX}}px), calc(-50% + ${{posY}}px)) scale(${{scale}})`; }}
        
        m.addEventListener('wheel', e => {{ e.preventDefault(); scale = Math.min(Math.max(0.5, scale * (e.deltaY > 0 ? 0.9 : 1.1)), 10); updateTransform(); }}, {{passive: false}});
        mi.addEventListener('mousedown', e => {{ isDragging = true; startX = e.clientX - posX; startY = e.clientY - posY; e.preventDefault(); }});
        window.addEventListener('mousemove', e => {{ if (isDragging) {{ posX = e.clientX - startX; posY = e.clientY - startY; updateTransform(); }} }});
        window.addEventListener('mouseup', () => isDragging = false);

        function showT(e, obj) {{
            let html = "";
            if (obj.img) {{
                html += `<div style="color:#4a9eff; font-weight:bold; font-size:12px; margin-bottom:2px;">${{obj.img}}</div>`;
                html += `<div style="color:#888; font-size:11px; margin-bottom:8px;">Date: ${{obj.date}}</div>`;
                html += `<hr style="border:0; border-top:1px solid #444; margin:8px 0;">`;
            }}
            
            html += `<div><strong>Type:</strong> ${{obj.info[0]}}</div>`;
            html += `<div><strong>Saison:</strong> ${{obj.info[1]}}</div>`;
            html += `<div><strong>Constellation:</strong> ${{obj.info[2]}}</div>`;
            html += `<div><strong>Magnitude:</strong> ${{obj.info[3]}}</div>`;
            html += `<div><strong>Taille:</strong> ${{obj.info[4]}}'</div>`;
            html += `<div><strong>Déclinaison:</strong> ${{obj.info[6]}}°</div>`;
            html += `<div><strong>Élévation Max:</strong> ${{obj.h_max}}°</div>`;
            
            html += `<hr style="border:0; border-top:1px solid #444; margin:8px 0;">`;
            html += `<div style="font-style:italic; color:#ccc; margin-top:5px;">${{obj.info[5]}}</div>`;
            
            t.innerHTML = html; t.style.display = 'block';
            let x = e.clientX + 15, y = e.clientY + 15;
            if (x + 250 > window.innerWidth) x = e.clientX - t.offsetWidth - 15;
            if (y + t.offsetHeight > window.innerHeight) y = e.clientY - t.offsetHeight - 15;
            t.style.left = x + 'px'; t.style.top = y + 'px';
        }}
        update();
    </script></body></html>"""
    
    with open(CONFIG["OUTPUT_HTML"], "w", encoding="utf-8") as f: f.write(html_template)

if __name__ == "__main__": generate()
