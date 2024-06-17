import tkinter as tk
from tkinter import ttk
import sqlite3
from xgboost import XGBClassifier
import numpy as np

# Инициализация базы данных SQLite
conn = sqlite3.connect('sepsis_data.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        absolute_basophil_count REAL,
        ast REAL,
        bands REAL,
        base_excess REAL,
        ck REAL,
        ferritin REAL,
        l REAL,
        lipase REAL,
        mcv REAL,
        magnesium REAL,
        monocytes REAL,
        neutrophils REAL,
        oxygen_saturation REAL,
        platelet_count REAL,
        rbc REAL,
        po2 REAL,
        sepsis_probability REAL
    )
''')
conn.commit()
model = XGBClassifier()
model.load_model('boosting.txt')

class RoundedEntry(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, borderwidth=0, highlightthickness=0, **kwargs)
        self.configure(bg='black')
        self.round_rectangle(5, 5, 200, 30, 20, outline='#fc0335', width=2, fill='black')
        self.entry = tk.Entry(self, bg='black', fg='white', borderwidth=0, highlightthickness=0, insertbackground='white')
        self.create_window(100, 18, window=self.entry, width=180, height=20)

    def round_rectangle(self, x1, y1, x2, y2, radius=20, **kwargs):
        points = [x1 + radius, y1,
                  x1 + radius, y1,
                  x2 - radius, y1,
                  x2 - radius, y1,
                  x2, y1,
                  x2, y1 + radius,
                  x2, y1 + radius,
                  x2, y2 - radius,
                  x2, y2 - radius,
                  x2, y2,
                  x2 - radius, y2,
                  x2 - radius, y2,
                  x1 + radius, y2,
                  x1 + radius, y2,
                  x1, y2,
                  x1, y2 - radius,
                  x1, y2 - radius,
                  x1, y1 + radius,
                  x1, y1 + radius,
                  x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def get(self):
        return self.entry.get()

    def insert(self, index, string):
        self.entry.insert(index, string)

class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command, **kwargs):
        super().__init__(parent, borderwidth=0, highlightthickness=0, **kwargs)
        self.configure(bg='black')
        self.command = command
        self.round_rectangle(5, 5, 200, 40, 20, outline='#fc0335', width=2, fill='#fc0335')
        self.text_id = self.create_text(100, 22, text=text, fill='white', font=("Arial", 12, "bold"))
        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def round_rectangle(self, x1, y1, x2, y2, radius=20, **kwargs):
        points = [x1 + radius, y1,
                  x1 + radius, y1,
                  x2 - radius, y1,
                  x2 - radius, y1,
                  x2, y1,
                  x2, y1 + radius,
                  x2, y1 + radius,
                  x2, y2 - radius,
                  x2, y2 - radius,
                  x2, y2,
                  x2 - radius, y2,
                  x2 - radius, y2,
                  x1 + radius, y2,
                  x1 + radius, y2,
                  x1, y2,
                  x1, y2 - radius,
                  x1, y2 - radius,
                  x1, y1 + radius,
                  x1, y1 + radius,
                  x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def on_click(self, event):
        self.command()

    def on_enter(self, event):
        self.itemconfig(self.text_id, fill='#d2d2d2')

    def on_leave(self, event):
        self.itemconfig(self.text_id, fill='white')

class HealthDataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Прогнозирование сепсиса")
        self.root.configure(bg='black')
        self.sepsis_probability = 0

        # Словарь с переводами на русский
        self.field_names = {
            'Absolute Basophil Count': 'Абсолютное количество базофилов',
            'Asparate Aminotransferase (AST)': 'Аспартатаминотрансфераза (АСТ)',
            'Bands': 'Палочкоядерные',
            'Base Excess': 'Избыток основания',
            'Creatine Kinase (CK)': 'Креатинкиназа (КК)',
            'Ferritin': 'Ферритин',
            'L': 'L',
            'Lipase': 'Липаза',
            'MCV': 'Средний объем клетки',
            'Magnesium': 'Магний',
            'Monocytes': 'Моноциты',
            'Neutrophils': 'Нейтрофилы',
            'Oxygen Saturation': 'Насыщение кислородом',
            'Platelet Count': 'Количество тромбоцитов',
            'Red Blood Cells': 'Эритроциты',
            'pO2': 'pO2'
        }

        # Создание и размещение меток и полей ввода
        self.entries = {}
        row = 0
        for field, translation in self.field_names.items():
            label = tk.Label(root, text=translation + ": ", bg='black', fg='white', font=("Arial", 10, "bold"))
            label.grid(row=row, column=0, sticky="e", padx=5, pady=2)
            entry = RoundedEntry(root, width=210, height=30)
            entry.grid(row=row, column=1, padx=5, pady=2, sticky="ew")
            self.entries[field] = entry
            row += 1

        # Кнопка для сохранения данных
        self.save_button = RoundedButton(root, "Сохранить", self.show_name_form, width=210, height=40)
        self.save_button.grid(row=row, columnspan=2, pady=2)
        row += 1

        # Кнопка для узнать диагноз
        self.diagnosis_button = RoundedButton(root, "Узнать диагноз", self.diagnose_sepsis, width=210, height=40)
        self.diagnosis_button.grid(row=row, columnspan=2, pady=2)
        row += 1

        # Кнопка для отображения сохраненных пациентов
        self.view_button = RoundedButton(root, "Просмотреть пациентов", self.show_patients, width=210, height=40)
        self.view_button.grid(row=row, columnspan=2, pady=2)
        row += 1

        # Метка для отображения вероятности и текста о вероятности
        self.probability_label = tk.Label(root, text="", font=("Arial", 12, "bold"), bg='black', fg='white', wraplength=400)
        self.probability_label.grid(row=row, columnspan=2, sticky="ew", pady=2)

    def show_name_form(self):
        self.name_window = tk.Toplevel(self.root)
        self.name_window.title("Введите имя и фамилию")
        self.name_window.configure(bg='black')

        tk.Label(self.name_window, text="Имя:", bg='black', fg='white', font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5)
        self.first_name_entry = tk.Entry(self.name_window, bg='black', fg='white', insertbackground='white')
        self.first_name_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.name_window, text="Фамилия:", bg='black', fg='white', font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, pady=5)
        self.last_name_entry = tk.Entry(self.name_window, bg='black', fg='white', insertbackground='white')
        self.last_name_entry.grid(row=1, column=1, padx=5, pady=5)

        save_button = tk.Button(self.name_window, text="Сохранить", command=self.save_data, bg='#fc0335', fg='white')
        save_button.grid(row=2, columnspan=2, pady=5)

    def save_data(self):
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()
        
        data = [entry.get() for entry in self.entries.values()]
        data = [float(d) if d else -1 for d in data]

        cursor.execute('''
            INSERT INTO patients (
                first_name, last_name, absolute_basophil_count, ast, bands, base_excess, ck, ferritin, l, lipase, mcv,
                magnesium, monocytes, neutrophils, oxygen_saturation, platelet_count, rbc, po2, sepsis_probability
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, *data, round(float(self.sepsis_probability), 2)))  
        conn.commit()

        self.name_window.destroy()

    def diagnose_sepsis(self):
        # Подготовка данных для модели
        features = []
        for entry in self.entries.values():
            try:
                value = float(entry.get())
            except ValueError:
                value = -1
            features.append(value)

        features = np.array(features).reshape(1, -1)
        
        # Предсказание вероятности сепсиса
        probability = model.predict_proba(features)[0][1]

        self.sepsis_probability = probability
        print(self.sepsis_probability)
        # Определение уровня вероятности
        if probability < 0.3:
            diagnosis = "низкая вероятность сепсиса"
            bg_color = "green"
        elif probability < 0.7:
            diagnosis = "средняя вероятность сепсиса"
            bg_color = "yellow"
        else:
            diagnosis = "высокая вероятность сепсиса"
            bg_color = "red"

        # Отображение вероятности на интерфейсе с учетом стилизации
        self.probability_label.config(text=f"Вероятность сепсиса: {probability:.2f}, {diagnosis}",
                                      bg=bg_color, fg="black")

    def show_patients(self):
        patients_window = tk.Toplevel(self.root)
        patients_window.title("Сохраненные пациенты")
        patients_window.configure(bg='black')

        tree = ttk.Treeview(patients_window, columns=('ID', 'First Name', 'Last Name', 'Probability'), show='headings')
        tree.heading('ID', text='ID')
        tree.heading('First Name', text='Имя')
        tree.heading('Last Name', text='Фамилия')
        tree.heading('Probability', text='Вероятность сепсиса')

        tree.column('ID', width=30)
        tree.column('First Name', width=100)
        tree.column('Last Name', width=100)
        tree.column('Probability', width=150)

        tree.pack(fill=tk.BOTH, expand=True)

        cursor.execute('SELECT id, first_name, last_name, sepsis_probability FROM patients')
        for row in cursor.fetchall():
            tree.insert('', tk.END, values=row)

        # Добавление прокрутки
        scrollbar = ttk.Scrollbar(patients_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        tree.bind('<Double-1>', self.on_patient_select)

    def on_patient_select(self, event):
        selected_item = event.widget.selection()[0]
        patient_id = event.widget.item(selected_item, 'values')[0]
        self.show_patient_history(patient_id)

    def show_patient_history(self, patient_id):
        history_window = tk.Toplevel(self.root)
        history_window.title("История анализов")
        history_window.configure(bg='black')

        columns = ('Parameter', 'Value')
        tree = ttk.Treeview(history_window, columns=columns, show='headings')
        tree.heading('Parameter', text='Параметр')
        tree.heading('Value', text='Значение')

        tree.column('Parameter', width=150)
        tree.column('Value', width=200)

        tree.pack(fill=tk.BOTH, expand=True)

        cursor.execute('SELECT * FROM patients WHERE id = ?', (patient_id,))
        patient_data = cursor.fetchone()

        field_names_with_prob = list(self.field_names.values()) + ['Вероятность сепсиса']
        for i, value in enumerate(patient_data[3:]):
            tree.insert('', tk.END, values=(field_names_with_prob[i], value))

        # Добавление прокрутки
        scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

        # Отображение вероятности сепсиса
        sepsis_probability = patient_data[-1]
        probability_label = tk.Label(history_window, text=f"Вероятность сепсиса: {sepsis_probability:.2f}", font=("Arial", 12, "bold"), bg='black', fg='white')
        probability_label.pack(pady=10)

root = tk.Tk()

app = HealthDataApp(root)
root.mainloop()
