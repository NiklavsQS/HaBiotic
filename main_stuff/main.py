import PySimpleGUI as sg  # Importējam PySimpleGUI bibliotēku saskarnei
import datetime  # Importējam datetime bibliotēku laikam
import sqlite3 as sq  # Importējam sqlite3 bibliotēku datubāzēm
from cryptography.fernet import Fernet  # Importējam Fernet kriptogrāfijai
import requests as rq  # Importējam requests moduli API
import os # importējam os bibliotēku failu meklēšanai

# SQL dati
lietotaja_parbaude = "SELECT * FROM users WHERE user_name = ? AND password = ?"
nepareiza_parole = "SELECT * FROM users WHERE user_name = ?"
lietotaja_id = "SELECT id FROM users WHERE user_name = ?"
paradumu_atlase = "SELECT * FROM habits WHERE user_id = ?"

# Izveido vai nolasa atslēgu
if os.path.exists('key.key'):
    with open('key.key', 'rb') as keyfile:
        key = keyfile.read()
        if len(key) == 0:
            key = Fernet.generate_key()
            with open('key.key', 'wb') as keyfile:
                keyfile.write(key)
else:
    key = Fernet.generate_key()
    with open('key.key', 'wb') as keyfile:
            keyfile.write(key)

class HaBioticLogin:
    def __init__(self):
        sg.theme('DarkAmber')  # Noformējums PySimpleGUI
        self.layout = [                     # Pieslēgšanās loga izkārtojums
            [sg.Text('Lietotājvārds'), sg.Stretch(), sg.InputText(key='Uname')],  
            [sg.Text('Parole'), sg.Stretch(), sg.InputText(key='Pass', password_char='*')],  
            [sg.Button('Pieslēgties'), sg.Button('Reģistrēties'), sg.Button('Aizvērt')]  
        ]
        self.window = sg.Window("Pieslēgšanās", self.layout, icon=r'HaBiotic/assets/download.ico')  # Pieslēgšanās loga izveide

    def run(self):        # Palaiž pieslēgšanās logu
        f = Fernet(key)  
        while True:
            self.conn = sq.connect('dati.db')       # Savienojas ar datubāzi un izveido datubāzes, ja to nav
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
            event, values = self.window.read()  # Nolasa informāciju no loga
            if event in (sg.WIN_CLOSED, 'Aizvērt'):  # Aizvērt pogas notikums
                return None
            if event == 'Pieslēgties':  # Pieslēgšanās pogas notikums
                self.c.execute("SELECT * FROM users WHERE user_name=?", (values['Uname'],))  # Pārbauda vai lietotāja ievadītie dati ir pareizi
                self.user = self.c.fetchone()
                if self.user:
                    parole_check = f.decrypt(self.user[3]).decode()        # Atšifrē paroli un salīdzina
                    if parole_check == values['Pass']:
                        self.window.close()  
                        user_id = self.user[0]  
                        return user_id  
                    else:
                        sg.popup_ok('Invalid password')  # Ja parole ir nepareiza, izvada ziņu
                else:
                    sg.popup_ok('Lietotājs neeksistē')  # Ja lietotājs neeksistē, izvada ziņu
            elif event == 'Reģistrēties':  # Reģistrācijas pogas notikums
                self.window.close()  # Aizver pieslēgšanās logu
                user_id = self.register()  # Atver reģistrēšanās logu
                if user_id is not None:  # Ja reģistrācija ir veiksmīga, atgriež lietotāja ID
                    return user_id

    def register(self):      # Palaiž reģistrēšanās logu
        f = Fernet(key)  # Izveido fernet objektu, lai varētu izmantot atslēgu
        conn = sq.connect('dati.db')  # Savienojas ar datubāzi
        c = conn.cursor() 
        
        while True:
            n_uname = sg.popup_get_text('Ievadiet jaunu lietotājvārdu', title="Lietotājvārds")  # Jauna lietotājvārda ievades lauks
            if not n_uname: 
                sg.popup('Lietotājvārds netika ievadīts') # Ja ievades lauks ir tukšs, izvada ziņu
                return None  
                
            c.execute(nepareiza_parole, (n_uname,))
            user_check = c.fetchone()
            if user_check:  # Pārbauda vai lietotājvārds jau ir datubāzē
                sg.popup('Lietotājvārds jau pastāv')  # Ja lietotājvārds jau ir datubāzē, izvada ziņu
            else:
                break  # Pārstaj ciklu, ja lietotājvārds ir pieņemams
        
        while True:
            n_pass = sg.popup_get_text('Ievadiet jaunu paroli', title="Parole", password_char='')  # Jaunas paroles ievades lauks
            if not n_pass:  
                sg.popup('Parole netika ievadīts')  # Ja ievades lauks ir tukšs, izvada ziņu
                return None  
            else:
                break  # Pārstaj ciklu, ja parole ir pieņemama    

        while True:
            location = sg.popup_get_text('Ievadiet pilsētu laikapstākļiem (neobligāti)', title="Laikapstākļi")  # Lokācijas ievades lauks
            if not location:  # Ja neaizpilda lauku, beidz ciklu
                break  
            if location: # Ja aizpilda lauku, beidz ciklu
                break  
        if location != '':  # Ja aizpilda
            location_encrypted = f.encrypt(location.encode())  # Šifrē lokāciju
            password_encrypted = f.encrypt(n_pass.encode())  # Šifrē paroli

            new_user = (location_encrypted, n_uname, password_encrypted)  # Izveido kortežu ar jaunajiem lietotāja datiem
            c.execute("INSERT INTO users (city, user_name, password) VALUES (?, ?, ?)", new_user)  # Ievieto jaunos datus datubāzē
            conn.commit()  
        else:
            new_user = (None, n_uname, n_pass)  # Jaunie dati bez atrašanās vietas
            c.execute("INSERT INTO users (city, user_name, password) VALUES (?, ?, ?)", new_user)  # Ievieto jaunos datus datubāzē
            conn.commit()  

        return c.lastrowid  


