import PySimpleGUI as sg
import datetime

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
paradit = []
sg.theme('Hotdogstand')   
fails = open("dati.txt", "a")
layout = [  [sg.Text('RUN!')],
            [sg.Text('Enter something on Row 2'), sg.InputText()],
            [sg.Button('OK'), sg.Button('Cancel')],
            [sg.Column(paradit)] ]

window = sg.Window('ParaDariPats', layout)
paradumi = []
while True:
    event, values = window.read(timeout = 1000)
    if event == sg.WIN_CLOSED or event == 'Cancel': 
        break

    
    elif event == 'OK':
        print(values[0])
        piev = str(f'{now}: {values[0]}\n')
        fails.write(piev)


        for val in values:
            for par in paradumi:
                if val == par:
                    break
                else:
                     paradumi += piev
                     paradit += [[sg.Button(par)]]
                     window.refresh()
                     break
                   
                    
            if len(paradumi) == 0:
                paradumi += piev
                paradit += [[sg.Button(piev)]]
                window.refresh()
                


        new_button = sg.Button('New Button')
        # Update the layout by adding the new button to the existing layout

        



fails.close()
window.close()