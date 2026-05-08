import sqlite3
from datetime import date
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

# ==========================================================
# 1. BAZA PODATAKA (Nexus OS - Centralna pohrana)
# ==========================================================
class Database:
    def __init__(self):
        self.conn = sqlite3.connect("nexus_final_v12.db")
        self.c = self.conn.cursor()
        self.init_db()

    def init_db(self):
        # Tablica pacijenata
        self.c.execute("CREATE TABLE IF NOT EXISTS Pacijent(id INTEGER PRIMARY KEY, ime TEXT, prezime TEXT, dob INTEGER, spol TEXT, email TEXT)")
        
        # Tablica nalaza (Analiza)
        self.c.execute("""CREATE TABLE IF NOT EXISTS MedicinskiNalaz(
            id INTEGER PRIMARY KEY, pacijent_id INTEGER, datum TEXT, 
            glukoza REAL, leukociti REAL, hemoglobin REAL, kolesterol REAL,
            tlak_sistolicki INTEGER, tlak_dijastolicki INTEGER,
            FOREIGN KEY(pacijent_id) REFERENCES Pacijent(id))""")
        
        # Tablica narudžbi (Naručivanje)
        self.c.execute("""CREATE TABLE IF NOT EXISTS appointments(
            id INTEGER PRIMARY KEY, patient_id INTEGER, specijalist TEXT,
            datum_termina TEXT, vrijeme TEXT, napomena TEXT,
            FOREIGN KEY(patient_id) REFERENCES Pacijent(id))""")
        self.conn.commit()

    def get_patients(self):
        return self.c.execute("SELECT * FROM Pacijent").fetchall()

    def get_history(self, pid):
        return self.c.execute("SELECT datum, glukoza, leukociti, hemoglobin, kolesterol, tlak_sistolicki, tlak_dijastolicki FROM MedicinskiNalaz WHERE pacijent_id=?", (pid,)).fetchall()

    def get_appointments(self, pid):
        return self.c.execute("SELECT specijalist, datum_termina, vrijeme, napomena FROM appointments WHERE patient_id=? ORDER BY datum_termina ASC", (pid,)).fetchall()

