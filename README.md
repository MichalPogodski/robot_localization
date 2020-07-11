# RAPORT projekt lokalizacja


## Lokalizacja

Obliczanie rozkładu lokalizacji robota zostało przeprowadzone poprzez:
* obliczanie prawdopodobienstwa przejscia robota z lokacji do lokacji, 
* obliczanie rozkładu prawdopodobieństwa dla aktualnego kierunku robota, 
* obliczanie rozkładu prawdopodobienstwa występowania przeszkód w miejscach wskazanych przez sensor. 

### Rozkład prawdopodobieństwa przejścia robota
został określony w macierzy o wymiarach NxN (gdzie N to liczba możliwych lokacji robota). 
Każda komórka macierzy określa prawdopodobieństwo przejścia pomiędzy lokacją określoną wierszem, a lokacją określoną kolumną. 
W wyznaczaniu wartości prawdopodobieństwa uwzględnione zostały możliwe błędy w reagowaniu robota na polecenie 'forward'.

### Rozkład prawdopodobieństwa kierunku robota
został określony w macierzy o wymiarach 4x4, gdzie każda komórka określa możliwość obrotu z kierunku określonego przez wiersz w kierunku określonym przez kolumnę. 
W wyznaczaniu wartości prawdopodobieństwa uwzględnione zostały możliwe błędy w reagowaniu robota na polecenia 'turnleft' oraz 'turnright'.

### Rozkład prawdopodobieństwa występowania przeszkód w miejscach wskazanych przez sensor
został wyznaczony poprzez sprawdzenie sąsiedztwa robota w lokacjach wskazanych przez sensor. W tym celu należało określić kierunek (N, E, S  lub W), na podstawie informacji zwracanych przez sensor (dla konkretnego kierunku względem robota, orientacja zamieniona została na kierunek geograficzny).
W wyznaczonym rozkładzie uwzględnione zostały możliwe błędy w danych zwracanych przez sensor. 


## Heurystyka
Heurystyka poruszająca robotem bazuje na regule, wedle której można szukać wyjścia z labiryntu. Mianowicie, należy przemieszczać się nie odrywając ręki od prawej (lub lewej) ściany. 
Robot, jeżeli po swojej prawej stronie nie wykrył przeszkody, to skręca w prawo.
Jeżeli po jego prawej stronie jest przeszkoda, a nie ma przed nim, to idzie prosto.
Jeżeli przeszkoda jest i po prawej stronie i na wprost, to robot obraca się. 

Dzięki takiej heurystyce, dla idealnie działających czujników, robot nie będzię 'krążył w kółko' w pokoju z mało widocznym wyjściem, a także ma szanse znaleźć się w większej liczbie lokacji niż przy losowym wyborze akcji.