class HaBiotic:
    def __init__(self, user_id):
        
        self.user_id = user_id  # Initialize the user ID
        self.now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")  # Iegūst pašreizējo datumu un laiku
        self.par = sq.connect('paradumi.db')  # Savienojas ar paradumu datubāzi
        self.fails = sq.connect('dati.db')  # Savienojas ar ievades datu datubāzi
        self.d = self.par.cursor()  
        self.c = self.fails.cursor()  
        # izveido datubāzes, ja to nav
        self.d.execute('''CREATE TABLE IF NOT EXISTS habits( 
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INT REFERENCES users(id),
              name BLOB
              )''')
        self.weather = self.dabut_laikapstaklus()  # Iegūst laikapstākļu datus
        self.layout = self.create_layout()  # Izkārtojums
        self.window = sg.Window("HaBiotic", self.layout, icon=r'HaBiotic/assets/download.ico')  # Izveido galveno logu
        

    def dabut_laikapstaklus(self):      # Metode laikapstākļu iegūšanai
            self.f = Fernet(key)  # Fernet objekts, lai varētu lietot šifrēšanu
            self.c.execute("SELECT city FROM users WHERE id=?", (self.user_id,))
            location_encrypted = self.c.fetchone()
            location = self.f.decrypt(location_encrypted[0]).decode() if location_encrypted else ''  # Atšifrē atrašanās vietu, ja iespējams
            
            # Izmanto requests lai iegūtu laikapstākļu datus no openweathermap API
            if location != '':
                APIkey = '468b7c127431d50c92409468e58abdc9'
                Url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={APIkey}&units=metric'
                try:
                    response = rq.get(Url)
                    response.raise_for_status()  
                    data = response.json()
                    return data  
                except rq.exceptions.RequestException as error:
                    print("Error:", error)  
                    return None  

    def create_layout(self):
        self.d.execute(paradumu_atlase, (self.user_id,))
        self.esosie_paradumii = [row[2] for row in self.d.fetchall()]  # Iegūst paradumus no datubāzes
        self.esosie_paradumi = []
        self.esosie_paradumi.extend(self.f.decrypt(i).decode() for i in self.esosie_paradumii)  # Atšifrē paradumu nosaukumus
        weather_data = self.weather.get('weather', [])  # Iegūst laikapstākļu datus
        weather_icon = weather_data[0].get('icon', '')  # Iegūst laikapstākļu ikonu
        temperature = float(self.weather.get('main', {}).get('temp', ''))  # Iegūst temperatūru

        icon_url = f'http://openweathermap.org/img/wn/{weather_icon}.png'  # Saite ikonai
        icon_response = rq.get(icon_url) 
        icon_data = icon_response.content 

        laiki = []
        
        # Cikls lai aprēķinātu laiku kopš pēdējās reizes, kad lietotājs ir atzīmējis paradumu
        for i in self.esosie_paradumii:
            self.c.execute("SELECT time FROM entries WHERE habit = ? AND user_id = ? ORDER BY id DESC LIMIT 1", (i, self.user_id,))
            times = self.c.fetchone()  
            if times is not None:
                time = times[0]  
                date_of_entry = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M') # Pārveido uz datetime objektu
                now_time = datetime.datetime.strptime(self.now, '%Y-%m-%d %H:%M')
                time_diff = now_time - date_of_entry # Aprēķina starpību
                laiki.append(time_diff)  # Pievieno laiku sarakstam
        # Galvenā loga izkārtojums
        layout = [
            [sg.Stretch(), sg.Image(key='Ikona', data=icon_data), sg.Text(f'Temperatūra šobrīd: {temperature}°C', key='Temp')],  
            [sg.Stretch(), sg.Text('Izveidojiet ieradumu vai izvēlieties kādu no esošajiem'), sg.Stretch()],
            [sg.Stretch(), sg.InputText(key='paradums'), sg.Stretch()],  # Ievades lauks jauniem ieradumiem
            [sg.Column([[sg.Checkbox(habit, key=f'checkbox_{i}'), sg.Text(laiki[i] if laiki else '')] for i, habit in enumerate(self.esosie_paradumi)])],  
            [sg.Stretch(), sg.Button('Turpināt'), sg.Button('Aizvērt'), sg.Stretch()]  
        ]
        return layout  # Atgriež izkārtojumu


    def run(self):    # Palaiž galveno logu
        while True:
            event, values = self.window.read()  # Nolasa vērtības no loga
            if event in (sg.WIN_CLOSED, 'Aizvērt'):  # Ja lietotājs aizver logu vai uzspiež pogu 'Aizvērt', logs aizveras
                break
            if event == 'Turpināt':  # Ja lietotājs nospiež pogu 'Turpināt'
                f = Fernet(key)
                new_entry_value = values['paradums']  # Iegūst laukā ievadīto 
                encrypted_habits = [f.encrypt(habit.encode()) for habit in self.esosie_paradumi]  # Šifrē eksistējošo paradumu nosaukumus
                selected_checks = [values[f'checkbox_{i}'] for i in range(len(self.esosie_paradumi))]  


                for i, habit in enumerate(self.esosie_paradumi):                # Cikls lai pārbaudītu checkbox
                    if selected_checks[i] and habit != new_entry_value:
                        self.c.execute("INSERT INTO entries (user_id, habit, time) VALUES (?, ?, ?)", (self.user_id, encrypted_habits[i], self.now))
                        self.fails.commit()  

                if new_entry_value:  # Pievieno jaunu ieradumu datubāzei
                    encrypted_new_entry = f.encrypt(new_entry_value.encode())
                    self.c.execute("INSERT INTO entries (user_id, habit, time) VALUES (?, ?, ?)", (self.user_id, encrypted_new_entry, self.now))
                    self.fails.commit()  
                    self.d.execute("INSERT INTO habits (user_id, name) VALUES (?, ?)", (self.user_id, encrypted_new_entry))
                    self.par.commit()

                # Atjaunina izkārtojumu
                self.layout = self.create_layout()  
                self.window.close()  # Aizver logu
                self.window = sg.Window("HaBiotic", self.layout, icon=r'assets/download.ico')  # Izveido logu ar jauno izvietojumu 

        # Aizver savienojumus ar datubāzēm
        self.par.close()   
        self.fails.close()  
        self.window.close()  


if __name__ == "__main__":
    login_app = HaBioticLogin()  
    user_id = login_app.run() 
    if user_id is not None:  
        app = HaBiotic(user_id)  
        app.run()  
