

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
with open('paradumi.txt', 'r') as ppar2:
    ppar2.seek(0)
    lines = ppar2.readlines()
    for line in lines:
        esosie_paradumi.append(line.strip())  # Strip to remove leading/trailing whitespaces

# Open 'paradumi.txt' for appending new entries
ppar = open('paradumi.txt', 'a')

# GUI layout
layout = [
    [sg.Text('Paradaripats slinki')],
    [sg.Text('Enter something on Row 2'), sg.InputText()],
    [sg.Button('submit'), sg.Button('Cancel')],
    [sg.Radio(x, 1) for x in esosie_paradumi]
]

# Create the PySimpleGUI window
window = sg.Window('ParaDariPats', layout)

# Main event loop
while True:
    event, values = window.read()

    # Check for window closed or Cancel button clicked
    if event == sg.WIN_CLOSED or event == 'Cancel':
        break

    # Check for submit button clicked
    if event == 'submit':
        # Print and write the new entry to 'dati.txt'
        print(values[0])
        piev = str(f'{now}: {values[0]}\n')
        fails.write(piev)

        # Check if the entry is not already in 'paradumi.txt'
        if values[0] not in esosie_paradumi:
            # Write the new entry to 'paradumi.txt' and update the list
            ppar.write(values[0] + '\n')
            esosie_paradumi.append(values[0])
            print(esosie_paradumi)

# Close the file handles and the window
ppar.close()
fails.close()
window.close()
