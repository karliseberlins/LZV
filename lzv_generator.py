import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import json

# Kopē uz starpliktuvi
def copy_to_clipboard():
    text = output_text.get()
    if text:
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        messagebox.showinfo("Kopēts", "Simbolu secība nokopēta uz starpliktuvi.")
    else:
        messagebox.showwarning("Nav ko kopēt", "Nav nevienas izdrukātas simbolu secības.")

# Notīra visus laukus
def clear_all():
    for entry in entry_list:
        entry.delete(0, tk.END)
    output_text.set("")

# Atceļ pēdējo ievadīto simbolu
def undo_last():
    sequence = []
    for sym in symbols:
        for entry in entries[sym]:
            val = entry.get().strip()
            if val.isdigit():
                seq = int(val)
                sequence.append((seq, entry))
    if sequence:
        sequence.sort(key=lambda x: x[0])
        _, last_entry = sequence[-1]
        last_entry.delete(0, tk.END)
        print_sequence()
    else:
        messagebox.showinfo("Nav ko atcelt", "Nav neviena simbolu, ko atcelt.")

# Beigt darbu
def exit_app():
    root.quit()

# Funkcija pievienot jaunu simbolu pēc ASCII koda
def add_new_symbol():
    try:
        # Pieprasa ievadīt ASCII kodu
        ascii_code = simpledialog.askinteger("Jauns simbols", "Ievadi jauno simbola ASCII kodu:")
        if ascii_code is None:  # Lietotājs atcēla ievadi
            return

        # Pārbauda, vai ASCII(paplašinātais) kods ir derīgs
        if not (0 <= ascii_code <= 120171):  # ASCII kods ir diapazonā no 0 līdz 120171
            messagebox.showerror("Kļūda", "ASCII kodam jābūt diapazonā no 0 līdz 120171.")
            return

        # Pārveido ASCII kodu par simbolu
        new_symbol = chr(ascii_code)

        # Pārbauda, vai simbols jau eksistē
        if new_symbol in symbols:
            messagebox.showerror("Kļūda", "Šis simbols jau eksistē.")
            return

        # Pieprasa ievadīt aprakstu
        new_description = simpledialog.askstring("Apraksts", "Ievadi simbola aprakstu:")
        if not new_description:
            messagebox.showerror("Kļūda", "Apraksts nedrīkst būt tukšs.")
            return

        # Pievieno jauno simbolu vārdnīcai
        symbols[new_symbol] = new_description
        save_symbols(symbols)  # Saglabā izmaiņas failā
        update_table()
    except Exception as e:
        messagebox.showerror("Kļūda", str(e))

# Funkcija dzēst simbolu pēc ASCII koda
def delete_symbol():
    try:
        ascii_code = simpledialog.askinteger("Dzēst simbolu", "Ievadi simbola ASCII kodu:")
        if ascii_code is None:  # Lietotājs atcēla ievadi
            return

        # Atrodam simbolu pēc ASCII koda
        symbol_to_delete = None
        for sym in symbols:
            if ord(sym) == ascii_code:
                symbol_to_delete = sym
                break

        if not symbol_to_delete:
            messagebox.showerror("Kļūda", f"Simbols ar ASCII kodu {ascii_code} neeksistē.")
            return

        # Dzēš simbolu no vārdnīcas
        del symbols[symbol_to_delete]
        save_symbols(symbols)  # Saglabā izmaiņas failā
        update_table()
    except Exception as e:
        messagebox.showerror("Kļūda", str(e))

# Funkcija atjaunot tabulu
def update_table():
    global entries, entry_list
    for widget in scrollable_frame.grid_slaves():
        widget.destroy()  # Notīra visus esošos elementus

    entries = {}
    entry_list = []

    # Izveido kolonnas virsrakstus
    tk.Label(scrollable_frame, text="Simbols").grid(row=0, column=0)
    tk.Label(scrollable_frame, text="ASCII kods").grid(row=0, column=1)
    tk.Label(scrollable_frame, text="Apraksts").grid(row=0, column=2)
    for i in range(8):
        tk.Label(scrollable_frame, text=f"#{i+1}").grid(row=0, column=3+i)

    # Izveido tabulu
    for row_index, (sym, desc) in enumerate(symbols.items(), start=1):
        tk.Label(scrollable_frame, text=sym).grid(row=row_index, column=0)
        tk.Label(scrollable_frame, text=str(ord(sym))).grid(row=row_index, column=1)  # ASCII kods
        tk.Label(scrollable_frame, text=desc).grid(row=row_index, column=2, sticky='w')
        if sym not in entries:
            entries[sym] = []  # Izveido jaunu sarakstu, ja tāda vēl nav
        for col in range(8):
            e = tk.Entry(scrollable_frame, width=4)
            e.grid(row=row_index, column=3+col)
            e.bind("<FocusIn>", on_focus)
            entries[sym].append(e)
            entry_list.append(e)

    # Atjauno izdruku
    print_sequence()

# Funkcija ielasīt simbolu vārdnīcu no JSON faila
def load_symbols(filename="symbols.json"):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        messagebox.showerror("Kļūda", f"Fails '{filename}' nav atrasts.")
        return {}
    except json.JSONDecodeError:
        messagebox.showerror("Kļūda", f"Fails '{filename}' satur nederīgus datus.")
        return {}

