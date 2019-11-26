# -*- coding: utf-8 -*-

# ***************************************************************************
#   This program is free software; you can redistribute it and/or modify    *
#   it under the terms of the GNU General Public License as published by    *
#   the Free Software Foundation; either version 2 of the License, or       *
#   (at your option) any later version.                                     *
# ***************************************************************************
#     begin                : 2019-10-28                                     *
#     copyright            : (C) 2019 by Adrian Bocianowski                 *
#     email                : adrian at bocianowski.com.pl                   *
# ***************************************************************************

from .resources import *
import requests
import os

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMessageBox, QTableWidgetItem, QAbstractItemView, QApplication, QMessageBox
from PyQt5.QtCore import QCoreApplication, Qt, pyqtSignal, QThread, QVariant, QSettings

from qgis.gui import QgsMapToolEmitPoint
from qgis.core import QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject, QgsVectorLayer, QgsLayerTreeLayer, QgsFeature, QgsPoint, QgsField, QgsLineString, QgsVector3D, QgsMapLayerType

class CalculateHeight:
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'QScan_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.actions = []
        self.menu = self.tr(u'&Oblicz wysokość (GUGiK NMT)')
        self.icon_path = ':/plugins/ObliczWysokosc/icons/'

        self.qgsProject = QgsProject.instance()

        self.toolsToolbar = self.iface.addToolBar(u'Oblicz wysokość (GUGiK NMT)')
        self.toolsToolbar.setObjectName(u'Oblicz wysokość (GUGiK NMT)')

        self.panel = leftPanel()
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.panel)

        self.panel.closingPanel.connect(lambda: self.captureButton.setChecked(False))
        self.panel.clearButton.setIcon(QIcon(os.path.join(self.icon_path,'mActionDeleteTable.svg')))
        self.panel.clearButton.clicked.connect(self.clearTable)
        self.panel.copyButton.setIcon(QIcon(os.path.join(self.icon_path,'mActionEditCopy.svg')))
        self.panel.copyButton.clicked.connect(self.copyToClipboard)
        self.panel.clearLayer.setIcon(QIcon(os.path.join(self.icon_path,'mActionDeleteSelected.png')))
        self.panel.clearLayer.clicked.connect(self.clearLayer)
        
        self.tool = canvasTool(self.iface,self.canvas)
        self.tool.clicked.connect(self.capturePoint)
        self.tool.deact.connect(self.panel.hide)

        self.panel.closingPanel.connect(lambda: self.canvas.unsetMapTool(self.tool))

        self.panel.hide()

        self.pDialog = profileDialog(parent=self.iface.mainWindow())
        self.pDialog.refreshButton.setIcon(QIcon(os.path.join(self.icon_path,'mActionRefresh.svg')))
        self.pDialog.refreshButton.clicked.connect(lambda: self.refreshComboBox(self.pDialog.comboBox, 1))
        self.pDialog.canel.clicked.connect(self.taskCanceled)
        self.pDialog.close.clicked.connect(self.closeDialog)
        self.pDialog.run.clicked.connect(self.generateProfile)
        self.pDialog.canel.setEnabled(False)

        self.first_start = None

    def tr(self, message):
        return QCoreApplication.translate('Oblicz wysokosc (GUGiK NMT)', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
        checkable=False,
        checked=False,
        shortcut=None):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None:
            action.setStatusTip(status_tip)
        if whats_this is not None:
            action.setWhatsThis(whats_this)
        if add_to_toolbar:
            self.toolsToolbar.addAction(action)
        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action
                )
        if checkable:
            action.setCheckable(True)
        if checked:
            action.setChecked(1)
        if shortcut:
            action.setShortcut(shortcut)
        self.actions.append(action)

        return action

    def initGui(self):
        self.first_start = True

        # <div>Icons made by <a href="https://www.flaticon.com/authors/wissawa-khamsriwath" title="Wissawa Khamsriwath">Wissawa Khamsriwath</a> from <a href="https://www.flaticon.com/"             title="Flaticon">www.flaticon.com</a></div>
        self.captureButton = self.add_action(
            os.path.join(self.icon_path,'cardinal-points.svg'),
            'Oblicz wysokość',
            self.clickGetHeightButton,
            checkable=True,
            parent=self.iface.mainWindow(),
            )
        self.tool.action = self.captureButton

        # <div>Icons made by <a href="https://www.flaticon.com/authors/wissawa-khamsriwath" title="Wissawa Khamsriwath">Wissawa Khamsriwath</a> from <a href="https://www.flaticon.com/"             title="Flaticon">www.flaticon.com</a></div>
        self.profleButton = self.add_action(
            os.path.join(self.icon_path,'line-chart.svg'),
            'Oblicz spadek terenu',
            self.clickProfleButon,
            checkable=False,
            parent=self.iface.mainWindow(),
            )

        if self.first_start == True:
            self.first_start = False

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Oblicz wysokość'),
                action)
            self.iface.removeToolBarIcon(action)

    def addMemoryLayer(self, source_layer, sect_length):
        layer_fields = source_layer.fields()

        output_layer_name = f'Spadek terenu - {sect_length} - GUGiK NMT'
        output_layer = QgsVectorLayer('LineStringZ?crs=epsg:2180', output_layer_name, 'memory')
        QgsProject.instance().addMapLayer(output_layer, False)
        layerTree = self.iface.layerTreeCanvasBridge().rootGroup()
        layerTree.insertChildNode(0, QgsLayerTreeLayer(output_layer))
        treeRoot = QgsProject.instance().layerTreeRoot()  
        if treeRoot.hasCustomLayerOrder():
            order = treeRoot.customLayerOrder()
            order.insert(0, order.pop(order.index(QgsProject.instance().mapLayersByName(output_layer_name)[0])))
            treeRoot.setCustomLayerOrder(order)

        pr = output_layer.dataProvider()
        att = [i for i in layer_fields]

        roznica_z = QgsField('roznica_z', QVariant.Double)
        att.append(roznica_z)

        dl_3d = QgsField('dlugosc_3d', QVariant.Double)
        att.append(dl_3d)

        spadek = QgsField('spadek', QVariant.Double)
        att.append(spadek)

        pr.addAttributes(att)

        output_layer.updateFields()

        return output_layer

    def addPointToLayer(self, x, y, z):
        x = float(x)
        y = float(y)
        z = float(z)

        name = 'Obliczone wysokości - GUGiK NMT'
        layers = QgsProject.instance().mapLayersByName(name)
        if not layers:
            layer = QgsVectorLayer('PointZ?crs=epsg:2180&field=x:double&field=y:double&field=z:double', name, 'memory')
            QgsProject.instance().addMapLayer(layer, False)
            layerTree = self.iface.layerTreeCanvasBridge().rootGroup()
            layerTree.insertChildNode(0, QgsLayerTreeLayer(layer))

            treeRoot = QgsProject.instance().layerTreeRoot()  
            if treeRoot.hasCustomLayerOrder():
                order = treeRoot.customLayerOrder()
                order.insert(0, order.pop(order.index(QgsProject.instance().mapLayersByName(name)[0])))
                treeRoot.setCustomLayerOrder(order) 
            
            layer.loadNamedStyle(os.path.join(self.plugin_dir,'layer_style.qml'), True)
        else:
            layer = layers[0]

        feature = QgsFeature()
        point = QgsGeometry(QgsPoint(x, y, z))
        feature.setGeometry(point)
        feature.setAttributes([x,y,z])
        layer.startEditing()
        layer.addFeature(feature)
        layer.commitChanges()
        layer.reload()

    def capturePoint(self,point):
        res = getRequests(point)
        if res[0] != False:
            rows = self.panel.tableWidget.rowCount()
            self.panel.tableWidget.setRowCount(rows + 1)
            self.panel.tableWidget.setItem(rows,0, QTableWidgetItem(str(round(point[0],2))))
            self.panel.tableWidget.setItem(rows,1, QTableWidgetItem(str(round(point[1],2))))
            self.panel.tableWidget.setItem(rows,2, QTableWidgetItem(str(res[1])))
            self.panel.tableWidget.selectRow(rows)

            if self.panel.checkBox.isChecked():
                self.addPointToLayer(point[0],point[1],res[1])
        else:
            QMessageBox.warning(None,res[1][0], res[1][1])
    
    def clearLayer(self):
        name = 'Obliczone wysokości - GUGiK NMT'
        layers = QgsProject.instance().mapLayersByName(name)

        if layers:
            layer = layers[0]
            layer.commitChanges()
            layer.dataProvider().truncate()
            self.iface.mapCanvas().refreshAllLayers()

    def clearTable(self):
        self.panel.tableWidget.setRowCount(0)

    def clickProfleButon(self):
        self.pDialog.show()
        self.refreshComboBox(self.pDialog.comboBox, 1)

    def clickGetHeightButton(self):
        if self.captureButton.isChecked():
            self.canvas.setMapTool(self.tool)
            self.panel.show()
        else:
            self.canvas.unsetMapTool(self.tool)
            self.panel.hide()

    def closeDialog(self):
        try:
            if self.pTask.stopTask == False:
                self.pTask.stopTask = True
                self.pTask.terminate()
                QMessageBox.warning(None,'Zatrzymanie procesu', 'Proces generowania spadku terenu został zatrzymany.')
        except:
            pass

        self.pDialog.run.setEnabled(True)
        self.pDialog.canel.setEnabled(False)
        self.pDialog.hide()
        self.pDialog.progressBar.setValue(0)

    def copyToClipboard(self):
        tmp = ''
        for i in range(0,self.panel.tableWidget.rowCount()):
            x = self.panel.tableWidget.item(i,0).text()
            y = self.panel.tableWidget.item(i,1).text()
            z = self.panel.tableWidget.item(i,2).text()
            tmp += f"{x}\t{y}\t{z}\n"
        
        clip = QApplication.clipboard()
        clip.setText(tmp)

    def getLayers(self, geometry_type):
        # 1 = Line layers
        # 2 = Polygon layers
        layers = []
        for l in self.qgsProject.mapLayers():
            layer = self.qgsProject.mapLayer(l)
            if layer.type() == QgsMapLayerType.VectorLayer:
                if layer.geometryType() == geometry_type:
                    layers.append(layer)
        return layers

    def generateProfile(self):
        l_idx = self.pDialog.comboBox.currentIndex()

        if l_idx == 0:
            QMessageBox.warning(None,'Brak warstwy', 'Wybierz warstwę źródłową')
            return
        
        layer = self.lineLayers[l_idx - 1]

        if self.pDialog.onlySelected.isChecked() and len(layer.selectedFeatures()) == 0:
            QMessageBox.warning(None,'Brak obiektów', 'Brak odcinków w selekcji')
            return

        try:
            self.dest_profile_layer = self.addMemoryLayer(layer, str(self.pDialog.spinBox.value()) + ' [m]')
        except:
            QMessageBox.warning(None,'Brakująca warstwa wejściowa', 'Wskazana warstwa wejściowa nie istnieje (prawdopodobnie została usunięta)')
            self.refreshComboBox(self.pDialog.comboBox, 1)
            return

        self.dest_profile_layer.loadNamedStyle(os.path.join(self.plugin_dir,'layer_style2.qml'), True)

        self.pTask = profileTool(layer, self.pDialog.onlySelected.isChecked(), self.pDialog.spinBox.value())
               
        self.pTask.progress.connect(self.pDialog.progressBar.setValue)
        self.pTask.end.connect(self.taskFinished)
        self.pTask.error.connect(self.taskError)
        self.pTask.add_feature.connect(self.taskAddFeature)

        self.pTask.start()
        
        self.pDialog.run.setEnabled(False)
        self.pDialog.canel.setEnabled(True)
        self.pDialog.comboBox.setEnabled(False)
        self.pDialog.spinBox.setEnabled(False)
        self.pDialog.onlySelected.setEnabled(False)
        self.pDialog.refreshButton.setEnabled(False)

    def refreshComboBox(self, combo, geometry_type):
        combo.clear()
        combo.addItem(None)

        if geometry_type == 1:
            self.lineLayers = self.getLayers(1)
        
            for i in self.lineLayers:
                combo.addItem(i.name())  

    def taskError(self,e):
        self.pTask.stopTaks = True
        self.pTask.terminate()
        QMessageBox.warning(None,e[0], e[1])
        self.pDialog.run.setEnabled(True)
        self.pDialog.canel.setEnabled(False)
        self.pDialog.progressBar.setValue(0)
        self.pDialog.comboBox.setEnabled(True)
        self.pDialog.spinBox.setEnabled(True)
        self.pDialog.onlySelected.setEnabled(True)
        self.pDialog.refreshButton.setEnabled(True)

    def taskCanceled(self):
        self.pTask.stopTaks = True
        self.pTask.terminate()
        QMessageBox.warning(None,'Zatrzymanie procesu', 'Proces generowania spadku terenu został zatrzymany.')
        self.pDialog.run.setEnabled(True)
        self.pDialog.canel.setEnabled(False)
        self.pDialog.progressBar.setValue(0)
        self.pDialog.comboBox.setEnabled(True)
        self.pDialog.spinBox.setEnabled(True)
        self.pDialog.onlySelected.setEnabled(True)
        self.pDialog.refreshButton.setEnabled(True)

    def taskFinished(self):
        self.pDialog.run.setEnabled(True)
        self.pDialog.canel.setEnabled(False)
        QMessageBox.information(self.iface.mainWindow(),'Spadek terenu', 'Proces generowania został zakończony')
        self.pDialog.progressBar.setValue(0)
        self.pDialog.comboBox.setEnabled(True)
        self.pDialog.spinBox.setEnabled(True)
        self.pDialog.onlySelected.setEnabled(True)
        self.pDialog.refreshButton.setEnabled(True)
        
        self.pTask.quit()
        self.pTask.wait()

    def taskAddFeature(self,feature):
        self.dest_profile_layer.startEditing()
        self.dest_profile_layer.addFeature(feature)
        self.dest_profile_layer.commitChanges()

