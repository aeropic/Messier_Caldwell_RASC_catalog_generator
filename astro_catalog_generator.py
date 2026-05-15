#=============================================================================
#                          (c) AEROPIC 2026
#           all in one Messier/Caldwell/RASC/O'Meara catalog generator
#  
# https://github.com/aeropic/Messier_Caldwell_RASC_OMeara_catalog_generator
# http://www.messier.seds.org/xtra/similar/rasc-ngc.html
# https://www.catchersofthelight.com/astrophotography-hidden-treasures-list.aspx
# https://app.astrobin.com/u/GaryI?collection=677&i=esls3b#gallery
#
#   V4.4 : hollow heart when no note 
#   V4.3 : a free comment can be added when loving an object. 
#          TODO.txt can be edited as well to manually add single line comments
#   V4.2 : tooltip labels in LANG dictionnary
#   V4.1 : season is computed from RA value. RA added in database
#   V4.0.1 : added few comments all in english
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
        "GC": "Amas Globulaire",                             # "globular cluster"
        "OC": "Amas Ouvert",                                 # "open cluster"
        "G": "Galaxie",                                      # "galaxy
        "SC": "Nuage Stellaire",                             # "stellar cloud"
        "D": "Étoile Double",                                # "double star"
        "A": "Astérisme",                                    # "asterim"
        "SNR": "Rémanent Supernova",                         # "super nova remnant"
        "EN": "Néb. Émission",                               # "Emission Nebula"
        "RN": "Néb. Réflexion",                              # "reflection nebula 
        "E/RN": "Néb. Ém./Réf.",                             # " emissin and reflexion nebula"
        "N+C": "Amas + Néb.",                                  # " Nebula and cluster"
        "QSR": "Qasar"
    },
    "FAMILIES_LABELS": {
        "ALL": "Tous objets",                               # "all objects"
        "NEB": "Nébuleuses",                                # "nebula"
        "GAL": "Galaxies",
        "CLU": "Amas et divers"                             # "clusters and others"
    },
    "SEASONS": {"P": "Printemps", "E": "Été", "A": "Automne", "H": "Hiver"},      # {"P": "Spring", "E": "Summer", "A": "Automn", "H": "Winter"},
    "TOOLTIP_LABELS": {
        "TYPE": "Type ",                                      # "Type"
        "SEASON": "Saison ",                                  # "Season"
        "CONSTELLATION": "Constellation ",                    # "Constellation"
        "MAGNITUDE": "Magnitude ",                            # "Magnitude"
        "SIZE": "Taille ",                                     # "Size"
        "ELEVATION": "Elévation max "                         # "max elevation"
    }
}



T, S = LANG["TYPES"], LANG["SEASONS"]

# --- DATABASES (MESSIER, CALDWELL, RASC) ---
# --- you can translate the constellation name and the usual name but keep the NGC reference as is ---
# --- replace the lists here after with the "English_databases.txt" content for the english translation


# --- Format: [Type, Tech_Ref, Constellation, Mag, Size, Common Name, RA, Dec]


MESSIER_DATA = {
    1: [T["SNR"], "NGC 1952", "Taureau", "8.4", "6'x4'", "Nébuleuse du Crabe", 5.57, 22.0],
    2: [T["GC"], "NGC 7089", "Verseau", "6.3", "16'", "Amas du Verseau", 21.56, -0.8],
    3: [T["GC"], "NGC 5272", "Ch. de Chasse", "6.2", "18'", "Amas des Chiens de Chasse", 13.7, 28.4],
    4: [T["GC"], "NGC 6121", "Scorpion", "5.9", "36'", "Amas du Scorpion", 16.4, -26.5],
    5: [T["GC"], "NGC 5904", "Serpent", "5.7", "23'", "Amas du Serpent", 15.31, 2.1],
    6: [T["OC"], "NGC 6405", "Scorpion", "4.2", "25'", "Amas du Papillon", 17.67, -32.2],
    7: [T["OC"], "NGC 6475", "Scorpion", "3.3", "80'", "Amas de Ptolémée", 17.89, -34.8],
    8: [T["N"], "NGC 6523", "Sagittaire", "6.0", "90'x40'", "Nébuleuse de la Lagune", 18.06, -24.4],
    9: [T["GC"], "NGC 6333", "Ophiuchus", "7.7", "11'", "Amas d'Ophiuchus", 17.32, -18.5],
    10: [T["GC"], "NGC 6254", "Ophiuchus", "6.6", "20'", "Amas d'Ophiuchus", 16.95, -4.1],
    11: [T["OC"], "NGC 6705", "Écu", "5.8", "14'", "Amas du Canard Sauvage", 18.85, -6.3],
    12: [T["GC"], "NGC 6218", "Ophiuchus", "6.7", "16'", "Amas d'Ophiuchus", 16.79, -1.9],
    13: [T["GC"], "NGC 6205", "Hercule", "5.8", "20'", "Grand Amas d'Hercule", 16.69, 36.5],
    14: [T["GC"], "NGC 6402", "Ophiuchus", "7.6", "11'", "Amas d'Ophiuchus", 17.62, -3.3],
    15: [T["GC"], "NGC 7078", "Pégase", "6.2", "18'", "Amas de Pégase", 21.5, 12.2],
    16: [T["N"], "NGC 6611", "Serpent", "6.0", "7'", "Nébuleuse de l'Aigle", 18.31, -13.8],
    17: [T["N"], "NGC 6618", "Sagittaire", "6.0", "11'", "Nébuleuse Omega", 18.35, -16.2],
    18: [T["OC"], "NGC 6613", "Sagittaire", "7.5", "9'", "Cygne Noir", 18.33, -17.1],
    19: [T["GC"], "NGC 6273", "Ophiuchus", "6.8", "17'", "Amas d'Ophiuchus", 17.04, -26.3],
    20: [T["N"], "NGC 6514", "Sagittaire", "6.3", "28'", "Nébuleuse Trifide", 18.04, -23.0],
    21: [T["OC"], "NGC 6531", "Sagittaire", "6.5", "13'", "Amas du Sagittaire", 18.08, -22.5],
    22: [T["GC"], "NGC 6656", "Sagittaire", "5.1", "32'", "Grand Amas du Sagittaire", 18.6, -23.9],
    23: [T["OC"], "NGC 6494", "Sagittaire", "6.9", "27'", "Amas du Sagittaire", 17.95, -19.0],
    24: [T["SC"], "NGC 6603", "Sagittaire", "4.6", "90'", "Petit Nuage Stellaire du Sagittaire", 18.28, -18.4],
    25: [T["OC"], "IC 4725", "Sagittaire", "4.6", "32'", "Amas du Sagittaire", 18.53, -19.2],
    26: [T["OC"], "NGC 6694", "Écu", "8.0", "15'", "Amas de l'Écu", 18.75, -9.4],
    27: [T["NP"], "NGC 6853", "Petit Renard", "7.4", "8'x6'", "Nébuleuse Dumbbell", 19.99, 22.7],
    28: [T["GC"], "NGC 6626", "Sagittaire", "6.8", "11'", "Amas du Sagittaire", 18.41, -24.9],
    29: [T["OC"], "NGC 6913", "Cygne", "7.1", "7'", "Amas du Cygne", 20.4, 38.5],
    30: [T["GC"], "NGC 7099", "Capricorne", "7.2", "12'", "Amas du Capricorne", 21.67, -23.2],
    31: [T["G"], "NGC 224", "Andromède", "3.4", "190'x60'", "Galaxie d'Andromède", 0.71, 41.3],
    32: [T["G"], "NGC 221", "Andromède", "8.1", "8'x6'", "Le Gentil (M32)", 0.71, 40.9],
    33: [T["G"], "NGC 598", "Triangle", "5.7", "70'x40'", "Galaxie du Triangle", 1.56, 30.7],
    34: [T["OC"], "NGC 1039", "Persée", "5.2", "35'", "Amas de Persée", 2.7, 42.8],
    35: [T["OC"], "NGC 2168", "Gémeaux", "5.1", "28'", "Amas des Gémeaux", 6.15, 24.3],
    36: [T["OC"], "NGC 1960", "Cocher", "6.0", "12'", "Amas du Cocher", 5.6, 34.1],
    37: [T["OC"], "NGC 2099", "Cocher", "5.6", "24'", "Amas du Cocher", 5.87, 32.5],
    38: [T["OC"], "NGC 1912", "Cocher", "6.4", "21'", "Amas de l'Étoile de Mer", 5.47, 35.8],
    39: [T["OC"], "NGC 7092", "Cygne", "4.6", "32'", "Amas du Cygne", 21.54, 48.4],
    40: [T["D"], "WNC 4", "Grande Ourse", "8.4", "0.8'", "Winnecke 4", 12.37, 58.1],
    41: [T["OC"], "NGC 2287", "Grand Chien", "4.5", "38'", "Amas du Petit Rucher", 6.78, -20.7],
    42: [T["N"], "NGC 1976", "Orion", "4.0", "85'x60'", "Nébuleuse d'Orion", 5.59, -5.4],
    43: [T["N"], "NGC 1982", "Orion", "9.0", "20'x15'", "Nébuleuse de De Mairan", 5.59, -5.2],
    44: [T["OC"], "NGC 2632", "Cancer", "3.1", "95'", "Amas de la Crèche", 8.67, 19.7],
    45: [T["OC"], "NGC 1432", "Taureau", "1.6", "110'", "Les Pléiades", 3.78, 24.1],
    46: [T["OC"], "NGC 2437", "Poupe", "6.1", "27'", "Amas de la Poupe", 7.7, -14.8],
    47: [T["OC"], "NGC 2422", "Poupe", "4.4", "30'", "Amas de la Poupe", 7.61, -14.4],
    48: [T["OC"], "NGC 2548", "Hydre", "5.8", "54'", "Amas de l'Hydre", 8.23, -5.8],
    49: [T["G"], "NGC 4472", "Vierge", "8.4", "10'x9'", "Galaxie de la Vierge", 12.5, 8.0],
    50: [T["OC"], "NGC 2323", "Licorne", "5.9", "16'", "Amas de la Licorne", 7.05, -8.3],
    51: [T["G"], "NGC 5194", "Ch. de Chasse", "8.4", "11'x7'", "Galaxie du Tourbillon", 13.5, 47.2],
    52: [T["OC"], "NGC 7654", "Cassiopée", "6.9", "13'", "Amas de Cassiopée", 23.4, 61.6],
    53: [T["GC"], "NGC 5024", "Chevelure", "7.6", "13'", "Amas de la Chevelure", 13.21, 18.2],
    54: [T["GC"], "NGC 6715", "Sagittaire", "7.6", "12'", "Amas du Sagittaire", 18.92, -30.5],
    55: [T["GC"], "NGC 6809", "Sagittaire", "6.3", "19'", "Amas du Sagittaire", 19.67, -30.9],
    56: [T["GC"], "NGC 6779", "Lyre", "8.3", "9'", "Amas de la Lyre", 19.28, 33.0],
    57: [T["NP"], "NGC 6720", "Lyre", "8.8", "1.5'x1'", "Nébuleuse de l'Anneau", 18.89, 33.0],
    58: [T["G"], "NGC 4579", "Vierge", "9.7", "6'x5'", "Galaxie de la Vierge", 12.63, 11.8],
    59: [T["G"], "NGC 4621", "Vierge", "10.6", "5'x4'", "Galaxie de la Vierge", 12.7, 11.6],
    60: [T["G"], "NGC 4649", "Vierge", "8.8", "7'x6'", "Galaxie de la Vierge", 12.73, 11.6],
    61: [T["G"], "NGC 4303", "Vierge", "9.7", "6'x6'", "Galaxie de la Vierge", 12.37, 4.5],
    62: [T["GC"], "NGC 6266", "Ophiuchus", "6.5", "15'", "Amas d'Ophiuchus", 17.02, -30.1],
    63: [T["G"], "NGC 5055", "Ch. de Chasse", "8.6", "12'x8'", "Galaxie du Tournesol", 13.26, 42.0],
    64: [T["G"], "NGC 4826", "Chevelure", "8.5", "10'x5'", "Galaxie de l'Œil Noir", 12.94, 21.7],
    65: [T["G"], "NGC 3623", "Lion", "9.3", "10'x3'", "Galaxie du Lion", 11.32, 13.1],
    66: [T["G"], "NGC 3627", "Lion", "8.9", "9'x4'", "Galaxie du Lion", 11.34, 13.0],
    67: [T["OC"], "NGC 2682", "Cancer", "6.1", "30'", "Amas du Cobra Royal", 8.85, 11.8],
    68: [T["GC"], "NGC 4590", "Hydre", "7.8", "11'", "Amas de l'Hydre", 12.66, -26.7],
    69: [T["GC"], "NGC 6637", "Sagittaire", "7.6", "10'", "Amas du Sagittaire", 18.52, -32.3],
    70: [T["GC"], "NGC 6681", "Sagittaire", "7.9", "9'", "Amas du Sagittaire", 18.72, -32.3],
    71: [T["GC"], "NGC 6838", "Flèche", "8.2", "7'", "Amas de la Flèche", 19.89, 18.8],
    72: [T["GC"], "NGC 6981", "Verseau", "9.3", "7'", "Amas du Verseau", 20.89, -12.5],
    73: [T["A"], "NGC 6994", "Verseau", "9.0", "2.8'", "Astérisme du Verseau", 20.98, -12.6],
    74: [T["G"], "NGC 628", "Poissons", "9.4", "10'x10'", "Galaxie du Fantôme", 1.61, 15.8],
    75: [T["GC"], "NGC 6864", "Sagittaire", "8.5", "7'", "Amas du Sagittaire", 20.1, -21.9],
    76: [T["NP"], "NGC 650", "Persée", "10.1", "2.7'x1.8'", "Nébuleuse de la Petite Haltère", 1.7, 51.6],
    77: [T["G"], "NGC 1068", "Baleine", "8.9", "7'x6'", "Galaxie de la Baleine", 2.71, -0.0],
    78: [T["N"], "NGC 2068", "Orion", "8.3", "8'x6'", "M78 (Nébuleuse)", 5.78, 0.1],
    79: [T["GC"], "NGC 1904", "Lièvre", "7.7", "10'", "Amas du Lièvre", 5.41, -24.5],
    80: [T["GC"], "NGC 6093", "Scorpion", "7.3", "10'", "Amas du Scorpion", 16.28, -22.9],
    81: [T["G"], "NGC 3031", "Grande Ourse", "6.9", "26'x14'", "Galaxie de Bode", 9.92, 69.1],
    82: [T["G"], "NGC 3034", "Grande Ourse", "8.4", "11'x4'", "Galaxie du Cigare", 9.93, 69.7],
    83: [T["G"], "NGC 5236", "Hydre", "7.5", "13'x11'", "Galaxie du Moulinet Austral", 13.62, -29.9],
    84: [T["G"], "NGC 4374", "Vierge", "9.1", "6'x6'", "Galaxie de la Vierge", 12.42, 12.9],
    85: [T["G"], "NGC 4382", "Chevelure", "9.1", "7'x5'", "Galaxie de la Chevelure", 12.42, 18.2],
    86: [T["G"], "NGC 4406", "Vierge", "8.9", "9'x6'", "Galaxie de la Vierge", 12.44, 12.9],
    87: [T["G"], "NGC 4486", "Vierge", "8.6", "8'x8'", "Virgo A", 12.51, 12.4],
    88: [T["G"], "NGC 4501", "Chevelure", "9.6", "7'x4'", "Galaxie de la Chevelure", 12.53, 14.4],
    89: [T["G"], "NGC 4552", "Vierge", "9.8", "5'x5'", "Galaxie de la Vierge", 12.59, 12.6],
    90: [T["G"], "NGC 4569", "Vierge", "9.5", "10'x4'", "Galaxie de la Vierge", 12.61, 13.2],
    91: [T["G"], "NGC 4548", "Chevelure", "10.2", "5'x4'", "Galaxie de la Chevelure", 12.59, 14.5],
    92: [T["GC"], "NGC 6341", "Hercule", "6.3", "14'", "Amas d'Hercule", 17.28, 43.1],
    93: [T["OC"], "NGC 2447", "Poupe", "6.0", "22'", "Amas de la Poupe", 7.74, -23.9],
    94: [T["G"], "NGC 4736", "Ch. de Chasse", "8.2", "11'x9'", "Galaxie de l'Œil de Crocodile", 12.85, 41.1],
    95: [T["G"], "NGC 3351", "Lion", "9.7", "7'x5'", "Galaxie du Lion", 10.73, 11.7],
    96: [T["G"], "NGC 3368", "Lion", "9.2", "8'x5'", "Galaxie du Lion", 10.78, 11.8],
    97: [T["NP"], "NGC 3587", "Grande Ourse", "9.9", "3.4'", "Nébuleuse du Hibou", 11.25, 55.0],
    98: [T["G"], "NGC 4192", "Chevelure", "10.1", "10'x3'", "Galaxie de la Chevelure", 12.23, 14.9],
    99: [T["G"], "NGC 4254", "Chevelure", "9.9", "5'x5'", "Galaxie du Coma Pinwheel", 12.31, 14.4],
    100: [T["G"], "NGC 4321", "Chevelure", "9.3", "7'x6'", "Galaxie de la Chevelure", 12.38, 15.8],
    101: [T["G"], "NGC 5457", "Grande Ourse", "7.9", "28'x27'", "Galaxie du Moulinet", 14.05, 54.4],
    102: [T["G"], "NGC 5866", "Dragon", "9.9", "6'x3'", "Galaxie du Fuseau", 15.11, 55.8],
    103: [T["OC"], "NGC 581", "Cassiopée", "7.4", "6'", "Amas de Cassiopée", 1.55, 60.7],
    104: [T["G"], "NGC 4594", "Vierge", "8.0", "9'x4'", "Galaxie du Sombrero", 12.67, -11.6],
    105: [T["G"], "NGC 3379", "Lion", "9.3", "5'x5'", "Galaxie du Lion", 10.79, 12.6],
    106: [T["G"], "NGC 4258", "Ch. de Chasse", "8.4", "18'x7'", "Galaxie des Chiens de Chasse", 12.32, 47.3],
    107: [T["GC"], "NGC 6171", "Ophiuchus", "7.9", "13'", "Amas d'Ophiuchus", 16.54, -13.1],
    108: [T["G"], "NGC 3556", "Grande Ourse", "10.0", "9'x2'", "Galaxie de la Planche à Surf", 11.19, 53.4],
    109: [T["G"], "NGC 3992", "Grande Ourse", "9.8", "8'x5'", "Galaxie de la Grande Ourse", 11.96, 53.4],
    110: [T["G"], "NGC 205", "Andromède", "8.1", "17'x10'", "Galaxie d'Andromède (sat.)", 0.67, 41.7]
}



