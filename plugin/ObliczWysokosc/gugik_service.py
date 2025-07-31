import requests
from typing import List, Tuple, Union

class GugikService:
    """Wrapper around GUGiK NMT service requests."""

    URL_TEMPLATE = (
        "https://services.gugik.gov.pl/nmt/?request=GetHbyXY&x={x}&y={y}"
    )

    def get_height(self, point: List[float]) -> Tuple[bool, Union[str, List[str]]]:
        """Return height value for given point.

        Parameters
        ----------
        point : List[float]
            Coordinates in order [x, y].

        Returns
        -------
        Tuple[bool, Union[str, List[str]]]
            Result flag and either height as string or error messages.
        """
        url = self.URL_TEMPLATE.format(x=point[1], y=point[0])
        try:
            resp = requests.get(url, timeout=120)
        except Exception:
            return False, [
                "Błąd połączenia",
                "Upłynął limit czasu oczekiwania na dane lub serwer nie odpowiada",
            ]

        if resp.status_code == 200:
            return True, resp.text

        return False, [
            "Błąd połączenia",
            "Wystąpił błąd podczas pobierania danych. Sprawdź połączenie internetowe",
        ]

