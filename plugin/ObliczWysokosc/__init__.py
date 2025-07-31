# -*- coding: utf-8 -*-

# ***************************************************************************
#   This program is free software; you can redistribute it and/or modify    *
#   it under the terms of the GNU General Public License as published by    *
#   the Free Software Foundation; either version 2 of the License, or       *
#   (at your option) any later version.                                     *
# ***************************************************************************
#     begin                : 2019-10-28                                     *
#     updated              : 2025-07-31                                     *
#     copyright            : (C) 2025 by Adrian Bocianowski                 *
#     email                : adrian at bocianowski.com.pl                   *
# ***************************************************************************

from qgis.gui import QgsInterface


def classFactory(iface: QgsInterface) -> "CalculateHeight":
    from .CalculateHeight import CalculateHeight
    return CalculateHeight(iface)
