import PySimpleGUI as sg
import datetime
import sqlite3 as sq
lietotaja_parbaude = "SELECT * FROM users WHERE user_name = ? AND password = ?"
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
              UserID,
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
             [sg.Text('Ieraksti paradumu vai izvelies no ieprieksejajiem'), sg.InputText(key='paradums')],
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
                self.c.execute(lietotaja_parbaude, ('Uname'),('Pass'))
                lietotajs = self.c.fetchone()
                if lietotajs:
                    self.handle_submit(values)  
                else:
                    print('te bus popups pieregistreties vai atcelt')
                

            

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
            entry = entry.strip()
            print(entry)
            if entry not in self.esosie_paradumi:
                piev = f'{self.now}: {entry}\n'
                self.fails.write(piev)
                print("New entry written:", piev)
                # Write the new entry to 'paradumi.txt' and update the list
                self.ppar.write('\n' + entry)
                self.esosie_paradumi.append(entry)
            else:
                piev = f'{self.now}: {entry}\n'
                self.fails.write(piev)
                print("New entry written:", piev)

    
        # Handle selected values separately
        for i in selected_indices:
            selected_value = self.esosie_paradumi[i]
            if selected_value not in new_entry_value:
                piev = f'{self.now}: {selected_value}\n'
                self.fails.write(piev)
                print("Selected entry written:", piev)
    

if __name__ == "__main__":
    app = HaBiotic()
    app.run()
