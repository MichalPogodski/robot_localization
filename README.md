# RAPORT projekt lokalizacja


## Lokalizacja

W zadaniu obliczania rozkładu prawdopodobieństwa lokalizacji oraz kierunku robota,
obliczany jest rozkład prawdopodobieństwa tranzycji robota, zmiany kierunku,
 a także prawdopodobieństwo występowania przeszkód na danych pozycjach. 

### Rozkład prawdopodobieństwa tranzycji robota
został określony w macierzy o wymiarach 4Nx4N (gdzie N to liczba możliwych lokacji robota, 
a 4 to liczba podstawowych kierunków geograficznych świata,
 które w tym projekcie pozwalają określić kierunek robota).
Każda komórka określa prawdopodobieństwo przejścia robota ze stanu określonego wierszem do stanu określonego kolumną. 
Stanem została określona lokalizacja robota a także jego kierunek.  
W wypadku akcji 'forward' macierz tranzycji przedstawia rozkład prawdopodobieństwa dla zmiany lokalizacji robota. 
W przypadku akcji obrotu ('turnleft' lub 'turnright') macierz tranzycji określa rozkład 
prawdopodobieństwa dla zmiany orientacji robota (przy pozostaniu w tej samej lokalizacji). 
W wyznaczaniu wartości prawdopodobieństwa uwzględnione zostały możliwe błędy w reagowaniu robota
 na polecenie wykonywania akcji.


### Rozkład prawdopodobieństwa występowania przeszkód
został wyznaczony poprzez sprawdzenie sąsiedztwa robota w lokalizacjach wskazanych przez sensor. 
W tym celu należało określić kierunek (N, E, S  lub W), na podstawie informacji zwracanych przez sensor 
(dla konkretnego kierunku względem robota, orientacja zamieniona została na kierunek geograficzny).
W wyznaczonym rozkładzie uwzględnione zostały możliwe błędy w danych zwracanych przez sensor. 

### Obsługa zdarzenia 'bump'
została określona w dwóch miejscach. 
* Pierwszym z nich jest macierz tranzycji po wykonaniu akcji forward.
 Jeżeli poprzednią akcją było 'forward' i wystąpiło zdarzenie 'bump', 
 robot zostanie w swojej starej lokalizacji.
* Drugim jest macierz przedstawiająca rozkład prawdopodobieństwa występowania przeszkód. Jeżeli wystąpiło zdarzenie 'bump',
a przed robotem (w pewnej lokacji i w pewnym kierunku) znajduje się ściana (lub pole niedostępne), 
prawdopodobieństwo wystąpienia przeszkody w tym miejscu jest mnożone *1.0 (co daje lepszy rezultat niż mnożenie *0.9,
w którym to uwzględniona jest niepoewność pomiarów sensora). Jeżeli jednak, po wystąpieniu akcji 'bump', w danym sąsiedztwie
nie ma przeszkody, możemy być pewni, że robot nie jest odwrócony w tą stronę (a przeszkoda tam nie istnieje) i wartość
prawdopodobieństwa mnożona jest *0.0.  
## Heurystyka
Niżej opisana heurystyka, w takim zadaniu, daje bardzo dobry rezultat, ponieważ robot nieustannie rejestruje 
występowanie przeszkód po jednej ze swoich stron. Im więcej lokacji odwiedzi, 
tym bardziej unikalną sekwencję ścian zarejestruje. 
Robot wybiera takie sekwencje akcji, które dają mu dużo informacji.

Heurystyka poruszająca robotem bazuje na regule, wedle której można szukać wyjścia z labiryntu. Mianowicie, 
należy przemieszczać się nie odrywając ręki od prawej (lub lewej) ściany. 
Robot, jeżeli po swojej prawej stronie nie wykrył przeszkody, to skręca w prawo.
Jeżeli po jego prawej stronie jest przeszkoda, a nie ma przed nim, to idzie prosto.
Jeżeli przeszkoda jest i po prawej stronie i na wprost, to robot obraca się. 

Dzięki takiej heurystyce, dla idealnie działających czujników, robot nie będzię 'krążył w kółko' 
w pokoju z mało widocznym wyjściem, a także ma szanse znaleźć się w większej liczbie lokacji niż przy losowym wyborze akcji.
