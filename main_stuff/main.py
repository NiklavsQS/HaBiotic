import PySimpleGUI as sg
import datetime
import sqlite3 as sq
lietotaja_parbaude = "SELECT * FROM users WHERE user_name = ? AND password = ?"
nepareiza_parole = "SELECT * FROM users WHERE user_name = ?"
lietotaja_id = "SELECT id FROM users WHERE user_name = ?"

class HaBiotic:
    def __init__(self):
        # Get current date and time
        self.now = datetime.datetime.now().strftime("%Y-%m-%d")

        # Set the PySimpleGUI theme
        sg.theme('SystemDefault')

        # Open file for appending new entries
        self.fails = sq.connect('dati.db')
        self.c = self.fails.cursor()
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
  
        # List to store existing entries from 'paradumi.txt'
        self.esosie_paradumi = self.read_existing_entries()

        # Open 'paradumi.txt' for appending new entries
        self.ppar = open(r'HaBiotic\main_stuff\paradumi.txt', 'a')
  
        self.layout = [
             [sg.Text('Ieraksti paradumu vai izvelies no ieprieksejajiem'), sg.InputText(key='paradums')],
             [sg.Text('Ieraksti lietotājvārdu'), sg.InputText(key='Uname')],
             [sg.Text('Ieraksti paroli'), sg.InputText(key='Pass')],
             [sg.Button('submit'), sg.Button('Cancel')],
             [sg.Column([[sg.Checkbox(habit, key=f'checkbox_{i}')] for i, habit in enumerate(self.esosie_paradumi)])]
         ]
 
        # Create the PySimpleGUI window
        self.window = sg.Window("HaBiotic", self.layout)

    def read_existing_entries(self):
        esosie_paradumi = []
        with open(r'HaBiotic\main_stuff\paradumi.txt', 'r') as ppar2:
            ppar2.seek(0)
            lines = ppar2.readlines()
            for line in lines:
                esosie_paradumi.append(line.strip())  # Strip to remove leading/trailing whitespaces
        return esosie_paradumi

    def run(self):
        # Main event loop
        while True:
            event, values = self.window.read()

            # Check for window closed or Cancel button clicked
            if event in (sg.WIN_CLOSED, 'Cancel'):
                break

            if event == 'submit':
                self.c.execute(lietotaja_parbaude, (values['Uname'],values['Pass'],))
                lietotajs = self.c.fetchone()
                if lietotajs:
                    user_search = self.c.execute(lietotaja_id, (values['Uname'],))
                    self.user_id = self.c.fetchone()
                    self.handle_submit(values)  
                else:
                    self.c.execute(nepareiza_parole, (values['Uname'],))
                    w_parole = self.c.fetchone()
                    if w_parole:
                        sg.popup_ok('nepareiza parole')
                    no_user = sg.popup_ok_cancel('Šāds lietotājs nepastāv, pārbaudiet vai pareizi ievadijāt lietotājvārdu. Vai vēlaties piereģistrēties?')

                    if no_user == 'Cancel':
                        break
                    #registering
                    if no_user == 'OK':
                        n_uname = sg.popup_get_text('ievadi jauno lietotājvārdu', title="Username")
                        self.c.execute(nepareiza_parole, (n_uname,))
                        user_check = self.c.fetchone()
                        if user_check:
                            sg.popup_ok('lietotājs jau pastāv')
                        else:
                            n_pass = sg.popup_get_text('ievadi jauno paroli', title="Username")
                            new_user = (n_uname,n_pass)
                            self.c.execute("INSERT INTO users (user_name, password) VALUES (?, ?)", new_user)
                            self.fails.commit()
                        

        # Close the file handles and the window
        self.ppar.close()
        self.fails.close()
        self.window.close()

    def handle_submit(self, values):
        # Retrieve the values from the checkboxes
        selected_indices = [i for i, habit in enumerate(self.esosie_paradumi) if values.get(f'checkbox_{i}')]
    
        # Retrieve the new entry from the input field
        new_entry_value = values['paradums']
    
        # Handle new entries
        for entry in new_entry_value.split(','):
            if entry == '':
                break
            entry = entry.strip()
            print(entry)
            if entry not in self.esosie_paradumi:
                piev = (str(self.user_id), str(entry), str(self.now))
                self.c.execute("INSERT INTO entries (user_id ,habit ,time) VALUES (?, ?, ?)", piev)
                self.fails.commit
                print("New entry written:", piev)
                # Write the new entry to 'paradumi.txt' and update the list
                self.ppar.write('\n' + entry)
                self.esosie_paradumi.append(entry)
            else:
                piev = (str(self.user_id), str(entry), str(self.now))
                self.c.execute("INSERT INTO entries (user_id ,habit ,time) VALUES (?, ?, ?)", piev)
                self.fails.commit()
                print("New entry written:", piev)
  
        # Handle selected values separately
        for i in selected_indices:
            selected_value = self.esosie_paradumi[i]
            if selected_value not in new_entry_value:
                piev = (str(self.user_id), str(selected_value), str(self.now))
                self.c.execute("INSERT INTO entries (user_id ,habit ,time) VALUES (?, ?, ?)", piev)
                self.fails.commit()
                print("Selected entry written:", piev)
    
if __name__ == "__main__":
    app = HaBiotic()
    app.run()
