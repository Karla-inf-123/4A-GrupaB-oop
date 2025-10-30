class Zaposlenik:
    def __init__(self, ime, prezime, placa):
        self.ime = ime
        self.prezime = prezime
        self.placa = placa

    def prikazi_info(self):
        print(f"Ime i prezime: {self.ime} {self.prezime}, Plaća: {self.placa} EUR")



class Programer(Zaposlenik):
    def __init__(self, ime, prezime, placa, programski_jezici):
        super().__init__(ime, prezime, placa)
        self.programski_jezici = programski_jezici

    def prikazi_info(self):
        super().prikazi_info()
        print(f"Programski jezici: {', '.join(self.programski_jezici)}")



class Menadzer(Zaposlenik):
    def __init__(self, ime, prezime, placa, tim):
        super().__init__(ime, prezime, placa)
        self.tim = tim

    def prikazi_info(self):
        super().prikazi_info()
        print("Članovi tima:", ", ".join(self.tim))

    
    def dodaj_clana_tima(self, novi_clan):
        self.tim.append(novi_clan)
        print(f" Novi član '{novi_clan}' dodan u tim.")




if __name__ == "__main__":
    
    z1 = Zaposlenik("Ana", "Anić", 1200)
    p1 = Programer("Petar", "Perić", 1800, ["Python", "JavaScript"])
    m1 = Menadzer("Iva", "Ivić", 2500, ["Ana Anić", "Petar Perić"])

    
    print("--- Podaci o zaposleniku ---")
    z1.prikazi_info()

    print("\n--- Podaci o programeru ---")
    p1.prikazi_info()

    print("\n--- Podaci o menadžeru ---")
    m1.prikazi_info()

    
    print("\n--- Dodavanje novog člana tima ---")
    m1.dodaj_clana_tima("Marko Markić")
    m1.prikazi_info()

