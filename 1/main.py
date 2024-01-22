import PySimpleGUI as sg
import datetime

now = datetime.datetime.now()

sg.theme('Hotdogstand')   

layout = [  [sg.Text('Some text on Row 1')],
            [sg.Text('Enter something on Row 2'), sg.InputText()],
            [sg.Button('Ok'), sg.Button('Cancel')] ]


window = sg.Window('ParaDariPats', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': 
        break
    print(values[0])
    fails = open("dati.txt", "a")
    piev = str(f'{now}: {values[0]}\n')
    fails.write(piev)
   
fails.close()


print(now)

window.close()