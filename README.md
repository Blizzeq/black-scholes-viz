# Black-Scholes Price Movement Simulator

Symulator losowych ruchów cen w modelu Black-Scholes z atrakcyjną wizualizacją "wachlarza" ścieżek cenowych.

## 🎯 Funkcjonalności

- **Symulacja Monte Carlo** - Generowanie setek losowych ścieżek cenowych
- **Model Black-Scholes** - Geometryczny ruch Browna z konfigurowalnymi parametrami
- **Wizualizacja wachlarzowa** - Gradient kolorów od zielonego (zysk) do czerwonego (strata)
- **Interaktywny wykres** - Zoom, pan, animacje
- **Panel kontrolny** - Łatwa konfiguracja parametrów symulacji
- **Statystyki** - VaR, Expected Shortfall, percentyle
- **Ciemny motyw** - Profesjonalny i atrakcyjny interfejs

## 🚀 Instalacja i Uruchomienie

### Wymagania
- Python 3.10+
- pip

### Kroki instalacji

1. **Klonowanie/pobranie projektu**
```bash
# Jeśli masz git
git clone <repository-url>
cd black-scholes-viz

# Lub po prostu rozpakuj folder
```

2. **Instalacja zależności**
```bash
pip install -r requirements.txt
```

3. **Uruchomienie aplikacji**
```bash
python main.py
```

## 🎮 Instrukcja Użytkowania

### Panel Kontrolny (Lewa Strona)

1. **Scenariusze** - Wybierz predefiniowany scenariusz rynkowy
2. **Liczba ścieżek** - Ustaw ilość symulowanych ścieżek (10-1000)
3. **Horyzont czasowy** - Okres symulacji w latach (0.1-5.0)
4. **Cena początkowa (S₀)** - Startowa cena akcji
5. **Oczekiwany zwrot (μ)** - Roczna stopa zwrotu (-50% do +50%)
6. **Zmienność (σ)** - Volatility rynkowa (5% do 100%)

### Wykres (Środek)

- **Ścieżki cenowe** - Kolorowane zgodnie z wynikiem (zielone=zysk, czerwone=strata)
- **Linie percentyli** - Pokazują różne kwantyle rozkładu (10%, 25%, 50%, 75%, 90%)
- **Interaktywność** - Scroll=zoom, LPM=przeciąganie
- **Animacja** - Przycisk "Animuj" pokazuje płynne powstawanie ścieżek

### Panel Statystyk (Dół)

- **Prawdopodobieństwo zysku** - % ścieżek z dodatnim zwrotem
- **VaR (95%)** - Value at Risk na poziomie 95%
- **Expected Shortfall** - Średnia strata w najgorszych scenariuszach

## 📊 Predefiniowane Scenariusze

- **Stable Growth** - Stabilny wzrost (μ=8%, σ=15%)
- **High Volatility** - Wysoka zmienność (μ=5%, σ=40%)
- **Bear Market** - Bessza (μ=-10%, σ=25%)
- **Bull Market** - Hossa (μ=15%, σ=20%)
- **Crisis** - Kryzys (μ=-20%, σ=60%)
- **Low Vol** - Niska zmienność (μ=6%, σ=8%)

## 🧮 Model Matematyczny

Aplikacja używa modelu Black-Scholes opartego na geometrycznym ruchu Browna:

```
dS(t) = μS(t)dt + σS(t)dW(t)
```

Gdzie:
- **S(t)** - cena akcji w czasie t
- **μ** - drift (oczekiwana stopa zwrotu)
- **σ** - zmienność (volatility)
- **W(t)** - proces Wienera (Brownian motion)

Dyskretne rozwiązanie:
```
S(t) = S₀ * exp((μ - σ²/2)t + σ√dt * Z)
```

gdzie Z ~ N(0,1) - rozkład normalny standardowy.

## 🎨 Technologie

- **PySide6** - Nowoczesny framework GUI
- **NumPy** - Obliczenia numeryczne i symulacje
- **Matplotlib** - Wykresy i wizualizacje
- **SciPy** - Funkcje statystyczne

## 📁 Struktura Projektu

```
black-scholes-viz/
├── main.py                 # Główny plik aplikacji
├── requirements.txt        # Zależności
├── README.md              # Ten plik
├── plan.txt               # Szczegółowy plan projektu
├── src/
│   ├── models/
│   │   └── black_scholes.py   # Model matematyczny
│   ├── ui/
│   │   ├── main_window.py     # Główne okno
│   │   ├── control_panel.py   # Panel kontrolny
│   │   └── chart_widget.py    # Widget wykresu
│   └── utils/
│       └── config.py          # Konfiguracja
└── resources/
    └── styles.qss         # Arkusze stylów
```

## 🔧 Możliwe Rozszerzenia

- Export wykresów do PNG/SVG
- Export danych do CSV
- Porównanie z rzeczywistymi danymi historycznymi
- Wycena opcji europejskich/amerykańskich
- Analiza portfela
- Tryb real-time z danymi giełdowymi

## 📝 Licencja

Ten projekt został stworzony w celach edukacyjnych i demonstracyjnych.

---

**Autor**: Symulator Black-Scholes
**Wersja**: 1.0.0
**Data**: Wrzesień 2024