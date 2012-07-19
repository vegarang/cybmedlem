from storage import Storage
import unittest
from datetime import datetime

class TestStorage(unittest.TestCase):

    def setUp(self):
        args={'fields':['name',
                        'date'],
              'ident':'name'
             }
        self.s=Storage(**args)

        self.spiderman={'name':'spiderman',
              'date':datetime.now(),
             }
        self.s.create(**self.spiderman)

        self.superman={'name':'superman',
              'date':datetime.now(),
             }
        self.s.create(**self.superman)

        self.batman={'name':'batman',
              'date':datetime.now(),
             }
        self.s.create(**self.batman)

        self.superdude={'name':'superdude',
              'date':datetime.now(),
             }
        self.s.create(**self.superdude)

    def test_read(self):
        retval=self.s.read(**{'id':0})
        self.assertTrue('success' in retval)
        obj=retval['success']
        self.assertEqual(obj['name'], self.spiderman['name'])

    def test_update(self):
        retval=self.s.update(**{'id':1, 'name':'superwoman'})
        self.assertTrue('success' in retval)

        obj=self.s.read(**{'id':1})
        self.assertEqual(obj['success']['name'], 'superwoman')

    def test_delete(self):
        retval=self.s.delete(**{'id':2})

        self.assertTrue('error' in self.s.read(**{'id':2}))

    def test_search(self):
        retval=self.s.search(**{'name':'man'})
        self.assertEqual(len(retval), 3)

        retval=self.s.search(**{'name':'dude'})
        self.assertEqual(len(retval), 1)

if __name__=='__main__':
    unittest.main()
