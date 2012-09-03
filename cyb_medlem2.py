#/usr/local/bin/python
# -*- coding: utf-8 -*-

from storage import Storage
from Tkinter import Frame, Menu, Button, Entry, Label, StringVar, END, TOP, BOTH, YES, Toplevel, RIDGE, LEFT
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
              'objectname':'person',
              'gui':self
             }
        self.storage=Storage(**args)
        self.is_clicked=False
        self.clicked_id=-1
        Frame.__init__(self, master)
        self.master.title('Medlemsregister Cybernetisk Selskab')
        self.grid(padx=15, pady=15)

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

        #global shortcuts
        self.master.bind('<F1>', self.display_help)
        self.master.bind('<Control-f>', self.search)
        self.master.bind('<Control-d>', self.delete)
        self.master.bind('<Control-r>', self._populate_list)
        self.master.bind('<Control-s>', self.save_to_file)

        monospace=tkFont.Font(family='Courier', size=10, weight='normal')

        #menubar:
        menubar=Menu(self.master)

        backupmenu=Menu(menubar, tearoff=0)
        backupmenu.add_command(label='Backup to Google (Note: Slow!)', command=self.google_write)
        backupmenu.add_command(label='Read backup from Google', command=self.google_read)
        backupmenu.add_separator()
        backupmenu.add_command(label='Merge with Wiki', command=self.wiki_merge)
        backupmenu.add_command(label='Overwrite Wiki with local storage', command=self.wiki_overwrite)

        specialmenu=Menu(menubar, tearoff=0)
        specialmenu.add_command(label='Set as lifetime member', command=self.set_lifetime)
        specialmenu.add_command(label='Remove lifetime membership', command=self.unset_lifetime)
        specialmenu.add_command(label='Change a users id', command=self.update_id)

        menubar.add_cascade(label='Backup', menu=backupmenu)
        menubar.add_cascade(label='Special Actions', menu=specialmenu)
        menubar.add_command(label='Help (F1)', command=self.display_help)

        self.master.config(menu=menubar)

        #Info-label
        self.infotext=StringVar()
        self.info=Label(self, textvariable=self.infotext)
        self.info.pack()
        self.info.grid(row=0, column=0, columnspan=10)
        self.infotext.set("Welcome")

        #Save-button
        self.savebtn=Button(self, text='Save (enter)', command=self.create, width=11)
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
        self.searchbtn=Button(self, text='Search (ctrl-f)', command=self.search, width=11)
        self.searchbtn.grid(row=3, column=8)

        self.searchlist=False

        #Delete-button
        self.delete_btn=Button(self, text='Delete (ctrl-d)', command=self.delete, width=11)
        self.delete_btn.grid(row=3, column=9)

        #Counter
        self.count=StringVar()
        self.countlbl=Label(self, textvariable=self.count)
        self.countlbl.pack()
        self.countlbl.grid(row=8, column=0, sticky='W')

        #Reset list-button
        self.refreshbtn=Button(self, text='Refresh list (ctrl-r)', command=self._populate_list, width=12)
        self.refreshbtn.grid(row=8, column=9)

        #Save to file-button
        self.saveallbtn=Button(self, text='Save to file (ctrl-s)', command=self.save_to_file, width=12)
        self.saveallbtn.grid(row=8, column=8)

        #Help-button
        #self.helpbutton=Button(self, text='Help', command=self.display_help, width=11)
        #self.helpbutton.grid(row=8, column=7)

    def display_help(self, event=None):
        """
        Display a new window with help-text from file 'help.txt'
        """
        help=Toplevel()
        help.title('Help and usage')
        path=os.path.abspath(__file__).rsplit('/',1)[0]
        f=open(u'{}/help.txt'.format(path), 'r')
        helptext=f.read()
        f.close
        helplabel=Label(help, text=helptext, relief=RIDGE, padx=15, pady=15, anchor='w', justify=LEFT, bg='white')
        helplabel.pack(side=TOP, fill=BOTH, expand=YES)

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
            self.infotext.set(u'FAILURE! {}'.format(obj['error']))
        else:
            self.infotext.set(u'Success! User added with id: {}'.format(obj['success']))
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

        if len(text.split('-')) > 1 or len (text.split(':')) == 2:
            date=text
        else:
            name=text

        args={'name':name, 'date':date}

        obj=self.storage.search(**args)
        self.searchlist=True
        self.memlist.clear()
        i=0
        l=0
        for k, v in obj.iteritems():
            self._list_add(k, v['name'], v['date'])
            if not 'L' in '{}'.format(k):
                i+=1
            else:
                l+=1

        self._update_count(u'Life: {} Normal: {}'.format(l, i))

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
                self.infotext.set(u'FAILURE! No id provided. Either click a person in the list or write an id.')
                return
        elif 'L' in val:
            id=val
        else:
            id=int(val)

        obj=self.storage.read(**{'id':id})
        if 'success' in obj:
            check=self._popup(u'Really delete?',
                              u"Do you really want to delete '{}'?".format(obj['success']['name'].title()), 'warning')
            if not check:
                self.infotext.set(u'Delete aborted..')
                return

        obj=self.storage.delete(**{'id':id})
        if 'success' in obj:
            self.infotext.set(u'Success! {}'.format(obj['success']))
            self._populate_list()
        else:
            self.infotext.set(u'FAILURE! {}'.format(obj['error']))
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
        sorted_keys=sorted(self.storage.storage.iterkeys())
        for k in sorted_keys:
            v=self.storage.storage[k]
            self._list_add(k, v['name'], v['date'])
        self._update_count()

    def _update_count(self, count=None):
        """
        Updates the counter in the ui with number from :func:`storage.size()<storage.Storage.size>`
        """
        if count:
            self.count.set(u'{}'.format(count))
        else:
            self.count.set(u'Total: {}'.format(self.storage.size()))

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
            self.infotext.set(u'Success! collection backed up to google spreadsheet.')
        else:
            self.infotext.set(u'Failure! {}'.format(obj['error']))

    def google_read(self):
        """
        read backup of collection from a google spreadsheet
        """
        obj=self.storage.google_read()
        if 'success' in obj:
            self.infotext.set(u'Success! {}'.format(obj['success']))
            self._populate_list()
        else:
            self.infotext.set(u'Failure! {}'.format(obj['error']))

    def wiki_merge(self):
        """
        Merge local collection with wiki
        """
        self.infotext.set(u'Please Wait...')
        val=self.storage.wiki_merge()
        val=self.storage.wiki_merge(lifetime=True)
        self.infotext.set(val['status'])

    def wiki_overwrite(self):
        """
        overwrite wiki with data from local storage
        """
        self.infotext.set(u'Please Wait...')
        val=self.storage.wiki_merge(overwrite_wiki=True, push_to_wiki=True)
        val=self.storage.wiki_merge(overwrite_wiki=True, push_to_wiki=True, lifetime=True)
        self.infotext.set(val['status'])

    def set_lifetime(self):
        """
        register lifetime membership for a user. The user is selected by clicking in the list.
        """
        if not self.is_clicked:
            self.infotext.set(u'FAILURE! No id provided. You have to click a person in the list!.')
            return

        id=self.clicked_id
        self.is_clicked=False
        self.clicked_id=-1

        obj=self.storage.read(**{'id':id})
        if 'success' in obj:
            check=self._popup(u'Set lifetime membership?',
                              u"Do you really want to give '{}' a lifetime membership?".format(obj['success']['name'].title()), 'warning')
            if not check:
                self.infotext.set(u'{} does NOT have a lifetime membership..'.format(obj['success']['name'].title()))
                return

        obj=self.storage.update(**{'id':id, 'life':True})
        if 'error' in obj:
            self.infotext.set(u'FAILURE! {}'.format(obj['error']))
        elif 'success' in obj:
            self.infotext.set(u'Success! {}'.format(obj['success']))
            self._populate_list()

    def unset_lifetime(self):
        """
        remove a lifetime membership from a user. The user is selected by clicking in the list.
        """
        if not self.is_clicked:
            self.infotext.set(u'FAILURE! No id provided. You have to click a person in the list!.')
            return

        id=self.clicked_id
        self.is_clicked=False
        self.clicked_id=-1

        obj=self.storage.read(**{'id':id})
        if 'success' in obj:
            check=self._popup(u'Remove lifetime membership?',
                              u"Do you really want to remove '{}'s' lifetime membership?".format(obj['success']['name'].title()), 'warning')
            if not check:
                self.infotext.set(u'{} is still a lifetime member.'.format(obj['success']['name'].title()))
                return

        obj=self.storage.update(**{'id':id, 'life':False})
        if 'error' in obj:
            self.infotext.set(u'FAILURE! {}'.format(obj['error']))
        elif 'success' in obj:
            self.infotext.set(u'Success! {}'.format(obj['success']))
            self._populate_list()

    def update_id(self):
        """
        Update the id of a user
        """
        if not self.is_clicked:
            self.infotext.set(u'FAILURE: You have to click a user in the list.')
            return

        newid=self._get_val()
        if newid=='':
            self.infotext.set(u'FAILURE: You have to enter a new id in the textfield.')
            return

        id=self.clicked_id
        self.is_clicked=False
        self.clicked_id=-1

        name=self.storage.read(**{'id':id})
        if not 'success' in name:
            self.infotext.set(u'FAILURE: id could not be found..')
            return

        name=u'{}'.format(name['success']['name'].title())
        if not self._popup(u'Change id?', u"Do you really want to change the id of '{}'?".format(name)):
            self.infotext.set(u'Aborted changing id.')
            return

        retval=self.storage.update_id(id, newid)

        self.infotext.set(retval['status'])

        self._populate_list()

    def _get_val(self):
        """
        clears the input-field and returns value that was there.
        """
        val=self.omnibar.get()
        self.omnibar.delete(0, END)
        val=u'{}'.format(val)
        return val.lower()

    def save_to_file(self, event=None):
        val=self.storage.save()

        self.infotext.set('{}'.format(val['msg']))

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
        print u'\n\nFolder not found! Create folder "{}/medlemslister" and restart the program\n'.format(path)
