import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from tkcalendar import DateEntry

# ------------------ DB INIT ------------------
def init_db():
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()

    # categories
    c.execute("""CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT UNIQUE NOT NULL
    )""")

    # inventory
    c.execute("""CREATE TABLE IF NOT EXISTS inventory (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL,
        quantity INTEGER NOT NULL
    )""")

    # transactions
    c.execute("""CREATE TABLE IF NOT EXISTS transactions (
        txn_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER,
        item_name TEXT,
        category TEXT,
        quantity INTEGER,
        txn_type TEXT,
        txn_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        user_name TEXT
    )""")

    conn.commit()
    conn.close()


# ------------------ CATEGORY MGMT ------------------
def manage_categories():
    win = tk.Toplevel(root)
    win.title("Manage Categories")
    win.geometry("500x400")
    win.transient(root)
    win.grab_set()

    frame = tk.Frame(win, padx=20, pady=20)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text="New Category:").pack()
    cat_entry = tk.Entry(frame, width=30)
    cat_entry.pack(pady=5)

    def add_category():
        name = cat_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Enter category name")
            return
        try:
            conn = sqlite3.connect("inventory.db")
            c = conn.cursor()
            c.execute("INSERT INTO categories (category_name) VALUES (?)", (name,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Category added")
            load_categories()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Category already exists")

    tk.Button(frame, text="Add Category", command=add_category).pack(pady=5)

    cols = ("ID", "Category")
    tree = ttk.Treeview(frame, columns=cols, show="headings", height=10)
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=200)
    tree.pack(pady=10, fill="both", expand=True)

    def load_categories():
        for r in tree.get_children():
            tree.delete(r)
        conn = sqlite3.connect("inventory.db")
        c = conn.cursor()
        c.execute("SELECT * FROM categories")
        rows = c.fetchall()
        conn.close()
        for r in rows:
            tree.insert("", "end", values=r)

    def delete_category():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a category to delete")
            return
        cat_id, cat_name = tree.item(selected[0], "values")
        conn = sqlite3.connect("inventory.db")
        c = conn.cursor()
        c.execute("DELETE FROM categories WHERE category_id=?", (cat_id,))
        conn.commit()
        conn.close()
        messagebox.showinfo("Deleted", f"Category '{cat_name}' deleted")
        load_categories()

    tk.Button(frame, text="Delete Selected", command=delete_category).pack(pady=5)
    load_categories()


# ------------------ ADD ITEM ------------------
def add_item_window():
    win = tk.Toplevel(root)
    win.title("Add Item")
    win.geometry("600x400")
    win.transient(root)
    win.grab_set()

    frame = tk.Frame(win, padx=20, pady=20)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text="Item Name:").grid(row=0, column=0, sticky="w")
    name_entry = tk.Entry(frame, width=30)
    name_entry.grid(row=0, column=1, pady=5)

    tk.Label(frame, text="Category:").grid(row=1, column=0, sticky="w")
    cat_var = tk.StringVar()
    cat_combo = ttk.Combobox(frame, textvariable=cat_var, width=27)
    cat_combo.grid(row=1, column=1, pady=5)

    def load_cat_options():
        conn = sqlite3.connect("inventory.db")
        c = conn.cursor()
        c.execute("SELECT category_name FROM categories")
        rows = [r[0] for r in c.fetchall()]
        conn.close()
        cat_combo["values"] = rows
    load_cat_options()

    tk.Label(frame, text="Quantity:").grid(row=2, column=0, sticky="w")
    qty_entry = tk.Entry(frame, width=30)
    qty_entry.grid(row=2, column=1, pady=5)

    tk.Label(frame, text="Recieved From:").grid(row=3, column=0, sticky="w")
    user_entry = tk.Entry(frame, width=30)
    user_entry.grid(row=3, column=1, pady=5)

    def save_item():
        name = name_entry.get().strip()
        cat = cat_var.get().strip()
        qty = qty_entry.get().strip()
        uname = user_entry.get().strip()

        if not name or not qty.isdigit() or not cat or not uname:
            messagebox.showerror("Error", "Fill all fields properly")
            return
        qty = int(qty)

        conn = sqlite3.connect("inventory.db")
        c = conn.cursor()

        c.execute("SELECT item_id FROM inventory WHERE item_name=?", (name,))
        row = c.fetchone()
        if row:  # update qty
            c.execute("UPDATE inventory SET quantity=quantity+?, category=? WHERE item_name=?", (qty, cat, name))
            item_id = row[0]
        else:  # new
            c.execute("INSERT INTO inventory (item_name, category, quantity) VALUES (?, ?, ?)", (name, cat, qty))
            item_id = c.lastrowid

        c.execute("""INSERT INTO transactions 
                     (item_id, item_name, category, quantity, txn_type, user_name) 
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (item_id, name, cat, qty, "IN", uname))

        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Item saved successfully")
        win.destroy()

    tk.Button(frame, text="Save", command=save_item).grid(row=4, column=1, pady=15)


# ------------------ REMOVE ITEM ------------------
def remove_item_window():
    win = tk.Toplevel(root)
    win.title("Remove Item")
    win.geometry("700x500")
    win.transient(root)
    win.grab_set()

    frame = tk.Frame(win, padx=20, pady=20)
    frame.pack(fill="both", expand=True)

    tk.Label(frame, text="Search Name:").grid(row=0, column=0, sticky="w")
    search_entry = tk.Entry(frame, width=30)
    search_entry.grid(row=0, column=1, padx=5)

    cols = ("ID", "Name", "Category", "Qty")
    tree = ttk.Treeview(frame, columns=cols, show="headings", height=8)
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.grid(row=1, column=0, columnspan=3, pady=10)

    def search_items():
        val = f"%{search_entry.get()}%"
        conn = sqlite3.connect("inventory.db")
        c = conn.cursor()
        c.execute("SELECT * FROM inventory WHERE item_name LIKE ?", (val,))
        rows = c.fetchall()
        conn.close()
        for r in tree.get_children():
            tree.delete(r)
        for r in rows:
            tree.insert("", "end", values=r)

    tk.Button(frame, text="Search", command=search_items).grid(row=0, column=2)

    tk.Label(frame, text="Quantity to Remove:").grid(row=2, column=0, sticky="w")
    qty_entry = tk.Entry(frame, width=30)
    qty_entry.grid(row=2, column=1, pady=5)

    tk.Label(frame, text="Given to:").grid(row=3, column=0, sticky="w")
    user_entry = tk.Entry(frame, width=30)
    user_entry.grid(row=3, column=1, pady=5)

    def remove_item():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select item")
            return
        qty = qty_entry.get().strip()
        uname = user_entry.get().strip()
        if not qty.isdigit() or not uname:
            messagebox.showerror("Error", "Fill details properly")
            return
        qty = int(qty)

        item_id, name, cat, current_qty = tree.item(selected[0], "values")
        current_qty = int(current_qty)
        if qty > current_qty:
            messagebox.showerror("Error", "Not enough stock")
            return

        conn = sqlite3.connect("inventory.db")
        c = conn.cursor()
        c.execute("UPDATE inventory SET quantity=quantity-? WHERE item_id=?", (qty, item_id))
        c.execute("""INSERT INTO transactions 
                     (item_id, item_name, category, quantity, txn_type, user_name) 
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (item_id, name, cat, qty, "OUT", uname))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Item removed successfully")
        win.destroy()

    tk.Button(frame, text="Remove", command=remove_item).grid(row=4, column=1, pady=15)


