# TODO — QuadCardBackplane_board (QCB)

Wygenerowane z pełnego design review (schematic + PCB) z 2026-08-03, zaktualizowane po odpowiedziach z 2026-08-04. Szczegóły i uzasadnienia: [DESIGN_REVIEW_2026-08-03.md](DESIGN_REVIEW_2026-08-03.md) (zawiera teraz też korekty tam, gdzie przegląd się mylił).

## 🔴 Krytyczne — funkcjonalne błędy

- [x] ~~I2C: kolizja adresów EEPROM~~ — **false positive, wycofane.** U6/U8/U10/U12 są na 4 (docelowo 5) fizycznie odrębnych magistralach I2C, po jednej na każdy wpinany moduł identyfikacyjny backplane'u — nie są ze sobą połączone. Mój wniosek o "wspólnej magistrali" wynikał z tego, że detektor `PR-001` grupuje komponenty po lokalnej nazwie etykiety (`SCL`/`SDA`) bez uwzględnienia prefiksu instancji arkusza — na PCB te same nazwy występują jako osobne sieci `/CON1/SCL`, `/CON2/SCL` itd., czego nie sprawdziłem krzyżowo przed nazwaniem tego "potwierdzonym błędem". Identyczne strapowanie E0/E1/E2 na każdym module nie jest problemem, bo każdy siedzi na swojej własnej magistrali.
- [x] ~~PCB: brak ciągłej płaszczyzny GND~~ — **zaakceptowane ryzyko, nie błąd.** Przy 3 warstwach sygnałowych + 1 masie nie ma miejsca na dedykowaną, w pełni litą płaszczyznę bez kompromisów w routingu; zasilanie ma tu niższy priorytet niż sygnały. Świadoma decyzja projektowa — zostawiam jak jest.
- [x] ~~USB D+/D− skew na CON1–CON4~~ — **nie dotyczy.** Kanały pracują jako USB 2.0 Full-Speed (12 Mb/s), nie Hi-Speed — przy tej prędkości budżet skew jest rzędu nanosekund, więc rozjazd 5.7–7.4mm nie ma praktycznego znaczenia. Mój wniosek zakładał Hi-Speed na podstawie samych możliwości hosta FE1.1s, nie faktycznej konfiguracji/wykorzystania portów.

## 🟠 Ważne — przed zamówieniem płytki

*(bez zmian — nadal otwarte)*

- [ ] **BOM: uzupełnić MPN** — tylko 33% (13/39) unikalnych linii BOM ma numer katalogowy. Brakuje głównie rezystorom, kondensatorom, diodom, złączom J1/J2/J4/J5/J7–J10. Użyć skilla `bom`/`digikey`/`lcsc` do uzupełnienia przed eksportem do zamówienia.
- [ ] **Footprint UT8413A (D12, D13, D14, D15)** — referencja biblioteczna `Diodes_UDFN-10_1.0x2.5mm_P0.5mm` w `Package_DFN_QFN` nie rozwiązuje się (błąd w natywnym ERC/DRC KiCad). Naprawić link biblioteczny lub dodać footprint do lokalnej biblioteki projektu.
- [ ] **Znaleźć/podać datasheet UT8413A** — nie znaleziony automatycznie (nie ma w LCSC bez klucza, brak trafień w wyszukiwarce). Bez niego pinout tego ESD/ochrony per-kanał jest tylko wewnętrznie spójny (schemat=PCB), niezweryfikowany wobec producenta.
- [ ] **Zdobyć klucze API DigiKey / Mouser / element14** (opcjonalnie), jeśli ma być pełny automatyczny sync datasheetów — obecnie tylko 1/10 komponentów z MPN ma pobrany datasheet (H1102NL).

## 🟡 Do poprawy — layout / EMC / DFM

- [x] ~~Drugi kondensator odsprzęgający równolegle do C1~~ — **sprawdzone, OK bez zmian.** (impedancja z SPICE zaakceptowana jako wystarczająca)
- [x] ~~Via GND przy TVS U4/U7/U9~~ — **sprawdzone, OK bez zmian.**
- [x] ~~Odległość TVS U7/U9/U11 od złączy J4/J5~~ — **sprawdzone, OK.** Zabezpieczenia są umyślnie jak najbliżej źródła zagrożenia (złącza) — zgodnie z dobrą praktyką ESD, nie wymaga zmiany.
- [x] ~~Routing zegarów (XIN/XOUT U1, OSCI IC1) na warstwie zewnętrznej~~ — **sprawdzone, OK bez zmian.**
- [ ] Dodać min. 3 fiducial markery na stronę (B.Cu ma komponenty fine-pitch/QFN — pad min. 0.20mm, brak fiducali utrudni pick-and-place). *(nadal otwarte)*
- [x] ~~Via annular ring 0.1mm poniżej IPC Class 2~~ — **sprawdzone, OK bez zmian** (akceptowany tier "advanced" w JLCPCB).
- [x] **Tentowanie/wypełnienie via-in-pad** (C21:2, C33:2, C49:2 ×2, C77:1, C80:2, C81:1, R2:2, TP11:1, TP2:1, Y1:2) — **wykonane.**
- [x] ~~Odległość J6 od krawędzi płyty (0.57mm)~~ — **sprawdzone, OK bez zmian.**
- [x] ~~Przydział pinów GND na J2~~ — **sprawdzone, OK bez zmian.**
- [x] ~~Miedź/via przy J3 (RJ45) pin 7~~ — **sprawdzone, OK bez zmian.**
- [x] ~~Punkty testowe (3% pokrycia sieci)~~ — **nie dotyczy.** Produkcja bez ICT/flying probe — wszystko ewentualnie testowane ręcznie, więc niskie pokrycie TP nie jest problemem.

## 🟢 Kosmetyka / higiena ERC (nie wpływa na działanie)

- [x] Dodać symbole `PWR_FLAG` w punktach wejścia zasilania (J6, regulator wewnętrzny IC1) — **zaznaczone jako zrobione.**
- [x] Ujednolicić nazwy sieci REG_IN/VDD33 — **zaznaczone jako zrobione.**
- [x] Zaktualizować symbole niezgodne z biblioteką (JP1–JP5, Y1, Y2) — **zaznaczone jako zrobione.**

## ⏭️ Do wykonania w kolejnym przeglądzie (gdy będzie więcej danych)

- [ ] Dociągnąć pełną weryfikację datasheetową dla IC1 (IP175G), M24C02-WMN, USBLC6-2SC6, UT8413A — obecnie zweryfikowany wobec pełnego datasheetu producenta jest tylko U1 (FE1.1s).

---

**Stan po tej turze**: sekcja krytyczna (🔴) w całości zamknięta — wszystkie trzy pozycje okazały się nieporozumieniami przeglądu, nie realnymi błędami. Sekcja 🟡 zamknięta poza fiducialami. Otwarte pozostają: fiducial markery, uzupełnienie BOM/MPN, i temat footprintu + datasheetu UT8413A (D12–D15) — to jedyne realnie nierozwiązane punkty przed zamówieniem płytki.
