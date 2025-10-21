import tkinter as tk
import csv
import os

class Kontakt:
    def __init__(self, ime, email, telefon):
        self.ime = ime  # 3 I VIŠE ZNAKA
        self.email = email  
        self.telefon = telefon  # 9,10 ZNAKOVA 

    def __str__(self):
        return f"{self.ime} - {self.email} - {self.telefon}"


class ImenikApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Jednostavni digitalni imenik")
        self.kontakti = []

        frame_unos = tk.Frame(root, padx=10, pady=10)
        frame_unos.grid(row=0, column=0, sticky="ew")

        tk.Label(frame_unos, text="Ime i prezime:").grid(row=0, column=0, sticky="w")
        tk.Label(frame_unos, text="Email:").grid(row=1, column=0, sticky="w")
        tk.Label(frame_unos, text="Telefon:").grid(row=2, column=0, sticky="w")

        self.entry_ime = tk.Entry(frame_unos, width=30)
        self.entry_email = tk.Entry(frame_unos, width=30)
        self.entry_telefon = tk.Entry(frame_unos, width=30)

        self.entry_ime.grid(row=0, column=1, padx=5, pady=2)
        self.entry_email.grid(row=1, column=1, padx=5, pady=2)
        self.entry_telefon.grid(row=2, column=1, padx=5, pady=2)

        tk.Button(frame_unos, text="Dodaj kontakt", command=self.dodaj_kontakt).grid(row=3, column=0, columnspan=2, pady=5)

        frame_lista = tk.Frame(root, padx=10, pady=10)
        frame_lista.grid(row=1, column=0, sticky="nsew")

        self.listbox = tk.Listbox(frame_lista, width=60, height=10)
        self.scrollbar = tk.Scrollbar(frame_lista, orient="vertical", command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        self.listbox.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        frame_gumbi = tk.Frame(root, padx=10, pady=10)
        frame_gumbi.grid(row=2, column=0, sticky="ew")

        tk.Button(frame_gumbi, text="Spremi kontakte", command=self.spremi_kontakte).grid(row=0, column=0, padx=5)
        tk.Button(frame_gumbi, text="Učitaj kontakte", command=self.ucitaj_kontakte).grid(row=0, column=1, padx=5)
        tk.Button(frame_gumbi, text="Obriši kontakt", command=self.obrisi_kontakt).grid(row=0, column=2, padx=5)

        root.rowconfigure(1, weight=1)
        root.columnconfigure(0, weight=1)
        frame_lista.rowconfigure(0, weight=1)
        frame_lista.columnconfigure(0, weight=1)

        self.ucitaj_kontakte()

    def dodaj_kontakt(self):
        ime = self.entry_ime.get().strip()
        email = self.entry_email.get().strip()
        telefon = self.entry_telefon.get().strip()

        
        greske = []

        if len(ime) < 3:
            greske.append("Ime mora imati najmanje 3 znaka.")

        if not email.lower().endswith("@gmail.com"):
            greske.append("Email mora biti Gmail adresa (npr. korisnik@gmail.com).")

        if len(telefon) < 9 or len(telefon) > 10:
            greske.append("Broj telefona mora imati najmanje 9 i najviše 10 znakova.")

        
        if greske:
            for g in greske:
                print(g)
            return
        

        kontakt = Kontakt(ime, email, telefon)
        self.kontakti.append(kontakt)
        self.osvjezi_listbox()

        
        self.entry_ime.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_telefon.delete(0, tk.END)

    def osvjezi_listbox(self):
        self.listbox.delete(0, tk.END)
        for kontakt in self.kontakti:
            self.listbox.insert(tk.END, str(kontakt))

    def spremi_kontakte(self):
        with open("kontakti.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for k in self.kontakti:
                writer.writerow([k.ime, k.email, k.telefon])

    def ucitaj_kontakte(self):
        self.kontakti = []
        if not os.path.exists("kontakti.csv"):
            return

        try:
            with open("kontakti.csv", "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) == 3:
                        ime, email, telefon = row
                        self.kontakti.append(Kontakt(ime, email, telefon))
            self.osvjezi_listbox()
        except Exception:
            pass

    def obrisi_kontakt(self):
        selekcija = self.listbox.curselection()
        if not selekcija:
            return
        indeks = selekcija[0]
        self.kontakti.pop(indeks)
        self.osvjezi_listbox()


if __name__ == "__main__":
    root = tk.Tk()
    app = ImenikApp(root)
    root.mainloop()
