import random
import sqlite3
import tkinter as tk

# Connect to the database
conn = sqlite3.connect('smart_key.db')

# Check if the table exists
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
table_exists = cursor.fetchone() is not None

# If the table doesn't exist, create it
if not table_exists:
    conn.execute('''CREATE TABLE users
                    (id INTEGER PRIMARY KEY,
                     name TEXT NOT NULL,
                     pin TEXT NOT NULL,
                     active INTEGER NOT NULL)''')
    print('Table created successfully')


# Insert three random users into the database
users = [('John Doe', '1234', 1),
         ('Jane Smith', '5678', 1),
         ('Bob Johnson', '4321', 0)]
cursor.executemany('INSERT INTO users (name, pin, active) VALUES (?, ?, ?)', users)

# Commit the changes to the database
conn.commit()



class SmartKey:
    def __init__(self, master):
        self.master = master
        master.title('SmartKey')

        # Create the buttons for the main screen
        self.bell_button = tk.Button(master, text='Pozvoniti', command=self.ring_bell)
        self.bell_button.pack(side=tk.TOP, padx=10, pady=10)
        self.unlock_button = tk.Button(master, text='Otključati', command=self.unlock_door)
        self.unlock_button.pack(side=tk.TOP, padx=10, pady=10)

        # Create the user form
        self.user_frame = tk.Frame(master)
        self.user_frame.pack(side=tk.TOP, padx=10, pady=10)
        self.pin_label = tk.Label(self.user_frame, text='PIN')
        self.pin_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.pin_entry = tk.Entry(self.user_frame, show='*')
        self.pin_entry.grid(row=1, column=1, padx=5, pady=5)
        self.name_label = tk.Label(self.user_frame, text='Ime i prezime')
        self.name_label.grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.name_entry = tk.Entry(self.user_frame)
        self.name_entry.grid(row=2, column=1, padx=5, pady=5)
        self.add_button = tk.Button(self.user_frame, text='Spremi', command=self.add_user)
        self.add_button.grid(row=3, column=0, padx=5, pady=5)
        self.cancel_button = tk.Button(self.user_frame, text='Odustani', command=self.cancel_user)
        self.cancel_button.grid(row=3, column=1, padx=5, pady=5)
        self.delete_button = tk.Button(self.user_frame, text='Izbriši', command=self.delete_user)
        self.delete_button.grid(row=3, column=2, padx=5, pady=5)

        # Create the status bar
        self.status = tk.Label(master, text='Dobrodošli!', bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    def ring_bell(self):
        self.status.config(text='Zvono je aktivirano! Netko će uskoro doći i otvoriti vrata.')

    def unlock_door(self):
        pin = self.pin_entry.get()
        name = self.get_name(pin)
        if name:
            self.status.config(text=f'Uspješno unesen PIN! Dobro došli {name}!')
        else:
            self.status.config

    def add_user(self):
        name = self.name_entry.get()
        pin = self.pin_entry.get()
        if name and pin:
            # Insert the new user into the database
            conn.execute('INSERT INTO users (name, pin, active) VALUES (?, ?, ?)', (name, pin, 1))
            conn.commit()
            self.status.config(text=f'Korisnik {name} je dodan u bazu podataka.')
        else:
            self.status.config(text='Unesite ime i PIN.')
    def cancel_user(self):
        self.name_entry.delete(0, tk.END)
        self.pin_entry.delete(0, tk.END)
        self.status.config(text='Unos otkazan.')
        
    def delete_user(self):
        name = self.name_entry.get()
        conn.execute('DELETE FROM users WHERE name=?', (name,))
        conn.commit()
        self.status.config(text=f'Korisnik {name} je uspješno izbrisan iz baze podataka.')

    def get_name(self, pin):
        cursor = conn.execute('SELECT name FROM users WHERE pin=? AND active=1', (pin,))
        row = cursor.fetchone()
        return row[0] if row else None


if __name__ == '__main__':
    root = tk.Tk()
    SmartKey(root)
    root.mainloop()
