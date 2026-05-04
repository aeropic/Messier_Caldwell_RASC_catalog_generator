# AllinOne_Messier_Caldwell_RASC_catalog_generator
This is a python script to build a catalog of your Messier/Caldwell/RASC  objects astrophotographies

After the Messier, the Calwel, the RASC catalogs, I needed to simplify all this and make a commun generic one : here it is.

Simply organize your image files in a folder and add the string "M1, Mxx, C1, Cx or NGCxyz or ICabc" to the image names.

Place the "Allinone_catalog_generator.py" script and the "Allinone.bat" file in the same folder. Double-click on Allinone.bat, accept the Windows prompts, and it generates an interactive HTML contact sheet.

thumbnails are created and stored into a "thumbnails" folder
The thumbnails are clickable to access the zoomable image.
reference of each object (eg C42) is clickable and points to telescopius
The marathon score is displayed at the top .

If there are multiple objects in the same image, name the file with both objects (e.g.,NGC4038_NGC4039_antenna.jpg). The script includes a mini-catalog, and the object type is indicated below the object number. <img width="1563" height="917" alt="cata" src="https://github.com/user-attachments/assets/d256ccf6-7ded-4834-9531-dd30f97555f1" />

The .bat file, of course, only runs on PC...

Let me know if it works for you too and if you see any improvements we could make!

Note: Open and edit the .bat file to specify the path to your Python installation. I pointed to SIRIL's path: :: Launch Python on the script located in the same folder: "C:\Program Files\Siril\python\python.exe" "Caldwell_generator.py"

You can easily translate the script in any langage as all strings are gathered at the top of the script... Meanwhile in french !
You may as well modify thise lines in order to reflect your latitude of observation:
- "LATITUDE": 43.6,           # Votre latitude
- "LIMIT_IMPOSSIBLE": 0,      # Hauteur max <= 0°
- "LIMIT_DIFFICILE": 10       # Hauteur max <= 10° 
as the script paints in orange/red low/impossibile objects
    
<img width="1335" height="500" alt="cata_impos" src="https://github.com/user-attachments/assets/774e3c35-e7a9-447d-9d1b-e3febc2cd131" />


