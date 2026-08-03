# Design Review — QuadCardBackplane_board (QCB), rev 0.1

Data przeglądu: 2026-08-03
Zakres: `pcb/QCB_board.kicad_sch` (+ arkusze `con1`, `eth_switch`, `usb_switch`, `pwr`) oraz `pcb/QCB_board.kicad_pcb`
Narzędzia: kicad-happy `kicad` (schematic/pcb/cross-analysis), `emc`, `spice` (ngspice), `analyze_thermal`, natywny `kicad-cli sch erc` / `kicad-cli pcb drc` (KiCad 10.0.4)

---

## 1. Co to za płytka

4-warstwowa karta backplane (F.Cu / In1.Cu / In2.Cu / B.Cu, grubość 1.586 mm), 101.6 × 128.7 mm, 216 komponentów. Funkcjonalnie:

- **U1 (FE1.1s)** — 4-portowy hub USB 2.0 Hi-Speed (480 Mb/s), rozprowadza D+/D− do 4 kanałów backplane (CON1–CON4).
- **IC1 (IP175G)** — 5-portowy switch Ethernet 10/100. Port 5 wyprowadzony na złącze RJ45 (J3, magnetyka H1102NL), porty 1–4 idą do kanałów backplane.
- **4× kanał (con1.kicad_sch reużyty jako CON1…CON4)** — każdy z własną parą USB D+/D−, parą Ethernet (CON_TX±/CON_RX±), RS485±, EEPROM identyfikacyjnym M24C02 na wspólnej magistrali I2C, ESD (USBLC6-2SC6, UT8413A) — wyprowadzone na złącza backplane DIN41612 2×32 (J7/J8/J9/J10).
- **pwr.kicad_sch** — wejście zasilania (złącze Molex Mini-Fit J6), bezpiecznik polimerowy F1, ferryt/dławik L1, ESD (D10). **Brak regulatora napięcia na płycie** — +3.3 V (i pozostałe szyny) pochodzą z backplane'u.

Zgodność schematyk↔PCB: **216 komponentów w schemacie = 216 footprintów na PCB** (dokładna zgodność). Liczba sieci: 237 (schematic) vs 263 (PCB) — różnica wynika z metodyki liczenia (PCB dolicza `unconnected-(...)` na niewykorzystanych pinach złączy DIN41612), nie jest błędem.

## 2. Co zostało uruchomione / czego brakowało

| Krok | Status |
|---|---|
| `analyze_schematic.py` | ✅ |
| `analyze_pcb.py --full --proximity` | ✅ |
| `cross_analysis.py` | ✅ (33 findings) |
| `analyze_emc.py` | ✅ (115 findings, 9 kategorii) |
| `kicad-cli sch erc` / `pcb drc` (natywny silnik KiCad 10.0.4) | ✅ — uruchomiony dodatkowo, poza standardowym workflow skilla, bo `D:\KiCad\10.0\bin\kicad-cli.exe` był dostępny |
| SPICE (ngspice) | ✅ — ngspice nie był w PATH, znaleziony pod `D:\Spice64\bin\ngspice.exe` (podałeś ścieżkę), użyty przez `NGSPICE_PATH`. 22 symulacje, 21 pass / 1 warn |
| Thermal | ✅ — 0 findings (na płycie nie ma zidentyfikowanych komponentów mocy typu regulator/driver z istotną dyssypacją — spójne z brakiem regulatora na tej karcie) |
| Sync datasheetów (DigiKey) | ❌ brak `DIGIKEY_CLIENT_ID`/`SECRET` w środowisku |
| Sync datasheetów (LCSC, bez klucza) | ⚠️ częściowy — tylko **1/10** komponentów z MPN miało pobieralny datasheet (H1102NL). Reszta (kondensatory GRM…, IP175G, USBLC6-2SC6 itd.) nie została znaleziona w LCSC/alt. źródłach automatycznie |
| Weryfikacja krytycznych pinów wobec prawdziwego datasheetu | ✅ ręcznie via WebSearch/WebFetch dla FE1.1s (Terminus Technology, Rev 1.0) — patrz sekcja 4 |
| Lifecycle audit (obsolescence) | ⛔ nie uruchomiony — pokrycie MPN w BOM to tylko 33% (13/39 unikalnych linii), audyt miałby sens dopiero po uzupełnieniu MPN |
| Gerber analyzer | ⛔ nie uruchomiony — w projekcie nie ma jeszcze wyeksportowanych gerberów |

