import json
import math
import numpy as np
import cv2


class Konwerter:
    def __init__(self, open_img_cv2, szerokosc_mm, wysokosci_mm, wielkosc_pola_mm=3):
        self.open_img_cv2 = open_img_cv2
        self.szerokosc_mm = szerokosc_mm
        self.wysokosci_mm = wysokosci_mm
        self.wielkosc_pola_mm = wielkosc_pola_mm
        self.slownik_posiadanych_kolorow = json.load(open("slownik_posiadanych_kolorow.json",encoding="utf-8"))

        self.main()
    def main(self):
        h_px, w_px, _ = self.open_img_cv2.shape
        h_pola, w_pola = self.przeliczenie_px_na_pola(h_px,w_px)

        dopasowny_obrazek_cv2 = cv2.resize(self.open_img_cv2, (h_pola,w_pola), interpolation=cv2.INTER_AREA)
        rgb_cv2 = cv2.cvtColor(dopasowny_obrazek_cv2, cv2.COLOR_BGR2RGB)
        macierz_obrazka = self.konwersja_kolorow_macierzy(rgb_cv2.tolist())


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
            macierz_pola.append(lista_przedu)

    def przeliczenie_px_na_pola(self, h_px, w_px):
        skala_kartki = self.wysokosci_mm/self.szerokosc_mm
        skala_obrazka = h_px/w_px
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
        return wysokosc, szerokosc
if __name__ == '__main__':
    konwerter = Konwerter(cv2.imread("zebra.webp"), 419,600)