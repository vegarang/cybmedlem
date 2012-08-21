#/usr/local/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime as dt
import os, sys, json, gspread
from gspread.exceptions import SpreadsheetNotFound
from account import username, passwd

class Storage:
    """
    A simple class used to save data, and back it up.

    TODO: add sync to `google`_ and/or our `wiki`_.

    .. _wiki: http://wiki.cyb.no
    .. _google: http://drive.google.com
    """
    def __init__(self, **kwargs):
        """
        Constructor. Takes a python-dict `kwargs` as argument. kwargs must contain
        a list/dict `fields` where all values in `fields` will be required to create
        new objects and a single value `ident` used to fetch a specific object instead of an `id`.

        if kwargs contains boolean 'uniqueident' and it is set to True, then 'ident' must be unique
        on create.

        :param \*\*kwargs: dict containing valid fields for an object, and ident-field.
        """
        self.storage={}
        self.uniqueident=False
        self.objectname='Object'
        if 'fields' in kwargs:
            self.fields=kwargs['fields']
        if 'ident' in kwargs:
            self.ident=kwargs['ident']
        if 'uniqueident' in kwargs:
            self.uniqueident=kwargs['uniqueident']
        if 'objectname' in kwargs:
            self.objectname=kwargs['objectname']

        self.wks=None


    def create(self, **kwargs):
        """
        Adds an object to collection with values from `kwargs`. If `self.fields` is used, only
        values from `fields` will be used, and all values from `fields` are required.

        All objects will automatically be given an `id` using :func:`_unique_id()<storage.Storage._unique_id>`.

        :param \*\*kwargs: dict with all fields for a new object.
        :returns: a dict with either 'success' containing the new object, or 'error' with errormessage.
        """
        if 'name' in kwargs:
            name=kwargs['name'].strip()
            if len(name.split())<2:
                return {'error':'You have to enter a full name!'}

            if len(name)<5:
                return {'error':'A name has to be more than 5 letters'}

        if self.uniqueident:
            if 'success' in self.read(**{self.ident:kwargs[self.ident]}):
                return {'error':'{} with {} {} already exists!'.format(self.objectname, self.ident, kwargs[self.ident])}

        args={}
        for f in self.fields:
            if not f in kwargs:
                return {'error':'missing field {} in arguments!'.format(f)}
            if kwargs[f]=='':
                return {'error':'missing value for field: {}!'.format(f)}
            args[f]=unicode(kwargs[f])

        key=self._unique_id()
        self.storage[key]=args
        return {'success':key, 'object':args}

    def read(self, **kwargs):
        """
        Find and return a spesific object from storage. Either based on `id` or `self.ident`

        :param kwargs: dict containing either `id` or `self.ident`
        :returns: a dict with either 'success' containing the object, or 'error' with errormessage.
        """
        if len(self.storage)==0:
            return {'error':'empty collection'}

        if 'id' in kwargs:
            if kwargs['id'] in self.storage:
                return {'success':self.storage[kwargs['id']]}

        match=0
        if self.ident in kwargs:
            for k, v in self.storage.iteritems():
                if v[self.ident]:
                    if v[self.ident]==kwargs[self.ident]:
                        retval=v
                        match+=1
        if match>1:
            return {'error':'multiple {}s matching name'.format(self.objectname)}
        if match==1:
            return {'success':retval}
        return {'error':'no {}s found'.format(self.objectname)}

    def update(self, **kwargs):
        """
        find an element based on `id` and update with values in `kwargs`. Any values in kwargs that
        are not in self.fields are ignored.

        :param kwargs: dict containing `id` of object as well as updated fields.
        :returns: a dict with either 'success' containing the updated object, or 'error' with errormessage.
        """
        if len(self.storage)==0:
            return {'error':'empty collection'}

        if not 'id' in kwargs:
            return {'error':'No id provided'}

        if not kwargs['id'] in self.storage:
            return {'error':'Provided id does not exist'}

        if 'life' in kwargs:
            if kwargs['life']:
                return self._set_lifetime(kwargs['id'])
            else:
                return self._unset_lifetime(kwargs['id'])

        id=kwargs['id']
        del kwargs['id']
        obj=self.storage[id]

        for k, v in kwargs.iteritems():
            if k in self.fields:
                obj[k]=v

        return {'success':self.storage[id]}


    def delete(self, **kwargs):
        """
        finds and deletes an object based on `id`

        :param kwargs: dict containing id of object.
        :returns: a dict with either 'success' containing the deleted `id`, or 'error' with errormessage.
        """

        if len(self.storage)==0:
            return {'error':'empty collection'}

        if not 'id' in kwargs:
            return {'error':'No id provided'}

        if not kwargs['id'] in self.storage:
            return {'error':'No {} matching id: {}'.format(self.objectname, kwargs['id'])}

        del self.storage[kwargs['id']]
        return {'success':'{} with id {} is deleted'.format(self.objectname, kwargs['id'])}


    def search(self, **kwargs):
        """
        search for any object that contains any values from `kwargs`.

        :param kwargs: dict containing search-fields. any field not in self.fields are ignored.
        :retval: returns a dictionary containing all objects that match search-fields.
        """
        retval={}
        for k, v in self.storage.iteritems():
            match=False
            for ak, av in kwargs.iteritems():
                if not match and ak in self.fields and not av=='':
                    value=v[ak]
                    if av in value:
                        retval[k]=v
                        match=True

        return retval

    def _set_lifetime(self, id):
        """
        Set a user as lifetime member.

        Give the user a lifetime ID: Lx where x is number.
        """
        if self.storage[id]['lifetime']=='y':
            return {'error':'{} with id {} is already set as lifetime member'.format(self.objectname, id)}

        lid=self._unique_id(True)
        self.storage[lid]=self.storage[id]
        self.storage[lid]['lifetime']='y'
        del self.storage[id]
        return {'success':'{} with id {} now has id {} and is set as lifetime'.format(self.objectname, id, lid)}

    def _unset_lifetime(self, lid):
        """
        Unset lifetime flag from a user.

        Give the user a normal id, instead of lifetime id.
        """
        if self.storage[lid]['lifetime']=='n':
            return {'error':'{} with id {} is not set as lifetime member'.format(self.objectname, lid)}

        id=self._unique_id()
        self.storage[id]=self.storage[lid]
        self.storage[id]['lifetime']='n'
        del self.storage[lid]
        return {'success':'{} with id {} now has id {} and is no longer set as lifetime'.format(self.objectname, lid, id)}

    def _unique_id(self, life=False):
        """
        Finds the first availible id and returns it.

        :returns: the first availible id.
        """
        if life:
            i=0
            val='L0'
            while val in self.storage:
                i+=1
                val='L{}'.format(i)
            return val

        i=0
        while i in self.storage:
            i+=1
        return i

    def save(self):
        """
        Saves entire collection to file. Filename is provided by :func:`_get_filename<storage.Storage._get_filename>`

        The collection is stored as JSON.
        """
        filename=self._get_filename()
        f=open(filename, 'w')
        js=json.dumps(self.storage, indent=3, sort_keys=True)
        f.write(js)
        f.close()

    def load(self):
        """
        Load from file if file exists. Filename is provided by :func:`_get_filename<storage.Storage._get_filename>`

        This function assumes that the collection is stored as JSON, created by :func:`save<storage.Storage.save>`.
        """
        filename=self._get_filename()
        if not os.path.exists(filename):
            self._load_lifetime(filename)
            return

        f=open(filename, 'r')
        js=f.read()
        f.close()
        #bugfix for keys..
        tmp=json.loads(js)
        for k, v in tmp.iteritems():
            if not 'L' in k:
                self.storage[int(k)]=v
            else:
                self.storage[k]=v

    def _load_lifetime(self, filename):
        m=re.search('(.+)medlemmer_(\S)(\d\d)\.json', filename)
        path=m.group(1)
        s=m.group(2)
        y=m.group(3)

        old_fname=''
        if s=='h':
            old_fname='{}medlemmer_{}{}.json'.format(path, 'v', y)
        elif s=='v':
            old_fname='{}medlemmer_{}{}.json'.format(path, 'h', (y-1))

        f=open(old_fname, 'r')
        old_storage=json.loads(f.read())

        for k, v in old_storage.iteritems():
            if 'L' in k:
                self.storage[k]=v

    def _get_filename(self, nameonly=False):
        """
        Calculates and returns current filename, e.g. 'medlemmer_h12' for autumn 2012.

        :returns: current filename.
        """
        month=dt.now().strftime("%m")
        year=dt.now().strftime("%y")
        path=sys.argv[0].rsplit('/', 1)[0]

        if month<8:
            if nameonly:
                return 'medlemmer_v{}'.format(year)
            return '{}/medlemslister/medlemmer_v{}.json'.format(path, year)

        if nameonly:
            return 'medlemmer_h{}'.format(year)
        return '{}/medlemslister/medlemmer_h{}.json'.format(path, year)

    def size(self):
        """
        returns the size of the collection
        """
        return len(self.storage)

    def google_write(self):
        """
        backup collection to a google spreadsheet.

        Note: lazy backup, does not merge.. overwrites google-data.
        """
        if not self._get_google_sheet():
            return {'error':'could not connect to google spreadsheet'}


        try:
            val=self.wks.col_values(1)
        except ValueError:
            val=[]

        for i in xrange(1, len(val)+1):
            self.wks.update_cell(i, 1, '')
            self.wks.update_cell(i, 2, '')

        x=1
        for k, v in self.storage.iteritems():
            self.wks.update_cell(x, 1, '{}'.format(k))
            self.wks.update_cell(x, 2, json.dumps(v))
            x+=1

        return {'success':'backed up to google'}

    def google_read(self):
        """
        read backup of collection from a google spreadsheet, merge values based on id and date.
        """
        if not self._get_google_sheet():
            return {'error':'could not connect to google spreadsheet'}

        empty=False
        try:
            keys=self.wks.col_values(1)
            vals=self.wks.col_values(2)
        except ValueError:
            empty=True

        if empty:
            return {'error':'spreadsheet is empty!'}

        gdoc={}
        for i in xrange(0, len(keys)):
            gdoc[keys[i]]=json.loads(vals[i])

        for k, v in gdoc.iteritems():
            if not k in self.storage:
                self.storage[k]=v
            else:
                if v['date']>self.storage[k]['date']:
                    self.storage[k]=v

        return {'success':'read and merged all values from google doc.'}


    def wiki_write(self):
        """
        backup collection to the cyb wiki
        """
        print 'wiki write'
        pass

    def wiki_read(self):
        """
        read backup of collection from the cyb wiki
        """
        print 'wiki read'
        pass

    def _get_google_sheet(self):
        """
        Connect to a google spreadsheet

        :returns: True if success, False if not
        """
        if self.wks:
            return True

        name=self._get_filename(nameonly=True)
        gc=gspread.login(username, passwd)
        try:
            wks=gc.open(name).sheet1
        except SpreadsheetNotFound:
            return False

        self.wks=wks
        return True