**Uwaga o poziomie zaufania**: przy MPN pokryciu 33% i praktycznie zerowym pokryciu datasheetami, większość poniższych ustaleń to **weryfikacja spójności** (schemat ↔ PCB ↔ symbol biblioteczny), nie pełna weryfikacja wobec danych producenta — poza miejscami, gdzie jawnie cytuję konkretny datasheet (FE1.1s).

---

## 3. NAJWAŻNIEJSZE — realne błędy potwierdzone na surowych danych

### 3.1 ~~🔴 Kolizja adresów I2C~~ — WYCOFANE (2026-08-04)

> **Korekta**: to nie jest błąd. Autor potwierdził, że U6/U8/U10/U12 siedzą na 4 (docelowo 5) fizycznie **odrębnych** magistralach I2C — po jednej na każdy wpinany moduł identyfikacyjny backplane'u — a nie na jednej wspólnej. Poniższa analiza opierała się na grupowaniu przez detektor `PR-001`, który dopasowuje komponenty po **lokalnej** nazwie etykiety (`SCL`/`SDA`) i nie uwzględnia prefiksu instancji arkusza. Na PCB te same nazwy lokalne występują jako w pełni odrębne sieci (`/CON1/SCL`, `/CON2/SCL`, ...) — to sprawdzenie zrobiłem już po fakcie, nie przed nazwaniem tego "potwierdzonym błędem" w oryginalnym przeglądzie. Wniosek poniżej pozostawiony dla śladu, ale nieaktualny.

<details>
<summary>Oryginalna (błędna) analiza — rozwiń</summary>

#### Kolizja adresów I2C — 4× M24C02 na wspólnej magistrali z identycznym adresem (NIEAKTUALNE)

**Potwierdzone bezpośrednio w pinach**, nie tylko heurystyką: U6, U8, U10, U12 (po jednym EEPROM-ie M24C02-WMN na każdy kanał CON1–CON4) wiszą na **wspólnej** magistrali SCL/SDA (widoczne na złączach J7–J10, sygnały `/CONx/SCL`, `/CONx/SDA` idą wspólnie), a każdy z nich ma identyczne podłączenie pinów adresowych:

```
U6:  E0=GND  E1=+3.3V  E2=GND
U8:  E0=GND  E1=+3.3V  E2=GND
U10: E0=GND  E1=+3.3V  E2=GND
U12: E0=GND  E1=+3.3V  E2=GND
```

Wszystkie cztery odpowiadają pod tym samym adresem 7-bit I2C (1010 E2E1E0 = 1010010). Master nigdy nie odróżni EEPROM-u kanału 1 od kanału 3 — kolizja na SDA, nieprzewidywalne odczyty.

**Przyczyna źródłowa**: `con1.kicad_sch` jest reużywany 4× jako CON1…CON4 bez zmiany strapowania adresu przy każdej instancji.

**Rekomendacja**: nadać każdemu kanałowi unikalny adres (np. 000/001/010/011 przez E2E1E0), albo rozdzielić na 4 oddzielne magistrale/mux I2C, jeśli identyfikacja per-kanał ma sens niezależnie.

*(koniec nieaktualnej analizy — patrz korekta powyżej)*

</details>

### 3.2 🟠 Struktura warstw PCB — brak ciągłej płaszczyzny odniesienia na całej płycie

> **Aktualizacja (2026-08-04)**: zaakceptowane jako świadomy kompromis projektowy, nie błąd do poprawy. Przy 3 warstwach sygnałowych + 1 warstwie masy nie ma miejsca na dedykowaną, w pełni litą płaszczyznę bez ograniczenia routingu sygnałów — a zasilanie ma tu niższy priorytet niż sygnały. Analiza poniżej (ustalenia analizatorów) zostaje jako dokumentacja rzeczywistej struktury miedzi, ale nie wymaga akcji.

