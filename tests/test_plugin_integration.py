from qgis.core import (
    QgsVectorLayer,
    QgsField,
    QgsProject,
    QgsFeature,
)
import ObliczWysokosc
import pytest
from PyQt5.QtCore import QMetaType

@pytest.fixture
def plugin(qgis_app, qgis_iface):
    plugin = ObliczWysokosc.classFactory(qgis_iface)
    plugin.initGui()
    return plugin

def test_add_memory_layer(plugin):
    """
    Verifies that the plugin correctly creates a memory LineStringZ layer
    with expected fields and geometry settings based on a source layer.
    """

    # --- Setup: Create input (source) vector layer with sample attributes ---
    source_layer = QgsVectorLayer("Point?crs=epsg:2180", "source", "memory")
    provider = source_layer.dataProvider()
    provider.addAttributes([
        QgsField("source_id", QMetaType.Int, "int"),
        QgsField("source_name", QMetaType.QString, "string")
    ])
    source_layer.updateFields()

    # --- Execution: Call method under test ---
    output_layer = plugin.addMemoryLayer(source_layer, 100)

    # --- Assertions: Check if output layer is registered in QGIS ---
    assert output_layer in QgsProject.instance().mapLayers().values(), "Output layer was not added to QGIS project"
    assert output_layer.name() == "Spadek terenu - 100 [m] - GUGiK NMT"

    # --- Assertions: Verify expected fields exist ---
    actual_field_names = [field.name() for field in output_layer.fields()]
    expected_fields = ["source_id", "source_name", "roznica_z", "dlugosc_3d", "spadek"]
    for field in expected_fields:
        assert field in actual_field_names, f"Missing expected field: {field}"

    # --- Assertions: Validate geometry type and Z-support ---
    assert output_layer.geometryType() == 1, "Expected LineString geometry (type 1)"
    assert output_layer.wkbType() == output_layer.wkbType().LineStringZ,"Expected LineStringZ WKB type"

def test_add_point_to_layer(plugin):
    """
    Verifies that a single 3D point is added to the correct memory layer
    and contains accurate Z value.
    """

    # --- Execution: Add a single 3D point ---
    plugin.addPointToLayer(500000, 500000, 100)

    # --- Assertions: Check if the point was added to the expected layer ---
    layers = QgsProject.instance().mapLayersByName("Obliczone wysokości - GUGiK NMT")
    assert len(layers) == 1
    layer = layers[0]


    assert layer.featureCount() == 1, "Expected one feature (point) in the layer"

    # --- Assertions: Verify geometry is 3D and contains correct Z value ---
    feature: QgsFeature = next(layer.getFeatures())
    point = feature.geometry().constGet()  # returns QgsPoint
    assert point.z() == 100.0, f"Expected Z value of 100.0, got {point.z()}"
