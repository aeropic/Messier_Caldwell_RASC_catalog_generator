# Messier_Caldwell_RASC_catalog_generator
This is a python script to build a catalog of your Messier/Caldwell/RASC  objects astrophotographies

After the Messier, the Caldwell, the RASC catalogs, I needed to simplify all this and make a commun generic one : here it is.

Simply organize your image files in a folder and add the string "M1, Mxx, C1, Cx or NGCxyz or ICabc" to the image names.

Place the "astro_catalog_generator.py" script and the "astro_catalog_launcher.bat" file in the same folder where the images are located. Double-click on "astro_catalog_launcher.bat", accept the Windows prompts, and it will automatically collect missing python libraries and it generates an interactive HTML contact sheet. The .bat file, of course, only runs on PC...
If there are multiple objects in the same image, name the file with both objects (e.g.,NGC4038_NGC4039_antenna.jpg). 

<img width="1478" height="662" alt="cata" src="https://github.com/user-attachments/assets/d9e50693-855b-4af2-8fbc-51fb83841687" />

thumbnails are created and stored into a "thumbnails" folder
The script includes a mini-catalog, and the object type is indicated below the object number. 
The thumbnails on the HTML page are clickable to access the zoomable image.
The marathon score is displayed at the top .
Placing the mouse over one object will display inside a popup window usefull data to prepare your imaging session.
If you want to get more details, reference of each object (eg C42) is clickable and points to the corresponding telescopius page

To switch between Messier/Caldwell/RASC catalog just select the required catalog from the menu bar.
<img width="609" height="233" alt="cata_switch" src="https://github.com/user-attachments/assets/bfe374e2-4118-4782-acad-c7d36484b4f2" />

In each catalog and especially in the Caldwell one the name of some objects are painted in orange or red.
- orange means the object is always low on horizon (by default < 20°)
- red means, it will never be above your horizon
<img width="1167" height="741" alt="cata_caldwell" src="https://github.com/user-attachments/assets/835fef8c-2600-49b6-8a4c-f3ad95d90d1d" />

you can edit the python file and change those lines according to your location :
- "LATITUDE": 43.6,           # Votre latitude
- "LIMIT_IMPOSSIBLE": 0,      # Hauteur max <= 0°
- "LIMIT_DIFFICILE": 10       # Hauteur max <= 10° 

You can easily translate the script in any langage as all strings are gathered at the top of the script... Meanwhile in french ! For the catalogs of objects, an english version is already available and placed indide a python bloc of comment 
(between 
"""
""")


Let me know if it works for you too and if you see any improvements we could make!

Note: Open and edit the .bat file to specify the path to your Python installation. I pointed to SIRIL's path: :: Launch Python on the script located in the same folder: "C:\Program Files\Siril\python\python.exe" "Caldwell_generator.py"



