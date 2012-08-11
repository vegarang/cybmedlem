#!/usr/bin/python
import gdata.docs
import gdata.docs.service
import gdata.spreadsheet.service
import re, os

class Google_Connect:
    def __init__(self):
        self.gd_client=gdata.spreadsheet.service.SpreadsheetsService()
        self.gd_client.email='cyb.medlemssystem'
        self.gd_client.password='Cybernetisk1969'
        self.gd_client.ProgrammaticLogin()

        q=gdata.spreadsheet.DocumentQuery()
        q['title']='Test'
        q['title-exact']='true'
        feed=self.gd_client.GetSpreadsheetsFeed(query=q)
        spreadsheet_id=feed.entry[0].id.text.rsplit('/', 1)[1]
        feed=self.gd_client.GetWorksheetsFeed(spreadsheet_id)
        worksheet_id=feed.entry[0].id.text.rsplit('/',1)[1]

if __name__=='__main__':
    Google_Connect()
