import json
import math
import numpy as np
import cv2
import string
import random

class Konwerter:
    def __init__(self, open_img_cv2, szerokosc_mm, wysokosci_mm, wielkosc_pola_mm=3, path_zapisu=False):
        self.open_img_cv2 = open_img_cv2
        self.szerokosc_mm = szerokosc_mm
        self.wysokosci_mm = wysokosci_mm
        self.wielkosc_pola_mm = wielkosc_pola_mm
        self.slownik_posiadanych_kolorow = json.load(open("slownik_posiadanych_kolorow.json",encoding="utf-8"))
        self.potrzebne = {}
        self.path_zapisu = path_zapisu or "static/wygenerowane/" + "".join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=30)) + ".png"
        try:
            self.status_dzialania = True
            self.main()
            self.status_dzialania = False
        except Exception as e:
            print(e)
    def main(self):
        h_px, w_px, _ = self.open_img_cv2.shape
        h_pola, w_pola, do_szerkosci = self.przeliczenie_px_na_pola(h_px,w_px)

        dopasowny_obrazek_cv2 = cv2.resize(self.open_img_cv2, (w_pola,h_pola), interpolation=cv2.INTER_AREA)
        rgb_cv2 = cv2.cvtColor(dopasowny_obrazek_cv2, cv2.COLOR_BGR2RGB)
        macierz_obrazka = self.konwersja_kolorow_macierzy(rgb_cv2.tolist())

        self.rysowanie(macierz_obrazka)
    def path(self):
        return self.path_zapisu
    def potrzebne_masz(self):
        potrzebne_masz = {}
        for x in self.potrzebne:
            potrzebne_masz[x] = [self.potrzebne[x], self.slownik_posiadanych_kolorow[x]["ilosc"]]
        return potrzebne_masz
    def rysowanie(self, macierz):
        szerokosc_px = int(self.szerokosc_mm * 11.81)
        wysokosci_px = int(self.wysokosci_mm * 11.81)
        wielkosc_pola_px = int(self.wielkosc_pola_mm * 11.81)
        plotno = np.ones((wysokosci_px, szerokosc_px, 3), dtype=np.uint8) * 255
        x_old = 0
        y_old = 0
        liczenie_x = 0
        liczenie_y = 0
        for x in range(0,szerokosc_px,wielkosc_pola_px):
            if len(macierz[0]) <= liczenie_x:
                break
            for y in range(0,wysokosci_px,wielkosc_pola_px):
                if len(macierz) <= liczenie_y:
                    break
                cv2.rectangle(plotno, (x_old, y_old), (x, y),
                              (macierz[liczenie_y][liczenie_x]["rgb"][2], macierz[liczenie_y][liczenie_x]["rgb"][1],
                               macierz[liczenie_y][liczenie_x]["rgb"][0]), -1)
                znak = macierz[liczenie_y][liczenie_x]["oznaczenie"]
                cv2.putText(
                    plotno,
                    znak,
                    (x_old, y - int(wielkosc_pola_px/ 5)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 0, 0) if macierz[liczenie_y][liczenie_x]["rgb"][2] + macierz[liczenie_y][liczenie_x]["rgb"][1] + macierz[liczenie_y][liczenie_x]["rgb"][0] > 380 else (255, 255, 255),
                    1,
                    cv2.LINE_AA
                )
                y_old = y
                liczenie_y += 1
            liczenie_y = 0
            x_old = x
            liczenie_x += 1
        cv2.imwrite(self.path_zapisu, plotno)

    def konwersja_kolorow_macierzy(self,macierz):
        macierz_pola = []
        for x in macierz:
            lista_przedu = []
            for y in x:
                lista_bliskosc = {}
                for z in self.slownik_posiadanych_kolorow:
                    lista_bliskosc[z] = math.sqrt((self.slownik_posiadanych_kolorow[z]["rgb"][0] - y[0])**2 + (self.slownik_posiadanych_kolorow[z]["rgb"][1] - y[1])**2 + (self.slownik_posiadanych_kolorow[z]["rgb"][2] - y[2])**2)
                najblizszy_kolor = min(lista_bliskosc, key=lista_bliskosc.get)
                lista_przedu.append({
                    "rgb":self.slownik_posiadanych_kolorow[najblizszy_kolor]["rgb"],
                    "nazwa":najblizszy_kolor,
                    "oznaczenie":self.slownik_posiadanych_kolorow[najblizszy_kolor]["oznaczenie"]
                })
                try:
                    self.potrzebne[najblizszy_kolor] += 1
                except:
                    self.potrzebne[najblizszy_kolor] = 1
            macierz_pola.append(lista_przedu)
        return macierz_pola

    def przeliczenie_px_na_pola(self, h_px, w_px):
        skala_kartki = self.wysokosci_mm/self.szerokosc_mm
        skala_obrazka = h_px/w_px
        do_szerokosci = False
        if skala_obrazka == skala_kartki:
            wysokosc = int(self.wysokosci_mm/self.wielkosc_pola_mm)
            szerokosc = int(self.szerokosc_mm/self.wielkosc_pola_mm)
        elif skala_kartki < skala_obrazka:
            wysokosc = self.wysokosci_mm/self.wielkosc_pola_mm
            szerokosc = int(wysokosc/skala_obrazka)
            wysokosc = int(wysokosc)
        else:
            szerokosc = self.szerokosc_mm/self.wielkosc_pola_mm
            wysokosc = int(szerokosc * skala_obrazka)
            szerokosc = int(szerokosc)
            do_szerokosci = True
        return wysokosc, szerokosc, do_szerokosci
if __name__ == '__main__':
    konwerter = Konwerter(cv2.imread("zebra.jpg"), 210,297)