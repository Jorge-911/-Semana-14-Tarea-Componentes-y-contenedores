import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
import calendar

# -------------------------
# DatePicker (sin dependencias externas)
# -------------------------
class DatePicker(tk.Toplevel):
    def __init__(self, master, initial_date=None, callback=None):
        super().__init__(master)
        self.title("Seleccionar fecha")
        self.resizable(False, False)
        self.callback = callback

        today = date.today()
        if isinstance(initial_date, date):
            self.year = initial_date.year
            self.month = initial_date.month
            self.day = initial_date.day
        else:
            self.year = today.year
            self.month = today.month
            self.day = today.day

        container = ttk.Frame(self, padding=10)
        container.grid(row=0, column=0, sticky="nsew")

        # Encabezado con navegación
        hdr = ttk.Frame(container)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.columnconfigure(1, weight=1)

        self.prev_btn = ttk.Button(hdr, text="◀", width=3, command=self.prev_month)
        self.prev_btn.grid(row=0, column=0, padx=2)

        self.title_var = tk.StringVar()
        self.title_lbl = ttk.Label(hdr, textvariable=self.title_var, font=("", 10, "bold"))
        self.title_lbl.grid(row=0, column=1, padx=8)

        self.next_btn = ttk.Button(hdr, text="▶", width=3, command=self.next_month)
        self.next_btn.grid(row=0, column=2, padx=2)

        # Cabecera días
        self.days_hdr = ttk.Frame(container)
        self.days_hdr.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        for i, d in enumerate(calendar.weekheader(2).split()):
            ttk.Label(self.days_hdr, text=d, width=4, anchor="center").grid(row=0, column=i, padx=2)

        # Cuerpo calendario
        self.grid_frame = ttk.Frame(container)
        self.grid_frame.grid(row=2, column=0, pady=6)

        # Botones aceptar/cancelar
        actions = ttk.Frame(container)
        actions.grid(row=3, column=0, sticky="ew")
        ttk.Button(actions, text="Hoy", command=self.choose_today).grid(row=0, column=0, padx=(0, 6))
        ttk.Button(actions, text="Cancelar", command=self.destroy).grid(row=0, column=1, padx=6)

        self.draw_calendar()

        # Modal
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.focus()

    def draw_calendar(self):
        # Limpiar botones anteriores
        for w in self.grid_frame.winfo_children():
            w.destroy()

        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.monthdayscalendar(self.year, self.month)

        self.title_var.set(f"{calendar.month_name[self.month]} {self.year}")

        # Pintar días
        for row, week in enumerate(month_days):
            for col, day in enumerate(week):
                if day == 0:
                    ttk.Label(self.grid_frame, text=" ", width=4).grid(row=row, column=col, padx=2, pady=2)
                else:
                    b = ttk.Button(self.grid_frame, text=str(day), width=4,
                                   command=lambda d=day: self.pick_day(d))
                    b.grid(row=row, column=col, padx=2, pady=2)

    def pick_day(self, d):
        self.day = d
        if self.callback:
            try:
                chosen = date(self.year, self.month, self.day)
                self.callback(chosen)
            except Exception:
                pass
        self.destroy()

    def prev_month(self):
        if self.month == 1:
            self.month, self.year = 12, self.year - 1
        else:
            self.month -= 1
        self.draw_calendar()

    def next_month(self):
        if self.month == 12:
            self.month, self.year = 1, self.year + 1
        else:
            self.month += 1
        self.draw_calendar()

    def choose_today(self):
        today = date.today()
        if self.callback:
            self.callback(today)
        self.destroy()


