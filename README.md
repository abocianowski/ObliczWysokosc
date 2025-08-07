# Oblicz Wysokość

**Wtyczka do QGIS** służąca do obliczania wysokości (Z) dla punktów oraz analizowania **spadków terenu** na podstawie danych NMT (Numeryczny Model Terenu) z serwisu GUGiK.

## Wymagania

- QGIS w wersji **3.8 lub nowszej**
- Dostęp do internetu (do pobierania danych z API GUGiK)

## Funkcje

- **Obliczanie wysokości punktów**  
  - Wskazywanie punktów na mapie i pobieranie dla nich wartości Z  
  - Dodawanie wyników do **warstwy tymczasowej**

- **Zarządzanie danymi punktów**  
  - Przechwytywanie współrzędnych i wysokości w **dokowalnym widgecie**  
  - Możliwość **kopiowania danych do schowka** i wykorzystywania w innych aplikacjach

- **Obliczanie spadków terenu dla linii**  
  - Linie z warstwy są dzielone na odcinki (gęstość ustawiana przez użytkownika)  
  - Wierzchołki odcinków są wzbogacane o wysokość  
  - Obliczane są:
    - spadek terenu,
    - długość 3D,
    - różnica wysokości między początkiem a końcem linii

## Wzór spadku terenu

Spadek obliczany jest ze wzoru:


Gdzie:
- `Δh` – różnica wysokości między punktami,
- `l` – długość odcinka (wzdłuż trasy)

![Wzór spadku terenu](https://upload.wikimedia.org/wikipedia/commons/thumb/d/dc/Grade_dimension.svg/400px-Grade_dimension.svg.png)

## Dane źródłowe

Wtyczka wykorzystuje API GUGiK:  
➡️ [http://services.gugik.gov.pl/nmt/](http://services.gugik.gov.pl/nmt/)

## Przykłady działania

### Obliczanie wysokości punktów

![Obliczanie wysokości punktów](https://github.com/abocianowski/ObliczWysokosc/blob/master/gifs/gif1.gif?raw=true)

### Obliczanie spadków terenu

![Obliczanie spadków terenu](https://github.com/abocianowski/ObliczWysokosc/blob/master/gifs/gif2.gif?raw=true)

---

© Autor: Adrian Bocianowski  
Repozytorium: [ObliczWysokosc](https://github.com/abocianowski/ObliczWysokosc)
