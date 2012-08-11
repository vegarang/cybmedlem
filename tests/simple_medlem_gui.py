#/usr/local/bin/python
#coding: utf-8
from Tkinter import *
from datetime import datetime as dt
import os, tkFont
from scrolledlist import ScrolledList as SL


class MainGui(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master.title('Medlemsregister Cybernetisk Selskab')
        self.grid(padx=25, pady=30)
        self.backuppath="/home/cyb/Stuff/medlem_backup/"
        self.members={}
        self.nr_of_members=0
        self.create_elements()
        self.read_file()

    def create_elements(self):
        monospace=tkFont.Font(family='Courier', size=10, weight='normal')

        self.blank=Label(self, text='')
        self.blank.grid(row=2, column=0)
        self.blank2=Label(self, text='')
        self.blank2.grid(row=4, column=0)

        self.infotext=StringVar()
        self.count=StringVar()

        self.info=Label(self, textvariable=self.infotext)
        self.info.pack()
        self.info.grid(row=1, column=0, columnspan=7)
        self.infotext.set("Welcome")

        self.countlbl=Label(self, textvariable=self.count)
        self.countlbl.pack()
        self.countlbl.grid(row=5, column=5, columnspan=2)

        self.bttext=Label(self, text='Enter name:')
        self.bttext.grid(row=3, column=0)

        self.entext=Entry(self)
        self.entext.grid(row=3, column=1, columnspan=4)
        self.entext.bind('<Return>', self.enter_create)
        self.entext.configure(font=monospace)

        self.numlbl=Label(self, text='Enter number:')
        self.numlbl.grid(row=4, column=0)

        self.numtext=Entry(self)
        self.numtext.grid(row=4, column=1, columnspan=4)
        self.numtext.bind('<Return>', self.enter_create)
        self.numtext.configure(font=monospace)

        self.savebtn=Button(self, text='Save person', command=self.create)
        self.savebtn.grid(row=3, column=5)

        self.searchbtn=Button(self, text='Search', command=self.search)
        self.searchbtn.grid(row=3, column=6)

        self.delbtn=Button(self, text='Delete', command=self.delete)
        self.delbtn.grid(row=3, column=7)

        self.memlist=SL(self, height=20, width=50)
        self.memlist.grid(row=7, column=0, columnspan=7)
        self.memlist.listbox.configure(font=monospace)

        self.saveallbtn=Button(self, text='Save all to file', command=self.export)
        self.saveallbtn.grid(row=8, column=0)

    def reset_list(self):
        self.memlist.clear()
        for name, date in self.members.iteritems():
            self.memlist.append('  {:25} - {}'.format(name, date))

    def update_count(self):
        self.count.set('nr of members: {}'.format(self.nr_of_members))
        self.numtext.delete(0, END)
        self.numtext.insert(0, self.nr_of_members)

    def delete(self):
        name=self.entext.get().lower()
        self.entext.delete(0, END)

        if name in self.members:
            del self.members[name]
            self.nr_of_members-=1
            self.update_count()
            self.infotext.set('{} has been deleted'.format(name))
            self.reset_list()
        else:
            self.infotext.set('ERROR: {} was NOT deleted!'.format(name))

    def search(self):
        name=self.entext.get().lower()
        self.entext.delete(0, END)

        if name in self.members:
            var=self.members[name]
            self.infotext.set('nr{} - {} became a member on {}'.format(var[0], name, var[1]))
        else:
            self.infotext.set('{} is not a member'.format(name))


    def enter_create(self, event):
        self.create()

    def unique_key(self, num):
        for name, var in self.members.iteritems():
            if num==var[0]:
                return False
        return True

    def create(self, values=''):
        name=''
        num=''
        date=''
        init=True

        if values=='':
            name=self.entext.get().lower()
            num=self.numtext.get().lower()
            self.entext.delete(0, END)
            self.numtext.delete(0, END)
            date=dt.now().strftime("%Y-%m-%d %H:%M")
            init=False
            if not self.unique_key(num):
                self.infotext.set('ERROR: number {} already in list. {} was NOT added'.format(num, name))
                return

        else:
            num=values[0]
            name=values[1]
            date=values[2]

        if not name in self.members and name!='' and num!='':
            self.members[name]=[num, date]
            self.nr_of_members+=1
            self.update_count()
            self.memlist.append(' {:2}-{:25} - {}'.format(num, name, date))
            if not init:
                self.infotext.set('{} is now added'.format(name))
            return

        if not init:
            self.infotext.set('ERROR: {} was NOT added'.format(name))


    def read_file(self):
        filename=self.get_filename()
        if not os.path.exists(filename):
            f=open(filename, 'w')
            f.write('')
            f.close()

        f=open(filename, "r")
        lines=f.read().split("\n")
        for line in lines:
            if line=="":
                continue

            line=line.split(';')
            values=[]
            self.create(line)
        f.close()

    def export(self):
        filename=self.get_filename()
        f=open(filename, "w")
        #backup=self.get_filename(self.backuppath)
        #f2=open(backup, "w")

        for name, var in self.members.iteritems():
            num=var[0]
            date=var[1]
            f.write('{};{};{}\n'.format(num, name, date))
            #f2.write('{};{}\n'.format(name, date))

        f.close();
        #f2.close();

    def get_filename(self, namebase=''):
        month=dt.now().strftime("%m")
        year=dt.now().strftime("%y")
        path=os.path.realpath(__file__).rsplit('/', 2)
        path=path[0]

        if month<8:
            if namebase=='':
                return '{}/medlemslister/medlemmer_v{}.txt'.format(path, year)
            return '{}/medlemmer_v{}_BACKUP.txt'.format(namebase, year)
        if namebase=='':
            return '{}/medlemslister/medlemmer_h{}.txt'.format(path, year)
        return '{}medlemmer_h{}_BACKUP.txt'.format(namebase, year)

if __name__=='__main__':
    gui=MainGui()
    gui.mainloop()
    gui.export()
