# Oblicz Wysokość
Wtyczka do programu Qgis umożliwiająca obliczanie wartości Z dla dodanych punktów oraz obliczanie spadów terenu. Dane NMT do analizy pochodzą z serwisu GUGiK.

Narzędzie jest kompatybilne z wersją Qgis'a od 3.8 wzwyż. Wtyczka umożliwia:
- obliczenie wysokości dla punktów wskazanych w oknie mapy i dodanie wyników do warstwy tymczasowej,
- zapisywanie przechwyconych wysokości i współrzędnych punktów w dokowalnym widgecie. Dane mogą być skopiowane do schowka przy użyciu narzędzia do kopiowania i wykorzystane w innych aplikacjach,
- obliczenie spadków terenu dla warstw zawierających obiekty liniowe. Linie zawarte w warstwie zostaną podzielone na sekcje (gęstość przekroju) podane przez użytkownika. Następnie wierzchołki sekcji zostaną wzbogacone o wysokość, dzięki którym obliczone zostaną: spadek terenu, długość 3d i różnica wysokości (punkt początkowy i końcowy).

Wtyczka wykorzystuje API GUGiK dostępne pod adresem: http://services.gugik.gov.pl/nmt/


Przykład wykorzystania narzędzia do obliczania punktów:
<img src="https://github.com/abocianowski/ObliczWysokosc/blob/master/gifs/gif1.gif?raw=true" alt="gif1.gif">

Przykład wykorzystania narzędzia do obliczania spadków terenu:
<img src="https://github.com/abocianowski/ObliczWysokosc/blob/master/gifs/gif2.gif?raw=true" alt="gif2.gif">