CALDWELL_DATA = {
    1: [T["OC"], "NGC 188", "Céphée", "8.1", "13'", "NGC 188", 0.74, 85.3],
    2: [T["NP"], "NGC 40", "Céphée", "10.2", "37''", "Nébuleuse du Nœud Coulant", 0.05, 72.5],
    3: [T["G"], "NGC 4236", "Dragon", "9.7", "18.6'x6.9'", "Galaxie du Dragon", 12.28, 69.5],
    4: [T["RN"], "NGC 7023", "Céphée", "-", "18'x18'", "Nébuleuse de l'Iris", 21.03, 68.2],
    5: [T["G"], "IC 342", "Girafe", "8.4", "21.1'x20.9'", "Galaxie de la Girafe", 3.78, 68.1],
    6: [T["NP"], "NGC 6543", "Dragon", "8.1", "18''", "Nébuleuse de l'Œil de Chat", 17.98, 66.6],
    7: [T["G"], "NGC 2403", "Girafe", "8.4", "24.9'x12'", "NGC 2403", 7.62, 65.6],
    8: [T["OC"], "NGC 559", "Cassiopée", "7.1", "5.8'", "NGC 559", 1.49, 63.3],
    9: [T["EN"], "Sh2-155", "Céphée", "-", "50'x40'", "Nébuleuse de la Grotte", 22.95, 62.3],
    10: [T["OC"], "NGC 663", "Cassiopée", "7.1", "16'", "NGC 663", 1.77, 61.2],
    11: [T["EN"], "NGC 7635", "Cassiopée", "-", "15'x8'", "Nébuleuse de la Bulle", 23.35, 61.2],
    12: [T["G"], "NGC 6946", "Céphée", "8.9", "11.5'x11.5'", "Galaxie du Feu d'Artifice", 20.58, 60.1],
    13: [T["OC"], "NGC 457", "Cassiopée", "6.7", "13'", "Amas de la Chouette", 1.32, 58.3],
    14: [T["OC"], "NGC 869", "Persée", "4.4", "30'", "Double Amas de Persée", 2.32, 57.1],
    15: [T["NP"], "NGC 6826", "Cygne", "9.8", "30''", "Nébuleuse de l'Œil Clignotant", 19.75, 50.5],
    16: [T["OC"], "NGC 7243", "Lézard", "6.4", "20'", "NGC 7243", 22.25, 49.9],
    17: [T["G"], "NGC 147", "Cassiopée", "9.1", "13'x8'", "NGC 147", 0.55, 48.5],
    18: [T["G"], "NGC 185", "Cassiopée", "9.2", "12'x10'", "NGC 185", 0.65, 48.3],
    19: [T["EN"], "IC 5146", "Céphée", "-", "12'", "Nébuleuse du Cocon", 21.89, 47.3],
    20: [T["EN"], "NGC 7000", "Cygne", "-", "120'x100'", "Nébuleuse de l'Amérique du Nord", 20.99, 44.3],
    21: [T["G"], "NGC 4449", "Chiens de Chasse", "9.4", "5'x4'", "NGC 4449", 12.47, 44.1],
    22: [T["NP"], "NGC 7662", "Andromède", "8.3", "20''", "Nébuleuse de la Boule de Neige Bleue", 23.43, 42.5],
    23: [T["G"], "NGC 891", "Andromède", "10.0", "13'x3'", "Galaxie de l'Aiguille d'Argent", 2.38, 42.3],
    24: [T["G"], "NGC 1275", "Persée", "11.7", "2'x2'", "Perseus A", 3.33, 41.5],
    25: [T["GC"], "NGC 2419", "Lynx", "10.4", "4'", "Amas de l'Errant Intergalactique", 7.63, 38.9],
    26: [T["G"], "NGC 4244", "Chiens de Chasse", "10.2", "16'x2'", "NGC 4244", 12.3, 37.8],
    27: [T["EN"], "NGC 6888", "Cygne", "-", "20'x10'", "Nébuleuse du Croissant", 20.2, 38.4],
    28: [T["OC"], "NGC 752", "Andromède", "5.2", "45'", "NGC 752", 1.96, 37.8],
    29: [T["G"], "NGC 5005", "Chiens de Chasse", "9.8", "5'x3'", "NGC 5005", 13.18, 37.1],
    30: [T["G"], "NGC 7331", "Pégase", "9.5", "11'x4'", "Galaxie de Deer Lick", 22.62, 34.4],
    31: [T["EN"], "IC 405", "Cocher", "-", "30'x20'", "Nébuleuse de l'Étoile Flamboyante", 5.27, 34.3],
    32: [T["G"], "NGC 4631", "Chiens de Chasse", "9.3", "15'x3'", "Galaxie de la Baleine", 12.7, 32.5],
    33: [T["SNR"], "NGC 6992", "Cygne", "-", "78'x8'", "Grande Dentelle du Cygne", 20.94, 31.7],
    34: [T["SNR"], "NGC 6960", "Cygne", "-", "70'x6'", "Petite Dentelle du Cygne", 20.76, 30.7],
    35: [T["G"], "NGC 4889", "Chevelure de Bérénice", "11.4", "1'x1'", "Amas de la Chevelure", 13.0, 28.0],
    36: [T["G"], "NGC 4559", "Chevelure de Bérénice", "9.6", "11'x5'", "NGC 4559", 12.6, 28.0],
    37: [T["OC"], "NGC 6885", "Petit Renard", "6.0", "14'", "NGC 6885", 20.2, 26.5],
    38: [T["G"], "NGC 4565", "Chevelure de Bérénice", "9.6", "16'x3'", "Galaxie de l'Aiguille", 12.6, 26.0],
    39: [T["NP"], "NGC 2392", "Gémeaux", "8.3", "13''", "Nébuleuse de l'Esquimau", 7.48, 20.9],
    40: [T["G"], "NGC 3626", "Lion", "10.7", "3'x2'", "NGC 3626", 11.33, 18.4],
    41: [T["OC"], "Mel 25", "Taureau", "0.5", "330'", "Les Hyades", 4.45, 15.9],
    42: [T["GC"], "NGC 7006", "Dauphin", "10.6", "3'", "NGC 7006", 21.02, 16.2],
    43: [T["G"], "NGC 7814", "Pégase", "10.0", "7'x2'", "NGC 7814", 0.05, 16.1],
    44: [T["G"], "NGC 7479", "Pégase", "10.3", "5'x4'", "NGC 7479", 23.08, 12.3],
    45: [T["G"], "NGC 5248", "Bouvier", "10.0", "5'x5'", "NGC 5248", 13.63, 8.9],
    46: [T["EN"], "NGC 2261", "Licorne", "-", "2'x1'", "Nébuleuse Variable de Hubble", 6.65, 8.7],
    47: [T["GC"], "NGC 6934", "Dauphin", "8.3", "7'", "NGC 6934", 20.57, 7.4],
    48: [T["G"], "NGC 2775", "Hydre", "9.2", "5'x4'", "NGC 2775", 9.17, 7.0],
    49: [T["EN"], "NGC 2237", "Licorne", "-", "80'x60'", "Nébuleuse de la Rosette", 6.54, 5.0],
    50: [T["OC"], "NGC 2244", "Licorne", "4.8", "24'", "Amas de la Rosette", 6.54, 4.9],
    51: [T["G"], "IC 1613", "Baleine", "9.0", "16'x15'", "IC 1613", 1.08, 2.1],
    52: [T["G"], "NGC 4697", "Vierge", "9.4", "4'x3'", "NGC 4697", 12.81, -5.8],
    53: [T["G"], "NGC 3115", "Sextant", "9.2", "8.3x3.2'", "Galaxie du Fuseau", 10.09, -7.7],
    54: [T["OC"], "NGC 2506", "Licorne", "7.6", "14'", "NGC 2506", 8.0, -10.8],
    55: [T["NP"], "NGC 7009", "Verseau", "8.0", "25''", "Nébuleuse Saturne", 21.07, -11.4],
    56: [T["NP"], "NGC 246", "Baleine", "8.0", "4'", "Nébuleuse du Crâne", 0.78, -11.9],
    57: [T["G"], "NGC 6822", "Sagittaire", "7.5", "15'x13'", "Galaxie de Barnard", 19.75, -14.8],
    58: [T["OC"], "NGC 2360", "Grand Chien", "7.2", "20'", "Amas de Caroline", 7.3, -15.6],
    59: [T["NP"], "NGC 3242", "Hydre", "8.3", "16''", "Le Fantôme de Jupiter", 10.41, -18.6],
    60: [T["G"], "NGC 4038", "Corbeau", "10.3", "3'x2'", "Galaxies des Antennes A", 12.03, -18.9],
    61: [T["G"], "NGC 4039", "Corbeau", "10.3", "3'x2'", "Galaxies des Antennes B", 12.03, -19.0],
    62: [T["G"], "NGC 247", "Baleine", "8.9", "12'x3'", "NGC 247", 0.78, -20.8],
    63: [T["NP"], "NGC 7293", "Verseau", "7.3", "13'", "Nébuleuse de l'Hélice", 22.49, -20.8],
    64: [T["OC"], "NGC 2362", "Grand Chien", "4.1", "20'", "NGC 2362", 7.31, -24.9],
    65: [T["G"], "NGC 253", "Sculpteur", "7.1", "25'x7'", "Galaxie du Sculpteur", 0.79, -25.3],
    66: [T["GC"], "NGC 5694", "Hydre", "8.5", "2'", "NGC 5694", 14.66, -26.5],
    67: [T["G"], "NGC 1097", "Fourneau", "9.3", "9'x6'", "NGC 1097", 2.77, -30.3],
    68: [T["EN"], "NGC 6729", "Couronne Australe", "-", "1'", "NGC 6729", 19.03, -36.9],
    69: [T["NP"], "NGC 6302", "Scorpion", "9.6", "2'", "Nébuleuse du Papillon", 17.23, -37.1],
    70: [T["G"], "NGC 300", "Sculpteur", "8.1", "12'x9'", "NGC 300", 0.91, -37.7],
    71: [T["OC"], "NGC 2477", "Poupe", "4.2", "27'", "NGC 2477", 7.87, -38.5],
    72: [T["G"], "NGC 55", "Sculpteur", "7.8", "31'x6'", "NGC 55", 0.25, -39.2],
    73: [T["GC"], "NGC 1851", "Colombe", "7.3", "11'", "NGC 1851", 5.24, -40.1],
    74: [T["NP"], "NGC 3132", "Voiles", "8.2", "1'", "Nébuleuse du Huit Éclatant", 10.12, -40.4],
    75: [T["OC"], "NGC 6124", "Loup", "5.8", "40'", "NGC 6124", 16.42, -40.7],
    76: [T["OC"], "NGC 6231", "Scorpion", "2.6", "15'", "NGC 6231", 16.9, -41.8],
    77: [T["G"], "NGC 5128", "Centaure", "6.8", "18'x14'", "Centaurus A", 13.42, -43.0],
    78: [T["GC"], "NGC 5139", "Centaure", "3.7", "36'", "Omega Centauri", 13.45, -47.5],
    79: [T["OC"], "NGC 4755", "Croix du Sud", "4.2", "10'", "La Boîte à Bijoux", 12.89, -60.3],
    80: [T["GC"], "NGC 5139", "Centaure", "3.7", "36'", "Omega Centauri bis", 13.45, -47.5],
    81: [T["GC"], "NGC 6352", "Autel", "8.1", "6'", "NGC 6352", 17.42, -48.4],
    82: [T["GC"], "NGC 6362", "Autel", "8.1", "12'", "NGC 6362", 17.53, -67.0],
    83: [T["G"], "NGC 4945", "Centaure", "8.6", "13'x4'", "NGC 4945", 13.09, -49.5],
    84: [T["GC"], "NGC 5286", "Centaure", "7.4", "10'", "NGC 5286", 13.77, -51.4],
    85: [T["OC"], "IC 2391", "Voiles", "2.5", "50'", "IC 2391", 8.67, -53.0],
    86: [T["GC"], "NGC 6397", "Autel", "5.3", "30'", "NGC 6397", 17.68, -53.7],
    87: [T["GC"], "NGC 1261", "Horloge", "8.4", "7'", "NGC 1261", 3.2, -55.2],
    88: [T["OC"], "NGC 5823", "Compas", "9.1", "11'", "NGC 5823", 15.09, -55.6],
    89: [T["OC"], "NGC 6067", "Règle", "5.1", "14'", "NGC 6067", 16.22, -54.2],
    90: [T["NP"], "NGC 2867", "Carène", "10.9", "18''", "NGC 2867", 9.36, -58.3],
    91: [T["OC"], "NGC 3532", "Carène", "3.9", "41'", "NGC 3532", 11.11, -58.7],
    92: [T["EN"], "NGC 3372", "Carène", "-", "120'", "Nébuleuse d'Eta Carinae", 10.75, -59.7],
    93: [T["GC"], "NGC 6752", "Paon", "5.4", "27'", "NGC 6752", 19.18, -59.9],
    94: [T["OC"], "NGC 4755", "Croix du Sud", "4.2", "10'", "La Boîte à Bijoux", 12.89, -60.3],
    95: [T["OC"], "NGC 6025", "Triangle Austral", "5.1", "12'", "NGC 6025", 16.03, -60.5],
    96: [T["OC"], "NGC 2516", "Carène", "3.8", "30'", "NGC 2516", 7.97, -60.8],
    97: [T["OC"], "NGC 3766", "Centaure", "3.9", "12'", "NGC 3766", 11.6, -61.5],
    98: [T["OC"], "NGC 4609", "Croix du Sud", "4.1", "5'", "NGC 4609", 12.71, -61.0],
    99: [T["EN"], "C99", "Croix du Sud", "-", "420'x300'", "Nébuleuse du Sac à Charbon", 12.83, -62.5],
    100: [T["EN"], "IC 2944", "Centaure", "-", "60'", "Nébuleuse du Poulet qui Court", 11.6, -63.0],
    101: [T["G"], "NGC 6744", "Paon", "8.3", "16'x11'", "NGC 6744", 19.16, -63.9],
    102: [T["OC"], "IC 2602", "Carène", "1.9", "100'", "Pléiades du Sud", 10.72, -64.4],
    103: [T["EN"], "NGC 2070", "Dorade", "-", "40'", "Nébuleuse de la Tarentule", 5.65, -69.1],
    104: [T["GC"], "NGC 47", "Toucan", "4.0", "31'", "NGC 47", 0.4, -72.1],
    105: [T["GC"], "NGC 4833", "Mouche", "7.8", "14'", "NGC 4833", 12.99, -70.9],
    106: [T["GC"], "NGC 104", "Toucan", "4.0", "31'", "47 Tucanae", 0.4, -72.1],
    107: [T["GC"], "NGC 6101", "Oiseau de Paradis", "9.2", "10'", "NGC 6101", 16.43, -72.2],
    108: [T["GC"], "NGC 4372", "Mouche", "7.2", "20'", "NGC 4372", 12.43, -73.0],
    109: [T["NP"], "NGC 3195", "Caméléon", "10.6", "15''", "NGC 3195", 10.16, -81.2]
}



