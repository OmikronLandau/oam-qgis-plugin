# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OpenAerialMapDialog
                                 A QGIS plugin
 This plugin can be used as an OAM client to browse, search, download and
 upload imagery from/to the OAM catalog.
                             -------------------
        begin                : 2015-07-01
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Humanitarian OpenStreetMap Team (HOT)
        email                : tassia@acaia.ca  / yoji.salut@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os, sys

from PyQt4 import QtGui, uic
from PyQt4.Qt import *
from PyQt4 import QtCore

from img_browser import ImgBrowser
from module.module_access_oam_catalog import OAMCatalogAccess

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'ui/img_search_dialog.ui'))

class ImgSearchDialog(QtGui.QDialog, FORM_CLASS):

    def __init__(self, iface, parent=None):
        """Constructor."""
        super(ImgSearchDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.iface = iface
        self.setupUi(self)

        # initialize GUI
        self.initGui()

        # event handling
        self.pushButtonSearch.clicked.connect(self.startSearch)
        self.pushButtonBrowseLatest.clicked.connect(self.browseLatest)
        self.pushButtonBrowseLocation.clicked.connect(self.browseLocation)
        self.connect(self.listWidget, QtCore.SIGNAL("itemClicked(QListWidgetItem *)"), self.browseThumbnailAndMeta);

        #self.buttonBox.clicked.connect(lambda: self.test(self.buttonBox))
        self.connect(self.buttonBox, QtCore.SIGNAL('accepted()'), self.execOk)
        self.connect(self.buttonBox, QtCore.SIGNAL('rejected()'), self.execCancel)

        #add objects for catalog access
        self.oamCatalogAccess = OAMCatalogAccess("https://oam-catalog.herokuapp.com")
        self.imgBrowser = None

    def test(self, *argv):
        print(str(argv))

    def initGui(self):

        item = QListWidgetItem()
        item.setText("Please set the conditions and press 'Search' button.")
        item.setData(Qt.UserRole, "Sample Data")
        self.listWidget.addItem(item)

        self.lineEditLocation.setText("")
        self.dateEditAcquisitionFrom.setDate(QDate.currentDate().addMonths(-3))
        self.dateEditAcquisitionTo.setDate(QDate.currentDate())
        self.lineEditResolutionFrom.setText("")
        self.lineEditResolutionTo.setText("")

    def refreshListWidget(self, metadataInList):

        self.listWidget.clear()

        for singleMetaInDict in metadataInList:
            item = QListWidgetItem()
            item.setText(str(singleMetaInDict['title']))
            item.setData(Qt.UserRole, singleMetaInDict)
            self.listWidget.addItem(item)

    def startSearch(self):
        action = "meta"
        dictQueries = {}
        #temporarily disable this part
        #dictQueries['location'] = self.lineEditLocation.text()
        dictQueries['acquisition_from'] = self.dateEditAcquisitionFrom.date().toString(Qt.ISODate)
        dictQueries['acquisition_to'] = self.dateEditAcquisitionTo.date().toString(Qt.ISODate)
        dictQueries['gsd_from'] = self.lineEditResolutionFrom.text()
        dictQueries['gsd_to'] = self.lineEditResolutionTo.text()

        self.oamCatalogAccess.setAction(action)
        self.oamCatalogAccess.setDictQueries(dictQueries)
        metadataInList = self.oamCatalogAccess.getMetadataInList()

        self.refreshListWidget(metadataInList)

    #change the name to search latest, or trigger the img_browser?
    #probably input the number of images?
    def browseLatest(self):
        print("Browse latest imagery...")

        action = "meta"
        dictQueries = {}
        dictQueries['sort'] = "desc"
        dictQueries['order_by'] = "acquisition_end"
        #isn't it better to make a textbox to accept the number of images displayed?
        dictQueries['limit'] = 3

        self.oamCatalogAccess.setAction(action)
        self.oamCatalogAccess.setDictQueries(dictQueries)
        metadataInList = self.oamCatalogAccess.getMetadataInList()

        self.refreshListWidget(metadataInList)

    def browseLocation(self):
        print("Browse location of loaded layer...")

    def browseThumbnailAndMeta(self, item):
        singleMetaInDict = item.data(Qt.UserRole)
        print(str(singleMetaInDict))

        if type(singleMetaInDict) is dict:

            if self.imgBrowser == None:
                self.imgBrowser = ImgBrowser(self.iface, singleMetaInDict)
            else:
                self.imgBrowser.setSingleMetaInDic(singleMetaInDict)

            if not self.imgBrowser.isVisible():
                self.imgBrowser.show()

            self.imgBrowser.displayThumbnailAndMeta()
            self.imgBrowser.activateWindow()

    def execOk(self):
        print("OK")

    def execCancel(self):
        print("Canceled")
