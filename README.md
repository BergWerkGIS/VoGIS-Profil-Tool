#VoGIS-Profil-Tool
 
##Developed for
 
Amt der Vorarlberger Landesregierung 

Landesamt für Vermessung und Geoinformation 

http://vorarlberg.at/vorarlberg/bauen_wohnen/bauen/vermessung_geoinformation/start.htm 
 
##Developed on
 
OSGeo-Live: 
http://live.osgeo.org/en/index.html
 
#Check out code and create plugin
 
Directory VoGISProfilTool contains current version 
Directory Z_VoGISProfilTool contains old version 
 
```
* git clone https://github.com/BergWerkGIS/VoGIS-Profil-Tool.git
* cd VoGISProfilTool
* make clean
* make derase
* make deploy
* make zip (to create plugin zip-file for deployment)
```
 
Git Reference: http://gitref.org/
 
#Download the ready-to-deploy PlugIn
 
https://github.com/BergWerkGIS/VoGIS-Profil-Tool/raw/master/VoGisProfilTool/VoGisProfilTool.zip

#Description

Create profiles from DHMs using vector geometries or a digitized line.
Interpolate vertices (equidistant or constant number of vertices per input geometry).
Display profile plots.
Export to
* point or line Shapefile
* point or line DXF
* text
* csv (optimized for MS Exel)
* graphic (png, jpg, pdf)

![Alt text](/screenshots/maindialog.png)
![Alt text](/screenshots/plotdialog.png)