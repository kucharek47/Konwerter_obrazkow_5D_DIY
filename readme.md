# 5D DIY Diamond Painting Converter - Desktop Edition 💎

![Angular](https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Desktop](https://img.shields.io/badge/Platform-Desktop-lightgrey?style=for-the-badge&logo=windows&logoColor=black)

## 📌 O Projekcie

**5D DIY Diamond Painting Converter** to hybrydowa aplikacja desktopowa stworzona w celu automatyzacji procesu tworzenia schematów do haftu diamentowego. Narzędzie pozwala użytkownikowi wgrać dowolne zdjęcie i przekonwertować je na gotowy wzór (wraz z legendą kolorów DMC), który można wydrukować i wykorzystać do wyklejania.

Projekt powstał w modelu **Rapid Application Development (RAD)** jako dedykowane rozwiązanie (prezent świąteczny) stworzone pod konkretne wymagania użytkownika końcowego. Głównym wyzwaniem było połączenie potężnych bibliotek graficznych Pythona z nowoczesnym, responsywnym interfejsem użytkownika, co osiągnięto poprzez architekturę klient-serwer działającą lokalnie.

## 💡 Dlaczego taka architektura?

Zamiast standardowego podejścia desktopowego (np. PyQt/Tkinter), zdecydowano się na nowoczesny stos technologiczny:
1.  **Python (Backend/Engine):** Odpowiada za ciężkie obliczenia, mapowanie kolorów i obróbkę obrazu (OpenCV/PIL), w czym jest bezkonkurencyjny.
2.  **Angular (Frontend/UI):** Zapewnia Material Design, płynność działania i podgląd "na żywo", co jest trudne do osiągnięcia w klasycznych frameworkach desktopowych.
3.  **Lokalny Serwer:** Aplikacja działa jako lokalna instancja, co pozwala w przyszłości na łatwe zapakowanie jej do pliku `.exe` (np. przy użyciu PyInstaller) lub dystrybucję jako aplikację Electron.

## 🚀 Kluczowe Funkcjonalności

* **Konwersja Obrazu:** Algorytmy dopasowujące kolory zdjęcia do ograniczonej palety dostępnych "diamentów".
* **Zarządzanie Zasobami:** System obsługi słownika posiadanych kolorów (format JSON), co pozwala optymalizować zużycie materiałów.
* **Intuicyjny UI:** Interfejs zaprojektowany z myślą o użytkowniku nietechnicznym – prostota "Drag & Drop" i czytelne wizualizacje.
* **Generowanie Wyników:** Tworzenie plików wyjściowych gotowych do druku bezpośrednio na dysku użytkownika.

## 🛠️ Technologie

**Core:**
* **Python 3.x** - Silnik aplikacji.
* **Flask** - Lekki framework spinający logikę Pythona z interfejsem.
* **OpenCV / Pillow** - Przetwarzanie grafiki rastrowej.

**Interfejs:**
* **Angular (v17+)** - Warstwa prezentacji.
* **TypeScript** - Logika interfejsu.
* **Angular Material** - Komponenty UI.

## ⚙️ Uruchomienie Deweloperskie

Aplikacja składa się z dwóch modułów, które w środowisku deweloperskim uruchamiane są niezależnie. Docelowo mogą być zbudowane do jednego pliku wykonywalnego.

### 1. Silnik (Python)
```bash
# Aktywacja środowiska i instalacja zależności
cd kucharek47-Konwerter_obrazkow_5D_DIY
pip install -r requirements.txt

# Uruchomienie lokalnego API
python app.py