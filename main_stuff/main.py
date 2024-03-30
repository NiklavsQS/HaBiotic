import PySimpleGUI as sg  # Importing PySimpleGUI for creating GUI
import datetime  # Importing datetime module for handling dates and times
import sqlite3 as sq  # Importing sqlite3 for working with SQLite databases
from cryptography.fernet import Fernet  # Importing Fernet from cryptography module for encryption
import requests as rq  # Importing requests module for making HTTP requests

# SQL queries for database operations
lietotaja_parbaude = "SELECT * FROM users WHERE user_name = ? AND password = ?"
nepareiza_parole = "SELECT * FROM users WHERE user_name = ?"
lietotaja_id = "SELECT id FROM users WHERE user_name = ?"
paradumu_atlase = "SELECT * FROM habits WHERE user_id = ?"

# Generate or read the encryption key
with open('key.key', 'rb') as keyfile:
    key = keyfile.read()
    # If key file is empty, generate a new key and save it
    if len(key) == 0:
        key = Fernet.generate_key()
        with open('key.key', 'wb') as keyfile:
            keyfile.write(key)

# Class for the login window
class HaBioticLogin:
    def __init__(self):
        sg.theme('DarkAmber')  # Set the theme for PySimpleGUI elements
        # Define the layout for the login window
        self.layout = [
            [sg.Text('Username'), sg.Stretch(), sg.InputText(key='Uname')],  # Username input field
            [sg.Text('Password'), sg.Stretch(), sg.InputText(key='Pass', password_char='*')],  # Password input field
            [sg.Button('Login'), sg.Button('Register'), sg.Button('Cancel')]  # Login, Register, and Cancel buttons
        ]
        self.window = sg.Window("Login", self.layout)  # Create the login window with the specified layout

    # Method to run the login window
    def run(self):
        f = Fernet(key)  # Create a Fernet object with the encryption key
        while True:
            # Connect to the database and create necessary tables if they don't exist
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
            event, values = self.window.read()  # Read events and values from the window
            if event in (sg.WIN_CLOSED, 'Cancel'):  # If user closes the window or clicks Cancel button, return None
                return None
            if event == 'Login':  # If user clicks the Login button
                # Check if user exists and password is correct
                self.c.execute("SELECT * FROM users WHERE user_name=?", (values['Uname'],))
                self.user = self.c.fetchone()
                if self.user:
                    # Decrypt password and check if it matches
                    parole_check = f.decrypt(self.user[3]).decode()
                    if parole_check == values['Pass']:
                        self.window.close()  # Close the login window
                        user_id = self.user[0]  # Get the user ID
                        return user_id  # Return the user ID
                    else:
                        sg.popup_ok('Invalid password')  # Show a popup for invalid password
                else:
                    sg.popup_ok('User does not exist. Please register or try a different username.')  # Show a popup for non-existent user
            elif event == 'Register':  # If user clicks the Register button
                self.window.close()  # Close the login window
                user_id = self.register()  # Call the register method to handle registration
                if user_id is not None:  # If registration is successful, return the user ID
                    return user_id

        self.window.close()  # Close the login window

    # Method to handle user registration
    def register(self):
        f = Fernet(key)  # Create a Fernet object with the encryption key
        conn = sq.connect('dati.db')  # Connect to the database
        c = conn.cursor()  # Create a cursor object for database operations
        
        while True:
            n_uname = sg.popup_get_text('Enter new username', title="Username")  # Get new username from user
            if not n_uname:  # If username is empty
                sg.popup('New username not entered')  # Show a popup message
                return None  # Return None if user cancels registration
                
            c.execute(nepareiza_parole, (n_uname,))
            user_check = c.fetchone()
            if user_check:  # If the username already exists in the database
                sg.popup('Username already exists')  # Show a popup message
            else:
                break  # Break the loop if the username is valid
        
        while True:
            n_pass = sg.popup_get_text('Enter new password', title="Password", password_char='*')  # Get new password from user
            if not n_pass:  # If password is empty
                sg.popup('New password not entered')  # Show a popup message
                return None  # Return None if user cancels registration
            else:
                break  # Break the loop if the password is entered    

        while True:
            location = sg.popup_get_text('Enter location for weather (optional)', title="Location")  # Get location for weather
            if not location:  # If location is empty
                break  # Break the loop
            if location:
                break  # Break the loop if location is entered
        if location != '':  # If location is not empty
            location_encrypted = f.encrypt(location.encode())  # Encrypt the location
            password_encrypted = f.encrypt(n_pass.encode())  # Encrypt the password

            new_user = (location_encrypted, n_uname, password_encrypted)  # Create a tuple for new user data
            c.execute("INSERT INTO users (city, user_name, password) VALUES (?, ?, ?)", new_user)  # Insert new user data into the database
            conn.commit()  # Commit the transaction
        else:
            # If location is not provided, insert NULL
            new_user = (None, n_uname, n_pass)  # Create a tuple for new user data with NULL location
            c.execute("INSERT INTO users (city, user_name, password) VALUES (?, ?, ?)", new_user)  # Insert new user data into the database
            conn.commit()  # Commit the transaction

        return c.lastrowid  # Return the last inserted row ID


