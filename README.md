#VoGIS-Profil-Tool
 
##Developed for
 
Amt der Vorarlberger Landesregierung 

Landesamt für Vermessung und Geoinformation 

http://vorarlberg.at/vorarlberg/bauen_wohnen/bauen/vermessung_geoinformation/start.htm 
 
##Developed on
 
OSGeo-Live 6.0, QGIS 1.8 (not yet working with 2.0): 

http://live.osgeo.org/en/index.html 
 
#Check out code and create plugin
 
Directory **VoGISProfilTool** contains new enhanced version. 

Directory **Z_VoGISProfilTool** contains old version. 
 
```
* git clone https://github.com/BergWerkGIS/VoGIS-Profil-Tool.git
* cd ./VoGISProfilTool
* make clean #(clean temporary files)
* make derase #(delete folder ~/.qgis/pyhton/plugins/VoGISProfilTool)
* make deploy #(compile and deploy to ~/.qgis/pyhton/plugins/VoGISProfilTool)
* make zip #(create plugin zip-file for deployment in local folder)
```
 
#Download the ready-to-deploy PlugIn
 
https://github.com/BergWerkGIS/VoGIS-Profil-Tool/raw/master/VoGisProfilTool/VoGisProfilTool.zip
 
#Description
 
Create profiles from DHMs using vector geometries or a digitized line. 
 
Interpolate vertices (equidistant or constant number of vertices per input geometry). 
 
Display profile plots. 

Export to:
* 2.5D point or 2.5D line Shapefile
* point or line DXF
* Autocad text
* text
* csv (optimized for MS Exel)
* graphic (png, jpg, pdf)

![Alt text](/screenshots/maindialog.png)
![Alt text](/screenshots/plotdialog.png)