To najpoważniejsza, systemowa obserwacja z warstwy PCB, widoczna niezależnie w kilku detektorach jednocześnie (nie pojedynczy false-positive):

- **SU-001 (deterministic, x3, error)**: każda para sąsiednich warstw miedzi — F.Cu/In1.Cu, In1.Cu/In2.Cu, In2.Cu/B.Cu — jest sklasyfikowana jako "sygnał obok sygnału" bez litej płaszczyzny odniesienia pomiędzy nimi.
- **GP-001 (x65: 30 error + 35 warning)**: sieci sygnałowe mają 25–75% pokrycia płaszczyzną odniesienia na swojej długości routingu ("major"/"partial reference plane gap").
- **RP-001 (x22: 11 error + 11 warning)**: brak via stitching przy przejściach warstw.
- **RP-002 (x10, error, deterministic — z cross_analysis, liczone przez union-find na realnej miedzi)**: 10 różnicowych par Ethernetu (`1RX1_P/N`, `0RX0_P/N`, `4TX4_P/N`, `2RX2_P/N` itd.) fizycznie przecina szczeliny w miedzi wylanej siecią **+3.3V** na warstwach zewnętrznych F.Cu/B.Cu.
- **PS-002 (error)**: sieć +3.3V jest podzielona na **10 wysp** miedzi, z 23 sygnałami przecinającymi granice między nimi.

Sprawdziłem geometrię zalewów (`zones`): "+3.3V" na F.Cu/B.Cu to dziesiątki małych, lokalnych plamek miedzi (rzędu 0.3–1 mm²) wokół pinów zasilania, a nie jedna ciągła płaszczyzna — natomiast "Earth"/"GND" jest zalane głównie na warstwach wewnętrznych, ale też nie na całej powierzchni płyty. Efekt: prąd powrotny sygnałów szybkich (5-portowy switch Ethernet, USB Hi-Speed) często nie ma bliskiej, ciągłej ścieżki powrotnej — pętla powrotna się wydłuża, co podnosi promieniowanie EMI i pogarsza integralność sygnału.

**Rekomendacja**: przeznaczyć co najmniej jedną warstwę wewnętrzną (In1.Cu lub In2.Cu) na **litą, nieprzerywaną płaszczyznę GND** bez routingu sygnałowego po niej, i referencjonować do niej wszystkie różnicowe pary Ethernetu/USB oraz zegary. Doszyć via stitching wzdłuż krawędzi płaszczyzn +3.3V tam, gdzie sygnały muszą je przecinać.

### 3.3 🟡 Rozjazd długości par różnicowych USB (D+/D−) na kanałach backplane

> **Aktualizacja (2026-08-04)**: nie dotyczy — porty CON1–CON4 pracują jako USB 2.0 **Full-Speed** (12 Mb/s), nie Hi-Speed. Poniższa analiza zakładała Hi-Speed na podstawie samych możliwości hosta FE1.1s (który obsługuje Hi-Speed), a nie faktycznej prędkości negocjowanej na tych portach. Przy Full-Speed budżet skew jest rzędu nanosekund — rozjazd 5.7–7.4mm nie ma praktycznego znaczenia, zmiana niekonieczna.

FE1.1s (U1) to hub **Hi-Speed (480 Mb/s)** — potwierdzone w tabeli poboru prądu datasheetu (tryby "High-Speed 4x…"). Dla USB HS skew wewnątrz pary powinien być rzędu ułamka mm (budżet ~kilkuset ps, czyli ~1 mm przy typowej prędkości propagacji FR4). Zmierzone rozjazdy na PCB:

| Para | Δ długości | % |
|---|---|---|
| /CON1/D+ // D− | 5.7 mm | 72% |
| /CON2/D+ // D− | 7.4 mm | 56% |
| /CON3/D+ // D− | 5.7 mm | 72% |
| /CON4/D+ // D− | 5.7 mm | 72% |