RASC_DATA = {
    1: [T["NP"], "NGC 7009", "Verseau", "8.3", "25''", "Nébuleuse Saturne", 21.07, -11.4],
    2: [T["NP"], "NGC 7293", "Verseau", "6.5", "12'50''", "Nébuleuse de l'Hélice", 22.49, -20.8],
    3: [T["G"], "NGC 7331", "Pégase", "9.5", "10.7x4.0'", "Galaxie de Deer Lick", 22.62, 34.4],
    4: [T["EN"], "NGC 7635", "Cassiopée", "-", "15x8'", "Nébuleuse de la Bulle", 23.35, 61.2],
    5: [T["OC"], "NGC 7789", "Cassiopée", "6.7", "16'", "Amas de la Rose Blanche", 23.95, 56.7],
    6: [T["G"], "NGC 185", "Cassiopée", "11.7", "2x2'", "Galaxie naine de Cassiopée", 0.65, 48.3],
    7: [T["EN"], "NGC 281", "Cassiopée", "-", "35x30'", "Nébuleuse Pacman", 0.87, 56.6],
    8: [T["OC"], "NGC 457", "Cassiopée", "6.4", "13'", "Amas de la Chouette", 1.32, 58.3],
    9: [T["OC"], "NGC 663", "Cassiopée", "7.1", "16'", "Amas de l'Écharpe (Scarf Cluster)", 1.77, 61.2],
    10: [T["NP"], "NGC 1289", "Cassiopée", "12.3", "34''", "Phantom Streak Nebula", 0.51, 61.3],
    11: [T["NP"], "NGC 7662", "Andromède", "9.2", "20''", "Nébuleuse de la Boule de Neige Bleue", 23.43, 42.5],
    12: [T["G"], "NGC 891", "Andromède", "10", "13.5x2.8'", "Galaxie de l'Aiguille d'Argent", 2.38, 42.3],
    13: [T["G"], "NGC 253", "Sculpteur", "7.1", "25.1x7.4'", "Galaxie du Sculpteur", 0.79, -25.3],
    14: [T["G"], "NGC 772", "Bélier", "10.3", "7.1x4.5'", "Galaxie Spirale", 1.98, 19.0],
    15: [T["NP"], "NGC 246", "Baleine", "8.0", "3'45''", "Nébuleuse du Crâne", 0.78, -11.9],
    16: [T["G"], "NGC 936", "Baleine", "10.1", "5.2x4.4'", "Galaxie lenticulaire", 2.47, -1.1],
    17: [T["OC"], "NGC 869", "Persée", "4.4", "30'/30'", "Double Amas de Persée", 2.32, 57.1],
    18: [T["G"], "NGC 1023", "Persée", "9.5", "8.7x4.3'", "Galaxie lenticulaire", 2.67, 39.0],
    19: [T["EN"], "NGC 1491", "Persée", "-", "3.0x3.0'", "Fossil Footprint Nebula", 4.05, 51.3],
    20: [T["NP"], "NGC 1501", "Girafe", "12.0", "52''", "Nébuleuse de l'Huître", 4.11, 60.9],
    21: [T["G"], "NGC 1232", "Eridan", "9.9", "7.8x6.9'", "Galaxie NGC 1232", 3.16, -20.6],
    22: [T["NP"], "NGC 1535", "Eridan", "10.4", "18''", "Nébuleuse de l'Œil de Cléopâtre", 4.24, -12.7],
    23: [T["NP"], "NGC 1514", "Taureau", "10.8", "1'54''", "Crystal Ball Nebula", 4.15, 30.8],
    24: [T["E/RN"], "NGC 1931", "Cocher", "-", "3.0x3.0'", "Fly Nebula", 5.52, 34.2],
    25: [T["RN"], "NGC 1788", "Orion", "-", "8.0x5.0'", "Nébuleuse de la Tête de Renard", 5.13, -3.3],
    26: [T["E/RN"], "NGC 1973", "Orion", "-", "40x25'", "Nébuleuse Courante", 5.58, -4.7],
    27: [T["NP"], "NGC 2022", "Orion", "12.4", "18''", "Nébuleuse planétaire", 5.7, 9.1],
    28: [T["EN"], "NGC 2024", "Orion", "-", "30x30'", "Nébuleuse de la Flamme", 5.69, -1.9],
    29: [T["OC"], "NGC 2194", "Orion", "8.5", "10'", "Amas ouvert", 6.23, 12.8],
    30: [T["NP"], "NGC 2371", "Gémeaux", "13.0", "55''", "Nébuleuse de la Cacahuète", 7.43, 29.5],
    31: [T["NP"], "NGC 2392", "Gémeaux", "8.3", "13''", "Nébuleuse de l'Esquimau", 7.48, 20.9],
    32: [T["EN"], "NGC 2237", "Licorne", "-", "80x60'", "Nébuleuse de la Rosette", 6.54, 5.0],
    33: [T["E/RN"], "NGC 2261", "Licorne", "var", "2x1'", "Nébuleuse Variable de Hubble", 6.65, 8.7],
    34: [T["EN"], "NGC 2359", "Grand Chien", "-", "8.0x6.0'", "Nébuleuse du Casque de Thor", 7.31, -13.2],
    35: [T["NP"], "NGC 2440", "Poupe", "10.3", "14''", "Nébuleuse de l'Insecte", 7.69, -18.2],
    36: [T["OC"], "NGC 2539", "Poupe", "6.5", "22'", "Amas ouvert", 8.18, -12.8],
    37: [T["G"], "NGC 2403", "Girafe", "8.4", "17.8x11.0'", "Galaxie spirale", 7.62, 65.6],
    38: [T["G"], "NGC 2655", "Girafe", "10.1", "5.1x4.4'", "Galaxie lenticulaire", 8.9, 78.2],
    39: [T["G"], "NGC 2683", "Lynx", "9.7", "9.3x2.5'", "Galaxie de la Soucoupe volante", 8.88, 33.4],
    40: [T["G"], "NGC 2841", "Grande Ourse", "9.3", "8.1x3.8'", "Galaxie spirale", 9.37, 51.0],
    41: [T["G"], "NGC 3079", "Grande Ourse", "10.6", "7.6x1.7'", "Galaxie spirale", 10.03, 55.7],
    42: [T["G"], "NGC 3184", "Grande Ourse", "9.7", "6.9x6.8'", "Galaxie spirale", 10.3, 41.4],
    43: [T["G"], "NGC 3877", "Grande Ourse", "10.9", "5.4x1.5'", "Galaxie spirale", 11.77, 47.5],
    44: [T["G"], "NGC 3941", "Grande Ourse", "9.8", "3.8x2.5'", "Galaxie lenticulaire", 11.88, 45.0],
    45: [T["G"], "NGC 4026", "Grande Ourse", "10.7", "5.1x1.4'", "Galaxie lenticulaire", 11.99, 50.9],
    46: [T["G"], "NGC 4088", "Grande Ourse", "10.5", "5.8x2.5'", "Galaxie spirale", 12.1, 50.5],
    47: [T["G"], "NGC 4157", "Grande Ourse", "11.9", "6.9x1.7'", "Galaxie spirale", 12.2, 50.5],
    48: [T["G"], "NGC 4605", "Grande Ourse", "9.6", "5.5x2.3'", "Galaxie spirale", 12.67, 61.6],
    49: [T["G"], "NGC 3115", "Sextant", "9.2", "8.3x3.2'", "Galaxie du Fuseau", 10.09, -7.7],
    50: [T["NP"], "NGC 3242", "Hydre", "8.6", "16''", "Le Fantôme de Jupiter", 10.41, -18.6],
    51: [T["G"], "NGC 3003", "Petit Lion", "11.7", "5.9x1.7'", "Galaxie spirale", 9.81, 33.4],
    52: [T["G"], "NGC 3344", "Petit Lion", "9.9", "6.9x6.5'", "Galaxie du Petit Moulinet", 10.73, 25.0],
    53: [T["G"], "NGC 3432", "Petit Lion", "11.3", "6.2x1.5'", "Galaxie spirale", 10.91, 36.6],
    54: [T["G"], "NGC 2903", "Lion", "8.9", "12.6x6.6'", "Galaxie spirale", 9.54, 21.5],
    55: [T["G"], "NGC 3384", "Lion", "9.9", "5.9x2.6'", "Galaxie lenticulaire", 10.8, 12.6],
    56: [T["G"], "NGC 3521", "Lion", "8.7", "9.5x5.0'", "Galaxie spirale", 11.08, -0.0],
    57: [T["G"], "NGC 3607", "Lion", "10.0", "3.7x3.2'", "Galaxie elliptique", 11.28, 18.0],
    58: [T["G"], "NGC 3628", "Lion", "9.5", "14.8x3.6'", "Galaxie de l'Arête", 11.34, 13.6],
    59: [T["G"], "NGC 4111", "Chiens de Chasse", "10.8", "4.8x1.1'", "Galaxie lenticulaire", 12.12, 43.1],
    60: [T["G"], "NGC 4214", "Chiens de Chasse", "9.7", "7.9x6.3'", "Galaxie irrégulière", 12.26, 36.3],
    61: [T["G"], "NGC 4244", "Chiens de Chasse", "10.2", "16.2x2.5'", "Galaxie de la Lame d'Argent", 12.3, 37.8],
    62: [T["G"], "NGC 4449", "Chiens de Chasse", "9.4", "5.1x3.7'", "Galaxie irrégulière", 12.47, 44.1],
    63: [T["G"], "NGC 4490", "Chiens de Chasse", "9.8", "5.9x3.1'", "Galaxies des Cocons", 12.51, 41.6],
    64: [T["G"], "NGC 4631", "Chiens de Chasse", "9.3", "15.1x3.3'", "Galaxie de la Baleine", 12.7, 32.5],
    65: [T["G"], "NGC 4656", "Chiens de Chasse", "10.4", "13.8x3.3'", "La Crosse de Hockey", 12.71, 32.2],
    66: [T["G"], "NGC 5005", "Chiens de Chasse", "9.8", "5.9x3.1'", "Galaxie spirale", 13.18, 37.1],
    67: [T["G"], "NGC 5033", "Chiens de Chasse", "10.1", "10.5x5.6'", "Galaxie spirale", 13.22, 36.6],
    68: [T["G"], "NGC 4274", "Chevelure de Bérénice", "10.4", "6.9x2.8'", "Galaxie spirale", 12.33, 29.6],
    69: [T["G"], "NGC 4414", "Chevelure de Bérénice", "10.2", "3.6x2.2'", "Galaxie spirale", 12.44, 31.2],
    70: [T["G"], "NGC 4494", "Chevelure de Bérénice", "9.8", "4.8x3.8'", "Galaxie elliptique", 12.52, 25.8],
    71: [T["G"], "NGC 4559", "Chevelure de Bérénice", "9.8", "10.5x4.9'", "Galaxie spirale", 12.6, 28.0],
    72: [T["G"], "NGC 4565", "Chevelure de Bérénice", "9.6", "16.2x2.8'", "Galaxie de l'Aiguille", 12.6, 26.0],
    73: [T["G"], "NGC 4725", "Chevelure de Bérénice", "9.2", "11.0x7.9'", "Galaxie spirale", 12.84, 25.5],
    74: [T["G"], "NGC 4038", "Corbeau", "10.7", "~3x2'", "Galaxies des Antennes", 12.03, -18.9],
    75: [T["NP"], "NGC 4361", "Corbeau", "10.3", "45''", "Galaxie de l'Atome pour la Paix", 12.41, -18.8],
    76: [T["G"], "NGC 4216", "Vierge", "9.9", "8.3x2.2'", "Galaxie spirale", 12.26, 13.1],
    77: [T["G"], "NGC 4388", "Vierge", "11.0", "5.1x1.4'", "Galaxie spirale", 12.43, 12.7],
    78: [T["G"], "NGC 4438", "Vierge", "10.1", "9.3x3.9'", "Les Yeux", 12.46, 13.0],
    79: [T["G"], "NGC 4517", "Vierge", "10.5", "10.2x1.9'", "Galaxie spirale", 12.54, 0.1],
    80: [T["G"], "NGC 4526", "Vierge", "9.6", "7.6x2.3'", "Galaxie spirale", 12.57, 7.7],
    81: [T["G"], "NGC 4535", "Vierge", "9.8", "6.8x5.0'", "Galaxie spirale", 12.57, 8.2],
    82: [T["G"], "NGC 4567", "Vierge", "~11", "4.6x2.1'", "Les Jumeaux Siamois", 12.61, 11.3],
    83: [T["G"], "NGC 4699", "Vierge", "9.6", "3.5x2.7'", "Galaxie spirale", 12.81, -8.7],
    84: [T["G"], "NGC 4762", "Vierge", "10.2", "8.7x1.6'", "Galaxie de l'Équerre", 12.88, 11.2],
    85: [T["G"], "NGC 5746", "Vierge", "10.6", "7.9x1.7'", "Galaxie spirale", 14.75, 1.9],
    86: [T["GC"], "NGC 5466", "Bouvier", "9.1", "11.0'", "Amas globulaire", 14.09, 28.5],
    87: [T["G"], "NGC 5907", "Dragon", "10.4", "12.3x1.8'", "Galaxie de l'Éclat", 15.26, 56.3],
    88: [T["G"], "NGC 6503", "Dragon", "10.2", "6.2x2.3'", "Galaxie spirale", 17.81, 70.1],
    89: [T["NP"], "NGC 6543", "Dragon", "8.8", "18''", "Nébuleuse de l'Œil de Chat", 17.98, 66.6],
    90: [T["NP"], "NGC 6210", "Hercule", "9.3", "14''", "Nébuleuse de la Tortue", 16.74, 23.8],
    91: [T["NP"], "NGC 6369", "Ophiuchus", "10.4", "30''", "Nébuleuse du Petit Fantôme", 17.49, -17.8],
    92: [T["NP"], "NGC 6572", "Ophiuchus", "9.0", "8''", "Emerald Nebula", 18.2, 6.8],
    93: [T["OC"], "NGC 6633", "Ophiuchus", "4.6", "27'", "Amas de Tweedledum", 18.46, 6.5],
    94: [T["GC"], "NGC 6712", "Ecu de Sobieski", "8.2", "7.2'", "Amas globulaire", 18.89, -8.7],
    95: [T["NP"], "NGC 6781", "Aigle", "11.8", "1'49''", "Phantom Feather Nebula", 19.31, 6.5],
    96: [T["OC"], "NGC 6819", "Cygne", "7.3", "5'", "Amas de la Tête de Renard (Foxhead)", 19.69, 40.2],
    97: [T["NP"], "NGC 6826", "Cygne", "9.8", "30''", "Nébuleuse de l'Œil Clignotant", 19.75, 50.5],
    98: [T["SNR"], "NGC 6888", "Cygne", "-", "20x10'", "Nébuleuse du Croissant", 20.2, 38.4],
    "99a": [T["SNR"], "NGC 6960", "Cygne", "-", "70x6'", "Petite Dentelle du Cygne", 20.76, 30.7],
    "99b": [T["SNR"], "NGC 6992", "Cygne", "-", "78x8'", "Grande Dentelle du Cygne", 20.94, 31.7],
    100: [T["EN"], "NGC 7000", "Cygne", "-", "120x100'", "Nébuleuse de l'Amérique du Nord", 20.99, 44.3],
    101: [T["NP"], "NGC 7027", "Cygne", "10.4", "15''", "Nébuleuse planétaire", 21.12, 42.2],
    102: [T["NP"], "NGC 6445", "Sagittaire", "11.8", "34''", "Little Gem Nebula", 17.82, -16.2],
    103: [T["OC"], "NGC 6520", "Sagittaire", "8.1", "6'", "Amas ouvert", 18.06, -27.9],
    104: [T["NP"], "NGC 6818", "Sagittaire", "9.9", "17''", "Little Gem Nebula", 19.73, -16.2],
    105: [T["OC"], "NGC 6802", "Petit Renard", "8.8", "3.2'", "Amas ouvert", 19.51, 20.3],
    106: [T["OC"], "NGC 6940", "Petit Renard", "6.3", "31'", "Amas ouvert", 20.58, 28.3],
    107: [T["OC"], "NGC 6939", "Céphée", "7.8", "8'", "Amas ouvert", 20.57, 60.6],
    108: [T["G"], "NGC 6946", "Céphée", "8.9", "11.0x9.8'", "Galaxie du Feu d'Artifice", 20.58, 60.1],
    109: [T["RN"], "NGC 7129", "Céphée", "-", "8x7'", "Nébuleuse par réflexion", 21.72, 66.1],
    110: [T["NP"], "NGC 40", "Céphée", "10.2", "37''", "Nébuleuse du Nœud Coulant", 0.05, 72.5]
}

