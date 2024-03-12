import PySimpleGUI as sg
import datetime

class RoutineRadar:
    def __init__(self):
        # Get current date and time
        self.now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Set the PySimpleGUI theme
        sg.theme('SystemDefault')

        # Open file for appending new entries
        self.fails = open("dati.txt", "a")

        # List to store existing entries from 'paradumi.txt'
        self.esosie_paradumi = self.read_existing_entries()

        # Open 'paradumi.txt' for appending new entries
        self.ppar = open(r'paradaritajs\main_stuff\paradumi.txt', 'a')

        # GUI layout
        self.layout = [
            [sg.Text('Ieraksti paradumu vai izvelies no ieprieksejajiem'), sg.InputText(key='paradums')],
            [sg.Button('submit'), sg.Button('Cancel')],
            [sg.Column([[sg.Checkbox(paradums, key=f'checkbox_{i}')] for i, paradums in enumerate(self.esosie_paradumi)])]
        ]

        # Create the PySimpleGUI window
        self.window = sg.Window("Routine Radar", self.layout)

    def read_existing_entries(self):
        esosie_paradumi = []
        with open(r'paradaritajs\main_stuff\paradumi.txt', 'r') as ppar2:
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
                self.handle_submit(values)

        # Close the file handles and the window
        self.ppar.close()
        self.fails.close()
        self.window.close()

    def handle_submit(self, values):
        # Retrieve the values from the checkboxes
        selected_indices = [i for i, paradums in enumerate(self.esosie_paradumi) if values.get(f'checkbox_{i}')]
    
        # Retrieve the new entry from the input field
        new_entry_value = values['paradums'].strip()
    
        # Handle new entries
        for entry in new_entry_value.split(','):
            entry = entry.strip()
            if entry not in self.esosie_paradumi:
                piev = f'{self.now}: {entry}\n'
                self.fails.write(piev)
                print("New entry written:", piev)
                # Write the new entry to 'paradumi.txt' and update the list
                self.ppar.write('\n' + entry)
                self.esosie_paradumi.append(entry)
    
        # Handle selected values separately
        for i in selected_indices:
            selected_value = self.esosie_paradumi[i]
            if selected_value not in new_entry_value:
                piev = f'{self.now}: {selected_value}\n'
                self.fails.write(piev)
                print("Selected entry written:", piev)
                # Write the selected entry to 'paradumi.txt' and update the list
                self.ppar.write(selected_value + '\n')
    

if __name__ == "__main__":
    app = RoutineRadar()
    app.run()
