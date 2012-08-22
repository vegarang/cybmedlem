#/usr/local/bin/python
# -*- coding: utf-8 -*-

from storage import Storage
from Tkinter import Frame, Menu, Button, Entry, Label, StringVar, END
from datetime import datetime as dt
import tkMessageBox, tkFont, os
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
        self.is_clicked=False
        self.clicked_id=-1
        Frame.__init__(self, master)
        self.master.title('Medlemsregister Cybernetisk Selskab')
        self.grid(padx=25, pady=30)

        if not self.storage._testfile():
            path=os.path.abspath(__file__).rsplit('/',1)[0]
            self._popup('ERROR!', 'Cannot write to file! make sure folder "{}/medlemslister" exists, then restart..'.format(path), 'error')
            self.destroy()
            self.master.destroy()
            return

        self.create_elements()

        loadmsg=self.storage.load()
        if 'error' in loadmsg:
            self.infotext.set('ERROR! {}'.format(loadmsg['error']))
        elif 'success' in loadmsg:
            self.infotext.set('Success! {}'.format(loadmsg['success']))

        self._populate_list()

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
        self.info.grid(row=0, column=0, columnspan=10)
        self.infotext.set("Welcome")

        #Save-button
        self.savebtn=Button(self, text='Save', command=self.create, width=11)
        self.savebtn.grid(row=3, column=7)

        #Omnibar (entry-field for add/search/delete)
        self.omnibar=Entry(self, width=28)
        self.omnibar.grid(row=3, column=0, columnspan=1)
        self.omnibar.bind('<Return>', self.create)
        self.omnibar.configure(font=monospace)

        #List of members
        self.memlist=SL(self, height=25, width=71, callback=self._click_list)
        self.memlist.grid(row=7, column=0, columnspan=10)
        self.memlist.listbox.configure(font=monospace)

        #Search-button
        self.searchbtn=Button(self, text='Search', command=self.search, width=11)
        self.searchbtn.grid(row=3, column=8)

        self.searchlist=False

        #Delete-button
        self.delete_btn=Button(self, text='Delete', command=self.delete, width=11)
        self.delete_btn.grid(row=3, column=9)

        #Counter
        self.count=StringVar()
        self.countlbl=Label(self, textvariable=self.count)
        self.countlbl.pack()
        self.countlbl.grid(row=8, column=0, sticky='W')

        #Reset list-button
        self.refreshbtn=Button(self, text='Refresh list', command=self._populate_list, width=11)
        self.refreshbtn.grid(row=8, column=9)

        #Save to file-button
        self.saveallbtn=Button(self, text='Save to file', command=self.storage.save, width=11)
        self.saveallbtn.grid(row=8, column=8)

    def create(self, event=None):
        """
        Called when a user clicks the 'save person'-button or presses enter while typing in the name-field.
        Sets the info-label with feedback from :class:`Storage<storage.Storage>`

        :param event: the button-event of the enter-key.
        """
        if self.searchlist:
            self._populate_list()
            self.searchlist=False

        name=self._get_val()
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
        text=self._get_val()

        name=''
        date=''

        if len(text.split('-')) >= 2 or len (text.split(':')) == 2:
            date=text
        else:
            name=text

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
        val=self._get_val()

        if val=='':
            if self.is_clicked:
                id=self.clicked_id
                self.is_clicked=False
                self.clicked_id=-1
            else:
                self.infotext.set('FAILURE! No id provided. Either click a person in the list or write an id.')
                return
        elif 'L' in val:
            id=val
        else:
            id=int(val)

        obj=self.storage.read(**{'id':id})
        if 'success' in obj:
            check=self._popup('Really delete?',
                              "Do you really want to delete '{}'?".format(obj['success']['name'].title()), 'warning')
            if not check:
                self.infotext.set('Delete aborted..')
                return

        obj=self.storage.delete(**{'id':id})
        if 'success' in obj:
            self.infotext.set('Success! {}'.format(obj['success']))
            self._populate_list()
        else:
            self.infotext.set('FAILURE! {}'.format(obj['error']))
        self._update_count()

    def _list_add(self, id, name, date):
        """
        adds a person with id, name and timestamp to the list of users in the ui.

        :param id: id of a person.
        :param name: name of a person.
        :param date: date of a person.
        """
        self.memlist.append(u' {:<5} - {:40} - {}'.format(id, name.title(), date))

    def _populate_list(self, event=None):
        """
        Refreshes the list of users in the ui.
        """
        self.memlist.clear()
        for k, v in self.storage.storage.iteritems():
            self._list_add(k, v['name'], v['date'])

        self._update_count()

    def _update_count(self):
        """
        Updates the counter in the ui with number from :func:`storage.size()<storage.Storage.size>`
        """
        self.count.set('Total:{}'.format(self.storage.size()))

    def _click_list(self, linenum):
        """
        called when a user clicks a member in the list of members. Saves the id of the user.

        :param linenum: the linenumber the user clicked.
        """
        line=''
        try:
            line=self.memlist[linenum]
        except(IndexError):
            return
        self._get_val()
        vals=line.split('-')
        if not 'L' in vals[0]:
            self.clicked_id=int(vals[0].strip())
        else:
            self.clicked_id=vals[0].strip()
        self.is_clicked=True

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
        """
        register lifetime membership for a user. The user is selected by clicking in the list.
        """
        if not self.is_clicked:
            self.infotext.set('FAILURE! No id provided. You have to click a person in the list!.')
            return

        id=self.clicked_id
        self.is_clicked=False
        self.clicked_id=-1

        obj=self.storage.read(**{'id':id})
        if 'success' in obj:
            check=self._popup('Set lifetime membership?',
                              "Do you really want to give '{}' a lifetime membership?".format(obj['success']['name'].title()), 'warning')
            if not check:
                self.infotext.set('{} does NOT have a lifetime membership..'.format(obj['success']['name'].title()))
                return

        obj=self.storage.update(**{'id':id, 'life':True})
        if 'error' in obj:
            self.infotext.set('FAILURE! {}'.format(obj['error']))
        elif 'success' in obj:
            self.infotext.set('Success! {}'.format(obj['success']))
            self._populate_list()

    def unset_lifetime(self):
        """
        remove a lifetime membership from a user. The user is selected by clicking in the list.
        """
        if not self.is_clicked:
            self.infotext.set('FAILURE! No id provided. You have to click a person in the list!.')
            return

        id=self.clicked_id
        self.is_clicked=False
        self.clicked_id=-1

        obj=self.storage.read(**{'id':id})
        if 'success' in obj:
            check=self._popup('Remove lifetime membership?',
                              "Do you really want to remove '{}'s' lifetime membership?".format(obj['success']['name'].title()), 'warning')
            if not check:
                self.infotext.set('{} is still a lifetime member.'.format(obj['success']['name'].title()))
                return

        obj=self.storage.update(**{'id':id, 'life':False})
        if 'error' in obj:
            self.infotext.set('FAILURE! {}'.format(obj['error']))
        elif 'success' in obj:
            self.infotext.set('Success! {}'.format(obj['success']))
            self._populate_list()

    def _get_val(self):
        """
        clears the input-field and returns value that was there.
        """
        val=self.omnibar.get()
        self.omnibar.delete(0, END)
        return val

    def _popup(self, title, text, style=None):
        """
        create a popup!

        :param title: title of the popup-window
        :param text: the text in the popup-window
        :param style: the icon-style of the popup. default is 'warning'
        """
        if style:
            if style=='error':
                return tkMessageBox.showerror(title, text)
            return tkMessageBox.askokcancel(title, text, icon=style)
        return tkMessageBox.askokcancel(title, text)

if __name__=='__main__':
    gui=Main()
    gui.mainloop()
    try:
        gui.storage.save()
    except IOError:
        path=os.path.abspath(__file__).rsplit('/',1)[0]
        print '\n\nFolder not found! Create folder "{}/medlemslister" and restart the program\n'.format(path)