O_MEARA_DATA = {
    # hidden treasures
    1: [T["OC"], "NGC 189", "Cassiopée", "8.8", "5'", "NGC 189", 0.38, 61.1],
    2: [T["OC"], "Amas du Voilier", "Cassiopée", "7.0", "15'", "Amas du Voilier", 0.73, 61.8],
    3: [T["N"], "NGC 281", "Cassiopée", "7.8", "30'x35'", "Nébuleuse Pacman", 0.87, 56.6],
    4: [T["GC"], "NGC 288", "Sculpteur", "8.1", "13'", "NGC 288", 0.88, -26.6],
    5: [T["G"], "NGC 404", "Andromède", "10.0", "3.5'", "Galaxie de la Perle Perdue", 1.16, 35.7],
    6: [T["G"], "NGC 584", "Céto", "10.5", "4'x2'", "Galaxie du Petit Fuseau", 1.52, -6.9],
    7: [T["OC"], "NGC 659", "Cassiopée", "7.9", "6'", "Amas Ying Yang", 1.77, 60.7],
    8: [T["G"], "NGC 772", "Bélier", "10.3", "7'x4'", "Galaxie Fiddlehead", 1.99, 19.0],
    9: [T["G"], "NGC 908", "Céto", "10.2", "6'x3'", "NGC 908", 2.38, -21.2],
    10: [T["G"], "NGC 1023", "Persée", "9.5", "7'x3'", "Galaxie Lenticulaire de Persée", 2.67, 39.1],
    11: [T["G"], "NGC 1232", "Éridan", "9.8", "7'x7'", "Galaxie de l'Œil de Dieu", 3.16, -20.6],
    12: [T["G"], "NGC 1291", "Éridan", "8.5", "11'x10'", "Galaxie au Col de Neige", 3.29, -41.1],
    13: [T["G"], "NGC 1316", "Fourneau", "9.4", "12'x9'", "Fornax A", 3.38, -37.2],
    14: [T["OC"], "Alpha Per", "Persée", "1.2", "185'", "Amas d'Alpha Persei", 3.40, 49.0],
    15: [T["N"], "NGC 1333", "Persée", "5.7", "3'", "nuage de Persée (NGC 1333)", 3.48, 31.4],
    16: [T["NP"], "NGC 1360", "Fourneau", "9.4", "6'", "Nébuleuse de l'Embryon", 3.55, -25.9],
    17: [T["G"], "NGC 1365", "Fourneau", "9.5", "11'x6'", "NGC 1365", 3.56, -36.1],
    18: [T["G"], "NGC 1399", "Fourneau", "9.4", "7'x7'", "NGC 1399", 3.64, -35.4],
    19: [T["G"], "NGC 1398", "Fourneau", "9.5", "8'x5'", "NGC 1398", 3.65, -26.3],
    20: [T["G"], "NGC 1404", "Fourneau", "10.0", "3'x3'", "NGC 1404", 3.65, -35.6],
    21: [T["A"], "Kemble 1", "Girafe", "5.0", "150'", "Cascade de Kemble", 3.96, 63.0],
    22: [T["NP"], "NGC 1501", "Girafe", "11.5", "0.9'", "Nébuleuse de l'Huître", 4.11, 61.0],
    23: [T["OC"], "NGC 1502", "Girafe", "6.0", "20'", "Amas du Jolly Roger", 4.13, 62.3],
    24: [T["NP"], "NGC 1535", "Éridan", "9.6", "0.9'", "Œil de Cléopâtre", 4.24, -12.7],
    25: [T["OC"], "NGC 1528", "Persée", "6.4", "18'", "Amas m & m", 4.25, 51.2],
    26: [T["OC"], "NGC 1545", "Persée", "6.2", "12'", "Amas m & m", 4.30, 50.3],
    27: [T["OC"], "NGC 1647", "Taureau", "6.4", "40'", "Amas de la Lune Pirate", 4.77, 19.1],
    28: [T["NP"], "IC 418", "Lièvre", "9.6", "0.5'", "Nébuleuse de la Framboise", 5.10, -12.7],
    29: [T["OC"], "Cr 69", "Orion", "5.0", "50'", "Amas de Lambda Orionis", 5.58, 9.9],
    30: [T["OC"], "NGC 1981", "Orion", "4.2", "28'", "Amas du Wagon de Charbon", 5.59, -4.4],
    31: [T["OC"], "NGC 1980", "Orion", "5.0", "30'", "Le Joyau Perdu d'Orion", 5.59, -4.9],
    32: [T["N"], "NGC 1977", "Orion", "6.3", "20'", "Nébuleuse de l'Homme qui Court", 5.59, -4.8],
    33: [T["N"], "NGC 1999", "Orion", "9.5", "2'", "Nébuleuse du Tampon en Caoutchouc", 5.61, -6.7],
    34: [T["N"], "NGC 2024", "Orion", "7.2", "30'", "Nébuleuse de la Flamme", 5.69, 1.9],
    35: [T["N"], "NGC 2163", "Orion", "10.0", "3'", "NGC 2163", 6.25, 18.7],
    36: [T["OC"], "NGC 2169", "Orion", "5.9", "6'", "Amas des Petites Pléiades", 6.36, 14.0],
    37: [T["N"], "NGC 2175", "Orion", "6.9", "18'", "NGC 2175", 6.38, 20.5],
    38: [T["OC"], "NGC 2264", "Licorne", "4.1", "40'", "Amas de l'Arbre de Noël", 6.68, 9.9],
    39: [T["OC"], "NGC 2301", "Licorne", "6.0", "15'", "Le Dragon d'Hagrid", 6.86, 0.5],
    40: [T["OC"], "NGC 2353", "Licorne", "7.1", "18'", "Avery's Island", 7.24, -10.3],
    41: [T["NP"], "NGC 2440", "Poupe", "9.4", "1.3'", "Nébuleuse du Papillon Albinos", 7.70, -18.2],
    42: [T["OC"], "NGC 2451", "Poupe", "2.8", "50'", "Amas du Scorpion Piquant", 7.75, -38.0],
    43: [T["N"], "NGC 2467", "Poupe", "7.1", "15'", "NGC 2467", 7.87, -26.4],
    44: [T["OC"], "NGC 2547", "Voiles", "4.7", "25'", "Amas de la Boucle d'Oreille d'Or", 8.17, -49.2],
    45: [T["OC"], "NGC 2539", "Poupe", "6.5", "15'", "Amas de l'Assiette", 8.18, -12.8],
    46: [T["OC"], "NGC 2546", "Poupe", "6.3", "70'", "Amas du Cœur et de la Dague", 8.20, -37.6],
    47: [T["G"], "NGC 2683", "Lynx", "9.7", "9'x2'", "Galaxie de l'OVNI", 8.88, 33.4],
    48: [T["G"], "NGC 2655", "Girafe", "10.1", "5'x4'", "NGC 2655", 8.93, 78.2],
    49: [T["G"], "NGC 2841", "Grande Ourse", "9.3", "8'x4'", "Galaxie de l'Œil de Tigre", 9.55, 51.0],
    50: [T["OC"], "IC 2488", "Voiles", "7.0", "15'", "Amas du Collier de Perles", 9.77, -57.0],
    51: [T["G"], "NGC 2903", "Lion", "8.8", "13'x6'", "NGC 2903", 9.53, 21.5],
    52: [T["G"], "NGC 3184", "Grande Ourse", "9.6", "7'x7'", "Petite Galaxie du Moulinet", 10.30, 41.4],
    53: [T["OC"], "NGC 3228", "Voiles", "6.0", "5'", "Amas du Trésor de la Reine", 10.36, -51.7],
    54: [T["OC"], "NGC 3293", "Carène", "4.7", "5'", "Petite Boîte à Bijoux", 10.58, -58.2],
    55: [T["G"], "NGC 3344", "Petit Lion", "9.7", "7'x7'", "NGC 3344", 10.73, 24.9],
    56: [T["G"], "NGC 3521", "Lion", "9.2", "11'x5'", "NGC 3521", 11.09, 0.0],
    57: [T["G"], "NGC 3621", "Hydre", "9.4", "12'x7'", "Galaxie Cadre", 11.31, -32.8],
    58: [T["G"], "NGC 3628", "Lion", "9.6", "13'x3'", "Galaxie du Fantôme du Roi Hamlet", 11.34, 13.6],
    59: [T["G"], "NGC 4214", "Chiens de Chasse", "9.6", "8'x7'", "NGC 4214", 12.26, 36.3],
    60: [T["G"], "NGC 4216", "Vierge", "10.3", "8'x2'", "Galaxie Silver Streak", 12.26, 13.1],
    61: [T["NP"], "NGC 4361", "Corbeau", "10.9", "2.1'", "NGC 4361", 12.41, -18.8],
    62: [T["OC"], "Mel 111", "Chevelure de Bérénice", "1.8", "300'", "Amas de Coma", 12.42, 25.9],
    63: [T["G"], "NGC 4490", "Chiens de Chasse", "9.5", "6'x3'", "Galaxie du Cocon", 12.51, 41.6],
    64: [T["NP"], "IC 3568", "Girafe", "10.6", "0.3'", "Nébuleuse du Citron Vert", 12.55, 82.6],
    65: [T["G"], "NGC 4526", "Vierge", "9.6", "7'x3'", "Galaxie du Sourcil Poilu", 12.57, 7.7],
    66: [T["G"], "NGC 4605", "Grande Ourse", "10.1", "6'x2'", "Galaxie de l'Œuf de Fabergé", 12.69, 61.6],
    67: [T["G"], "NGC 4656", "Chiens de Chasse", "10.1", "15'x2'", "Galaxie du Crochet", 12.71, 32.2],
    68: [T["G"], "NGC 4699", "Vierge", "9.6", "4'x3'", "NGC 4699", 12.82, -8.7],
    69: [T["G"], "NGC 4725", "Chevelure de Bérénice", "9.3", "11'x8'", "NGC 4725", 12.84, 25.5],
    70: [T["G"], "NGC 5102", "Centaure", "9.5", "9'x3'", "Le Fantôme d'Iota", 13.36, -36.6],
    71: [T["OC"], "NGC 5281", "Centaure", "5.9", "8'", "Amas du Petit Scorpion", 13.80, -62.9],
    72: [T["G"], "NGC 5363", "Vierge", "10.5", "4'x3'", "NGC 5363", 13.94, 5.3],
    73: [T["OC"], "NGC 5662", "Centaure", "5.5", "30'", "NGC 5662", 14.59, -56.7],
    74: [T["G"], "NGC 5746", "Vierge", "10.5", "7'x1'", "Galaxie de la Lame et la Perle", 14.75, 2.0],
    75: [T["G"], "NGC 5866", "Dragon", "9.9", "7'x3'", "Galaxie de l'Or des Fous", 15.11, 55.8],
    76: [T["GC"], "NGC 5897", "Balance", "8.4", "11'", "Amas Globulaire Fantôme", 15.30, -21.0],
    77: [T["GC"], "NGC 5986", "Loup", "7.6", "10'", "NGC 5986", 15.77, -37.8],
    78: [T["NP"], "NGC 6210", "Hercule", "8.8", "0.4'", "Nébuleuse de la Tortue", 16.74, 23.8],
    79: [T["OC"], "NGC 6242", "Scorpion", "6.4", "9'", "NGC 6242", 16.92, -39.5],
    80: [T["OC"], "NGC 6281", "Scorpion", "5.4", "8'", "Amas de l'Aile de Papillon de Nuit", 17.01, -37.9],
    81: [T["NP"], "NGC 6369", "Ophiuchus", "11.4", "0.6'", "Nébuleuse du Petit Fantôme", 17.49, -23.8],
    82: [T["OC"], "NGC 6400", "Scorpion", "8.8", "12'", "Amas Fantôme", 17.67, -37.0],
    83: [T["OC"], "NGC 4665", "Ophiuchus", "8.3", "45'", "La Ruche d'Été", 17.66, 5.7],
    84: [T["NP"], "NGC 6445", "Sagittaire", "11.2", "0.7'", "Nébuleuse de la Boîte", 17.82, -20.0],
    85: [T["G"], "NGC 6503", "Dragon", "10.2", "7'x3'", "Galaxie Perdue dans l'Space", 17.82, 70.1],
    86: [T["GC"], "NGC 6441", "Scorpion", "7.2", "10'", "Amas de la Pépite d'Argent", 17.83, -37.1],
    87: [T["D"], "Barnard", "Ophiuchus", "9.5", "n/a", "Étoile de Barnard", 17.96, 4.7],
    88: [T["OC"], "NGC 6520", "Sagittaire", "7.6", "5'", "Le Coffre du Mort", 18.06, -27.9],
    89: [T["GC"], "NGC 6544", "Sagittaire", "7.5", "9'", "Amas de l'Étoile de Mer", 18.12, -25.0],
    90: [T["NP"], "NGC 6572", "Ophiuchus", "8.1", "0.3'", "Nébuleuse de l'Œil d'Émeraude", 18.20, 6.9],
    91: [T["GC"], "NGC 6624", "Sagittaire", "7.6", "9'", "NGC 6624", 18.39, -30.4],
    92: [T["OC"], "NGC 6633", "Ophiuchus", "4.6", "20'", "Amas de Tweedledum", 18.46, 6.5],
    93: [T["OC"], "IC 4756", "Serpent", "5.0", "52'", "Amas de Graff", 18.65, 5.4],
    94: [T["OC"], "NGC 6709", "Aigle", "6.7", "15'", "Amas de la Licorne Volante", 18.86, 10.3],
    95: [T["GC"], "NGC 6712", "Écu", "8.1", "10'", "NGC 6712", 18.88, -8.7],
    96: [T["GC"], "NGC 6723", "Sagittaire", "6.8", "13'", "NGC 6723", 18.99, -36.6],
    97: [T["A"], "Cr 399", "Petit Renard", "3.6", "60'", "Le Cintre", 19.42, 20.2],
    98: [T["OC"], "NGC 6819", "Cygne", "7.3", "5'", "Amas de la Tête de Renard", 19.69, 40.2],
    99: [T["NP"], "NGC 6818", "Sagittaire", "9.3", "0.8'", "Nébuleuse du Petit Joyau", 19.73, -14.2],
    100: [T["OC"], "NGC 6866", "Cygne", "7.6", "7'", "Amas de la Frégate Pirate", 20.06, 44.2],
    101: [T["OC"], "NGC 6940", "Petit Renard", "6.3", "25'", "Amas de Mothra", 20.58, 28.3],
    102: [T["N"], "LDN 906", "Cygne", "n/a", "480'", "Sac à Charbon du Nord", 20.62, 41.0],
    103: [T["NP"], "NGC 7008", "Cygne", "10.7", "1.4'", "Nébuleuse du Bouton de Manteau", 21.01, 54.5],
    104: [T["NP"], "NGC 7027", "Cygne", "8.5", "0.3'", "NGC 7027", 21.12, 42.2],
    105: [T["N+C"], "IC 1396", "Céphée", "3.5", "154'", "Amas de l'Éléphant / Trèfle", 21.65, 57.8],
    106: [T["OC"], "NGC 7380", "Céphée", "7.2", "20'", "Vif d'Or de Harry Potter", 22.78, 58.1],
    107: [T["A"], "Asterism", "Poissons", "8.0", "12'", "Petite Louche", 23.82, 8.0],
    108: [T["OC"], "NGC 7789", "Cassiopée", "6.7", "25'", "Amas de la Rose Rose (O'Meara)", 23.95, 56.7],
    109: [T["G"], "NGC 7793", "Sculpteur", "9.0", "9'", "Galaxie de Bond", 23.98, -32.6],
    # secret deep
    1001: [T["RN"], "vdB 1", "Cassiopée", "10.1", "8.6'", "vdB 1", 0.18, 58.7],
    1002: [T["G"], "NGC 134", "Sculpteur", "10.4", "8.1'", "Galaxie du Calmar Géant", 0.50, -33.2],
    1003: [T["G"], "NGC 488", "Poissons", "10.4", "5.2'", "Galaxie du Tourbillon", 1.39, 5.2],
    1004: [T["OC"], "NGC 654", "Cassiopée", "7.9", "40'", "Amas ouvert avec nébulosité", 1.74, 61.8],
    1005: [T["OC"], "Collinder 463", "Cassiopée", "9.1", "57'", "Lund 57 / Loch Ness monster", 1.89, 71.9],
    1006: [T["OC"], "Stock 2", "Cassiopée", "4.4", "130'", "Strong Man Cluster", 2.25, 59.4],
    1007: [T["G"], "NGC 936", "Céto", "10.1", "5.2'", "Galaxie de la Soucoupe", 2.46, -1.1],
    1008: [T["G"], "NGC 1084", "Éridan", "10.6", "2.9'", "Galaxie de la Truffe", 2.77, -7.5],
    1009: [T["OC"], "NGC 1245", "Persée", "7.6", "10'", "Amas de l'Étoile de Mer", 3.24, 47.2],
    1010: [T["G"], "NGC 1300", "Éridan", "10.4", "6.5'", "Galaxie spirale barrée", 3.33, -19.4],
    1011: [T["OC"], "NGC 1342", "Persée", "8.1", "30'", "Amas de la Raie / Petit Scorpion", 3.53, 37.3],
    1012: [T["N"], "Barnard 33", "Orion", "10.0", "90'", "La Tête de Cheval (dans Barnard's Loop)", 5.68, 0.7],
    1013: [T["G"], "NGC 1400", "Éridan", "10.8", "1.9'", "Galaxie avec NGC 1407", 3.66, -18.6],
    1014: [T["G"], "NGC 1407", "Éridan", "9.7", "2.5'", "Galaxie avec NGC 1400", 3.67, -18.5],
    1015: [T["EN"], "NGC 1491", "Persée", "10.0", "12'", "Nébuleuse de l'Empreinte Fossile", 4.05, 51.3],
    1016: [T["NP"], "NGC 1514", "Taureau", "10.0", "2'", "Nébuleuse de la Boule de Cristal", 4.15, 30.7],
    1017: [T["EN"], "NGC 1579", "Persée", "10.0", "12'", "Trifide du Nord", 4.51, 35.2],
    1018: [T["OC"], "NGC 1750", "Taureau", "7.0", "60'", "Amas ouvert", 5.06, 23.6],
    1019: [T["OC"], "NGC 1758", "Taureau", "7.0", "90'", "Amas ouvert", 5.07, 23.7],
    1020: [T["EN"], "NGC 1788", "Orion", "10.0", "8'", "Chauve-Souris Cosmique / Foxface", 5.13, -3.3],
    1021: [T["OC"], "NGC 1807", "Taureau", "7.0", "17'", "Amas ouvert", 5.20, 16.5],
    1022: [T["OC"], "NGC 1817", "Taureau", "7.7", "16'", "Amas ouvert", 5.21, 16.6],
    1023: [T["EN"], "IC 417", "Cocher", "10.0", "13'", "Nébuleuse de l'Araignée", 5.47, 34.4],
    1024: [T["OC"], "NGC 1931", "Cocher", "8.3", "3'", "La Mouche (avec IC 417)", 5.52, 34.2],
    1025: [T["OC"], "Collinder 70", "Orion", "0.4", "150'", "Ceinture d'Orion", 5.60, -1.0],
    1026: [T["NP"], "NGC 2022", "Orion", "11.6", "0.5'", "Nébuleuse des Baisers", 5.70, 9.1],
    1027: [T["NP"], "IC 2149", "Cocher", "11.5", "0.25'", "Nébuleuse planétaire", 5.91, 46.1],
    1028: [T["EN"], "NGC 2149", "Licorne", "10.0", "3'", "Nébuleuse par émission", 6.13, -9.7],
    1029: [T["RN"], "NGC 2170", "Licorne", "10.0", "110'", "Nébuleuse de l'Ange", 6.13, -6.3],
    1030: [T["OC"], "NGC 2281", "Cocher", "7.2", "15'", "Amas du Cœur Brisé", 6.81, 41.1],
    1031: [T["GC"], "NGC 2298", "Poupe", "7.3", "6.8'", "Amas Globulaire de la Poupe", 6.81, -36.0],
    1032: [T["EN"], "NGC 2316", "Licorne", "10.0", "4'", "Nébuleuse par émission", 7.02, -7.7],
    1033: [T["OC"], "NGC 2343", "Licorne", "5.5", "7'", "Amas ouvert", 7.14, -10.6],
    1034: [T["NP"], "NGC 2346", "Licorne", "10.3", "2'", "Nébuleuse du Papillon", 7.15, -0.8],
    1035: [T["EN"], "NGC 2359", "Grand Chien", "10.0", "10'", "Casque de Thor / Canard", 7.31, -13.2],
    1036: [T["NP"], "NGC 2371", "Gémeaux", "9.1", "2.1'", "Nébuleuse de la Double Bulle", 7.43, 29.4],
    1037: [T["OC"], "NGC 2420", "Gémeaux", "9.1", "10'", "Amas de la Comète Scintillante", 7.64, 21.5],
    1038: [T["G"], "NGC 3079", "Grande Ourse", "10.1", "7.6'", "Galaxie du Frisbee Fantôme", 10.03, 55.6],
    1039: [T["G"], "NGC 3077", "Grande Ourse", "10.0", "4.6'", "Galaxie irrégulière", 10.06, 68.7],
    1040: [T["G"], "NGC 3166", "Sextant", "10.5", "30'", "Galaxie Impétueuse", 10.27, 3.4],
    1041: [T["G"], "NGC 3169", "Sextant", "10.3", "4.8'", "Galaxie spirale", 10.27, 3.4],
    1042: [T["G"], "NGC 3198", "Grande Ourse", "10.7", "8.3'", "Galaxie spirale", 10.33, 45.5],
    1043: [T["G"], "NGC 3226", "Lion", "10.3", "2.8'", "Arp 94 (avec NGC 3227)", 10.40, 19.8],
    1044: [T["G"], "NGC 3227", "Lion", "10.3", "5.6'", "Arp 94 (avec NGC 3226)", 10.40, 19.8],
    1045: [T["G"], "NGC 3432", "Petit Lion", "10.5", "6.2'", "Arp 206 / Aiguille à tricoter", 10.87, 36.6],
    1046: [T["G"], "NGC 3675", "Grande Ourse", "10.1", "5.9'", "Galaxie spirale", 11.44, 43.5],
    1047: [T["G"], "NGC 3893", "Grande Ourse", "10.6", "4.4'", "Galaxie spirale", 11.81, 48.7],
    1048: [T["G"], "NGC 3953", "Grande Ourse", "10.3", "6.6'", "Galaxie spirale", 11.91, 52.3],
    1049: [T["G"], "NGC 4036", "Grande Ourse", "10.5", "4.5'", "Galaxie avec NGC 4041", 12.04, 61.9],
    1050: [T["G"], "NGC 4051", "Grande Ourse", "10.1", "5'", "Galaxie spirale", 12.05, 44.5],
    1051: [T["G"], "NGC 4111", "Chiens de Chasse", "10.7", "4.8'", "Galaxie spirale", 12.12, 43.0],
    1052: [T["GC"], "NGC 4147", "Chevelure de Bérénice", "10.3", "4'", "Amas Kick the Can", 12.17, 18.5],
    1053: [T["G"], "NGC 4293", "Chevelure de Bérénice", "10.1", "6'", "Galaxie de l'Oeil Noir", 12.36, 18.3],
    1054: [T["G"], "NGC 4414", "Chevelure de Bérénice", "10.3", "3.6'", "Galaxie en troupeau", 12.44, 31.2],
    1055: [T["G"], "NGC 4435", "Vierge", "11.0", "3'", "Arp 120 (les yeux avec NGC 4438)", 12.46, 13.0],
    1056: [T["G"], "NGC 4438", "Vierge", "10.1", "9.3'", "Les Yeux (Arp 120)", 12.46, 13.0],
    1057: [T["G"], "NGC 4450", "Chevelure de Bérénice", "10.1", "4.8'", "Galaxie spirale", 12.48, 17.0],
    1058: [T["G"], "NGC 4461", "Vierge", "10.3", "3.7'", "Galaxie proche des Yeux", 12.49, 13.1],
    1059: [T["QSR"], "3C 273", "Vierge", "11.7-13.2", "-", "Quasar", 12.49, 2.05],
    1060: [T["G"], "NGC 4473", "Chevelure de Bérénice", "10.2", "3.7' x 2.4'", "Galaxie elliptique / Part of Pair", 12.50, 13.4],
    1061: [T["G"], "NGC 4477", "Chevelure de Bérénice", "10.4", "3.9' x 3.6'", "Galaxie spirale / Part of Pair", 12.50, 13.6],
    1062: [T["G"], "NGC 4636", "Vierge", "9.5", "7.1' x 5.2'", "Galaxie elliptique", 12.71, 2.6],
    1063: [T["G"], "NGC 4665", "Vierge", "10.5", "4.1' x 4.1'", "Galaxie spirale", 12.75, 3.0],
    1064: [T["G"], "NGC 4753", "Vierge", "9.9", "4.1' x 2.3'", "Galaxie lenticulaire / Dust Devil", 12.87, -1.2],
    1065: [T["G"], "NGC 4762", "Vierge", "10.1", "9.1' x 2.2'", "Galaxie avec NGC 4754 / Paper-Kite", 12.88, 11.2],
    1066: [T["G"], "NGC 5033", "Chiens de Chasse", "10.2", "10.5' x 5.1'", "Galaxie spirale / Waterbug", 13.22, 36.5],
    1067: [T["G"], "NGC 5195", "Chiens de Chasse", "9.6", "6.4' x 4.6'", "Compagne de M51 (Arp 85)", 13.50, 47.25],
    1068: [T["GC"], "NGC 5466", "Bouvier", "9.0", "9'", "Amas Globulaire Fantôme / Snowglobe", 14.09, 28.5],
    1069: [T["G"], "NGC 5846", "Vierge", "10.0", "3.0' x 3.0'", "Galaxie spirale", 15.10, 1.6],
    1070: [T["G"], "NGC 5907", "Dragon", "10.3", "11.5' x 1.7'", "Galaxie de l'Éclat / Splinter", 15.27, 56.3],
    1071: [T["NP"], "IC 4593", "Hercule", "10.7", ">12\"", "Nébuleuse du Petit Pois / White-Eyed Pea", 16.20, 12.07],
    1072: [T["GC"], "NGC 6144", "Scorpion", "9.0", "9'", "Amas Globulaire", 16.45, -26.02],
    1073: [T["G"], "NGC 6207", "Hercule", "11.6", "3.0' x 1.1'", "Galaxie proche de M13", 16.72, 36.83],
    1074: [T["GC"], "NGC 6229", "Hercule", "9.4", "4.5'", "Amas Globulaire d'Hercule / \"Prize Comet\"", 16.78, 47.53],
    1075: [T["GC"], "NGC 6293", "Ophiuchus", "8.2", "7.9'", "Amas Globulaire", 17.17, -26.58],
    1076: [T["NP"], "NGC 6309", "Ophiuchus", "11.5", ">16\"", "Nébuleuse de la Boîte / Box", 17.24, -12.92],
    1077: [T["GC"], "NGC 6356", "Ophiuchus", "8.2", "10'", "Amas Globulaire", 17.39, -17.82],
    1078: [T["GC"], "NGC 6522", "Sagittaire", "8.3", "9.4'", "Fenêtre de Baade", 18.06, -30.03],
    1079: [T["GC"], "NGC 6528", "Sagittaire", "9.6", "3.7'", "Amas Globulaire", 18.08, -30.05],
    1080: [T["NP"], "NGC 6563", "Sagittaire", "11.0", "50\" x 38\"", "Anneau Austral / Southern Ring", 18.20, -33.87],
    1081: [T["RN"], "NGC 6589", "Sagittaire", "10.0", "5' x 3'", "Nébuleuse par réflexion", 18.28, -19.78],
    1082: [T["RN"], "NGC 6595", "Sagittaire", "10.0", "4' x 3'", "Nébuleuse par réflexion / = NGC 6590", 18.29, -19.87],
    1083: [T["GC"], "NGC 6638", "Sagittaire", "9.2", "7.3'", "Amas Globulaire", 18.52, -25.50],
    1084: [T["OC"], "NGC 6664", "Écu de Sobieski", "7.8", "12'", "Amas du Traîneau / Santa's Sleigh", 18.61, -8.18],
    1085: [T["GC"], "NGC 6717", "Sagittaire", "8.4", "5.4'", "Amas Globulaire (Palomar 9)", 18.92, -22.70],
    1086: [T["NP"], "NGC 6751", "Aigle", "11.9", "24\"", "Nébuleuse de la Fleur de Pissenlit / Glowing Eye", 19.10, -5.99],
    1087: [T["OC"], "NGC 6755", "Aigle", "7.5", "15'", "Amas avec NGC 6756 / Part of Binary Cluster?", 19.12, 4.27],
    1088: [T["OC"], "NGC 6756", "Aigle", "10.6", "4'", "Amas avec NGC 6755 / Part of Binary Cluster?", 19.15, 4.70],
    1089: [T["NP"], "NGC 6778", "Aigle", "11.9", "20\" x 40\"", "Mini Dumbbell / Son of M76", 19.31, -1.60],
    1090: [T["NP"], "NGC 6781", "Aigle", "11.4", "2'", "Nébuleuse de la Boule de Neige / Ghost of the Moon", 19.31, 6.53],
    1091: [T["NP"], "NGC 6804", "Aigle", "12.2", "~50\"", "Nébuleuse du Rétrécissement / Incredible Shrinking", 19.53, 9.22],
    1092: [T["OC"], "NGC 6811", "Cygne", "6.8", "15'", "Smoke Ring / Hole in a Cluster", 19.62, 46.38],
    1093: [T["A"], "Cygnus Kite Asterism", "Cygne", "8.8 (star)", "-", "Astérisme du Cerf-Volant / HDE 226868", 19.97, 35.20],
    1094: [T["A"], "OME 3", "Cygne", "-", "12'", "Alessi J20053+4732", 20.09, 47.53],
    1095: [T["NP"], "NGC 6891", "Dauphin", "10.5", ">18\"", "Nébuleuse planétaire", 20.25, 12.70],
    1096: [T["NP"], "NGC 6894", "Cygne", "12.3", ">42\"", "Petite Nébuleuse de l'Anneau / Diamond Ring", 20.27, 30.57],
    1097: [T["EN"], "IC 1318(a)", "Cygne", "-", "45' x 20'", "Nébuleuse Gamma Cygni / Near Gamma Cygni", 20.28, 41.82],
    1098: [T["NP"], "NGC 6905", "Dauphin", "11.1", "42\" x 35\"", "Nébuleuse de l'Éclair Bleu / Blue Flash", 20.37, 20.10],
    1099: [T["OC"], "NGC 6910", "Cygne", "6.6", "10'", "Amas de l'Arpenteur (Inchworm)", 20.39, 40.78],
    1100: [T["OC"], "NGC 6939", "Céphée", "7.8", "10'", "Astérisme de l'Oie en vol / Flying Geese", 20.53, 60.67],
    1101: [T["NP"], "NGC 7026", "Cygne", "10.9", "21\"", "Nébuleuse du Cheeseburger / Cheeseburger", 21.11, 47.85],
    1102: [T["NP"], "NGC 7048", "Cygne", "12.1", "61\"", "Nébuleuse du Disque Fantôme / Peek-a-Boo", 21.24, 46.28],
    1103: [T["RN"], "NGC 7129", "Céphée", "-", "7' x 7'", "Rose Cosmique / Cosmic Rosebud", 21.71, 66.10],
    1104: [T["OC"], "NGC 7160", "Céphée", "6.1", "5'", "Alligator Nageur / Bruce Lee", 21.90, 62.60],
    1105: [T["OC"], "NGC 7209", "Lézard", "7.7", "15'", "Amas ouvert / Star Lizard", 22.10, 46.48],
    1106: [T["NP"], "NGC 7354", "Céphée", "12.2", "22\" x 18\"", "Nébuleuse planétaire", 22.67, 61.28],
    1107: [T["OC"], "NGC 7510", "Céphée", "7.9", "7'", "Amas du Loir (Dormouse)", 23.19, 60.57],
    1108: [T["EN"], "NGC 7538", "Céphée", "-", "9' x 6'", "Nébuleuse de la Lagune Nord / Northern Lagoon", 23.23, 61.52],
    1109: [T["OC"], "NGC 7790", "Cassiopée", "8.5", "5'", "Widow's Web", 23.97, 61.21],
}



