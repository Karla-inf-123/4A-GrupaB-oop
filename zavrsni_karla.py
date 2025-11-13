import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from collections import Counter
import csv


class AktivnostUcenja:
    def __init__(self, predmet, datum: date, trajanje, odradjeno=False):
        self.predmet = predmet
        self.datum = datum
        self.trajanje = trajanje
        self.odradjeno = odradjeno

    def opis(self):
        status = "✔" if self.odradjeno else ""
        return f"{self.predmet} - {self.datum} - {self.trajanje} min {status}"

    def to_xml(self):
        el = ET.Element('aktivnost', attrib={'type': 'bazna'})
        ET.SubElement(el, 'predmet').text = self.predmet
        ET.SubElement(el, 'datum').text = self.datum.isoformat()
        ET.SubElement(el, 'trajanje').text = str(self.trajanje)
        ET.SubElement(el, 'odradjeno').text = str(int(self.odradjeno))
        return el

    @classmethod
    def from_xml(cls, el):
        predmet = el.find('predmet').text or ''
        datum = date.fromisoformat(el.find('datum').text)
        trajanje = int(el.find('trajanje').text)
        odradjeno = bool(int(el.find('odradjeno').text or 0))
        return cls(predmet, datum, trajanje, odradjeno)


class TeorijskaSesija(AktivnostUcenja):
    def __init__(self, predmet, datum: date, trajanje, teme, odradjeno=False):
        super().__init__(predmet, datum, trajanje, odradjeno)
        self.teme = teme

    def opis(self):
        status = "✔" if self.odradjeno else ""
        return f"[Teorija] {self.predmet} - {self.datum} - {self.trajanje} min | Teme: {self.teme} {status}"

    def to_xml(self):
        el = ET.Element('aktivnost', attrib={'type': 'teorija'})
        ET.SubElement(el, 'predmet').text = self.predmet
        ET.SubElement(el, 'datum').text = self.datum.isoformat()
        ET.SubElement(el, 'trajanje').text = str(self.trajanje)
        ET.SubElement(el, 'teme').text = self.teme
        ET.SubElement(el, 'odradjeno').text = str(int(self.odradjeno))
        return el

    @classmethod
    def from_xml(cls, el):
        predmet = el.find('predmet').text or ''
        datum = date.fromisoformat(el.find('datum').text)
        trajanje = int(el.find('trajanje').text)
        teme = el.find('teme').text or ''
        odradjeno = bool(int(el.find('odradjeno').text or 0))
        return cls(predmet, datum, trajanje, teme, odradjeno)


class Vjezbe(AktivnostUcenja):
    def __init__(self, predmet, datum: date, trajanje, broj_zadataka, poteskoca, odradjeno=False):
        super().__init__(predmet, datum, trajanje, odradjeno)
        self.broj_zadataka = broj_zadataka
        self.poteskoca = poteskoca

    def opis(self):
        status = "✔" if self.odradjeno else ""
        return f"[Vježbe] {self.predmet} - {self.datum} - {self.trajanje} min | Zad.: {self.broj_zadataka} | Poteškoća: {self.poteskoca} {status}"

    def to_xml(self):
        el = ET.Element('aktivnost', attrib={'type': 'vjezbe'})
        ET.SubElement(el, 'predmet').text = self.predmet
        ET.SubElement(el, 'datum').text = self.datum.isoformat()
        ET.SubElement(el, 'trajanje').text = str(self.trajanje)
        ET.SubElement(el, 'broj_rjesenih').text = str(self.broj_zadataka)
        ET.SubElement(el, 'poteskoca').text = self.poteskoca
        ET.SubElement(el, 'odradjeno').text = str(int(self.odradjeno))
        return el

    @classmethod
    def from_xml(cls, el):
        predmet = el.find('predmet').text or ''
        datum = date.fromisoformat(el.find('datum').text)
        trajanje = int(el.find('trajanje').text)
        broj = int(el.find('broj_rjesenih').text or 0)
        pot = el.find('poteskoca').text or ''
        odradjeno = bool(int(el.find('odradjeno').text or 0))
        return cls(predmet, datum, trajanje, broj, pot, odradjeno)


