#/usr/local/bin/python
# -*- coding: utf-8 -*-

from storage import Storage
from Tkinter import *
from datetime import datetime as dt
import tkFont
from scrolledlist import ScrolledList as SL

class Main(Frame):
    """
    Main class of the system.
    """
    def __init__(self, master=None):
        """
        Main contstructor. Creates an instance of :class:`Storage<storage.Storage>` and starts the graphics-window.
        """
        args={'fields':['name', 'date', 'lifetime'],
              'ident':'name',
              'uniqueident':True,
              'objectname':'person'
             }
        self.storage=Storage(**args)
        self.storage.load()
        self.is_clicked=False
        self.clicked_id=-1
        Frame.__init__(self, master)
        self.master.title('Medlemsregister Cybernetisk Selskab')
        self.grid(padx=25, pady=30)
        self.create_elements()
        self._populate_list()

    def hello(self):
        print 'hello'

    def create_elements(self):
        """
        creates all graphics elements and places them in the graphics grid.
        """
        monospace=tkFont.Font(family='Courier', size=10, weight='normal')

        #menubar:
        menubar=Menu(self.master)

        backupmenu=Menu(menubar, tearoff=0)
        backupmenu.add_command(label='Backup to Google (Note: Slow!)', command=self.google_write)
        backupmenu.add_command(label='Read backup from Google', command=self.google_read)
        backupmenu.add_separator()
        backupmenu.add_command(label='Backup to Wiki', command=self.wiki_write)
        backupmenu.add_command(label='Read backup from Wiki', command=self.wiki_read)

        specialmenu=Menu(menubar, tearoff=0)
        specialmenu.add_command(label='Set as lifetime member', command=self.set_lifetime)
        specialmenu.add_command(label='Remove lifetime membership', command=self.unset_lifetime)

        menubar.add_cascade(label='Backup', menu=backupmenu)
        menubar.add_cascade(label='Special Actions', menu=specialmenu)

        self.master.config(menu=menubar)

        #Info-label
        self.infotext=StringVar()
        self.info=Label(self, textvariable=self.infotext)
        self.info.pack()
        self.info.grid(row=0, column=0, columnspan=7)
        self.infotext.set("Welcome")

        #Save-button
        self.savebtntext=Label(self, text='Enter name:')
        self.savebtntext.grid(row=3, column=0)
        self.savebtn=Button(self, text='Save', command=self.create)
        self.savebtn.grid(row=3, column=5)

        #Name-field
        self.nametxt=Entry(self)
        self.nametxt.grid(row=3, column=1, columnspan=4)
        self.nametxt.bind('<Return>', self.create)
        self.nametxt.configure(font=monospace)

        #List of members
        self.memlist=SL(self, height=15, width=57, callback=self._click_list)
        self.memlist.grid(row=7, column=0, columnspan=7)
        self.memlist.listbox.configure(font=monospace)

        #Search-label
        self.searchtext=StringVar()
        self.search_lbl=Label(self, textvariable=self.searchtext)
        self.search_lbl.pack()
        self.search_lbl.grid(row=9, column=0, columnspan=10)
        self.searchtext.set("  \nEnter values in one of the fields below,\nthen press search to search for people.")

        #Search-fields
        self.search_name_label=Label(self, text='Name:')
        self.search_name_label.grid(row=10, column=0)
        self.search_name=Entry(self)
        self.search_name.grid(row=10, column=1, columnspan=4)
        self.search_name.bind('<Return>', self.search)
        self.search_name.configure(font=monospace)

        self.search_date_label=Label(self, text='Date/Time:')
        self.search_date_label.grid(row=11, column=0)
        self.search_date=Entry(self)
        self.search_date.grid(row=11, column=1, columnspan=4)
        self.search_date.bind('<Return>', self.search)
        self.search_date.configure(font=monospace)

        #Search-button
        self.savebtn=Button(self, text='Search', command=self.search)
        self.savebtn.grid(row=10, column=5)

        self.searchlist=False

        #Delete-label
        self.delete_text=StringVar()
        self.delete_lbl=Label(self, textvariable=self.delete_text)
        self.delete_lbl.pack()
        self.delete_lbl.grid(row=12, column=0, columnspan=10)
        self.delete_text.set("  \nClick a person in the list, or enter an id in the field below,\n then press delete to delete a person.")

        #Delete-fields
        self.delete_id_label=Label(self, text='Id:')
        self.delete_id_label.grid(row=13, column=0)
        self.delete_id=Entry(self)
        self.delete_id.grid(row=13, column=1, columnspan=4)
        self.delete_id.bind('<Return>', self.delete)
        self.delete_id.configure(font=monospace)

        #Delete-button
        self.delete_btn=Button(self, text='Delete', command=self.delete)
        self.delete_btn.grid(row=13, column=5)

        #Counter
        self.count=StringVar()
        self.countlbl=Label(self, textvariable=self.count)
        self.countlbl.pack()
        self.countlbl.grid(row=8, column=5, columnspan=2)

    def create(self, event=None):
        """
        Called when a user clicks the 'save person'-button or presses enter while typing in the name-field.
        Sets the info-label with feedback from :class:`Storage<storage.Storage>`

        :param event: the button-event of the enter-key.
        """
        if self.searchlist:
            self._populate_list()
            self.searchlist=False

        name=self.nametxt.get().lower()
        self.nametxt.delete(0, END)
        date=dt.now().strftime("%Y-%m-%d %H:%M")

        obj=self.storage.create(**{'name':name, 'date':date, 'lifetime':'n'})
        if not 'success' in obj:
            self.infotext.set('FAILURE! {}'.format(obj['error']))
        else:
            self.infotext.set('Success! User added with id: {}'.format(obj['success']))
            self._list_add(obj['success'], obj['object']['name'], obj['object']['date'])

        self._update_count()

    def search(self, event=None):
        """
        Locate all people matching search-parameters in search-fields.

        called when user clicks search or when user presses enter while cursor is in one of the search-fields.

        :param event: button-event for enter-click.
        """
        self.infotext.set('')
        name=self.search_name.get().lower()
        date=self.search_date.get().lower()
        self.search_name.delete(0, END)
        self.search_date.delete(0, END)

        args={'name':name, 'date':date}

        obj=self.storage.search(**args)
        self.searchlist=True
        self.memlist.clear()
        for k, v in obj.iteritems():
            self._list_add(k, v['name'], v['date'])

    def delete(self, event=None):
        """
        Delete a person from collection based on `id`.

        called when user clicks delete or when user presses enter while cursor is in the delete-field.
        """
        val=self.delete_id.get()
        self.delete_id.delete(0, END)

        if val=='':
            if self.is_clicked:
                id=self.clicked_id
                self.is_clicked=False
                self.clicked_id=-1
            else:
                self.infotext.set('FAILURE! No id provided. Either click a person in the list or write an id.')
                return
        else:
            id=int(val)

        obj=self.storage.delete(**{'id':id})
        if 'success' in obj:
            self.infotext.set('Success! {}'.format(obj['success']))
            self._populate_list()
        else:
            self.infotext.set('FAILURE! {}'.format(obj['error']))
        self._update_count()

    def _list_add(self, id, name, date, lifetime='n'):
        """
        adds a person with id, name and timestamp to the list of users in the ui.

        :param id: id of a person.
        :param name: name of a person.
        :param date: date of a person.
        """
        life=''
        if lifetime=='y':
            life='- X'
        self.memlist.append(u' {:<4} - {:25} - {} {}'.format(id, name.title(), date, life))

    def _populate_list(self):
        """
        Refreshes the list of users in the ui.
        """
        self.memlist.clear()
        for k, v in self.storage.storage.iteritems():
            self._list_add(k, v['name'], v['date'], v['lifetime'])

        self._update_count()

    def _update_count(self):
        """
        Updates the counter in the ui with number from :func:`storage.size()<storage.Storage.size>`
        """
        self.count.set('Total:{}'.format(self.storage.size()))

    def _click_list(self, linenum):
        self._clear_all_textbox()
        line=self.memlist[linenum]
        vals=line.split('-')
        self.clicked_id=int(vals[0].strip())
        self.is_clicked=True

    def _clear_all_textbox(self):
        self.delete_id.delete(0, END)
        self.search_name.delete(0, END)
        self.search_date.delete(0, END)
        self.nametxt.delete(0, END)

    def google_write(self):
        """
        backup collection to a google spreadsheet
        """
        obj=self.storage.google_write()
        if 'success' in obj:
            self.infotext.set('Success! collection backed up to google spreadsheet.')
        else:
            self.infotext.set('Failure! {}'.format(obj['error']))

    def google_read(self):
        """
        read backup of collection from a google spreadsheet
        """
        obj=self.storage.google_read()
        if 'success' in obj:
            self.infotext.set('Success! {}'.format(obj['success']))
            self._populate_list()
        else:
            self.infotext.set('Failure! {}'.format(obj['error']))

    def wiki_write(self):
        """
        backup collection to the cyb wiki
        """
        self.infotext.set('Please Wait...')
        print 'wiki write'

    def wiki_read(self):
        """
        read backup of collection from the cyb wiki
        """
        self.infotext.set('Please Wait...')
        print 'wiki read'

    def set_lifetime(self):
        if not self.is_clicked:
            self.infotext.set('FAILURE! No id provided. You have to click a person in the list!.')
            return

        id=self.clicked_id
        self.is_clicked=False
        self.clicked_id=-1

        self.storage.update(**{'id':id, 'lifetime':'y'})
        self._populate_list()

    def unset_lifetime(self):
        if not self.is_clicked:
            self.infotext.set('FAILURE! No id provided. You have to click a person in the list!.')
            return

        id=self.clicked_id
        self.is_clicked=False
        self.clicked_id=-1

        self.storage.update(**{'id':id, 'lifetime':'n'})
        self._populate_list()

if __name__=='__main__':
    gui=Main()
    gui.mainloop()
    gui.storage.save()
