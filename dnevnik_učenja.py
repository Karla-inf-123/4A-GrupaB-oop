import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import xml.etree.ElementTree as ET
from datetime import date, timedelta

class AktivnostUcenja:
    def __init__(self, predmet, datum, trajanje):
        self.predmet = predmet
        self.datum = datum
        self.trajanje = trajanje

    def opis(self):
        return f"{self.predmet} - {self.datum} - {self.trajanje} min"

    def to_xml(self):
        el = ET.Element('aktivnost', attrib={'type': 'bazna'})
        ET.SubElement(el, 'predmet').text = self.predmet
        ET.SubElement(el, 'datum').text = self.datum
        ET.SubElement(el, 'trajanje').text = str(self.trajanje)
        return el

class TeorijskaSesija(AktivnostUcenja):
    def __init__(self, predmet, datum, trajanje, teme):
        super().__init__(predmet, datum, trajanje)
        self.teme = teme

    def opis(self):
        return f"[Teorija] {self.predmet} - {self.datum} - {self.trajanje} min | Teme: {self.teme}"

    def to_xml(self):
        el = ET.Element('aktivnost', attrib={'type': 'teorija'})
        ET.SubElement(el, 'predmet').text = self.predmet
        ET.SubElement(el, 'datum').text = self.datum
        ET.SubElement(el, 'trajanje').text = str(self.trajanje)
        ET.SubElement(el, 'teme').text = self.teme
        return el

class Vjezbe(AktivnostUcenja):
    def __init__(self, predmet, datum, trajanje, broj_zadataka, poteskoca):
        super().__init__(predmet, datum, trajanje)
        self.broj_zadataka = broj_zadataka
        self.poteskoca = poteskoca

    def opis(self):
        return (f"[Vježbe] {self.predmet} - {self.datum} - {self.trajanje} min | "
                f"Broj riješenih: {self.broj_zadataka} | Poteškoća: {self.poteskoca}")

    def to_xml(self):
        el = ET.Element('aktivnost', attrib={'type': 'vjezbe'})
        ET.SubElement(el, 'predmet').text = self.predmet
        ET.SubElement(el, 'datum').text = self.datum
        ET.SubElement(el, 'trajanje').text = str(self.trajanje)
        ET.SubElement(el, 'broj_rjesenih').text = str(self.broj_zadataka)
        ET.SubElement(el, 'poteskoca').text = self.poteskoca
        return el

class PlanerkoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('PLANERKO ♥ - Dnevnik učenja v1.0')
        self.configure(bg='#FDE8F2')
        self.geometry('760x620')
        self.aktivnosti = []
        self._kreiraj_meni()
        self._kreiraj_ui()
        self._status('Spremno')

    def _kreiraj_meni(self):
        menubar = tk.Menu(self)
        filem = tk.Menu(menubar, tearoff=0)
        filem.add_command(label='Spremi', command=self.spremi_xml)
        filem.add_command(label='Učitaj', command=self.ucitaj_xml)
        filem.add_separator()
        filem.add_command(label='Izlaz', command=self.quit)
        menubar.add_cascade(label='Datoteka', menu=filem)
        helpm = tk.Menu(menubar, tearoff=0)
        helpm.add_command(label='O aplikaciji', command=self.o_aplikaciji)
        menubar.add_cascade(label='Pomoć', menu=helpm)
        self.config(menu=menubar)

    def _kreiraj_ui(self):
        logo_frame = tk.Frame(self, bg='#FDE8F2')
        logo_frame.pack(pady=8)
        tk.Label(logo_frame, text='PLANERKO', font=('Arial', 34, 'bold'),
                 bg='#FDE8F2', fg='#D85D9C').pack()
        tk.Label(logo_frame, text='Sve se može uz dobar plan ♥', font=('Arial', 13, 'italic'),
                 bg='#FDE8F2', fg='#9C4B7D').pack(pady=(2,6))
        main_frame = tk.Frame(self, bg='#FDE8F2')
        main_frame.pack(padx=12, pady=6, fill='x')
        main_frame.columnconfigure(1, weight=1)
        tk.Label(main_frame, text='Tip aktivnosti:', bg='#FDE8F2').grid(row=0, column=0, sticky='w')
        self.tip_var = tk.StringVar(value='Teorija')
        ttk.Radiobutton(main_frame, text='Teorijska sesija', variable=self.tip_var, value='Teorija',
                        command=self._promjena_tipa).grid(row=0, column=1, sticky='w')
        ttk.Radiobutton(main_frame, text='Vježbe', variable=self.tip_var, value='Vjezbe',
                        command=self._promjena_tipa).grid(row=1, column=1, sticky='w')
        tk.Label(main_frame, text='Predmet:', bg='#FDE8F2').grid(row=2, column=0, sticky='w', pady=(6,0))
        self.predmet_entry = tk.Entry(main_frame)
        self.predmet_entry.grid(row=2, column=1, sticky='ew', padx=(0,6))
        tk.Label(main_frame, text='Datum (YYYY-MM-DD):', bg='#FDE8F2').grid(row=3, column=0, sticky='w', pady=(6,0))
        self.datum_entry = tk.Entry(main_frame)
        self.datum_entry.insert(0, date.today().isoformat())
        self.datum_entry.grid(row=3, column=1, sticky='ew', padx=(0,6))
        tk.Label(main_frame, text='Trajanje (min):', bg='#FDE8F2').grid(row=4, column=0, sticky='w', pady=(6,0))
        self.trajanje_entry = tk.Entry(main_frame)
        self.trajanje_entry.grid(row=4, column=1, sticky='ew', padx=(0,6))
        self.dynamic_frame = tk.Frame(main_frame, bg='#FDE8F2')
        self.dynamic_frame.grid(row=5, column=0, columnspan=2, pady=8, sticky='ew')
        self._promjena_tipa()
        tk.Button(main_frame, text='Dodaj aktivnost', command=self.dodaj, bg='#D85D9C', fg='white').grid(
            row=6, column=0, columnspan=2, pady=6, sticky='ew')
        tk.Label(main_frame, text='Filtriraj po predmetu:', bg='#FDE8F2').grid(row=7, column=0, sticky='w', pady=(6,0))
        self.filter_entry = tk.Entry(main_frame)
        self.filter_entry.grid(row=7, column=1, sticky='ew', padx=(0,6))
        tk.Button(main_frame, text='Primijeni filter', command=self.primijeni_filter, bg='#D85D9C', fg='white').grid(
            row=8, column=0, columnspan=2, pady=6, sticky='ew')
        tk.Button(main_frame, text='Tjedni sažetak', command=self.tjedni_sazetak, bg='#D85D9C', fg='white').grid(
            row=9, column=0, columnspan=2, pady=(0,8), sticky='ew')
        self.listbox = tk.Listbox(self)
        self.listbox.pack(padx=12, pady=6, fill='both', expand=True)
        self.status_var = tk.StringVar()
        tk.Label(self, textvariable=self.status_var, bd=1, relief='sunken', anchor='w', bg='#FDE8F2').pack(fill='x', side='bottom')

    def _promjena_tipa(self):
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()
        if self.tip_var.get() == 'Teorija':
            tk.Label(self.dynamic_frame, text='Obrađene teme:', bg='#FDE8F2').grid(row=0, column=0, sticky='w')
            self.teme_entry = tk.Entry(self.dynamic_frame)
            self.teme_entry.grid(row=0, column=1, sticky='ew', padx=(4,0))
            self.dynamic_frame.columnconfigure(1, weight=1)
        else:
            tk.Label(self.dynamic_frame, text='Broj riješenih zadataka:', bg='#FDE8F2').grid(row=0, column=0, sticky='w')
            self.broj_entry = tk.Entry(self.dynamic_frame)
            self.broj_entry.grid(row=0, column=1, sticky='ew', padx=(4,0))
            tk.Label(self.dynamic_frame, text='Poteškoća:', bg='#FDE8F2').grid(row=1, column=0, sticky='w', pady=(6,0))
            self.poteskoca_entry = tk.Entry(self.dynamic_frame)
            self.poteskoca_entry.grid(row=1, column=1, sticky='ew', padx=(4,0))
            self.dynamic_frame.columnconfigure(1, weight=1)

    def dodaj(self):
        predmet = self.predmet_entry.get().strip()
        datum = self.datum_entry.get().strip()
        trajanje = self.trajanje_entry.get().strip()
        if not predmet or not datum or not trajanje:
            messagebox.showerror('Greška', 'Sva polja moraju biti popunjena')
            return
        try:
            _ = date.fromisoformat(datum)
        except Exception:
            messagebox.showerror('Greška', 'Datum mora biti u formatu YYYY-MM-DD')
            return
        try:
            trajanje = int(trajanje)
            if trajanje <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror('Greška', 'Trajanje mora biti pozitivan cijeli broj (minuta)')
            return
        tip = self.tip_var.get()
        if tip == 'Teorija':
            teme = self.teme_entry.get().strip()
            aktiv = TeorijskaSesija(predmet, datum, trajanje, teme)
        else:
            try:
                broj = int(self.broj_entry.get().strip())
                if broj < 0:
                    raise ValueError
            except Exception:
                messagebox.showerror('Greška', 'Broj riješenih zadataka mora biti nenegativan cijeli broj')
                return
            pot = self.poteskoca_entry.get().strip()
            aktiv = Vjezbe(predmet, datum, trajanje, broj, pot)
        self.aktivnosti.append(aktiv)
        self._update_listbox()
        self._status(f'Dodana aktivnost: {aktiv.predmet}')

    def _update_listbox(self, filter_text=''):
        self.listbox.delete(0, tk.END)
        for a in self.aktivnosti:
            if filter_text.lower() in a.predmet.lower():
                self.listbox.insert(tk.END, a.opis())

    def primijeni_filter(self):
        tekst = self.filter_entry.get().strip()
        self._update_listbox(tekst)
        self._status(f'Filter primijenjen: \"{tekst}\"')

    def tjedni_sazetak(self):
        danas = date.today()
        start = danas - timedelta(days=danas.weekday())
        end = start + timedelta(days=6)
        ukupno = 0
        count = 0
        for a in self.aktivnosti:
            try:
                adatum = date.fromisoformat(a.datum)
            except Exception:
                continue
            if start <= adatum <= end:
                ukupno += a.trajanje
                count += 1
        messagebox.showinfo('Tjedni sažetak',
                            f'Tjedni sažetak ({start} - {end})\nUkupno aktivnosti: {count}\nUkupno vremena: {ukupno} minuta')
        self._status('Prikazan tjedni sažetak')

    def spremi_xml(self):
        if not self.aktivnosti:
            messagebox.showinfo('Info', 'Nema aktivnosti za spremiti')
            return
        path = filedialog.asksaveasfilename(defaultextension='.xml', filetypes=[('XML', '*.xml')])
        if not path:
            return
        root = ET.Element('dnevnik')
        for a in self.aktivnosti:
            root.append(a.to_xml())
        tree = ET.ElementTree(root)
        try:
            tree.write(path, encoding='utf-8', xml_declaration=True)
            self._status(f'Spremljeno u {path}')
        except Exception as e:
            messagebox.showerror('Greška', f'Neuspjelo spremanje: {e}')

    def ucitaj_xml(self):
        path = filedialog.askopenfilename(filetypes=[('XML', '*.xml')])
        if not path:
            return
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            novi = []
            for el in root.findall('aktivnost'):
                predmet_el = el.find('predmet')
                datum_el = el.find('datum')
                traj_el = el.find('trajanje')
                if predmet_el is None or datum_el is None or traj_el is None:
                    continue
                predmet = predmet_el.text or ''
                datum = datum_el.text or ''
                try:
                    trajanje = int(traj_el.text)
                except Exception:
                    continue
                t = el.get('type', 'bazna')
                if t == 'teorija':
                    teme = el.find('teme').text if el.find('teme') is not None else ''
                    obj = TeorijskaSesija(predmet, datum, trajanje, teme)
                elif t == 'vjezbe':
                    broj = 0
                    if el.find('broj_rjesenih') is not None:
                        try:
                            broj = int(el.find('broj_rjesenih').text)
                        except Exception:
                            broj = 0
                    pot = el.find('poteskoca').text if el.find('poteskoca') is not None else ''
                    obj = Vjezbe(predmet, datum, trajanje, broj, pot)
                else:
                    obj = AktivnostUcenja(predmet, datum, trajanje)
                novi.append(obj)
            self.aktivnosti = novi
            self._update_listbox()
            self._status(f'Učitano {len(self.aktivnosti)} aktivnosti')
        except Exception as e:
            messagebox.showerror('Greška pri učitavanju', f'Neuspjelo učitavanje: {e}')

    def o_aplikaciji(self):
        top = tk.Toplevel(self)
        top.title('O aplikaciji')
        tk.Label(top, text='PLANERKO', font=('Arial', 20, 'bold')).pack(padx=12, pady=(10,4))
        tk.Label(top, text='Dnevnik učenja v1.0\nAutor: Učenik', justify='center').pack(padx=12, pady=(0,10))
        tk.Button(top, text='Zatvori', command=top.destroy).pack(pady=(0,12))

    def _status(self, tekst):
        self.status_var.set(tekst)

if __name__ == '__main__':
    app = PlanerkoApp()
    app.mainloop()
