import gspread

gc=gspread.login('cyb.medlemssystem', 'Cybernetisk1969')

wks=gc.open("Test").sheet1

wks.update_acell('B2', "Does this work?")