# ==========================================================
# 2. GLAVNA APLIKACIJA (GUI)
# ==========================================================
class NexusApp:
    def __init__(self):
        self.db = Database()
        self.root = tk.Tk()
        self.root.title("NEXUS OS - Upravljanje Bazom Podataka")
        self.root.geometry("1100x850")
        
        style = ttk.Style()
        style.configure("TNotebook.Tab", padding=[20, 5])
        
        self.main_gui()

    def main_gui(self):
        for w in self.root.winfo_children(): w.destroy()
        self.nb = ttk.Notebook(self.root)
        self.tab1 = ttk.Frame(self.nb)
        self.tab2 = ttk.Frame(self.nb)
        self.tab3 = ttk.Frame(self.nb)
        
        self.nb.add(self.tab1, text=" Upis pacijenata ")
        self.nb.add(self.tab2, text=" Analiza i Nalazi ")
        self.nb.add(self.tab3, text=" Naručivanje ")
        self.nb.pack(expand=True, fill="both")
        
        self.setup_t1()
        self.setup_t2()
        self.setup_t3()

    # --- KARTICA 1: UPIS PACIJENATA (Spremanje u bazu) ---
    def setup_t1(self):
        f = tk.Frame(self.tab1, padx=20, pady=20)
        f.pack(side="left", fill="y")
        self.ins = {}
        for l in ["Ime", "Prezime", "Dob", "Spol", "Email"]:
            tk.Label(f, text=l).pack(anchor="w")
            e = ttk.Entry(f); e.pack(fill="x", pady=5); self.ins[l] = e
        
        # GUMB SPREMI ZA PACIJENTA
        ttk.Button(f, text="SPREMI PACIJENTA", command=self.save_patient_to_db).pack(pady=20, fill="x")

    def save_patient_to_db(self):
        try:
            self.db.c.execute("INSERT INTO Pacijent(ime, prezime, dob, spol, email) VALUES(?,?,?,?,?)", 
                             (self.ins["Ime"].get(), self.ins["Prezime"].get(), self.ins["Dob"].get(), self.ins["Spol"].get(), self.ins["Email"].get()))
            self.db.conn.commit()
            messagebox.showinfo("Nexus OS", "Pacijent spremljen u bazu!")
            self.main_gui() # Osvježi sve liste i comboboxove
        except Exception as e:
            messagebox.showerror("Greška", f"Neuspješno spremanje: {e}")

    # --- KARTICA 2: ANALIZA I NALAZI (Spremanje i prikaz) ---
    def setup_t2(self):
        side = tk.Frame(self.tab2, width=250, bg="#f0f0f0", padx=10); side.pack(side="left", fill="y")
        tk.Label(side, text="Popis pacijenata:", bg="#f0f0f0", font=("Arial", 10, "bold")).pack(pady=5)
        
        self.p_list = tk.Listbox(side)
        self.p_list.pack(fill="both", expand=True, pady=5)
        for p in self.db.get_patients():
            self.p_list.insert("end", f"{p[0]}: {p[1]} {p[2]}")
        
        self.p_list.bind('<<ListboxSelect>>', lambda e: self.show_analysis_results())
        
        # GUMB SPREMI PLUS (DODAVANJE NALAZA)
        ttk.Button(side, text="SPREMI NALAZ (+)", command=self.add_medical_report).pack(fill="x", pady=10)
        
        self.res_area = tk.Frame(self.tab2, padx=10, pady=10); self.res_area.pack(side="right", fill="both", expand=True)
        self.txt_output = tk.Text(self.res_area, font=("Consolas", 10))
        self.txt_output.pack(fill="both", expand=True)

    def add_medical_report(self):
        sel = self.p_list.curselection()
        if not sel:
            messagebox.showwarning("!", "Odaberite pacijenta s liste!")
            return
        pid = self.p_list.get(sel[0]).split(":")[0]
        
        try:
            g = simpledialog.askstring("Nalaz", "Glukoza:"); l = simpledialog.askstring("Nalaz", "Leukociti:")
            h = simpledialog.askstring("Nalaz", "Hemoglobin:"); k = simpledialog.askstring("Nalaz", "Kolesterol:")
            ts = simpledialog.askstring("Nalaz", "Tlak (Sistolički):"); td = simpledialog.askstring("Nalaz", "Tlak (Dijastolički):")
            
            if None in [g, l, h, k, ts, td]: return # Ako se stisne Cancel

            self.db.c.execute("INSERT INTO MedicinskiNalaz VALUES(NULL,?,?,?,?,?,?,?,?)", 
                             (pid, str(date.today()), float(g), float(l), float(h), float(k), int(ts), int(td)))
            self.db.conn.commit()
            messagebox.showinfo("Nexus OS", "Nalaz uspješno spremljen u bazu podataka!")
            self.show_analysis_results()
        except Exception as e:
            messagebox.showerror("Greška", "Provjerite jeste li unijeli brojeve!")

    def show_analysis_results(self):
        sel = self.p_list.curselection()
        if not sel: return
        pid = self.p_list.get(sel[0]).split(":")[0]
        
        history = self.db.get_history(pid)
        self.txt_output.delete("1.0", "end")
        self.txt_output.insert("end", f"{'DATUM':<12} | {'GLU':<5} | {'LEU':<5} | {'HEM':<5} | {'KOL':<5} | {'TLAK':<8}\n")
        self.txt_output.insert("end", "-"*65 + "\n")
        
        for h in history:
            tlak = f"{h[5]}/{h[6]}"
            self.txt_output.insert("end", f"{h[0]:<12} | {h[1]:<5} | {h[2]:<5} | {h[3]:<5} | {h[4]:<5} | {tlak:<8}\n")

    # --- KARTICA 3: NARUČIVANJE (Spremanje i prikaz termina) ---
    def setup_t3(self):
        f_left = tk.Frame(self.tab3, width=300, bg="#e8f5e9", padx=20, pady=20); f_left.pack(side="left", fill="y")
        
        tk.Label(f_left, text="ODABERI PACIJENTA:", bg="#e8f5e9").pack(anchor="w")
        pts = [f"{p[0]}: {p[1]} {p[2]}" for p in self.db.get_patients()]
        self.cb_p_appoint = ttk.Combobox(f_left, values=pts, state="readonly")
        self.cb_p_appoint.pack(fill="x", pady=5)
        self.cb_p_appoint.bind("<<ComboboxSelected>>", lambda e: self.show_appointments_list())
        
        tk.Label(f_left, text="SPECIJALIST:", bg="#e8f5e9").pack(anchor="w")
        self.cb_spec = ttk.Combobox(f_left, values=["Opća praksa", "Kardiolog", "Endokrinolog", "Laboratorij"], state="readonly")
        self.cb_spec.pack(fill="x", pady=5); self.cb_spec.current(0)
        
        tk.Label(f_left, text="DATUM (DD.MM.YYYY):", bg="#e8f5e9").pack(anchor="w")
        self.ent_datum = ttk.Entry(f_left); self.ent_datum.pack(fill="x", pady=5)
        self.ent_datum.insert(0, date.today().strftime("%d.%m.%Y"))
        
        tk.Label(f_left, text="NAPOMENA:", bg="#e8f5e9").pack(anchor="w")
        self.ent_napomena = ttk.Entry(f_left); self.ent_napomena.pack(fill="x", pady=5)
        
        # GUMB SPREMI ZA NARUDŽBU
        ttk.Button(f_left, text="SPREMI NARUDŽBU", command=self.save_appointment_to_db).pack(pady=20, fill="x")
        
        self.app_display = tk.Frame(self.tab3, padx=20, pady=20); self.app_display.pack(side="right", fill="both", expand=True)

    def save_appointment_to_db(self):
        p_sel = self.cb_p_appoint.get()
        if not p_sel: return
        pid = p_sel.split(":")[0]
        
        self.db.c.execute("INSERT INTO appointments(patient_id, specijalist, datum_termina, vrijeme, napomena) VALUES(?,?,?,?,?)", 
                         (pid, self.cb_spec.get(), self.ent_datum.get(), "00:00", self.ent_napomena.get()))
        self.db.conn.commit()
        messagebox.showinfo("Nexus OS", "Termin je uspješno spremljen!")
        self.show_appointments_list()

    def show_appointments_list(self):
        for w in self.app_display.winfo_children(): w.destroy()
        p_sel = self.cb_p_appoint.get()
        if not p_sel: return
        pid = p_sel.split(":")[0]
        
        tk.Label(self.app_display, text=f"Termini naručenih pregleda za: {p_sel}", font=("Arial", 11, "bold")).pack(pady=10)
        
        for a in self.db.get_appointments(pid):
            f = tk.Frame(self.app_display, relief="groove", borderwidth=1, pady=5)
            f.pack(fill="x", pady=2)
            tk.Label(f, text=f"🩺 {a[0]} | 📅 {a[1]} | 📝 {a[3]}").pack(side="left", padx=10)

if __name__ == "__main__":
    NexusApp().root.mainloop()