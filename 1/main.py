import PySimpleGUI as sg

sg.theme('Hotdogstand')   

layout = [  [sg.Text('Some text on Row 1')],
            [sg.Text('Enter something on Row 2'), sg.InputText()],
            [sg.Button('Ok'), sg.Button('Cancel')] ]


window = sg.Window('ParaDariPats', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': 
        break
    print('You entered ', values[0])

window.close()