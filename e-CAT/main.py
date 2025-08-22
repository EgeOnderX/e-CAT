import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import random

# ---------- SETTINGS ----------
DATA_FILE = "cats.json"
            
# ---------- LOAD / SAVE ----------
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

def load_cats():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_cats(cats):
    with open(DATA_FILE, "w") as f:
        json.dump(cats, f, indent=4)

def generate_id():
    chars = ['C','A','T']
    return ''.join(random.choice(chars + [str(i) for i in range(10)]) for _ in range(10))

# ---------- MAIN APP ----------
class CatRegistryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🐱 Cat Population Registry")
        self.geometry("900x600")
        self.resizable(False, False)  # kareleşmiş
        self.cats = load_cats()

        self.create_menu()
        self.create_tree()
        self.refresh_table()

    # ---------- MENU ----------
    def create_menu(self):
        menubar = tk.Menu(self)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Add", command=self.add_cat)
        file_menu.add_command(label="Edit", command=self.edit_cat)
        file_menu.add_command(label="Delete", command=self.delete_cat)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # ID menu
        id_menu = tk.Menu(menubar, tearoff=0)
        id_menu.add_command(label="Change ID", command=self.change_id)
        id_menu.add_command(label="Regenerate ID", command=self.regenerate_id)
        menubar.add_cascade(label="ID", menu=id_menu)
        
        self.config(menu=menubar)

    # ---------- TREEVIEW ----------
    def create_tree(self):
        columns = ("id","name","age","gender","color","mother","father","breed","notes","vaccinated")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=90, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for cat in self.cats:
            self.tree.insert("", tk.END, values=(
                cat.get("id",""),
                cat.get("name",""),
                cat.get("age",""),
                cat.get("gender",""),
                cat.get("color",""),
                cat.get("mother",""),
                cat.get("father",""),
                cat.get("breed",""),
                cat.get("notes",""),
                cat.get("vaccinated","")
            ))

    # ---------- CRUD ----------
    def add_cat(self):
        CatForm(self, "Add Cat")

    def edit_cat(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection","Please select a cat first!")
            return
        cat_id = self.tree.item(selected[0])["values"][0]
        cat = next((c for c in self.cats if c["id"]==cat_id), None)
        if cat:
            CatForm(self,"Edit Cat",cat)

    def delete_cat(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection","Please select a cat first!")
            return
        cat_id = self.tree.item(selected[0])["values"][0]
        self.cats = [c for c in self.cats if c["id"]!=cat_id]
        save_cats(self.cats)
        self.refresh_table()

    # ---------- ID OPERATIONS ----------
    def change_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a cat first!")
            return

        cat_id = self.tree.item(selected[0])["values"][0]
        cat = next((c for c in self.cats if c["id"] == cat_id), None)
        if not cat:
            messagebox.showerror("Error", "Selected cat not found!")
            return

        new_id = simpledialog.askstring(
            "Change ID",
            "Enter new ID (10 chars, C/A/T/0-9):"
        )

        if new_id is None:
            # Kullanıcı cancel tuşuna bastı, hiçbir şey yapma
            return

        new_id = new_id.strip().upper()
        if len(new_id) == 10 and all(c in "CAT0123456789" for c in new_id):
            cat["id"] = new_id
            save_cats(self.cats)
            self.refresh_table()
        else:
            messagebox.showerror(
                "Invalid ID",
                "ID must be 10 characters long, using only C/A/T and digits."
            )


    def regenerate_id(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection","Please select a cat first!")
            return
        cat_id = self.tree.item(selected[0])["values"][0]
        cat = next((c for c in self.cats if c["id"]==cat_id), None)
        if cat:
            cat["id"] = generate_id()
            save_cats(self.cats)
            self.refresh_table()

# ---------- CAT FORM ----------
class CatForm(tk.Toplevel):
    def __init__(self,parent,title,cat=None):
        super().__init__(parent)
        self.parent = parent
        self.cat = cat
        self.title(title)
        self.geometry("310x330")
        self.resizable(False, False)

        labels = ["Name","Age","Gender","Color","Mother","Father","Breed","Notes","Vaccinated"]
        self.entries = {}
        for i,label in enumerate(labels):
            tk.Label(self,text=label, width=12, anchor="e").grid(row=i,column=0,pady=5)
            if label=="Gender":
                combo = ttk.Combobox(self,values=["Male","Female"],state="readonly", width=27)
                combo.grid(row=i,column=1,pady=5)
                combo.set(cat.get("gender","Male") if cat else "Male")
                self.entries[label]=combo
            elif label=="Vaccinated":
                combo = ttk.Combobox(self,values=["Yes","No"],state="readonly", width=27)
                combo.grid(row=i,column=1,pady=5)
                combo.set(cat.get("vaccinated","No") if cat else "No")
                self.entries[label]=combo
            else:
                entry = tk.Entry(self,width=30)
                entry.grid(row=i,column=1,pady=5)
                if cat:
                    entry.insert(0,cat.get(label.lower(),""))
                self.entries[label]=entry

        # Save button
        tk.Button(self, text="Save", width=20, command=self.save).grid(row=len(labels), column=0, columnspan=2, pady=10)

    def save(self):
        data = {}
        for key, entry in self.entries.items():
            value = entry.get().strip()
            if key.lower() in ["name","color","mother","father","breed","notes"]:
                value = value.title()
            data[key.lower()]=value

        data["vaccinated"]=self.entries["Vaccinated"].get()
        data["gender"]=self.entries["Gender"].get()

        if not self.cat:
            data["id"]=generate_id()
            self.parent.cats.append(data)
            self.cat = data
        else:
            for i,c in enumerate(self.parent.cats):
                if c["id"]==self.cat["id"]:
                    data["id"]=c["id"]
                    self.parent.cats[i]=data
                    break

        save_cats(self.parent.cats)
        self.parent.refresh_table()

# ---------- RUN ----------
if __name__=="__main__":
    app = CatRegistryApp()
    app.mainloop()
