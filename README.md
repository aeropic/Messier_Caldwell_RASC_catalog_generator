# Messier_Caldwell_RASC_O'Meara_catalog_generator
This is a python script to build a catalog of your Messier/Caldwell/RASC  objects astrophotographies

After the Messier, the Caldwell, the RASC catalogs, I needed to simplify all this and make a commun generic one : here it is.

Simply organize your image files in a folder and add the string "M1, Mxx, C1, Cx or NGCxyz or ICabc" to the image names.
The script is able to manage files in .jpg, .jpeg, .png, .webp, .tif, .tiff and .lnk (window shortcut to image).

Place the "astro_catalog_generator.py" script and the "astro_catalog_launcher.bat" file in the same folder where the images are located. Double-click on "astro_catalog_launcher.bat", accept the Windows prompts, and it will automatically collect missing python libraries and it generates an interactive HTML contact sheet. The .bat file, of course, only runs on PC...
If there are multiple objects in the same image, name the file with both objects (e.g.,NGC4038_NGC4039_antenna.jpg). 

<img width="1317" height="846" alt="cata" src="https://github.com/user-attachments/assets/b41ce7cf-49e7-4031-b952-cd606bdb0e34" />



thumbnails are created and stored into a "thumbnails" folder
The script includes a mini-catalog, and the object type is indicated below the object number. 
The thumbnails on the HTML page are clickable to access the zoomable image.
The marathon score is displayed at the top .
Placing the mouse over one object will display inside a popup window usefull data to prepare your imaging session.
If you want to get more details, reference of each object (eg C42) is clickable and points to the corresponding telescopius page

To switch between Messier/Caldwell/RASC/OMEARA catalogs just select the required catalog from the menu bar.
you can also filter by type of objects (Nebula, galaxies, clusters and others)
<img width="1307" height="690" alt="nebu" src="https://github.com/user-attachments/assets/4151d09a-49de-4be1-97fe-0f72126a35ec" />


In each catalog and especially in the Caldwell and O'Meara the name of some objects are painted in orange or red.
- orange means the object is always low on horizon (by default < 20°)
- red means, it will never be above your horizon

The best season to observe each object is written in the thumbnail area. You may also want to filter each catalog by season just clicking of the season menu. (here summer-été is selected).
<img width="1210" height="659" alt="cata_summer" src="https://github.com/user-attachments/assets/a7deded7-636b-47e4-b196-d956e28ccd0c" />

There is also one menu to sort the objects by direction of the telescope according to your latitude. (My house is North/South with two terrasses one North one South !)
And the direction of observation is also displayed in the tooltip.
<img width="841" height="529" alt="cata_north" src="https://github.com/user-attachments/assets/88f843cc-cd34-45a6-be23-8399374cfd7a" />



To avoid being too disapointed when imaging a too small object, the tooltip displays the size of the object in orange when both dimensions are lower than than 2'

<img width="375" height="329" alt="smallsize" src="https://github.com/user-attachments/assets/faad9cbd-bcab-4bb8-8c8b-59e4eecda315" />

you can edit the python file and change this value
-    "LIMIT_SMALL_OBJECT": 120                     # arcseconds ; paint small objects size in orange

you can edit the python file and change those lines according to your location :
-   "LATITUDE": 43.6,                             # your latitude
-   "LIMIT_IMPOSSIBLE": 0,                          # degrees : change here if your horizon is masked
-   "LIMIT_DIFFICILE": 20

You can easily translate the script in any langage as all strings are gathered at the top of the script... Meanwhile in french ! For the catalogs of objects, an english version is already available and placed inside a python bloc of comment 
(between 
"""
""")


Let me know if it works for you too and if you see any improvements we could make!

Note: Open and edit the .bat file to specify the path to your Python installation. I pointed to SIRIL's path: :: Launch Python on the script located in the same folder: "C:\Program Files\Siril\python\python.exe" "Caldwell_generator.py"