# ------------------ VIEW INVENTORY ------------------
def view_inventory():
    win = tk.Toplevel(root)
    win.title("Inventory")
    win.geometry("800x500")
    win.transient(root)
    win.grab_set()

    # Added a small filter frame so we can keep the original layout and only add the Category filter
    filter_frame = tk.Frame(win, padx=10, pady=10)
    filter_frame.pack(fill="x")

    tk.Label(filter_frame, text="Search Name:").grid(row=0, column=0, padx=5)
    search_entry = tk.Entry(filter_frame, width=20)
    search_entry.grid(row=0, column=1, padx=5)

    tk.Label(filter_frame, text="Category:").grid(row=0, column=2, padx=5)
    cat_var = tk.StringVar(value="All")
    cat_combo = ttk.Combobox(filter_frame, textvariable=cat_var, width=20)
    # load categories from DB
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()
    c.execute("SELECT category_name FROM categories")
    cats = [r[0] for r in c.fetchall()]
    conn.close()
    cat_combo["values"] = ["All"] + cats
    cat_combo.grid(row=0, column=3, padx=5)

    cols = ("ID", "Name", "Category", "Qty")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=15)
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack(fill="both", expand=True, pady=10)

    def load_items():
        val = f"%{search_entry.get()}%"
        cat = cat_var.get()
        conn = sqlite3.connect("inventory.db")
        c = conn.cursor()
        if cat and cat != "All":
            c.execute("SELECT * FROM inventory WHERE item_name LIKE ? AND category=?", (val, cat))
        else:
            c.execute("SELECT * FROM inventory WHERE item_name LIKE ?", (val,))
        rows = c.fetchall()
        conn.close()
        for r in tree.get_children():
            tree.delete(r)
        for r in rows:
            tree.insert("", "end", values=r)

    tk.Button(filter_frame, text="Search", command=load_items).grid(row=0, column=4, padx=10)
    load_items()