# Funkcija saglabāt simbolu vārdnīcu JSON failā
def save_symbols(symbols, filename="symbols.json"):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump(symbols, file, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("Kļūda", f"Neizdevās saglabāt failā '{filename}': {str(e)}")

# Funkcija pievienot "Atstarpe" simbolu izdrukas secībai
def add_space_to_sequence():
    try:
        for entry in entries["␣"]:
            if not entry.get().strip().isdigit():  # Atrod pirmo tukšo lauku
                next_num = get_next_sequence_number()
                entry.insert(0, str(next_num))
                print_sequence()
                return
        messagebox.showinfo("Informācija", "Visi 'Atstarpe' lauki jau ir aizpildīti.")
    except KeyError:
        messagebox.showerror("Kļūda", "Simbols 'Atstarpe' nav pieejams simbolu sarakstā.")

# Funkcija pievienot "Enter" simbolu izdrukas secībai
def add_enter_to_sequence():
    try:
        for entry in entries["⏎"]:
            if not entry.get().strip().isdigit():  # Atrod pirmo tukšo lauku
                next_num = get_next_sequence_number()
                entry.insert(0, str(next_num))
                print_sequence()
                return
        messagebox.showinfo("Informācija", "Visi 'Enter' lauki jau ir aizpildīti.")
    except KeyError:
        messagebox.showerror("Kļūda", "Simbols 'Enter' nav pieejams simbolu sarakstā.")

# Simbolu vārdnīca
symbols = load_symbols()
root = tk.Tk()
root.title("Simbolu secības veidotājs")
root.geometry("840x600")


# Pogas pirmajā rindā
tk.Button(root, text="Kopēt uz starpliktuvi", command=copy_to_clipboard).grid(row=0, column=0, pady=10, padx=5)
tk.Button(root, text="Notīrīt visu", command=clear_all).grid(row=0, column=1, pady=10, padx=5)
tk.Button(root, text="Atcelt pēdējo", command=undo_last).grid(row=0, column=2, pady=10, padx=5)
tk.Button(root, text="Beigt darbu", command=exit_app).grid(row=0, column=3, pady=10, padx=5)
tk.Button(root, text="Pievienot simbolu", command=add_new_symbol).grid(row=0, column=4, pady=10, padx=5)
tk.Button(root, text="Dzēst simbolu", command=delete_symbol).grid(row=0, column=5, pady=10, padx=5)
tk.Button(root, text="Atstarpe", command=add_space_to_sequence).grid(row=0, column=6, pady=10, padx=5)
tk.Button(root, text="Enter", command=add_enter_to_sequence).grid(row=0, column=7, pady=10, padx=5)

# Pievieno skrolleri un tabulu zem pogām
canvas = tk.Canvas(root, width=710, height=400)  # Palielina platumu un augstumu
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

# Funkcija, lai konfigurētu skrollera rāmi
def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

# Iepako skrolleri un rāmi
scrollable_frame.bind("<Configure>", on_frame_configure)
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.grid(row=1, column=0, columnspan=6, sticky="nsew")  # Tabula sākas no otrās rindas
scrollbar.grid(row=1, column=6, sticky="ns")

# Pārnes visus elementus uz `scrollable_frame`
entries = {}
entry_list = []
output_text = tk.StringVar()

# Izdruka (novietota ārpus skrollera)
output_label = tk.Label(root, textvariable=output_text, wraplength=600, justify="left",
                        bg="white", anchor="w", relief="sunken", padx=5, pady=5)
output_label.grid(row=2, column=0, columnspan=6, sticky="we", pady=(10, 0))

# Funkcija nākamajam secības numuram
def get_next_sequence_number():
    used = set()
    for entry in entry_list:
        val = entry.get().strip()
        if val.isdigit():
            used.add(int(val))
    i = 1
    while i in used:
        i += 1
    return i

# Klikšķa notikums
def on_focus(event):
    entry = event.widget
    val = entry.get().strip()
    if not val.isdigit():
        next_num = get_next_sequence_number()
        entry.delete(0, tk.END)
        entry.insert(0, str(next_num))
        print_sequence()

# Izveido kolonnas virsrakstus
tk.Label(scrollable_frame, text="Simbols").grid(row=0, column=0)
tk.Label(scrollable_frame, text="ASCII kods").grid(row=0, column=1)
tk.Label(scrollable_frame, text="Apraksts").grid(row=0, column=2)
for i in range(8):
    tk.Label(scrollable_frame, text=f"#{i+1}").grid(row=0, column=3+i)

# Izveido tabulu
for row_index, (sym, desc) in enumerate(symbols.items(), start=1):
    tk.Label(scrollable_frame, text=sym).grid(row=row_index, column=0)
    tk.Label(scrollable_frame, text=str(ord(sym))).grid(row=row_index, column=1)  # ASCII kods
    tk.Label(scrollable_frame, text=desc).grid(row=row_index, column=2, sticky='w')
    if sym not in entries:
        entries[sym] = []  # Izveido jaunu sarakstu, ja tāda vēl nav
    for col in range(8):
        e = tk.Entry(scrollable_frame, width=4)
        e.grid(row=row_index, column=3+col)
        e.bind("<FocusIn>", on_focus)
        entries[sym].append(e)
        entry_list.append(e)

# Izdrukas funkcija
def print_sequence():
    try:
        sequence = []
        for sym in symbols:
            for entry in entries[sym]:
                val = entry.get().strip()
                if val.isdigit():
                    seq = int(val)
                    if seq > 0:
                        sequence.append((seq, sym, entry))

        sequence.sort(key=lambda x: x[0])
        output = ''
        for _, sym, _ in sequence:
            if sym == '␣':
                output += ' '
            elif sym == '⏎':
                output += '\n'
            else:
                output += sym
        output_text.set(output)
    except Exception as e:
        messagebox.showerror("Kļūda", str(e))

root.mainloop()