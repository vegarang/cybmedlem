
class Storage:
    """
    A simple class used to save data, and eventually back up data to an online client.
    """
    def __init__(self, **kwargs):
        """
        Constructor. Takes a python-dict `kwargs` as argument. kwargs must contain
        a list/dict `fields` where all values in `fields` will be required to create
        new objects and a single value `ident` used to fetch a specific object instead of an `id`.

        :param \*\*kwargs: dict containing valid fields for an object, and ident-field.
        """
        self.storage={}
        if 'fields' in kwargs:
            self.fields=kwargs['fields']
        if 'ident' in kwargs:
            self.ident=kwargs['ident']

    def create(self, **kwargs):
        """
        Adds an object to collection with values from `kwargs`. If `self.fields` is used, only
        values from `fields` will be used, and all values from `fields` are required.

        All objects will automatically be given an `id` using :func:`storage.Storage._unique_id<_unique_id()>`.

        :param \*\*kwargs: dict with all fields for a new object.
        :returns: a dict with either 'success' containing the new object, or 'error' with errormessage.
        """
        args={}
        for f in self.fields:
            if not f in kwargs:
                return {'error':'missing field {} in arguments!'.format(f)}
            args[f]=kwargs[f]

        id=self._unique_id()
        self.storage[id]=args

        return {'success':id, 'object':args}

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
            return {'error':'multiple objects matching name'}
        if match==1:
            return {'success':retval}
        return {'error':'no objects found'}

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
            return {'error':'No object matching id'}

        del self.storage[kwargs['id']]
        return {'success':'object with id {} is deleted'.format(kwargs['id'])}


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
                if not match and ak in self.fields:
                    value=v[ak]
                    if av in value:
                        retval[k]=v
                        match=True

        return retval


    def _unique_id(self):
        """
        Finds the first availible id and returns it.

        :returns: the first availible id.
        """
        i=0
        while i in self.storage:
            i+=1
        return i
