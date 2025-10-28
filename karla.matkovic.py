

#1.Koristimo trajnu pohranu poput datoteka jer se podaci u RAM-u brišu kada se računalo ugasi, dok datoteke ostaju sačuvane i nakon isključivanja.
#2.CSV je jednostavan format u kojem su podaci odvojeni zarezima, dok XML koristi oznake (tagove) za opis strukture podataka i zato je složeniji.
#3.Konstrukcija `with open(...) as f:` automatski zatvara datoteku nakon što se završi s radom, što je sigurnije i praktičnije od ručnog zatvaranja jer sprječava moguće greške.
#4.Listbox treba očistiti prije učitavanja novih podataka kako se stari podaci ne bi pomiješali s novima i kako bi prikaz bio točan.
#5.Prednost csv.DictWriter i DictReader je u tome što omogućuju rad s podacima pomoću imena stupaca, što je jasnije i lakše nego ručno razdvajanje podataka pomoću split(',').

import tkinter as tk
from tkinter import messagebox
import csv
import xml.etree.ElementTree as ET


class Ucenik:
    def __init__(self, ime, prezime, razred):
        self.ime = ime
        self.prezime = prezime
        self.razred = razred

    def __str__(self):
        return f"{self.ime} {self.prezime} ({self.razred})"


class EvidencijaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Evidencija učenika – provjera")
        self.root.geometry("600x400")
        self.root.configure(bg="#f0f0f0")  

        self.font = ("Arial", 11)          
        self.btn_font = ("Arial", 10, "bold")  

        self.ucenici = []
        self.kreiraj_gui()

    def kreiraj_gui(self):
        unos = tk.Frame(self.root, padx=10, pady=10, bg="#f0f0f0")
        unos.grid(row=0, column=0, sticky="EW")
        unos.columnconfigure(1, weight=1)

        tk.Label(unos, text="Ime:", bg="#f0f0f0", font=self.font).grid(row=0, column=0, sticky="W")
        self.e_ime = tk.Entry(unos, font=self.font)
        self.e_ime.grid(row=0, column=1, sticky="EW")

        tk.Label(unos, text="Prezime:", bg="#f0f0f0", font=self.font).grid(row=1, column=0, sticky="W")
        self.e_prezime = tk.Entry(unos, font=self.font)
        self.e_prezime.grid(row=1, column=1, sticky="EW")

        tk.Label(unos, text="Razred:", bg="#f0f0f0", font=self.font).grid(row=2, column=0, sticky="W")
        self.e_razred = tk.Entry(unos, font=self.font)
        self.e_razred.grid(row=2, column=1, sticky="EW")

        gumbi = tk.Frame(unos, bg="#f0f0f0")
        gumbi.grid(row=3, column=0, columnspan=2, pady=8)

        
        def stil_gumba(parent, text, command, bg, fg="white"):
            return tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                             font=self.btn_font, padx=6, pady=4)

        stil_gumba(gumbi, "Dodaj učenika", self.dodaj_ucenika, "#2563eb").pack(side="left", padx=4)
        stil_gumba(gumbi, "Spremi CSV", self.spremi_u_csv, "#059669").pack(side="left", padx=4)
        stil_gumba(gumbi, "Učitaj CSV", self.ucitaj_iz_csv, "#f59e0b").pack(side="left", padx=4)
        stil_gumba(gumbi, "Spremi XML", self.spremi_u_xml, "#6b21a8").pack(side="left", padx=4)
        stil_gumba(gumbi, "Učitaj XML", self.ucitaj_iz_xml, "#db2777").pack(side="left", padx=4)

        prikaz = tk.Frame(self.root, padx=10, pady=10, bg="#f0f0f0")
        prikaz.grid(row=1, column=0, sticky="NSEW")
        prikaz.columnconfigure(0, weight=1)
        prikaz.rowconfigure(0, weight=1)

        self.lb = tk.Listbox(prikaz, font=self.font)
        self.lb.grid(row=0, column=0, sticky="NSEW")

        sc = tk.Scrollbar(prikaz, orient="vertical", command=self.lb.yview)
        sc.grid(row=0, column=1, sticky="NS")
        self.lb.configure(yscrollcommand=sc.set)

    
    def osvjezi(self):
        self.lb.delete(0, tk.END)
        for u in self.ucenici:
            self.lb.insert(tk.END, str(u))

    def ocisti_unos(self):
        self.e_ime.delete(0, tk.END)
        self.e_prezime.delete(0, tk.END)
        self.e_razred.delete(0, tk.END)

    
    def dodaj_ucenika(self):
        ime = self.e_ime.get().strip()
        prezime = self.e_prezime.get().strip()
        razred = self.e_razred.get().strip()
        if not (ime and prezime and razred):
            messagebox.showwarning("Upozorenje", "Sva polja moraju biti popunjena.")
            return
        self.ucenici.append(Ucenik(ime, prezime, razred))
        self.osvjezi()
        self.ocisti_unos()

    def spremi_u_csv(self):
        try:
            with open("ucenici.csv", "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=["ime", "prezime", "razred"])
                writer.writeheader()
                for u in self.ucenici:
                    writer.writerow({"ime": u.ime, "prezime": u.prezime, "razred": u.razred})
            messagebox.showinfo("Info", "Podaci su spremljeni u ucenici.csv")
        except Exception as e:
            messagebox.showerror("Greška", f"Nije moguće spremiti CSV: {e}")

    def ucitaj_iz_csv(self):
        try:
            self.ucenici.clear()
            self.lb.delete(0, tk.END)
            with open("ucenici.csv", "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.ucenici.append(Ucenik(row["ime"], row["prezime"], row["razred"]))
            self.osvjezi()
            messagebox.showinfo("Info", "Podaci su učitani iz ucenici.csv")
        except FileNotFoundError:
            messagebox.showwarning("Upozorenje", "Datoteka ucenici.csv ne postoji.")
        except Exception as e:
            messagebox.showerror("Greška", f"Nije moguće učitati CSV: {e}")

    def spremi_u_xml(self):
        try:
            root = ET.Element("evidencija")
            for u in self.ucenici:
                e = ET.SubElement(root, "ucenik")
                ET.SubElement(e, "ime").text = u.ime
                ET.SubElement(e, "prezime").text = u.prezime
                ET.SubElement(e, "razred").text = u.razred
            tree = ET.ElementTree(root)
            tree.write("ucenici.xml", encoding="utf-8", xml_declaration=True)
            messagebox.showinfo("Info", "XML spremljen u ucenici.xml")
        except Exception as e:
            messagebox.showerror("Greška", f"Nije moguće spremiti XML: {e}")

    def ucitaj_iz_xml(self):
        try:
            self.ucenici.clear()
            self.lb.delete(0, tk.END)
            tree = ET.parse("ucenici.xml")
            root = tree.getroot()
            for e in root.findall("ucenik"):
                ime = e.findtext("ime", "")
                prezime = e.findtext("prezime", "")
                razred = e.findtext("razred", "")
                if ime and prezime and razred:
                    self.ucenici.append(Ucenik(ime, prezime, razred))
            self.osvjezi()
            messagebox.showinfo("Info", "XML učitan iz ucenici.xml")
        except FileNotFoundError:
            messagebox.showwarning("Upozorenje", "Datoteka ucenici.xml ne postoji.")
        except Exception as e:
            messagebox.showerror("Greška", f"Nije moguće učitati XML: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = EvidencijaApp(root)
    root.mainloop()
