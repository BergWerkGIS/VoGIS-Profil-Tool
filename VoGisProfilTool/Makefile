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
SOURCES = vogisprofiltoolmain.py\
          ui/ui_vogisprofiltoolmain.py\
          ui/ui_vogisprofiltoolplot.py\
          ui/ui_vogisprofiltoollayouts.py\
          ui/ui_vogisprofiltoolscale.py\
          __init__.py\
          vogisprofiltoolmaindialog.py\
          vogisprofiltoolplot.py\
          vogisprofiltoollayouts.py\
          vogisprofiltoolscale.py\
          util/u.py\
          util/createProfile.py\
          bo/profile.py
TRANSLATIONS = i18n/vogisprofiltoolmain_en.ts
#TRANSLATIONS =

# global

PLUGINNAME = VoGisProfilTool
QGISPIDIR = .local/share/QGIS/QGIS3/profiles/default

PY_FILES = vogisprofiltoolmain.py vogisprofiltoolmaindialog.py vogisprofiltoolplot.py vogisprofiltoollayouts.py vogisprofiltoolscale.py __init__.py
EXTRAS = icons/home.png \
         icons/icon.png \
         icons/identify.png \
         icons/measure.png \
         icons/pan.png \
         icons/save.png \
         icons/zoomlast.png \
         icons/zoomnext.png \
         icons/zoomrectangle.png \
         icons/zoomselect.png
BO_FILES = bo/__init__.py \
           bo/chartpoint.py \
           bo/intersection.py \
           bo/line.py \
           bo/lineCollection.py \
           bo/polygon.py \
           bo/polygonCollection.py \
           bo/mapdata.py \
           bo/raster.py \
           bo/rasterCollection.py \
           bo/settings.py \
           bo/profile.py \
           bo/segment.py \
           bo/vertex.py \
           bo/zVal.py \
           bo/node.py \
           bo/linkedList.py \
           bo/plotExtent.py
UTIL_FILES =    util/__init__.py \
                util/u.py \
                util/createProfile.py \
                util/exportShape.py \
                util/ptmaptool.py \
                util/exportDxf.py \
                util/exportXls.py
XLSX_FILES =    util/xlsxwriter/app.py \
                util/xlsxwriter/chart_area.py \
                util/xlsxwriter/chart_bar.py \
                util/xlsxwriter/chart_column.py \
                util/xlsxwriter/chart_doughnut.py \
                util/xlsxwriter/chart_line.py \
                util/xlsxwriter/chart_pie.py \
                util/xlsxwriter/chart.py \
                util/xlsxwriter/chart_radar.py \
                util/xlsxwriter/chart_scatter.py \
                util/xlsxwriter/chartsheet.py \
                util/xlsxwriter/chart_stock.py \
                util/xlsxwriter/comments.py \
                util/xlsxwriter/compat_collections.py \
                util/xlsxwriter/compatibility.py \
                util/xlsxwriter/contenttypes.py \
                util/xlsxwriter/core.py \
                util/xlsxwriter/drawing.py \
                util/xlsxwriter/format.py \
                util/xlsxwriter/__init__.py \
                util/xlsxwriter/packager.py \
                util/xlsxwriter/relationships.py \
                util/xlsxwriter/sharedstrings.py \
                util/xlsxwriter/styles.py \
                util/xlsxwriter/table.py \
                util/xlsxwriter/theme.py \
                util/xlsxwriter/utility.py \
                util/xlsxwriter/vml.py \
                util/xlsxwriter/workbook.py \
                util/xlsxwriter/worksheet.py \
                util/xlsxwriter/xmlwriter.py
UI_FILES = ui/ui_vogisprofiltoolmain.py ui/ui_vogisprofiltoolplot.py ui/ui_vogisprofiltoollayouts.py ui/ui_vogisprofiltoolscale.py
RESOURCE_FILES = resources_rc.py

HELP = help/build/html

default: compile

compile: $(UI_FILES) $(RESOURCE_FILES)

%_rc.py : %.qrc
	pyrcc5 -o $*_rc.py  $<

%.py : %.ui
	pyuic5 -o $@ $<

%.qm : %.ts
	lrelease $<

# The deploy  target only works on unix like operating system where
# the Python plugin directory is located at:
# $HOME/.qgis/python/plugins
#deploy: compile doc transcompile
deploy: compile transcompile
	mkdir -p $(HOME)/$(QGISPIDIR)/python/plugins/$(PLUGINNAME)
	mkdir -p $(HOME)/$(QGISPIDIR)/python/plugins/$(PLUGINNAME)/bo
	mkdir -p $(HOME)/$(QGISPIDIR)/python/plugins/$(PLUGINNAME)/util
	mkdir -p $(HOME)/$(QGISPIDIR)/python/plugins/$(PLUGINNAME)/ui
	mkdir -p $(HOME)/$(QGISPIDIR)/python/plugins/$(PLUGINNAME)/icons
	mkdir -p $(HOME)/$(QGISPIDIR)/python/plugins/$(PLUGINNAME)/util/xlsxwriter

	cp -vf metadata.txt $(HOME)/$(QGISPIDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(PY_FILES) $(HOME)/$(QGISPIDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(BO_FILES) $(HOME)/$(QGISPIDIR)/python/plugins/$(PLUGINNAME)/bo
	cp -vf $(UTIL_FILES) $(HOME)/$(QGISPIDIR)/python/plugins/$(PLUGINNAME)/util
	cp -vf $(UI_FILES) $(HOME)/$(QGISPIDIR)/python/plugins/$(PLUGINNAME)/ui
	cp -vf __init__.py $(HOME)/$(QGISPIDIR)/python/plugins/$(PLUGINNAME)/ui
	cp -vf $(XLSX_FILES) $(HOME)/$(QGISPIDIR)/python/plugins/$(PLUGINNAME)/util/xlsxwriter
	cp -vf $(RESOURCE_FILES) $(HOME)/$(QGISPIDIR)/python/plugins/$(PLUGINNAME)
	cp -vf $(EXTRAS) $(HOME)/$(QGISPIDIR)/python/plugins/$(PLUGINNAME)/icons
	cp -vfr i18n $(HOME)/$(QGISPIDIR)/python/plugins/$(PLUGINNAME)
	cp -vfr $(HELP) $(HOME)/$(QGISPIDIR)/python/plugins/$(PLUGINNAME)/help

# The dclean target removes compiled python files from plugin directory
# also delets any .svn entry
dclean:
	find $(HOME)/$(QGISPIDIR)/python/plugins/$(PLUGINNAME) -iname "*.pyc" -delete
	find $(HOME)/$(QGISPIDIR)/python/plugins/$(PLUGINNAME) -iname ".svn" -prune -exec rm -Rf {} \;

# The derase deletes deployed plugin
derase:
	rm -Rf $(HOME)/$(QGISPIDIR)/python/plugins/$(PLUGINNAME)

# The zip target deploys the plugin and creates a zip file with the deployed
# content. You can then upload the zip file on http://plugins.qgis.org
zip: deploy dclean
	rm -f $(CURDIR)/../$(PLUGINNAME).zip
	cd $(HOME)/$(QGISPIDIR)/python/plugins; zip -9r $(CURDIR)/../$(PLUGINNAME).zip $(PLUGINNAME)

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
	pylupdate5 -noobsolete Makefile

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