To zdecydowanie za dużo dla Hi-Speed USB (kilka razy więcej niż typowy budżet skew). Jeśli te porty faktycznie mają negocjować Hi-Speed (a nic w schemacie nie ogranicza ich do Full-Speed), warto dostroić długości do <1 mm różnicy, albo świadomie potwierdzić, że kanały backplane mają działać tylko Full-Speed (12 Mb/s), gdzie ten skew nie ma znaczenia.

Dla porównania, pary Ethernetu (100 Mb/s, tolerancja dużo luźniejsza) mają rozjazdy 7–24% — mniej krytyczne, ale też warto wyrównać przy okazji poprawek layoutu.

### 3.4 🟠 BOM — 33% pokrycia MPN, blokada pre-fab

`SS-001`: tylko 13/39 unikalnych linii BOM (33.3%) ma numer katalogowy producenta — głównie brakuje MPN dla rezystorów, kondensatorów, diod, złączy J1/J2/J4/J5/J7-J10. Bez uzupełnienia MPN nie da się wygenerować BOM do zamówienia (JLCPCB/DigiKey/Mouser) ani zweryfikować dostępności/lifecycle. To task na skille `bom`/`digikey`/`lcsc`, jeśli chcesz iść w stronę zamówienia płytki.

### 3.5 🟡 Footprint D12–D15 (UT8413A) nie rozwiązuje się w bibliotece

Natywny `kicad-cli` (i ERC, i DRC) zgłasza dla D12, D13, D14, D15: footprint `Diodes_UDFN-10_1.0x2.5mm_P0.5mm` nie został znaleziony w bibliotece `Package_DFN_QFN`. Geometria na PCB istnieje (routing kompletny, liczba footprintów się zgadza), więc płytka fizycznie ma tam coś wylutowanego — ale referencja biblioteczna jest zerwana. Przed kolejną edycją/aktualizacją footprintów warto naprawić link (albo dodać brakujący footprint do lokalnej biblioteki projektu), inaczej KiCad nie będzie w stanie zaktualizować/zweryfikować tego footprintu przy re-imporcie.

Nie znalazłem datasheetu dla **UT8413A** (prawdopodobnie ESD/ochrona per-kanał, analogicznie do USBLC6-2SC6, w obudowie UDFN-10) — ani przez wyszukiwarkę, ani w LCSC/DigiKey bez kluczy API. **Jeśli masz link/PDF do UT8413A, chętnie zweryfikuję pinout wobec niego** — bez tego pinout tego komponentu jest tylko wewnętrznie spójny (schemat=PCB), niezweryfikowany wobec producenta.

---

## 4. Zweryfikowane FALSE POSITIVE (nie wymagają poprawki)

Zgodnie z metodologią przeglądu — poniższe zostały podniesione przez analizatory jako poważne, ale po weryfikacji wobec datasheetu / realnej topologii pinów okazują się prawidłowe:

**PP-001 — "U1 pin 28 (VD18) nie ma ścieżki DC do szyny zasilania"** (zgłoszone jako `error`).
Sprawdziłem prawdziwy datasheet FE1.1s (Terminus Technology, Rev. 1.0, tabela opisu pinów, SSOP-28):
- pin 28 `VD18` = "1.8V power input"
- pin 12 (w symbolu KiCad; pin 7 wg diagramu SSOP producenta) `VD18_O` = "1.8V power output from 3.3V→1.8V integrated regulator — a 10µF decoupling capacitor is required"

W schemacie oba piny (12 i 28) siedzą na **tej samej** sieci, razem z kondensatorem C5 = **10 µF** — dokładnie zgodnie z wymogiem datasheetu. To poprawny, zalecany obwód aplikacyjny; heurystyka BFS analizatora nie rozpoznała "power_out pin tego samego IC na tej samej sieci" jako ważnego źródła DC, bo sieć jest nienazwana (`__unnamed_109`). Nie wymaga zmian.

**DC-002 — "Brak kondensatora odsprzęgającego przy U14"** (zgłoszone jako `error`, EMC).
U14 to USBLC6-2SC6 — czysta macierz diod TVS (piny: I/O1, I/O2×2, GND, VBUS-jako-linia-chroniona). **Nie ma pinu zasilania** (brak VCC/power_in) — to komponent pasywny, odsprzęgnięcie fizycznie nie ma zastosowania. Heurystyka "każdy IC potrzebuje decoupling" fałszywie zadziałała na układ ochronny bez zasilania.