class canvasTool(QgsMapToolEmitPoint):
    clicked = pyqtSignal(list)
    deact = pyqtSignal()

    def __init__(self, iface, canvas):
        QgsMapToolEmitPoint.__init__(self, canvas)
        self.canvas = canvas
        self.iface = iface
        self.action = None

    def activate(self):
        self.action.setChecked(True)
        self.setCursor(Qt.CrossCursor)

    def canvasPressEvent(self, e):
        point = self.toMapCoordinates(self.canvas.mouseLastXY())
        point = QgsGeometry.fromPointXY(point)

        canvas_crs = self.canvas.mapSettings().destinationCrs().authid()
        target_crs = QgsCoordinateReferenceSystem(2180)

        point = self.geometryCrs2Crs(point, canvas_crs, target_crs)
        point = point.asPoint()
        x = point.x()
        y = point.y()

        self.clicked.emit([x,y])

    def deactivate(self):
        self.action.setChecked(False)
        self.deact.emit()

    def geometryCrs2Crs(self,geometry, source_crs, destination_crs):
        geometry = QgsGeometry(geometry)
        src_crs = QgsCoordinateReferenceSystem(source_crs)
        dest_crs = QgsCoordinateReferenceSystem(destination_crs)
        crs2crs = QgsCoordinateTransform(src_crs, dest_crs, QgsProject.instance())
        geometry.transform(crs2crs)
        return geometry