CATALOGS = {
    "Messier": {"prefix": "M", "data": MESSIER_DATA},          # the prefix is used in the HTML page
    "Caldwell": {"prefix": "C", "data": CALDWELL_DATA},
    "RASC": {"prefix": "R", "data": RASC_DATA},
    "O'Meara": {"prefix": "X", "data": O_MEARA_DATA}
}

TODO_FILE = "TODO.txt" # format is {"Catalog name": {"IdObjet": "free Comment"}}


# --- SCRIPT ---


def compute_best_season(ra):
    """Calculates the best observation season based on Right Ascension (RA)"""
    if 3 <= ra < 9:
        return LANG["SEASONS"]["H"] # Hiver
    elif 9 <= ra < 15:
        return LANG["SEASONS"]["P"] # Printemps
    elif 15 <= ra < 21:
        return LANG["SEASONS"]["E"] # Été
    else:
        return LANG["SEASONS"]["A"] # Automne
        

def find_image(prefix, obj_id, tech_ref):
    """Search for a matching image in the source directory based on technical references or IDs"""
    valid_exts = ('.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff', '.lnk')
    if not os.path.exists(CONFIG["SOURCE_DIR"]): return None
    
    # Pre-filter files with valid extensions and exclude thumbnails
    files = [f for f in os.listdir(CONFIG["SOURCE_DIR"]) 
             if f.lower().endswith(valid_exts) and "_thumb" not in f]

    if tech_ref:
        # Search by technical designation (e.g., NGC 7000, IC 434)
        match = re.search(r"(NGC|IC|SH2|Mel|WNC|M|Barnard|vdB)\s?(\d+)", tech_ref, re.IGNORECASE)
        if match:
            a_type, a_num = match.group(1), match.group(2)
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
            if exif and 306 in exif:
                return datetime.strptime(exif[306], "%Y:%m:%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
    except: pass
    return datetime.fromtimestamp(os.path.getmtime(path)).strftime("%d/%m/%Y %H:%M")

def make_thumbnail(src):
    """Generate a square thumbnail and convert TIF files for web display"""
    if not os.path.exists(CONFIG["THUMB_DIR"]): os.makedirs(CONFIG["THUMB_DIR"])
    dest = os.path.join(CONFIG["THUMB_DIR"], f"thumb_{src}")
    
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
    
def load_todo_list():
    """Load the list of marked objects from TODO.txt (JSON format)"""
    if not os.path.exists(TODO_FILE): return {}
    try:
        with open(TODO_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content: return {}
            return json.loads(content)
    except Exception as e:
        print(f"Error reading TODO.txt : {e}")
        return {}
        
def generate():
    """Main function: processes data and generates the HTML gallery"""
    final_json = {}
    stats = {}
    todo_list = load_todo_list() 
    prefixes_js = {k: v["prefix"] for k, v in CATALOGS.items()}
    
    for name, data_dict in CATALOGS.items():
        marked_dict = todo_list.get(name, {})
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
            tech_ref = info[1]
            img_file = find_image(prefix, k, tech_ref)
            thumb, date = "", ""
            if img_file:
                found_count += 1
                thumb, date = make_thumbnail(img_file), get_exif_date(img_file)
            
            ra, dec = info[6], info[7]
            h_max = 90 - abs(CONFIG["LATITUDE"] - dec)
            season_computed = compute_best_season(ra)

            color = "#c9d1d9" 
            if h_max <= CONFIG["LIMIT_IMPOSSIBLE"]: color = "#da3633" 
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
                "season_computed": season_computed,
                "label_color": color,
                "todo": str(k) in marked_dict,
                "todo_comment": marked_dict.get(str(k), "")
            })
            
        final_json[name] = objs
        stats[name] = f"{found_count}/{len(data_dict['data'])}"

    select_options = "".join([f'<option value="{c}" {"selected" if c == CONFIG["SELECTED_CATALOG"] else ""}>{c}</option>' for c in CATALOGS.keys()])
    season_options = "".join([f'<option value="{val}">{val}</option>' for val in LANG["SEASONS"].values()])
    dir_options = f'<option value="Tous">{LANG["ALL_DIR"]}</option><option value="{LANG["NORTH"]}">{LANG["NORTH"]}</option><option value="{LANG["SOUTH"]}">{LANG["SOUTH"]}</option>'
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
            .filter-bar {{ margin-bottom: 30px; display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; }}
            .filter-select {{ 
                background: #21262d; color: #fff; border: 1px solid #388bfd; 
                padding: 8px 35px 8px 15px; border-radius: 20px; cursor: pointer; 
                font-family: inherit; font-size: 14px; outline: none; transition: 0.2s;
                appearance: none; -webkit-appearance: none; -moz-appearance: none;
                background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23ffffff%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E');
                background-repeat: no-repeat; background-position: right 12px top 50%; background-size: 10px auto;
            }}
            .btn-export {{ 
                position: fixed; top: 10px; right: 10px; z-index: 1000;
                background: #161b22; border: 1px solid #30363d; color: #8b949e;
                padding: 6px 12px; border-radius: 6px; font-size: 11px;
                cursor: pointer; transition: 0.2s;
            }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(var(--case-size), 1fr)); gap: 15px; width: 100%; margin: 0 auto; }}
            .case {{ background: #161b22; border-radius: 8px; border: 1px solid #30363d; overflow: hidden; position: relative; display: flex; flex-direction: column; }}
            
            /* Gestion des coeurs - Taille identique */
            .todo-heart {{ 
                position: absolute; top: 5px; right: 8px; 
                font-size: 20px; z-index: 10; 
                user-select: none; pointer-events: none;
                color: #ff4d4d;
                line-height: 1;
            }}
            .todo-heart.no-comment {{ 
                color: transparent;
                -webkit-text-stroke: 1.5px #ff4d4d;
            }}

            .img-box {{ width: 100%; aspect-ratio: 1 / 1; display: flex; align-items: center; justify-content: center; background: #000; cursor: pointer; overflow: hidden; }}
            .img-box img {{ width: 100%; height: 100%; object-fit: cover; }}
            .empty-info {{ color: #484f58; font-size: 11px; font-weight: bold; text-align: center; padding: 5px; line-height: 1.2; }}
            .label {{ background: #21262d; padding: 8px 5px; font-weight: bold; font-size: 12px; border-top: 1px solid #30363d; cursor: pointer; transition: 0.2s; }}
            #tooltip {{ position: fixed; display: none; background: #0d1117; border: 1px solid #3498db; border-radius: 8px; padding: 12px; z-index: 2000; text-align: left; min-width: 220px; box-shadow: 0 8px 24px #000; pointer-events: none; }}
            #overlay {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 9999; justify-content: center; align-items: center; overflow: hidden; }}
            #fullImg {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); cursor: grab; user-select: none; max-width: 95%; max-height: 95%; transition: transform 0.05s linear; }}
            
            #customPrompt {{ background: #161b22; color: #fff; border: 1px solid #388bfd; border-radius: 8px; padding: 15px; box-shadow: 0 8px 24px #000; max-width: 300px; text-align: center; }}
            #customPrompt::backdrop {{ background: rgba(0,0,0,0.6); }}
            #customPrompt label {{ display: block; font-size: 13px; margin-bottom: 10px; color: #c9d1d9; }}
            #customPrompt input {{ background: #0d1117; color: #fff; border: 1px solid #30363d; border-radius: 4px; padding: 6px; width: 90%; margin-bottom: 12px; outline: none; }}
            #customPrompt button {{ background: #21262d; border: 1px solid #388bfd; color: #fff; padding: 6px 15px; border-radius: 4px; cursor: pointer; font-size: 13px; }}
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
            <button onclick="exportTodo()" class="filter-select btn-export">💾 TODO.txt ❤</button>
        </div>
        <div class="grid" id="grid"></div>
        <div id="tooltip"></div>
        <div id="overlay" onclick="if(event.target===this) closeM()"><img id="fullImg"></div>

        <dialog id="customPrompt">
            <form method="dialog" id="promptForm">
                <label>Entrez une description optionnelle :</label>
                <input type="text" id="promptInput" autocomplete="off">
                <br>
                <button type="submit">Valider</button>
            </form>
        </dialog>

        <script>
            const data = {json.dumps(final_json)};
            const stats = {json.dumps(stats)};
            const prefixes = {json.dumps(prefixes_js)};
            const thumbDir = "{CONFIG['THUMB_DIR']}";
            const userLat = {CONFIG['LATITUDE']}; 
            
            // Sync local storage with JSON data on load
            let localTodo = JSON.parse(localStorage.getItem('astro_todo')) || {{}};
            for (let cat in data) {{
                if (!localTodo[cat]) localTodo[cat] = {{}};
                data[cat].forEach(obj => {{
                    if (obj.todo) {{ localTodo[cat][obj.id] = obj.todo_comment || ""; }}
                }});
            }}
            localStorage.setItem('astro_todo', JSON.stringify(localTodo));

            const FAMILIES = {{
                "Nébuleuse": ["{LANG['TYPES']['N']}", "{LANG['TYPES']['NP']}", "{LANG['TYPES']['SC']}", "{LANG['TYPES']['SNR']}", "{LANG['TYPES']['EN']}", "{LANG['TYPES']['RN']}", "{LANG['TYPES']['E/RN']}", "{LANG['TYPES']['N+C']}"],
                "Galaxie": ["{LANG['TYPES']['G']}"],
                "Amas": ["{LANG['TYPES']['GC']}", "{LANG['TYPES']['OC']}", "{LANG['TYPES']['D']}", "{LANG['TYPES']['A']}", "{LANG['TYPES']['N+C']}", "{LANG['TYPES']['QSR']}"]
            }};
            
            let currentSeason = 'Tous', currentDir = 'Tous', currentFamily = 'Tous';
            let scale = 1, posX = 0, posY = 0, isDragging = false, startX, startY;
            const m = document.getElementById("overlay"), mi = document.getElementById("fullImg"), t = document.getElementById('tooltip');

            function filterS(s) {{ currentSeason = s; update(); }}
            function filterD(d) {{ currentDir = d; update(); }}
            function filterF(f) {{ currentFamily = f; update(); }}

            function exportTodo() {{
                const blob = new Blob([JSON.stringify(localTodo, null, 4)], {{type: 'text/plain'}});
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url; a.download = 'TODO.txt'; a.click();
                window.URL.revokeObjectURL(url);
            }}

            function toggleHeart(e, catName, objId) {{
                e.preventDefault(); 
                if (!localTodo[catName]) localTodo[catName] = {{}};
                
                if (localTodo[catName][objId] !== undefined) {{
                    delete localTodo[catName][objId];
                    localStorage.setItem('astro_todo', JSON.stringify(localTodo));
                    update();
                }} else {{
                    const dialog = document.getElementById('customPrompt');
                    const form = document.getElementById('promptForm');
                    const input = document.getElementById('promptInput');
                    input.value = ""; 
                    dialog.showModal();
                    form.onsubmit = () => {{
                        localTodo[catName][objId] = input.value.trim();
                        localStorage.setItem('astro_todo', JSON.stringify(localTodo));
                        update();
                    }};
                }}
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
                    const objSeason = obj.season_computed; 
                    const declin = parseFloat(obj.info[7]);
                    const objDir = declin > userLat ? "{LANG['NORTH']}" : "{LANG['SOUTH']}";
                    
                    if (currentFamily !== 'Tous' && !(FAMILIES[currentFamily] && FAMILIES[currentFamily].includes(objType))) return;
                    if (currentSeason !== 'Tous' && objSeason !== currentSeason) return;
                    if (currentDir !== 'Tous' && objDir !== currentDir) return;
                    
                    const d = document.createElement('div'); d.className = 'case';
                    const isTodo = localTodo[cat] && localTodo[cat][obj.id] !== undefined;
                    const currentComment = isTodo ? localTodo[cat][obj.id] : "";
                    
                    d.onmousemove = (e) => showT(e, obj, currentComment);
                    d.onmouseleave = () => t.style.display='none';
                    d.oncontextmenu = (e) => toggleHeart(e, cat, obj.id);
                    
                    const heartClass = currentComment ? 'has-comment' : 'no-comment';
                    const heart = isTodo ? `<div class="todo-heart ${{heartClass}}">❤</div>` : '';

                    let displaySeason = currentSeason === 'Tous' ? `<br>(${{objSeason}})` : '';
                    let content = obj.thumb ? `<img src="${{obj.thumb}}">` : `<div class="empty-info">${{objType}}${{displaySeason}}</div>`;
                    
                    let clickImg = obj.img;
                    if (obj.img && (obj.img.toLowerCase().endsWith('.tif') || obj.img.toLowerCase().endsWith('.tiff'))) {{
                        let baseName = obj.img.substring(0, obj.img.lastIndexOf('.'));
                        if (baseName.startsWith('thumb_')) baseName = baseName.substring(6);
                        clickImg = thumbDir + "/view_" + baseName + ".jpg";
                    }}
                    
                    // Telescopius Link Generation
                    let tUrl = "https://telescopius.com/deep-sky-objects/";
                    if (obj.prefix === prefixes.Messier) tUrl += "m-" + obj.id;
                    else if (obj.prefix === prefixes.Caldwell) tUrl += "c-" + obj.id;
                    else if (obj.prefix === prefixes.RASC || obj.prefix === prefixes["O'Meara"]) {{
                        const match = obj.tech_ref.match(/(?:NGC|IC|SH2|BARNARD|VDB)[_ \-]?(\d+)/i);
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

            function openM(s) {{ if(!s) return; scale = 1; posX = 0; posY = 0; mi.src = s; m.style.display = "flex"; updateTransform(); }}
            function closeM() {{ m.style.display = "none"; }}
            function updateTransform() {{ mi.style.transform = `translate(calc(-50% + ${{posX}}px), calc(-50% + ${{posY}}px)) scale(${{scale}})`; }}
            
            // Image viewer pan & zoom
            m.addEventListener('wheel', e => {{ e.preventDefault(); scale = Math.min(Math.max(0.5, scale * (e.deltaY > 0 ? 0.9 : 1.1)), 10); updateTransform(); }}, {{passive: false}});
            mi.addEventListener('mousedown', e => {{ isDragging = true; startX = e.clientX - posX; startY = e.clientY - posY; e.preventDefault(); }});
            window.addEventListener('mousemove', e => {{ if (isDragging) {{ posX = e.clientX - startX; posY = e.clientY - startY; updateTransform(); }} }});
            window.addEventListener('mouseup', () => isDragging = false);

            function showT(e, obj, comment) {{
                let html = "";
                if (obj.img) {{
                    html += `<div style="color:#4a9eff; font-weight:bold; font-size:12px; margin-bottom:2px;">${{obj.img}}</div>`;
                    html += `<div style="color:#888; font-size:11px; margin-bottom:8px;">Date: ${{obj.date}}</div>`;
                    html += `<hr style="border:0; border-top:1px solid #444; margin:8px 0;">`;
                }}
                
                // Small object detection logic
                let s = obj.info[4] || "", c = "", threshold = {limit_small}; 
                let dims = s.split(/[x×]/), isSmall = dims.length > 0;
                for (let i = 0; i < dims.length; i++) {{
                    let d = dims[i].trim(), tm = 0, ts = 0;
                    let mMatch = d.match(/([0-9.]+)'($|[^'])/), sMatch = d.match(/([0-9.]+)(?:''|["])/);
                    if (mMatch) tm = parseFloat(mMatch[1]);
                    if (sMatch) ts = parseFloat(sMatch[1]);
                    if (!mMatch && !sMatch) {{ let v = parseFloat(d); if (!isNaN(v)) tm = v; }}
                    if ((tm * 60) + ts >= threshold || (tm * 60) + ts === 0) {{ isSmall = false; break; }}
                }}
                if (isSmall) c = ' style="color:orange;"';

                // Direction and badge calculation
                const declin = parseFloat(obj.info[7]), isNorth = declin > userLat;
                const direction = isNorth ? "{LANG['NORTH']}" : "{LANG['SOUTH']}";
                const badgeColor = isNorth ? "#3498db" : "#f1c40f";

                html += `<div><strong>{LANG["TOOLTIP_LABELS"]["TYPE"]}:</strong> ${{obj.info[0]}}</div>`;
                html += `<div><strong>{LANG["TOOLTIP_LABELS"]["SEASON"]}:</strong> ${{obj.season_computed}}</div>`;
                html += `<div><strong>{LANG["TOOLTIP_LABELS"]["CONSTELLATION"]}:</strong> ${{obj.info[2]}}</div>`;
                html += `<div><strong>{LANG["TOOLTIP_LABELS"]["MAGNITUDE"]}:</strong> ${{obj.info[3]}}</div>`;
                html += `<div ${{c}}><strong>{LANG["TOOLTIP_LABELS"]["SIZE"]}:</strong> ${{s}}</div>`;
                
                // RA conversion to HMS
                let raDecimal = parseFloat(obj.info[6]);
                let hours = Math.floor(raDecimal), minDec = (raDecimal - hours) * 60, minutes = Math.floor(minDec), seconds = Math.round((minDec - minutes) * 60);
                if (seconds === 60) {{ seconds = 0; minutes += 1; }}
                if (minutes === 60) {{ minutes = 0; hours += 1; }}

                html += `<div><strong>RA :</strong> ${{hours}}h ${{String(minutes).padStart(2, '0')}}m ${{String(seconds).padStart(2, '0')}}s</div>`;
                html += `<div><strong>Dec :</strong> ${{obj.info[7]}}° <span style="font-size:9px; background:#21262d; color:${{badgeColor}}; padding:1px 4px; border-radius:3px; border:1px solid ${{badgeColor}}; margin-left:5px; vertical-align:middle; font-weight:bold;">${{direction}}</span></div>`;
                html += `<div><strong>{LANG["TOOLTIP_LABELS"]["ELEVATION"]}:</strong> ${{obj.h_max}}</div>`;
                
                if (comment) {{
                    html += `<hr style="border:0; border-top:1px solid #ff4d4d; margin:8px 0;">`;
                    html += `<div style="color:#ff6b6b; font-size:12px;"><strong>Note :</strong> ${{comment}}</div>`;
                }}

                html += `<hr style="border:0; border-top:1px solid #444; margin:8px 0;">`;
                html += `<div style="font-style:italic; color:#3498db; margin-top:5px;"><strong>${{obj.info[5]}}</strong></div>`;
                
                t.innerHTML = html; t.style.display = 'block';
                let x = e.clientX + 15, y = e.clientY + 15;
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