**9× "Input Power pin not driven" (natywny ERC) + 12× RS-001 "brak zadeklarowanego źródła"** (REG_OUT, VDD10, VDD33, DVCC, DVDD, +3.3V i in.).
Zweryfikowałem to na poziomie sieci — **nie są to pływające szyny**:
- `REG_OUT` (pin 41 `VREG_LDO` układu IC1/IP175G) zasila `VDD10` przez ferryt FB1 i `DVDD` przez ferryt FB2 — to wewnętrzny regulator IP175G analogicznie do przypadku VD18_O w FE1.1s. Ścieżka DC istnieje (rezystancja ferrytu DC ≈ 0), sam schematic-analyzer (bardziej wyrafinowany, uwzględnia ferryty w BFS) tego nie zgłasza jako PP-001 — zgadza się.
- `VDD33`/`DVCC` są zasilane z głównej szyny +3.3V przez ferryty FB3/FB4.
- Sam +3.3V nie ma nigdzie w projekcie pinu jawnie typowanego jako `power_out` — źródło to złącze zasilania J6 (Molex, `pwr.kicad_sch`), ale generyczny symbol złącza ma typy pinów `passive`, nie `power_out`.

**Przyczyna źródłowa (jedna, powtarzająca się)**: symbol IP175G pochodzi z SamacSys/Ultra Librarian i ma **wszystkie** piny stypowane jako `passive` zamiast `power_in`/`power_out` — ERC nie widzi wewnętrznego regulatora jako źródła. Do tego część szyn wewnętrznych (DVDD, VDD10, VDD33, DVCC, REG_OUT, PWR_OFF) jest nazwana przez generyczny symbol `power:VDD` (który w bibliotece KiCad ma typ pinu **input**, nie output) zamiast `PWR_FLAG`.

**Rekomendacja (kosmetyczna, nie funkcjonalna)**: dodać symbole `PWR_FLAG` w rzeczywistych punktach wejścia zasilania (pin J6 dla +3.3V/+5V/+12V na `pwr.kicad_sch`, ew. przy pinach regulatorów wewnętrznych IC1/U1) — wyciszy to i natywny ERC, i `RS-001`, bez zmiany realnego połączenia. Docelowo warto też poprawić typy pinów w niestandardowych symbolach SamacSys (IP175G, UT8413A, 100616-2 itd.) — obecnie "passive" wszędzie maskuje tę klasę błędów na przyszłość.

---

## 5. Pozostałe ustalenia — do przejrzenia, mniej pilne

| Obszar | Ustalenie | Rekomendacja |
|---|---|---|
| Zasilanie/SPICE | C1 (odsprzęgający) — SPICE (ngspice) pokazuje wysoką impedancję Z(100kHz)=1.59 kΩ, Z(1MHz)=159 Ω — pojedynczy kondensator, brak wsparcia przy wyższych częstotliwościach | Dodać drugi, mniejszy kondensator równolegle (np. 100nF + 10nF) |
| ESD | U4 (USBLC6-2SC6) — brak via GND w promieniu 3mm; U7/U9 — tylko 1 via GND (zalecane ≥2) | Dodać via GND blisko padów GND układów TVS — indukcyjność ścieżki do masy krytyczna przy ESD 8kV |
| ESD | U7/U9/U11 fizycznie oddalone od chronionych złączy J4/J5 | Przybliżyć układy TVS do złącza |
| Zegary | XIN/XOUT (U1), OSCI (IC1) routowane na warstwie zewnętrznej; OSCI blisko J5 | Rozważyć routing na warstwie wewnętrznej / stripline, odsunąć od złącza |
| Assembly | Brak fiducali na obu stronach (B.Cu ma komponenty fine-pitch/QFN, pad min. 0.20mm) | Dodać min. 3 fiducial markery na stronę |
| Test | Pokrycie punktami testowymi: 9/261 sieci (3%) | Rozważyć dodanie TP na kluczowych sieciach przed produkcją |
| DFM | Via annular ring 0.1mm < wymóg IPC Class 2 (0.125mm); płyta >100×100mm → wyższy próg cenowy JLCPCB (tier "advanced") | Zwiększyć annular ring, jeśli zamawiasz w klasie standard |
| Via-in-pad | 11× via w padzie bez tentowania (C21, C33, C49×2, C77, C80, C81, R2, TP11, TP2, Y1) | Zatentować/wypełnić lub potwierdzić, że fab obsługuje via-in-pad |
| Mechanika | J6 tylko 0.57mm od krawędzi płyty (zalecane ≥1.0mm) | Odsunąć lub potwierdzić z fabem |
| I2C | Poza kolizją adresów (3.1) — brak innych problemów na magistrali | — |
| Higiena ERC | "REG_IN" i "VDD33" to dwie etykiety tej samej sieci (ERC wybrał REG_IN) | Ujednolicić nazewnictwo dla czytelności |
| Złącza | J2 — zbyt mało pinów GND jak na wysokoprędkościowe sygnały; J3 (RJ45) pin 7 ma 25% pokrycia płaszczyzną odniesienia | Sprawdzić przydział GND na J2; doszyć miedź/via przy J3 pin 7 |

