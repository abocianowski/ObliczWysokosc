import ObliczWysokosc

def test_plugin_is_loaded(qgis_app, qgis_iface):
    # Importuj plugin i załaduj go przez classFactory z iface
    plugin = ObliczWysokosc.classFactory(qgis_iface)
    plugin.initGui()

    # Sprawdź, czy iface i plugin są poprawnie ustawione
    assert qgis_iface is not None
    assert plugin is not None