class HaBiotic:
    def __init__(self, user_id):
        
        self.user_id = user_id  # Initialize the user ID
        self.now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")  # Get the current date and time
        self.par = sq.connect('paradumi.db')  # Connect to the database for habits
        self.fails = sq.connect('dati.db')  # Connect to the database for entries
        self.d = self.par.cursor()  # Create a cursor object for habits database
        self.c = self.fails.cursor()  # Create a cursor object for entries database
        # Create tables if they do not exist
        self.d.execute('''CREATE TABLE IF NOT EXISTS habits(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INT REFERENCES users(id),
              name BLOB
              )''')
        self.weather = self.dabut_laikapstaklus()  # Get weather data
        self.layout = self.create_layout()  # Initialize layout
        self.window = sg.Window("HaBiotic", self.layout)  # Create the main window

    # Method to fetch weather data
    def dabut_laikapstaklus(self):
            self.f = Fernet(key)  # Create a Fernet object with the encryption key
            self.c.execute("SELECT city FROM users WHERE id=?", (self.user_id,))
            location_encrypted = self.c.fetchone()
            location = self.f.decrypt(location_encrypted[0]).decode() if location_encrypted else ''  # Decrypt location if available
            
            if location != '':
                APIkey = '468b7c127431d50c92409468e58abdc9'
                Url = f'http://api.openweathermap.org/data/2.5/weather?q={location}&appid={APIkey}&units=metric'
                try:
                    response = rq.get(Url)  # Make a GET request to the weather API
                    response.raise_for_status()  # Raise an exception for 4xx and 5xx errors
                    data = response.json()  # Convert response to JSON format
                    return data  # Return the weather data
                except rq.exceptions.RequestException as error:
                    print("Error:", error)  # Print error message
                    return None  # Return None if there's an error

    # Method to create the layout for the main window
    def create_layout(self):
        # Fetch existing habits from the database
        self.d.execute(paradumu_atlase, (self.user_id,))
        self.esosie_paradumii = [row[2] for row in self.d.fetchall()]  # Fetch habits from the database
        self.esosie_paradumi = []
        self.esosie_paradumi.extend(self.f.decrypt(i).decode() for i in self.esosie_paradumii)  # Decrypt habit names
        weather_data = self.weather.get('weather', [])  # Get weather data
        weather_icon = weather_data[0].get('icon', '')  # Get weather icon
        temperature = float(self.weather.get('main', {}).get('temp', ''))  # Get temperature

        icon_url = f'http://openweathermap.org/img/wn/{weather_icon}.png'  # URL for weather icon
        icon_response = rq.get(icon_url)  # Get weather icon
        icon_data = icon_response.content  # Get content of weather icon image

                # Initialize an empty list for time differences
        laiki = []
        
        # Iterate over the habits to calculate time differences
        for i in self.esosie_paradumii:
            self.c.execute("SELECT time FROM entries WHERE habit = ? AND user_id = ? ORDER BY id DESC LIMIT 1", (i, self.user_id,))
            times = self.c.fetchone()  # Fetch the latest entry time for each habit
            if times is not None:
                time = times[0]  # Extract the time value
                # Convert the date string to a datetime object
                date_of_entry = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
                now_time = datetime.datetime.strptime(self.now, '%Y-%m-%d %H:%M')
                # Calculate the time difference
                time_diff = now_time - date_of_entry
                laiki.append(time_diff)  # Append the time difference to the list

        # Main window layout
        layout = [
            [sg.Stretch(), sg.Image(key='Ikona', data=icon_data), sg.Text(f'Temperatūra šobrīd: {temperature}°C', key='Temp')],  # Weather icon and temperature display
            [sg.Text('Enter habit or select from existing'), sg.Stretch(), sg.InputText(key='paradums')],  # Input field for new habit
            [sg.Column([[sg.Checkbox(habit, key=f'checkbox_{i}'), sg.Text(laiki[i] if laiki else '')] for i, habit in enumerate(self.esosie_paradumi)])],  # Display existing habits and their time differences
            [sg.Stretch(), sg.Button('Submit'), sg.Button('Cancel'), sg.Stretch()]  # Submit and Cancel buttons
        ]
        return layout  # Return the layout

    # Method to run the main window
    def run(self):
        while True:
            event, values = self.window.read()  # Read events and values from the window
            if event in (sg.WIN_CLOSED, 'Cancel'):  # If user closes the window or clicks Cancel button, break the loop
                break
            if event == 'Submit':  # If user clicks the Submit button
                # Encrypt habit names
                f = Fernet(key)
                new_entry_value = values['paradums']  # Get the value entered in the input field
                encrypted_habits = [f.encrypt(habit.encode()) for habit in self.esosie_paradumi]  # Encrypt existing habit names
                selected_checks = [values[f'checkbox_{i}'] for i in range(len(self.esosie_paradumi))]  # Get the state of checkboxes

                # Iterate over existing habits to handle checked checkboxes
                for i, habit in enumerate(self.esosie_paradumi):
                    if selected_checks[i] and habit != new_entry_value:
                        # Insert checked habits into the entries database
                        self.c.execute("INSERT INTO entries (user_id, habit, time) VALUES (?, ?, ?)", (self.user_id, encrypted_habits[i], self.now))
                        self.fails.commit()  # Commit the transaction

                if new_entry_value:  # If a new habit is entered
                    # Insert new habit into the entries and habits databases
                    encrypted_new_entry = f.encrypt(new_entry_value.encode())
                    self.c.execute("INSERT INTO entries (user_id, habit, time) VALUES (?, ?, ?)", (self.user_id, encrypted_new_entry, self.now))
                    self.fails.commit()  # Commit the transaction
                    self.d.execute("INSERT INTO habits (user_id, name) VALUES (?, ?)", (self.user_id, encrypted_new_entry))
                    self.par.commit()  # Commit the transaction

                # Recreate layout to reflect changes
                self.layout = self.create_layout()  # Recreate the layout
                self.window.close()  # Close the window
                self.window = sg.Window("HaBiotic", self.layout)  # Create a new window with the updated layout

        # Close database connections and the window when the loop breaks
        self.par.close()  # Close the habits database connection
        self.fails.close()  # Close the entries database connection
        self.window.close()  # Close the main window


# Main program logic
if __name__ == "__main__":
    login_app = HaBioticLogin()  # Create an instance of the login window
    user_id = login_app.run()  # Run the login window and get the user ID
    if user_id is not None:  # If user ID is obtained
        app = HaBiotic(user_id)  # Create an instance of the main application
        app.run()  # Run the main application
