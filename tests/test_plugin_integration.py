# -*- coding: utf-8 -*-

# ***************************************************************************
#   This program is free software; you can redistribute it and/or modify    *
#   it under the terms of the GNU General Public License as published by    *
#   the Free Software Foundation; either version 2 of the License, or       *
#   (at your option) any later version.                                     *
# ***************************************************************************
#     begin                : 2019-10-28                                     *
#     updated              : 2025-08-07                                     *
#     copyright            : (C) 2025 by Adrian Bocianowski                 *
#     email                : adrian at bocianowski.com.pl                   *
# ***************************************************************************

from qgis.core import QgsProject
import ObliczWysokosc
import pytest

@pytest.fixture
def plugin(qgis_app, qgis_iface):
    plugin = ObliczWysokosc.classFactory(qgis_iface)
    plugin.initGui()
    return plugin

def test_capture_point_success(plugin):
    # Arrange
    point = [500000.123, 500000.456]
    plugin.capturePoint(point)

    assert plugin.panel.tableWidget.rowCount() == 1
    assert plugin.panel.tableWidget.item(0, 0).text() == str(round(point[0], 2))
    assert plugin.panel.tableWidget.item(0, 1).text() == str(round(point[1], 2))

def test_clear_layer(plugin):
    # Arrange
    layer_name = "Obliczone wysokości - GUGiK NMT"
    layer = QgsProject.instance().mapLayersByName(layer_name)[0]
    assert layer.featureCount() > 0  # sanity check

    # Act
    plugin.clearLayer()

    # Assert
    assert layer.featureCount() == 0