import PySimpleGUI as sg
import datetime
import sqlite3 as sq
from cryptography.fernet import Fernet as Fer
# SQL queries
lietotaja_parbaude = "SELECT * FROM users WHERE user_name = ? AND password = ?"
nepareiza_parole = "SELECT * FROM users WHERE user_name = ?"
lietotaja_id = "SELECT id FROM users WHERE user_name = ?"
paradumu_atlase = "SELECT * FROM habits WHERE user_id = ?"

class HaBioticLogin:
    def __init__(self):
        sg.theme('SystemDefault')
        # Login window layout
        self.layout = [
            [sg.Text('Username'), sg.InputText(key='Uname')],
            [sg.Text('Password'), sg.InputText(key='Pass', password_char='*')],
            [sg.Button('Login'), sg.Button('Register'), sg.Button('Cancel')]
        ]
        self.window = sg.Window("Login", self.layout)

    def run(self):
        while True:
            event, values = self.window.read()
            if event in (sg.WIN_CLOSED, 'Cancel'):
                return None
            if event == 'Login':
                # Connect to the database
                self.conn = sq.connect('dati.db')
                self.c = self.conn.cursor()
                # Check if user exists and password is correct
                self.c.execute("SELECT * FROM users WHERE user_name=?", (values['Uname'],))
                self.user = self.c.fetchone()
                if self.user:
                    if self.user[1] == values['Pass']:  # Check if password matches
                        self.window.close()
                        return self.user[0]  # Return the user ID
                    else:
                        sg.popup_ok('Invalid password')
                else:
                    sg.popup_ok('User does not exist. Please register or try a different username.')
            elif event == 'Register':
                self.window.close()
                user_id = self.register()  # Get user ID after registration
                if user_id is not None:
                    return user_id  # Return the user ID after registration

        self.window.close()

    def register(self):
        conn = sq.connect('dati.db')
        c = conn.cursor()
        
        while True:
            n_uname = sg.popup_get_text('Ievadi jauno lietotājvārdu', title="Username")
            if not n_uname:
                sg.popup('Jaunais lietotājvārds netika ievadīts')
                return None  # Return None if user cancels registration
                
            c.execute(nepareiza_parole, (n_uname,))
            user_check = c.fetchone()
            if user_check:
                sg.popup('Lietotājs jau pastāv')
            else:
                break  # Break the loop if the username is valid
        
        while True:
            n_pass = sg.popup_get_text('Ievadi jauno paroli', title="Password", password_char='*')
            if not n_pass:
                sg.popup('Jaunā parole netika ievadīta')
                return None  # Return None if user cancels registration
            else:
                break  # Break the loop if the password is valid
        
        new_user = (n_uname, n_pass)
        c.execute("INSERT INTO users (user_name, password) VALUES (?, ?)", new_user)
        conn.commit()
        
        return c.lastrowid  # Return the last inserted row ID


class HaBiotic:
    def __init__(self, user_id):
        with open('key.key', 'rb') as keyread:
            self.key = keyread.read()
        if len(self.key) == 0:
            keygen = Fer.generate_key()
            self.key = keygen
            with open('key.key', 'wb') as keywrite:
                keywrite.write(self.key)
        self.user_id = user_id
        self.now = datetime.datetime.now().strftime("%Y-%m-%d")
        self.par = sq.connect('paradumi.db')
        self.fails = sq.connect('dati.db')
        self.d = self.par.cursor()
        self.c = self.fails.cursor()
        # Create tables if they do not exist
        self.d.execute('''CREATE TABLE IF NOT EXISTS habits(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INT REFERENCES users(id),
              name TEXT
              )''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS users(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_name TEXT,
              password TEXT   
        )''')

        self.c.execute('''CREATE TABLE IF NOT EXISTS entries(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INT REFERENCES users(id),
              habit TEXT,
              time TEXT   
              )''')

        self.layout = self.create_layout()  # Initialize layout
        self.window = sg.Window("HaBiotic", self.layout)

    def create_layout(self):
        # Fetch existing habits from the database
        self.d.execute(paradumu_atlase, (self.user_id,))
        self.esosie_paradumi = [row[2] for row in self.d.fetchall()]
        # Main window layout
        layout = [
            [sg.Text('Enter habit or select from existing'), sg.InputText(key='paradums')],
            [sg.Column([[sg.Checkbox(habit, key=f'checkbox_{i}')] for i, habit in enumerate(self.esosie_paradumi)])],
            [sg.Button('Submit'), sg.Button('Cancel')]
        ]
        return layout

    def run(self):
        while True:
            f = Fer(self.key)
            event, values = self.window.read()
            if event in (sg.WIN_CLOSED, 'Cancel'):
                break
            if event == 'Submit':
                
                g = 0
                gow = []
                for i in self.esosie_paradumi:
                    g += 1
                    if 'checkbox_{g}':
                        gow.append(i) 
                new_entry_value = values['paradums']
                for entry in new_entry_value.split(','):
                    entry = entry.strip()
                    if entry:
                        if entry not in self.esosie_paradumi:
                            # Insert new entry into entries and habits tables

                            piev = (self.user_id, entry, self.now)
                            self.c.execute("INSERT INTO entries (user_id ,habit ,time) VALUES (?, ?, ?)", piev)
                            self.fails.commit()
                            self.d.execute("INSERT INTO habits (user_id ,name) VALUES (?, ?)", (self.user_id, entry))
                            self.par.commit()
                for a in gow:
                    if a != new_entry_value:
                        piev = (self.user_id, a, self.now)
                        self.c.execute("INSERT INTO entries (user_id ,habit ,time) VALUES (?, ?, ?)", piev)
                        self.fails.commit()

                # Recreate layout to reflect changes
                self.layout = self.create_layout()
                self.window.close()
                self.window = sg.Window("HaBiotic", self.layout)

        self.par.close()
        self.fails.close()
        self.window.close()
        self.fails.close()

if __name__ == "__main__":
    login_app = HaBioticLogin()
    user_id = login_app.run()
    if user_id is not None:
        app = HaBiotic(user_id)
        app.run()
