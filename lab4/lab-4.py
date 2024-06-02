import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3

# Ініціалізація БД
conn = sqlite3.connect('real_estate.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS нерухомість
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, назва TEXT UNIQUE, опис TEXT, дата_публікації TEXT, ціна REAL)''')
conn.commit()

# Глобальна змінна для зберігання ролі поточного користувача
current_role = 'user'  # Може бути 'user' або 'manager'

# Функції для додавання, редагування, видалення, пошуку та виведення оголошень
def add_property():
    if current_role != 'manager':
        messagebox.showerror("Помилка", "У вас немає дозволу додавати нерухомість!")
        return

    name = entry_name.get().strip()
    desc = entry_description.get().strip()
    date = entry_date.get().strip()
    price = entry_price.get().strip()

    if not name or not desc or not date or not price:
        messagebox.showerror("Помилка", "Всі поля повинні бути заповнені!")
        return

    try:
        cursor.execute("INSERT INTO нерухомість (назва, опис, дата_публікації, ціна) VALUES (?, ?, ?, ?)",
                       (name, desc, date, price))
        conn.commit()
        messagebox.showinfo("Успіх", "Нерухомість додано!")
        clear_entries()
    except sqlite3.IntegrityError:
        messagebox.showerror("Помилка", "Нерухомість з такою назвою вже існує!")

def edit_property():
    if current_role != 'manager':
        messagebox.showerror("Помилка", "У вас немає дозволу редагувати нерухомість!")
        return

    name = entry_name.get().strip()
    desc = entry_description.get().strip()
    date = entry_date.get().strip()
    price = entry_price.get().strip()

    if not name or not desc or not date or not price:
        messagebox.showerror("Помилка", "Всі поля повинні бути заповнені!")
        return

    cursor.execute("SELECT id FROM нерухомість WHERE назва=?", (name,))
    if cursor.fetchone() is None:
        messagebox.showerror("Помилка", "Нерухомість з такою назвою не знайдено!")
        return

    cursor.execute("UPDATE нерухомість SET опис=?, дата_публікації=?, ціна=? WHERE назва=?",
                   (desc, date, price, name))
    conn.commit()
    messagebox.showinfo("Успіх", "Нерухомість оновлено!")
    clear_entries()

def delete_property():
    if current_role != 'manager':
        messagebox.showerror("Помилка", "У вас немає дозволу видаляти нерухомість!")
        return

    name = entry_name.get().strip()

    if not name:
        messagebox.showerror("Помилка", "Поле назви повинно бути заповнене!")
        return

    cursor.execute("DELETE FROM нерухомість WHERE назва=?", (name,))
    if cursor.rowcount == 0:
        messagebox.showerror("Помилка", "Нерухомість з такою назвою не знайдено!")
    else:
        conn.commit()
        messagebox.showinfo("Успіх", "Нерухомість видалено!")
        clear_entries()

def search_property_by_name():
    name = entry_name.get().strip()

    if not name:
        messagebox.showerror("Помилка", "Поле назви повинно бути заповнене!")
        return

    cursor.execute("SELECT * FROM нерухомість WHERE назва LIKE ?", ('%' + name + '%',))
    properties = cursor.fetchall()
    output_text.delete(1.0, tk.END)
    if properties:
        for prop in properties:
            output_text.insert(tk.END, f"Назва: {prop[1]}\nОпис: {prop[2]}\nДата публікації: {prop[3]}\nЦіна: {prop[4]}\n\n")
    else:
        messagebox.showerror("Помилка", "Нерухомість не знайдено!")

def display_properties():
    cursor.execute("SELECT * FROM нерухомість")
    properties = cursor.fetchall()
    output_text.delete(1.0, tk.END)
    if properties:
        for prop in properties:
            output_text.insert(tk.END, f"Назва: {prop[1]}\nОпис: {prop[2]}\nДата публікації: {prop[3]}\nЦіна: {prop[4]}\n\n")
    else:
        output_text.insert(tk.END, "Немає наявних оголошень.")

def clear_entries():
    entry_name.delete(0, tk.END)
    entry_description.delete(0, tk.END)
    entry_date.delete(0, tk.END)
    entry_price.delete(0, tk.END)

def change_account():
    global current_role
    password = simpledialog.askstring("Пароль", "Введіть пароль менеджера:", show='*')
    if password == "12345":
        current_role = 'manager'
        messagebox.showinfo("Успіх", "Ви увійшли в ролі менеджера.")
    else:
        current_role = 'user'
        messagebox.showinfo("Пароль невірний", "Ви увійшли в ролі користувача.")

# Створення GUI
root = tk.Tk()
root.title("Агентство Продажу Нерухомості")

tk.Label(root, text="Назва").grid(row=0, column=0)
entry_name = tk.Entry(root)
entry_name.grid(row=0, column=1, columnspan=2, sticky='ew')

tk.Label(root, text="Опис").grid(row=1, column=0)
entry_description = tk.Entry(root)
entry_description.grid(row=1, column=1, columnspan=2, sticky='ew')

tk.Label(root, text="Дата публікації").grid(row=2, column=0)
entry_date = tk.Entry(root)
entry_date.grid(row=2, column=1, columnspan=2, sticky='ew')

tk.Label(root, text="Ціна").grid(row=3, column=0)
entry_price = tk.Entry(root)
entry_price.grid(row=3, column=1, columnspan=2, sticky='ew')

tk.Button(root, text="Додати", command=add_property).grid(row=4, column=0)
tk.Button(root, text="Редагувати", command=edit_property).grid(row=4, column=1)
tk.Button(root, text="Видалити", command=delete_property).grid(row=4, column=2)
tk.Button(root, text="Пошук по назві", command=search_property_by_name).grid(row=5, column=0, columnspan=3, sticky='ew')
tk.Button(root, text="Показати всю нерухомість", command=display_properties).grid(row=6, column=0, columnspan=3, sticky='ew')
tk.Button(root, text="Змінити аккаунт", command=change_account).grid(row=7, column=0, columnspan=3, sticky='ew')

tk.Label(root, text="Наявна нерухомість:").grid(row=8, column=0, columnspan=3)
output_text = tk.Text(root, height=15, width=50)
output_text.grid(row=9, column=0, columnspan=3)

root.mainloop()
