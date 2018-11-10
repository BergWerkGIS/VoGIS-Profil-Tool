# VoGIS-Profil-Tool

PlugIn for creating profile lines with QGIS >=3.4.

## Development funded by

Amt der Vorarlberger Landesregierung - Landesamt für Vermessung und Geoinformation

http://vorarlberg.at/vorarlberg/bauen_wohnen/bauen/vermessung_geoinformation/start.htm

# Known issues

If you get an error message about shapely missing get it via

```bash
sudo apt-get install python3-shapely
```


# Download the ready-to-deploy PlugIn

Download via 
* QGIS Plugin Manager 
* or GitHub https://github.com/BergWerkGIS/VoGIS-Profil-Tool/releases


# Build from source

```bash
* git clone git@github.com:BergWerkGIS/VoGIS-Profil-Tool.git
* cd VoGIS-Profil-Tool/VoGisProfilTool
* make clean #(clean temporary files)
* make derase #(delete folder ~/.qgis/pyhton/plugins/VoGISProfilTool)
* make deploy #(compile and deploy to ~/.qgis/pyhton/plugins/VoGISProfilTool)
* make zip #(create plugin zip-file for deployment in local folder)
```

# Description

Create profiles from DEMs using vector geometries or a digitized line.

Interpolate vertices (equidistant or constant number of vertices per input geometry).

Display profile plots.

Export to:
* 2.5D point or 2.5D line Shapefile
* point or line DXF
* Autocad text
* text
* csv (optimized for MS Exel)
* graphic (png, jpg, pdf)
* graphic with defined scale and DPI
* add profile line to layout

## Main Dialog
![main dialog](/screenshots/maindialog.png)

## Plot Dialog
![plot dialog](/screenshots/plotdialog.png)

If you get an error message about missing shapely, just do
`sudo apt-get install python3-shapely`.