## 6. Weryfikacja SPICE

22 automatycznie wykryte podukłady (filtry RC, odsprzęganie zasilania), symulowane w ngspice-46:

- **21/22 pass** — obliczone częstotliwości odcięcia filtrów RC zgadzają się z SPICE z błędem 0.24% (rezystory/kondensatory mają prawidłowe wartości względem topologii).
- **1 warning** — C1 (opisane w sekcji 5, wysoka impedancja odsprzęgania powyżej ~1MHz).
- Sieci odsprzęgające C6–C33 (grupy kondensatorów przy IC1) mają Z_min rzędu 5–9 mΩ — bardzo dobre.

## 7. Nie wykonano / ograniczenia przeglądu

- **Lifecycle/obsolescence audit** — pominięty (za niskie pokrycie MPN, brak sensu bez uzupełnienia BOM).
- **Gerber analyzer** — pominięty (brak wyeksportowanych gerberów w projekcie).
- **Pełna weryfikacja datasheetowa** wszystkich 15 układów IC — tylko FE1.1s (U1) zweryfikowany wobec pełnego datasheetu producenta. IP175G (IC1), M24C02-WMN (U6/U8/U10/U12), USBLC6-2SC6 (U4/U7/U9/U11/U13/U14), UT8413A (D12-D15) — bez pobranych datasheetów, ustalenia dla nich to weryfikacja spójności schemat↔PCB↔symbol, nie wobec dokumentacji producenta.
- Jeśli chcesz, mogę spróbować ręcznie doszukać brakujące datasheety (IP175G, UT8413A, 100616-2) przez WebSearch/WebFetch tak jak zrobiłem dla FE1.1s — zajmie to dodatkowy czas, ale podniesie pewność ustaleń w sekcjach 3.1/3.5.

---

## 8. Priorytetowa lista działań

*(zaktualizowane 2026-08-04 po odpowiedziach autora — patrz [TODO.md](TODO.md) dla pełnego stanu)*

1. ~~I2C: rozdzielić adresy U6/U8/U10/U12~~ — **wycofane, false positive** (3.1).
2. ~~PCB stackup/GND: przeznaczyć warstwę wewnętrzną na litą płaszczyznę GND~~ — **zaakceptowany kompromis, nie wymaga zmiany** (3.2).
3. ~~USB D+/D−: wyrównać długości par~~ — **nie dotyczy, porty Full-Speed** (3.3).
4. **BOM**: uzupełnić MPN (skill `bom`) przed zamówieniem (3.4) — **nadal otwarte**.
5. **Footprint D12–D15**: naprawić referencję biblioteczną UT8413A + znaleźć datasheet (3.5) — **nadal otwarte**.
6. Fiducial markery (sekcja 5) — **nadal otwarte**. Reszta pozycji z sekcji 5 potwierdzona jako OK bez zmian — patrz [TODO.md](TODO.md).