# ------------------ VIEW TRANSACTIONS ------------------
def view_transactions():
    win = tk.Toplevel(root)
    win.title("Transactions")
    win.geometry("1100x600")
    win.transient(root)
    win.grab_set()

    filter_frame = tk.Frame(win, padx=10, pady=10)
    filter_frame.pack(fill="x")

    tk.Label(filter_frame, text="Search Name:").grid(row=0, column=0, padx=5)
    search_entry = tk.Entry(filter_frame, width=20)
    search_entry.grid(row=0, column=1, padx=5)

    tk.Label(filter_frame, text="Type:").grid(row=0, column=2, padx=5)
    type_var = tk.StringVar(value="All")
    type_combo = ttk.Combobox(filter_frame, textvariable=type_var, values=["All", "IN", "OUT"], width=7)
    type_combo.grid(row=0, column=3, padx=5)

    # Added Category filter here (minimal change)
    tk.Label(filter_frame, text="Category:").grid(row=0, column=4, padx=5)
    cat_var = tk.StringVar(value="All")
    cat_combo = ttk.Combobox(filter_frame, textvariable=cat_var, width=15)
    # load categories from DB
    conn = sqlite3.connect("inventory.db")
    c = conn.cursor()
    c.execute("SELECT category_name FROM categories")
    cats = [r[0] for r in c.fetchall()]
    conn.close()
    cat_combo["values"] = ["All"] + cats
    cat_combo.grid(row=0, column=5, padx=5)

    # Added User filter here (minimal change)
    tk.Label(filter_frame, text="User:").grid(row=0, column=6, padx=5)
    user_entry = tk.Entry(filter_frame, width=15)
    user_entry.grid(row=0, column=7, padx=5)

    tk.Label(filter_frame, text="From:").grid(row=0, column=8, padx=5)
    from_cal = DateEntry(filter_frame, width=12, maxdate=datetime.today(), date_pattern="yyyy-mm-dd")
    from_cal.grid(row=0, column=9, padx=5)

    tk.Label(filter_frame, text="To:").grid(row=0, column=10, padx=5)
    to_cal = DateEntry(filter_frame, width=12, maxdate=datetime.today(), date_pattern="yyyy-mm-dd")
    to_cal.grid(row=0, column=11, padx=5)

    def load_transactions():
        val = f"%{search_entry.get()}%"
        ttype = type_var.get()
        from_date = from_cal.get_date()
        to_date = to_cal.get_date()
        cat = cat_var.get()
        uname = f"%{user_entry.get()}%"

        if to_date < from_date:
            messagebox.showerror("Error", "To Date must be after From Date")
            return

        conn = sqlite3.connect("inventory.db")
        c = conn.cursor()
        query = """SELECT txn_id, item_id, item_name, category, quantity, txn_type, txn_date, user_name 
                   FROM transactions 
                   WHERE item_name LIKE ? 
                   AND user_name LIKE ?
                   AND DATE(txn_date) BETWEEN ? AND ?"""
        params = (val, uname, from_date, to_date)

        if ttype != "All":
            query += " AND txn_type=?"
            params = params + (ttype,)
        if cat != "All":
            query += " AND category=?"
            params = params + (cat,)

        c.execute(query, params)
        rows = c.fetchall()
        conn.close()

        for r in tree.get_children():
            tree.delete(r)
        for r in rows:
            tree.insert("", "end", values=r)

    tk.Button(filter_frame, text="Apply Filter", command=load_transactions).grid(row=0, column=12, padx=10)

    cols = ("Txn ID", "Item ID", "Name", "Category", "Qty", "Type", "Date", "User")
    tree = ttk.Treeview(win, columns=cols, show="headings", height=20)
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=120)
    tree.pack(fill="both", expand=True, pady=10)

    load_transactions()


# ------------------ MAIN UI ------------------
root = tk.Tk()
root.title("Inventory Management")
root.state("zoomed")

btn_frame = tk.Frame(root, pady=20)
btn_frame.pack()

tk.Button(btn_frame, text="Add Item", width=20, command=add_item_window).grid(row=0, column=0, padx=10)
tk.Button(btn_frame, text="Remove Item", width=20, command=remove_item_window).grid(row=0, column=1, padx=10)
tk.Button(btn_frame, text="View Inventory", width=20, command=view_inventory).grid(row=0, column=2, padx=10)
tk.Button(btn_frame, text="View Transactions", width=20, command=view_transactions).grid(row=0, column=3, padx=10)
tk.Button(btn_frame, text="Manage Categories", width=20, command=manage_categories).grid(row=0, column=4, padx=10)

init_db()
root.mainloop()
