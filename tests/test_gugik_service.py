import os
import sys
import types

qgis_stub = types.ModuleType("qgis")
qgis_stub.gui = types.ModuleType("gui")
qgis_stub.gui.QgsInterface = object  # minimal stub
sys.modules.setdefault("qgis", qgis_stub)
sys.modules.setdefault("qgis.gui", qgis_stub.gui)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    import requests
except ModuleNotFoundError:  # pragma: no cover - fallback for test env
    import sys
    import types

    requests = types.ModuleType("requests")
    def _dummy(*args, **kwargs):
        raise NotImplementedError
    requests.get = _dummy
    requests.exceptions = types.SimpleNamespace(Timeout=Exception)
    sys.modules['requests'] = requests

from plugin.ObliczWysokosc.gugik_service import GugikService
from unittest.mock import patch


def test_get_height_success():
    service = GugikService()
    with patch('plugin.ObliczWysokosc.gugik_service.requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '123.45'
        res = service.get_height([10.0, 20.0])
        assert res == (True, '123.45')
        mock_get.assert_called_once_with(
            service.URL_TEMPLATE.format(x=20.0, y=10.0), timeout=120
        )


def test_get_height_http_error():
    service = GugikService()
    with patch('plugin.ObliczWysokosc.gugik_service.requests.get') as mock_get:
        mock_get.return_value.status_code = 500
        mock_get.return_value.text = 'Error'
        res = service.get_height([10.0, 20.0])
        assert res[0] is False
        assert 'Błąd połączenia' in res[1][0]


def test_get_height_exception():
    service = GugikService()
    with patch(
        'plugin.ObliczWysokosc.gugik_service.requests.get',
        side_effect=requests.exceptions.Timeout,
    ):
        res = service.get_height([10.0, 20.0])
        assert res[0] is False
        assert 'Błąd połączenia' in res[1][0]