class Dnevnik:
    def __init__(self):
        self.aktivnosti = []

    def dodaj(self, aktivnost):
        self.aktivnosti.append(aktivnost)

    def obrisi(self, indeks):
        if 0 <= indeks < len(self.aktivnosti):
            del self.aktivnosti[indeks]

    def spremi_xml(self, path):
        root = ET.Element('dnevnik')
        for a in self.aktivnosti:
            root.append(a.to_xml())
        ET.ElementTree(root).write(path, encoding='utf-8', xml_declaration=True)

    def ucitaj_xml(self, path):
        root = ET.parse(path).getroot()
        novi = []
        for el in root.findall('aktivnost'):
            t = el.get('type','bazna')
            if t=='teorija':
                obj = TeorijskaSesija.from_xml(el)
            elif t=='vjezbe':
                obj = Vjezbe.from_xml(el)
            else:
                obj = AktivnostUcenja.from_xml(el)
            novi.append(obj)
        self.aktivnosti = novi


class PlanerkoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('PLANERKO ♥ - Dnevnik učenja')
        self.configure(bg='#FDE8F2')
        self.geometry('950x650')
        self.dnevnik = Dnevnik()
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
        tk.Label(logo_frame, text='PLANERKO', font=('Arial', 34, 'bold'), bg='#FDE8F2', fg='#D85D9C').pack()
        tk.Label(logo_frame, text='Sve se može uz dobar plan ♥', font=('Arial', 13, 'italic'), bg='#FDE8F2', fg='#9C4B7D').pack(pady=(2,6))

        main_frame = tk.Frame(self, bg='#FDE8F2')
        main_frame.pack(padx=12, pady=6, fill='x')
        main_frame.columnconfigure(1, weight=1)

        tk.Label(main_frame, text='Tip aktivnosti:', bg='#FDE8F2').grid(row=0, column=0, sticky='w')
        self.tip_var = tk.StringVar(value='Teorija')
        ttk.Radiobutton(main_frame, text='Teorijska sesija', variable=self.tip_var, value='Teorija', command=self._promjena_tipa).grid(row=0, column=1, sticky='w')
        ttk.Radiobutton(main_frame, text='Vježbe', variable=self.tip_var, value='Vjezbe', command=self._promjena_tipa).grid(row=1, column=1, sticky='w')

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

        tk.Button(main_frame, text='Dodaj aktivnost', command=self.dodaj, bg='#D85D9C', fg='white').grid(row=6, column=0, columnspan=2, pady=6, sticky='ew')

        tk.Label(main_frame, text='Filtriraj po predmetu:', bg='#FDE8F2').grid(row=7, column=0, sticky='w', pady=(6,0))
        self.filter_entry = tk.Entry(main_frame)
        self.filter_entry.grid(row=7, column=1, sticky='ew', padx=(0,6))

        tk.Label(main_frame, text='Od datuma (YYYY-MM-DD):', bg='#FDE8F2').grid(row=8,column=0, sticky='w', pady=(6,0))
        self.od_datum_entry = tk.Entry(main_frame)
        self.od_datum_entry.grid(row=8,column=1, sticky='ew', padx=(0,6))
        tk.Label(main_frame, text='Do datuma (YYYY-MM-DD):', bg='#FDE8F2').grid(row=9,column=0, sticky='w', pady=(6,0))
        self.do_datum_entry = tk.Entry(main_frame)
        self.do_datum_entry.grid(row=9,column=1, sticky='ew', padx=(0,6))

        tk.Button(main_frame, text='Primijeni filter', command=self.primijeni_filter, bg='#D85D9C', fg='white').grid(row=10, column=0, columnspan=2, pady=6, sticky='ew')

        gumbi_frame = tk.Frame(main_frame, bg='#FDE8F2')
        gumbi_frame.grid(row=11, column=0, columnspan=2, pady=4, sticky='ew')
        tk.Button(gumbi_frame, text='Označi kao odrađeno', command=self.oznaci_odradeno, bg='#4CAF50', fg='white', width=18).pack(side='left', padx=2)
        tk.Button(gumbi_frame, text='Izbriši odabrano', command=self.brisi_odabrano, bg='#D85D9C', fg='white', width=18).pack(side='left', padx=2)
        tk.Button(gumbi_frame, text='Tjedni sažetak', command=self.tjedni_izvjestaj, bg='#D85D9C', fg='white', width=18).pack(side='left', padx=2)
        tk.Button(gumbi_frame, text='Mjesečni izvještaj', command=self.mjesecni_izvjestaj, bg='#D85D9C', fg='white', width=18).pack(side='left', padx=2)

        self.tree = ttk.Treeview(self, columns=('Datum','Predmet','Tip','Trajanje','Dodatno'), show='headings')
        for col in ('Datum','Predmet','Tip','Trajanje','Dodatno'):
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_by(c, False))
            self.tree.column(col, width=150)
        self.tree.pack(padx=12, pady=6, fill='both', expand=True)
        self.tree.bind("<Double-1>", self.uredi_stavku)

        self.status_var = tk.StringVar()
        tk.Label(self, textvariable=self.status_var, bd=1, relief='sunken', anchor='w', bg='#FDE8F2').pack(fill='x', side='bottom')


    def _promjena_tipa(self):
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()
        if self.tip_var.get()=='Teorija':
            tk.Label(self.dynamic_frame, text='Obrađene teme:', bg='#FDE8F2').grid(row=0,column=0, sticky='w')
            self.teme_entry = tk.Entry(self.dynamic_frame)
            self.teme_entry.grid(row=0,column=1, sticky='ew', padx=(4,0))
            self.dynamic_frame.columnconfigure(1, weight=1)
        else:
            tk.Label(self.dynamic_frame, text='Broj riješenih zadataka:', bg='#FDE8F2').grid(row=0,column=0, sticky='w')
            self.broj_entry = tk.Entry(self.dynamic_frame)
            self.broj_entry.grid(row=0,column=1, sticky='ew', padx=(4,0))
            tk.Label(self.dynamic_frame, text='Poteškoća:', bg='#FDE8F2').grid(row=1,column=0, sticky='w', pady=(6,0))
            self.poteskoca_entry = tk.Entry(self.dynamic_frame)
            self.poteskoca_entry.grid(row=1,column=1, sticky='ew', padx=(4,0))
            self.dynamic_frame.columnconfigure(1, weight=1)

    def dodaj(self):
        predmet = self.predmet_entry.get().strip()
        datum_str = self.datum_entry.get().strip()
        trajanje_str = self.trajanje_entry.get().strip()
        if not predmet or not datum_str or not trajanje_str:
            messagebox.showerror('Greška','Sva polja moraju biti popunjena')
            return
        try:
            datum = date.fromisoformat(datum_str)
        except:
            messagebox.showerror('Greška','Datum mora biti YYYY-MM-DD')
            return
        try:
            trajanje = int(trajanje_str)
            if trajanje<=0: raise ValueError
        except:
            messagebox.showerror('Greška','Trajanje mora biti pozitivan broj')
            return
        tip = self.tip_var.get()
        if tip=='Teorija':
            teme = self.teme_entry.get().strip()
            aktiv = TeorijskaSesija(predmet, datum, trajanje, teme)
        else:
            try:
                broj = int(self.broj_entry.get().strip())
                if broj<0: raise ValueError
            except:
                messagebox.showerror('Greška','Broj riješenih zadataka mora biti nenegativan cijeli broj')
                return
            pot = self.poteskoca_entry.get().strip()
            aktiv = Vjezbe(predmet, datum, trajanje, broj, pot)
        self.dnevnik.dodaj(aktiv)
        self._update_tree()
        self._status(f'Dodana aktivnost: {predmet}')

    def _update_tree(self, filter_predmet='', od_datum=None, do_datum=None):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for idx,a in enumerate(self.dnevnik.aktivnosti):
            if filter_predmet.lower() not in a.predmet.lower():
                continue
            if od_datum and a.datum<od_datum: continue
            if do_datum and a.datum>do_datum: continue
            tip = 'Teorija' if isinstance(a, TeorijskaSesija) else 'Vježbe' if isinstance(a,Vjezbe) else 'Bazna'
            dodatno = getattr(a,'teme', '') if tip=='Teorija' else f"{getattr(a,'broj_zadataka','')} zad. {getattr(a,'poteskoca','')}" if tip=='Vjezbe' else ''
            row = (a.datum.isoformat(), a.predmet, tip, a.trajanje, dodatno)
            iid = self.tree.insert('', 'end', values=row)
            if a.trajanje>=60:
                self.tree.item(iid, tags=('duboka',))
            if a.odradjeno:
                self.tree.item(iid, tags=('odradjeno',))
        self.tree.tag_configure('duboka', background='#FFDDDD')
        self.tree.tag_configure('odradjeno', background='#CCFFCC')

    def primijeni_filter(self):
        filter_predmet = self.filter_entry.get().strip()
        od = None
        do = None
        if self.od_datum_entry.get().strip():
            try: od = date.fromisoformat(self.od_datum_entry.get().strip())
            except: pass
        if self.do_datum_entry.get().strip():
            try: do = date.fromisoformat(self.do_datum_entry.get().strip())
            except: pass
        self._update_tree(filter_predmet, od, do)
        self._status('Filter primijenjen')

    def brisi_odabrano(self):
        sel = self.tree.selection()
        if not sel: return
        i = self.tree.index(sel[0])
        self.dnevnik.obrisi(i)
        self._update_tree()
        self._status('Odabrana aktivnost izbrisana')

    def oznaci_odradeno(self):
        sel = self.tree.selection()
        if not sel: return
        i = self.tree.index(sel[0])
        a = self.dnevnik.aktivnosti[i]
        a.odradjeno = True
        self._update_tree()
        self._status(f'Aktivnost "{a.predmet}" označena kao odrađena')

    def tjedni_izvjestaj(self):
        danas = date.today()
        tjedan = danas - timedelta(days=danas.weekday())
        aktivnosti = [a for a in self.dnevnik.aktivnosti if a.datum>=tjedan]
        if not aktivnosti:
            messagebox.showinfo('Tjedni izvještaj','Nema aktivnosti ovaj tjedan')
            return
        uk_traj = sum(a.trajanje for a in aktivnosti)
        predmeti = Counter(a.predmet for a in aktivnosti)
        naj = predmeti.most_common(1)[0][0] if predmeti else ''
        avg = uk_traj/len(aktivnosti)
        messagebox.showinfo('Tjedni izvještaj',f'Ukupno minuta: {uk_traj}\nNajčešći predmet: {naj}\nProsječno trajanje: {avg:.1f} min')

    def mjesecni_izvjestaj(self):
        danas = date.today()
        aktivnosti = [a for a in self.dnevnik.aktivnosti if a.datum.month==danas.month and a.datum.year==danas.year]
        if not aktivnosti:
            messagebox.showinfo('Mjesečni izvještaj','Nema aktivnosti ovaj mjesec')
            return
        uk_traj = sum(a.trajanje for a in aktivnosti)
        predmeti = Counter(a.predmet for a in aktivnosti)
        avg = uk_traj/len(aktivnosti)

        top = tk.Toplevel(self)
        top.title('Mjesečni izvještaj')
        tk.Label(top, text=f'Ukupno minuta: {uk_traj}').pack()
        tk.Label(top, text=f'Prosječno trajanje: {avg:.1f} min').pack()
        tk.Label(top, text='Broj aktivnosti po predmetu:').pack()
        tree = ttk.Treeview(top, columns=('Predmet','Broj'), show='headings')
        tree.heading('Predmet', text='Predmet')
        tree.heading('Broj', text='Broj aktivnosti')
        for p,c in predmeti.items():
            tree.insert('', 'end', values=(p,c))
        tree.pack(fill='both', expand=True)
        tk.Button(top, text='Spremi izvještaj (CSV)', command=lambda:self.export_csv(aktivnosti)).pack(pady=4)

    def export_csv(self, aktivnosti):
        path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV','*.csv')])
        if not path: return
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Datum','Predmet','Tip','Trajanje','Dodatno','Odradjeno'])
            for a in aktivnosti:
                tip = 'Teorija' if isinstance(a, TeorijskaSesija) else 'Vjezbe' if isinstance(a,Vjezbe) else 'Bazna'
                dodatno = getattr(a,'teme','') if tip=='Teorija' else f"{getattr(a,'broj_zadataka','')} zad. {getattr(a,'poteskoca','')}" if tip=='Vjezbe' else ''
                writer.writerow([a.datum.isoformat(), a.predmet, tip, a.trajanje, dodatno, '✔' if a.odradjeno else ''])
        self._status(f'Izvještaj spremljen u {path}')

    def spremi_xml(self):
        path = filedialog.asksaveasfilename(defaultextension='.xml', filetypes=[('XML','*.xml')])
        if path: self.dnevnik.spremi_xml(path); self._status('Spremljeno')

    def ucitaj_xml(self):
        path = filedialog.askopenfilename(filetypes=[('XML','*.xml')])
        if path: self.dnevnik.ucitaj_xml(path); self._update_tree(); self._status('Učitano')

    def o_aplikaciji(self):
        messagebox.showinfo('O aplikaciji','PLANERKO ♥ - Dnevnik učenja\nVerzija 4.0')

    def _status(self,msg):
        self.status_var.set(msg)

    def sort_by(self, col, reverse):
        data = [(self.tree.set(k,col), k) for k in self.tree.get_children('')]
        if col in ['Datum','Trajanje']:
            data.sort(key=lambda t: date.fromisoformat(t[0]) if col=='Datum' else int(t[0]), reverse=reverse)
        else:
            data.sort(reverse=reverse)
        for index, (val,k) in enumerate(data):
            self.tree.move(k,'',index)
        self.tree.heading(col, command=lambda: self.sort_by(col, not reverse))

    def uredi_stavku(self, event):
        sel = self.tree.selection()
        if not sel: return
        i = self.tree.index(sel[0])
        a = self.dnevnik.aktivnosti[i]
        top = tk.Toplevel(self)
        top.title('Uredi aktivnost')
        tk.Label(top, text='Predmet:').grid(row=0,column=0)
        predmet_e = tk.Entry(top); predmet_e.grid(row=0,column=1); predmet_e.insert(0,a.predmet)
        tk.Label(top, text='Datum:').grid(row=1,column=0)
        datum_e = tk.Entry(top); datum_e.grid(row=1,column=1); datum_e.insert(0,a.datum.isoformat())
        tk.Label(top, text='Trajanje:').grid(row=2,column=0)
        trajanje_e = tk.Entry(top); trajanje_e.grid(row=2,column=1); trajanje_e.insert(0,str(a.trajanje))
        if isinstance(a,TeorijskaSesija):
            tk.Label(top, text='Teme:').grid(row=3,column=0)
            teme_e = tk.Entry(top); teme_e.grid(row=3,column=1); teme_e.insert(0,a.teme)
        elif isinstance(a,Vjezbe):
            tk.Label(top, text='Broj zadataka:').grid(row=3,column=0)
            broj_e = tk.Entry(top); broj_e.grid(row=3,column=1); broj_e.insert(0,str(a.broj_zadataka))
            tk.Label(top, text='Poteškoća:').grid(row=4,column=0)
            pot_e = tk.Entry(top); pot_e.grid(row=4,column=1); pot_e.insert(0,a.poteskoca)
        def spremi():
            a.predmet = predmet_e.get().strip()
            try: a.datum = date.fromisoformat(datum_e.get().strip())
            except: return
            try: a.trajanje = int(trajanje_e.get().strip())
            except: return
            if isinstance(a,TeorijskaSesija):
                a.teme = teme_e.get().strip()
            elif isinstance(a,Vjezbe):
                try: a.broj_zadataka = int(broj_e.get().strip())
                except: a.broj_zadataka = 0
                a.poteskoca = pot_e.get().strip()
            self._update_tree()
            top.destroy()
            self._status('Aktivnost uređena')
        tk.Button(top, text='Spremi', command=spremi, bg='#D85D9C', fg='white').grid(row=5,column=0,columnspan=2,pady=4)


if __name__=='__main__':
    app = PlanerkoApp()
    app.mainloop()
