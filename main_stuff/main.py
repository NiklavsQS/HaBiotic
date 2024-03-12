import PySimpleGUI as sg
import datetime

# Get current date and time
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Set the PySimpleGUI theme
sg.theme('SystemDefault')

# Open file for appending new entries
fails = open("dati.txt", "a")

# List to store existing entries from 'paradumi.txt'
esosie_paradumi = []

# Read existing entries from 'paradumi.txt'
with open(r'main_stuff\paradumi.txt','r') as ppar2:
    ppar2.seek(0)
    lines = ppar2.readlines()
    for line in lines:
        esosie_paradumi.append(line.strip())  # Strip to remove leading/trailing whitespaces

# Open 'paradumi.txt' for appending new entries
ppar = open(r'main_stuff\paradumi.txt','a')

# GUI layout
layout = [
    [sg.Text('Ieraksti paradumu vai izvelies no ieprieksejajiem'), sg.InputText(key='paradums')],
    [sg.Button('submit'), sg.Button('Cancel')],
    [sg.Column([[sg.Checkbox(paradums, key=f'checkbox_{i}')] for i, paradums in enumerate(esosie_paradumi)])]
]

# Create the PySimpleGUI window
window = sg.Window("Routine Radar",layout)

# Main event loop
while True:
    event, values = window.read()

    # Check for window closed or Cancel button clicked
    if event in ('sg.WIN_CLOSED' or 'Cancel'):
        break

    if event == 'submit':
        # Retrieve the values from the checkboxes
        selected_indices = [i for i, paradums in enumerate(esosie_paradumi) if values.get(f'checkbox_{i}')]
        
        # Retrieve the new entry from the input field
        new_entry_value = values['paradums'].strip()
        
        # If there are selected values from checkboxes, add them to the new entry
        if selected_indices:
            selected_values = [esosie_paradumi[i] for i in selected_indices]
            new_entry_value += ', '.join(selected_values)
                
        # Check if any new entries are not already in 'paradumi.txt'
        for entry in new_entry_value.split(','):
            entry = entry.strip()
            piev = f'{now}: {entry}\n'
            fails.write(piev)
            print("New entry written:", piev)
            if entry not in esosie_paradumi:
                # Write the new entry to 'paradumi.txt' and update the list
                ppar.write(entry + '\n')
                print(entry)



# Close the file handles and the window
ppar.close()
fails.close()
window.close()
