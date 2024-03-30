import PySimpleGUI as sg
import datetime
import sqlite3 as sq
from cryptography.fernet import Fernet
import requests as rq

# SQL queries
lietotaja_parbaude = "SELECT * FROM users WHERE user_name = ? AND password = ?"
nepareiza_parole = "SELECT * FROM users WHERE user_name = ?"
lietotaja_id = "SELECT id FROM users WHERE user_name = ?"
paradumu_atlase = "SELECT * FROM habits WHERE user_id = ?"

# Generate or read the encryption key
with open('key.key', 'rb') as keyfile:
    key = keyfile.read()
    if len(key) == 0:
        key = Fernet.generate_key()
        with open('key.key', 'wb') as keyfile:
            keyfile.write(key)

class HaBioticLogin:
    def __init__(self):
        sg.theme('DarkAmber')
        # Login window layout
        self.layout = [
            [sg.Text('Username'), sg.Stretch(), sg.InputText(key='Uname')],
            [sg.Text('Password'), sg.Stretch(), sg.InputText(key='Pass', password_char='*')],
            [sg.Button('Login'), sg.Button('Register'), sg.Button('Cancel')]
        ]
        self.window = sg.Window("Login", self.layout)

    def run(self):
        f = Fernet(key)
        while True:
            self.conn = sq.connect('dati.db')
            self.c = self.conn.cursor()
            self.c.execute('''CREATE TABLE IF NOT EXISTS users(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   city BLOB,
                   user_name TEXT,
                   password BLOB   
             )''')
        
            self.c.execute('''CREATE TABLE IF NOT EXISTS entries(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   user_id INT REFERENCES users(id),
                   habit BLOB,
                   time TEXT   
                   )''')
            event, values = self.window.read()
            if event in (sg.WIN_CLOSED, 'Cancel'):
                return None
            if event == 'Login':
                # Check if user exists and password is correct
                self.c.execute("SELECT * FROM users WHERE user_name=?", (values['Uname'],))
                self.user = self.c.fetchone()
                if self.user:
                    # Decrypt password and check if it matches
                    parole_check = f.decrypt(self.user[3]).decode()
                    if parole_check == values['Pass']:

                        self.window.close()
                        user_id = self.user[0]
                        return user_id  # Return the user ID
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
        f = Fernet(key)
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
                break    

        while True:
            Atrvieta = sg.popup_get_text('Ievadi atrašanās vietu priekš laikapstākļu noteikšanas (neobligāti)', title="Atrašanās vieta")
            if not Atrvieta:
                break
            if Atrvieta:
                break
        if Atrvieta != '':
            Atrvieta_en = f.encrypt(Atrvieta.encode())
            n_pass_en = f.encrypt(n_pass.encode())

            new_user = (Atrvieta_en, n_uname, n_pass_en)
            c.execute("INSERT INTO users (city, user_name, password) VALUES (?, ?, ?)", new_user)
            conn.commit()
        else:
            # If location is not provided, insert NULL
            new_user = (None, n_uname, n_pass)
            c.execute("INSERT INTO users (city, user_name, password) VALUES (?, ?, ?)", new_user)
            conn.commit()

        
        return c.lastrowid  # Return the last inserted row ID