# -------------------------
# Aplicación de Agenda
# -------------------------
class AgendaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Agenda Personal - Tkinter")
        self.geometry("820x520")
        self.minsize(780, 480)

        # Contenedor raíz (Padding general)
        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        # -------------------------
        # Frames (organización)
        # -------------------------
        # Frame de lista (Treeview)
        self.frame_lista = ttk.LabelFrame(root, text="Eventos / Tareas")
        self.frame_lista.pack(side="top", fill="both", expand=True)

        # Frame de formulario
        self.frame_form = ttk.LabelFrame(root, text="Nuevo evento / tarea")
        self.frame_form.pack(side="left", fill="x", expand=True, pady=(10, 0))

        # Frame de acciones
        self.frame_acciones = ttk.LabelFrame(root, text="Acciones")
        self.frame_acciones.pack(side="right", fill="x", expand=True, pady=(10, 0))

        # -------------------------
        # Treeview de eventos
        # -------------------------
        columns = ("fecha", "hora", "descripcion")
        self.tree = ttk.Treeview(self.frame_lista, columns=columns, show="headings", height=12)
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("hora", text="Hora")
        self.tree.heading("descripcion", text="Descripción")

        self.tree.column("fecha", width=120, anchor="center")
        self.tree.column("hora", width=80, anchor="center")
        self.tree.column("descripcion", width=520, anchor="w")

        # Scrollbar vertical
        vsb = ttk.Scrollbar(self.frame_lista, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # -------------------------
        # Formulario (Labels + Entradas + DatePicker)
        # -------------------------
        frm = ttk.Frame(self.frame_form, padding=10)
        frm.pack(fill="x")

        self.var_fecha = tk.StringVar()
        self.var_hora = tk.StringVar()
        self.var_desc = tk.StringVar()

        # Fila fecha
        ttk.Label(frm, text="Fecha (YYYY-MM-DD):").grid(row=0, column=0, sticky="w", pady=6)
        self.entry_fecha = ttk.Entry(frm, textvariable=self.var_fecha, width=18)
        self.entry_fecha.grid(row=0, column=1, sticky="w", pady=6, padx=(0, 6))
        ttk.Button(frm, text="📅", width=3, command=self.abrir_datepicker).grid(row=0, column=2, sticky="w")

        # Fila hora
        ttk.Label(frm, text="Hora (HH:MM 24h):").grid(row=1, column=0, sticky="w", pady=6)
        self.entry_hora = ttk.Entry(frm, textvariable=self.var_hora, width=18)
        self.entry_hora.grid(row=1, column=1, sticky="w", pady=6)

        # Fila descripción
        ttk.Label(frm, text="Descripción:").grid(row=2, column=0, sticky="w", pady=6)
        self.entry_desc = ttk.Entry(frm, textvariable=self.var_desc, width=60)
        self.entry_desc.grid(row=2, column=1, columnspan=2, sticky="we", pady=6)

        frm.columnconfigure(1, weight=1)

        # -------------------------
        # Acciones
        # -------------------------
        act = ttk.Frame(self.frame_acciones, padding=10)
        act.pack(fill="x")

        self.btn_agregar = ttk.Button(act, text="Agregar evento", command=self.agregar_evento)
        self.btn_eliminar = ttk.Button(act, text="Eliminar seleccionado", command=self.eliminar_seleccion)
        self.btn_salir = ttk.Button(act, text="Salir", command=self.destroy)

        self.btn_agregar.grid(row=0, column=0, sticky="we", pady=6)
        self.btn_eliminar.grid(row=1, column=0, sticky="we", pady=6)
        self.btn_salir.grid(row=2, column=0, sticky="we", pady=6)

        act.columnconfigure(0, weight=1)

        # Atajos
        self.bind("<Return>", lambda e: self.agregar_evento())
        self.bind("<Delete>", lambda e: self.eliminar_seleccion())

        # Lista interna de eventos (tuplas normalizadas)
        self.eventos = []  # [(dt, fecha_str, hora_str, desc, iid)]

    # -------------------------
    # Lógica
    # -------------------------
    def abrir_datepicker(self):
        # Intentar parsear fecha actual del entry
        init = None
        try:
            init = datetime.strptime(self.var_fecha.get().strip(), "%Y-%m-%d").date()
        except Exception:
            init = None

        DatePicker(self, initial_date=init, callback=self.set_fecha_from_picker)

    def set_fecha_from_picker(self, chosen_date):
        self.var_fecha.set(chosen_date.strftime("%Y-%m-%d"))

    def validar_fecha(self, s):
        try:
            datetime.strptime(s, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def validar_hora(self, s):
        try:
            datetime.strptime(s, "%H:%M")
            return True
        except ValueError:
            return False

    def agregar_evento(self):
        fecha = self.var_fecha.get().strip()
        hora = self.var_hora.get().strip()
        desc = self.var_desc.get().strip()

        # Validaciones
        if not fecha or not hora or not desc:
            messagebox.showwarning("Campos incompletos", "Completa fecha, hora y descripción.")
            return
        if not self.validar_fecha(fecha):
            messagebox.showerror("Fecha inválida", "Usa el formato YYYY-MM-DD (ej. 2025-09-16).")
            return
        if not self.validar_hora(hora):
            messagebox.showerror("Hora inválida", "Usa el formato HH:MM en 24h (ej. 08:30 o 17:45).")
            return

        try:
            dt = datetime.strptime(f"{fecha} {hora}", "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Fecha/Hora inválidas", "Revisa los formatos e intenta de nuevo.")
            return

        # Insertar en Treeview
        iid = self.tree.insert("", "end", values=(fecha, hora, desc))
        self.eventos.append((dt, fecha, hora, desc, iid))
        # Ordenar por datetime
        self.eventos.sort(key=lambda x: x[0])
        self.refrescar_treeview()

        # Limpiar campos (opcional)
        self.var_desc.set("")
        # Mantener fecha/hora por comodidad

    def refrescar_treeview(self):
        # Limpiar tree y reinsertar en orden
        for item in self.tree.get_children():
            self.tree.delete(item)
        for _, f, h, d, iid in self.eventos:
            new_iid = self.tree.insert("", "end", values=(f, h, d))

        new_list = []
        for item in self.tree.get_children():
            f, h, d = self.tree.item(item, "values")
            dt = datetime.strptime(f"{f} {h}", "%Y-%m-%d %H:%M")
            new_list.append((dt, f, h, d, item))
        self.eventos = new_list

    def eliminar_seleccion(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Sin selección", "Selecciona un evento en la lista.")
            return

        # Confirmación opcional
        if not messagebox.askyesno("Confirmar eliminación", "¿Eliminar el evento seleccionado?"):
            return

        for item in sel:
            vals = self.tree.item(item, "values")
            self.tree.delete(item)
            self.eventos = [e for e in self.eventos if e[4] != item]

# -------------------------
# Inicio de la app
# -------------------------
def main():
    try:
        root = AgendaApp()
        try:
            style = ttk.Style()
            if "clam" in style.theme_names():
                style.theme_use("clam")
        except Exception:
            pass
        root.mainloop()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