class profileTool(QThread):
    progress = pyqtSignal(int)
    end = pyqtSignal()
    error = pyqtSignal(list)
    add_feature = pyqtSignal(object)

    def __init__(self, source_layer, only_selected, distance):
        QThread.__init__(self)
        self.source_layer = source_layer
        self.only_selected = only_selected
        self.distance = distance
        self.stopTask = False
    
    def run(self):    
        f_count = 0
        
        if self.only_selected:
            f_count += len(self.source_layer.selectedFeatures())
            features = [i for i in self.source_layer.selectedFeatures()]
        else:
            f_count += self.source_layer.featureCount()
            features = [i for i in self.source_layer.getFeatures()]
        i = 0
        prg = 0

        for f in features:
            f_geom = f.geometry()

            for part in f_geom.parts():
                part_geom = QgsGeometry.fromWkt(part.asWkt())
                part_geom_sections = self.generateSections(part_geom, self.distance)
                part_geom_sections_len = len(part_geom_sections)
                i2 = 0

                for pgs in part_geom_sections:
                    if not self.stopTask:
                        att = f.attributes()
                        geom_z = self.addZvalue(pgs)
                        if geom_z[0] == False:
                            self.error.emit(geom_z[1])
                            return
                        feature = QgsFeature()
                        v_lst = [i for i in geom_z[1].vertices()]

                        # roznica_z
                        z_diff= round(abs(v_lst[0].z() - v_lst[-1].z()),2)
                        att.append(z_diff)

                        # dl_3d
                        dl_3d = [ QgsVector3D (i.x(), i.y(), i.z()) for i in v_lst]
                        dl_3d = [dl_3d[i].distance(dl_3d[i+1])  for i,e in enumerate(dl_3d[:-1])]
                        dl_3d = round(sum(dl_3d),2)
                        att.append(dl_3d)
                        # spadek
                        if dl_3d == 0:
                            continue
                        spadek = round((z_diff/dl_3d) * 100,2)
                        att.append(spadek)
                        
                        feature.setAttributes(att)
                        feature.setGeometry(geom_z[1])
                        self.add_feature.emit(feature)

                        i2 += 1
                        prg2 = ((i2 / part_geom_sections_len / f_count) * 100) + prg
                        if (prg2 - prg) > 1:
                            self.progress.emit(prg2)
                    else:
                        return
            i += 1
            prg = (i/f_count) * 100
            self.progress.emit(prg)

        self.end.emit()

    def addZvalue(self, geometry):
        geom_list = []
        for v in geometry.vertices():
            x = float(v.x())
            y = float(v.y())
            z = getRequests([x,y])
            if z[0] == False:
                return False,z[1]
            point = QgsPoint(x, y, float(z[1]))
            geom_list.append(point)

        geom = QgsGeometry.fromPolyline(geom_list)
        return True, geom

    def generateSections(self, geometry, distance):
        geom_length = geometry.length()
        vertices = [geometry.lineLocatePoint(QgsGeometry.fromWkt(i.asWkt())) for i in geometry.vertices()]
        geom_list = []
        i = 0

        while i < geom_length:
            end = i + distance
            if end > geom_length:
                end = geom_length

            tmp_geom = []
            tmp_geom.append(i)
            for v in vertices:
                if v > i and v < end:
                    tmp_geom.append(v)
            tmp_geom.append(end)
            tmp_geom = QgsGeometry.fromPolylineXY([geometry.interpolate(i).asPoint() for i in tmp_geom])
            geom_list.append(tmp_geom)
            i += distance
        return geom_list

def getRequests(point):
    url = f'https://services.gugik.gov.pl/nmt/?request=GetHbyXY&x={point[1]}&y={point[0]}'
    try:
        req = requests.get(url, timeout=120)
    except:
        return False,['Błąd połączenia', 'Upłynął limit czasu oczekiwania na dane lub serwer nie odpowiada']

    if req.status_code == 200:
        return True, req.text
    else:
        return False,['Błąd połączenia', 'Wystąpił błąd podczas pobierania danych. Sprawdź połączenie internetowe']

LEFT_PANEL, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),'qt','leftPanel.ui'))
PROFILE_DIALOG, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__),'qt','calculate_decrease.ui'))

class leftPanel(QtWidgets.QDockWidget, LEFT_PANEL):
    closingPanel = pyqtSignal()

    def __init__(self, parent=None):
        super(leftPanel, self).__init__(parent)
        self.setupUi(self)

    def closeEvent(self, event):
        self.closingPanel.emit()
        event.accept()

class profileDialog(QtWidgets.QDialog, PROFILE_DIALOG):
    def __init__(self, parent=None):
        super(profileDialog, self).__init__(parent)
        self.setupUi(self)