class HaBiotic:
    def __init__(self, user_id):
        
        self.user_id = user_id
        self.now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.par = sq.connect('paradumi.db')
        self.fails = sq.connect('dati.db')
        self.d = self.par.cursor()
        self.c = self.fails.cursor()
        # Create tables if they do not exist
        self.d.execute('''CREATE TABLE IF NOT EXISTS habits(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INT REFERENCES users(id),
              name BLOB
              )''')
        self.weather = self.dabut_laikapstaklus()
        self.layout = self.create_layout()  # Initialize layout
        self.window = sg.Window("HaBiotic", self.layout)
 

    def dabut_laikapstaklus(self):
            self.f = Fernet(key)
            self.c.execute("SELECT city FROM users WHERE id=?", (self.user_id,))
            atrvieta_en = self.c.fetchone()
            Atrvieta_en = atrvieta_en[0]
            Atrvieta = self.f.decrypt(Atrvieta_en).decode() if Atrvieta_en else ''
            
            if Atrvieta != '':
                APIkey = '468b7c127431d50c92409468e58abdc9'
                Url = f'http://api.openweathermap.org/data/2.5/weather?q={Atrvieta}&appid={APIkey}&units=metric'
                try:
                    atbilde = rq.get(Url)
                    atbilde.raise_for_status()  # Raise an exception for 4xx and 5xx errors
                    dati = atbilde.json()
                    return dati
                except rq.exceptions.RequestException as error:
                    print("Radās kļūda:", error)
                    return None

    def create_layout(self):
        # Fetch existing habits from the database
        self.d.execute(paradumu_atlase, (self.user_id,))
        self.esosie_paradumii = [row[2] for row in self.d.fetchall()]
        self.esosie_paradumi = []
        self.esosie_paradumi.extend(self.f.decrypt(i).decode() for i in self.esosie_paradumii)
        weather_data = self.weather.get('weather', [])
        weather_icon = weather_data[0].get('icon', '')
        temperature = float(self.weather.get('main', {}).get('temp', ''))

        icon_url = f'http://openweathermap.org/img/wn/{weather_icon}.png'
        icon_response = rq.get(icon_url)
        icon_data = icon_response.content

        laiki = []
        for i in self.esosie_paradumii:
            self.c.execute("SELECT time FROM entries WHERE habit = ? AND user_id = ? ORDER BY id DESC LIMIT 1", (i, self.user_id,))
            times = self.c.fetchone() 
            if times is not None :
                time = times[0]
                # Convert the date string to a datetime object
                date_of_entry = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
                now_time = datetime.datetime.strptime(self.now, '%Y-%m-%d %H:%M')
                # Calculate the time difference
                time_diff = now_time - date_of_entry
                laiki.append(time_diff)

        # Main window layout
        layout = [
            [sg.Stretch(), sg.Image(key='Ikona', data=icon_data),
             sg.Text(f'Temperatūra šobrīd: {temperature}°C', key='Temp')],
            [sg.Text('Enter habit or select from existing'), sg.Stretch(), sg.InputText(key='paradums')],
            [sg.Column([[sg.Checkbox(habit, key=f'checkbox_{i}'), sg.Text(laiki[i] if laiki is not None else '')] for i, habit in enumerate(self.esosie_paradumi)])],
            [sg.Stretch(), sg.Button('Submit'), sg.Button('Cancel'), sg.Stretch()]
        ]
        return layout
    
    def run(self):
        while True:
            event, values = self.window.read()
            if event in (sg.WIN_CLOSED, 'Cancel'):
                break
            if event == 'Submit':
                # Encrypt habit names
                f = Fernet(key)
                new_entry_value = values['paradums']
                encrypted_habits = [f.encrypt(habit.encode()) for habit in self.esosie_paradumi]
                selected_checks = [values[f'checkbox_{i}'] for i in range(len(self.esosie_paradumi))]

                for i, habit in enumerate(self.esosie_paradumi):
                    if selected_checks[i] and habit != new_entry_value:
                        # Insert checked habits
                        self.c.execute("INSERT INTO entries (user_id, habit, time) VALUES (?, ?, ?)", (self.user_id, encrypted_habits[i], self.now))
                        self.fails.commit()

                if new_entry_value:
                    # Insert new habit
                    encrypted_new_entry = f.encrypt(new_entry_value.encode())
                    self.c.execute("INSERT INTO entries (user_id, habit, time) VALUES (?, ?, ?)", (self.user_id, encrypted_new_entry, self.now))
                    self.fails.commit()
                    self.d.execute("INSERT INTO habits (user_id, name) VALUES (?, ?)", (self.user_id, encrypted_new_entry))
                    self.par.commit()

                # Recreate layout to reflect changes
                self.layout = self.create_layout()
                self.window.close()
                self.window = sg.Window("HaBiotic", self.layout)

        self.par.close()
        self.fails.close()
        self.window.close()

if __name__ == "__main__":
    login_app = HaBioticLogin()
    user_id = login_app.run()
    if user_id is not None:
        app = HaBiotic(user_id)
        app.run()
