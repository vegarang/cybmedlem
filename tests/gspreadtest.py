import gspread
from account import username, passwd

gc=gspread.login(username, passwd)

wks=gc.open("H2012").sheet1

wks.update_acell('A1', "Does this work?")
