#/***************************************************************************
# VoGISProfilToolMain
# 
# VoGIS ProfilTool
#                             -------------------
#        begin                : 2013-05-28
#        copyright            : (C) 2013 by BergWerk GIS
#        email                : wb@BergWerk-GIS.at
# ***************************************************************************/
# 
#/***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# ***************************************************************************/

# CONFIGURATION
PLUGIN_UPLOAD = $(CURDIR)/plugin_upload.py

# Makefile for a PyQGIS plugin 

# translation
SOURCES = vogisprofiltoolmain.py ui/ui_vogisprofiltoolmain.py __init__.py vogisprofiltoolmaindialog.py
TRANSLATIONS = i18n/vogisprofiltoolmain_en.ts
#TRANSLATIONS = 

# global

PLUGINNAME = vogisprofiltoolmain

PY_FILES = vogisprofiltoolmain.py vogisprofiltoolmaindialog.py vogisprofiltoolplot.py __init__.py
EXTRAS = icons/icon.png icons/home.png icons/pan.png icons/save.png icons/zoomlast.png icons/zoomnext.png icons/zoomrectangle.png icons/zoomselect.png icons/identify.png
BO_FILES = bo/__init__.py bo/line.py bo/lineCollection.py bo/mapdata.py bo/raster.py bo/rasterCollection.py bo/settings.py bo/profile.py bo/segment.py bo/vertex.py bo/zVal.py bo/node.py bo/linkedList.py bo/plotExtent.py
UTIL_FILES = util/__init__.py util/u.py util/createProfile.py util/exportShape.py util/ptmaptool.py util/exportDxf.py
UI_FILES = ui/ui_vogisprofiltoolmain.py ui/ui_vogisprofiltoolplot.py
RESOURCE_FILES = resources_rc.py

HELP = help/build/html

default: compile

compile: $(UI_FILES) $(RESOURCE_FILES)

%_rc.py : %.qrc
	pyrcc4 -o $*_rc.py  $<

%.py : %.ui
	pyuic4 -o $@ $<

%.qm : %.ts
	lrelease $<

# The deploy  target only works on unix like operating system where
# the Python plugin directory is located at:
# $HOME/.qgis/python/plugins
deploy: compile doc transcompile
	mkdir -p $(HOME)/.qgis/python/plugins/$(PLUGINNAME)
	mkdir -p $(HOME)/.qgis/python/plugins/$(PLUGINNAME)/bo
	mkdir -p $(HOME)/.qgis/python/plugins/$(PLUGINNAME)/util
	mkdir -p $(HOME)/.qgis/python/plugins/$(PLUGINNAME)/ui
	mkdir -p $(HOME)/.qgis/python/plugins/$(PLUGINNAME)/icons

	cp -vf $(PY_FILES) $(HOME)/.qgis/python/plugins/$(PLUGINNAME)
	cp -vf $(BO_FILES) $(HOME)/.qgis/python/plugins/$(PLUGINNAME)/bo
	cp -vf $(UTIL_FILES) $(HOME)/.qgis/python/plugins/$(PLUGINNAME)/util
	cp -vf $(UI_FILES) $(HOME)/.qgis/python/plugins/$(PLUGINNAME)/ui
	cp -vf __init__.py $(HOME)/.qgis/python/plugins/$(PLUGINNAME)/ui
	cp -vf $(RESOURCE_FILES) $(HOME)/.qgis/python/plugins/$(PLUGINNAME)
	cp -vf $(EXTRAS) $(HOME)/.qgis/python/plugins/$(PLUGINNAME)/icons
	cp -vfr i18n $(HOME)/.qgis/python/plugins/$(PLUGINNAME)
	cp -vfr $(HELP) $(HOME)/.qgis/python/plugins/$(PLUGINNAME)/help

# The dclean target removes compiled python files from plugin directory
# also delets any .svn entry
dclean:
	find $(HOME)/.qgis/python/plugins/$(PLUGINNAME) -iname "*.pyc" -delete
	find $(HOME)/.qgis/python/plugins/$(PLUGINNAME) -iname ".svn" -prune -exec rm -Rf {} \;

# The derase deletes deployed plugin
derase:
	rm -Rf $(HOME)/.qgis/python/plugins/$(PLUGINNAME)

# The zip target deploys the plugin and creates a zip file with the deployed
# content. You can then upload the zip file on http://plugins.qgis.org
zip: deploy dclean 
	rm -f $(PLUGINNAME).zip
	cd $(HOME)/.qgis/python/plugins; zip -9r $(CURDIR)/$(PLUGINNAME).zip $(PLUGINNAME)

# Create a zip package of the plugin named $(PLUGINNAME).zip. 
# This requires use of git (your plugin development directory must be a 
# git repository).
# To use, pass a valid commit or tag as follows:
#   make package VERSION=Version_0.3.2
package: compile
		rm -f $(PLUGINNAME).zip
		git archive --prefix=$(PLUGINNAME)/ -o $(PLUGINNAME).zip $(VERSION)
		echo "Created package: $(PLUGINNAME).zip"

upload: zip
	$(PLUGIN_UPLOAD) $(PLUGINNAME).zip

# transup
# update .ts translation files
transup:
	pylupdate4 Makefile

# transcompile
# compile translation files into .qm binary format
transcompile: $(TRANSLATIONS:.ts=.qm)

# transclean
# deletes all .qm files
transclean:
	rm -f i18n/*.qm

clean:
	rm $(UI_FILES) $(RESOURCE_FILES)

# build documentation with sphinx
doc: 
	cd help; make html
