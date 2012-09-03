#/usr/local/bin/python
# -*- coding: utf-8 -*-

import mwclient
from account import username, passwd

class WikiLink:
    """
    Class using ``mwclient`` to access a wiki. Has methods for login, read, write, getting a table from a page and creating a table on a page.
    """
    def __init__(self, **args):
        """
        Initiates the WikiLink class with values in ``args`` or default values.

        :param args['url']: Base-url of the wiki. Default: ``cyb.ifi.uio.no``.
        :param args['path']: Path to wiki-files. Default: ``/aktiv/``.
        :param args['pagename']: Name of the page to edit. Default: ``testside_for_medlemssystem``.
        """
        if 'url' in args:
            self.url=args['url']
        else:
            self.url='cyb.ifi.uio.no'

        if 'path' in args:
            self.path=args['path']
        else:
            self.path='/aktiv/'

        if 'pagename' in args:
            self.pagename=args['pagename']
        else:
            self.pagename='testside_for_medlemssystem'

        self.page=None
        self.site=None

    def login(self):
        """
        login to the wiki. username and password is read from module ``account.py``.

        :return: ``True, 'logged in'`` if login was successful. ``False, 'wrong username or password'`` if unsuccessful.
        """
        self.site=mwclient.Site(self.url, path=self.path, do_init=False)
        try:
            self.site.login(username, passwd)
        except:
            return False, 'wrong username or password'

        return True, 'logged in'

    def read(self):
        """
        Read a page from the wiki.

        :return: ``False, msg`` if not logged in. ``True, text`` if logged in. ``text`` is the text from the page.
        """
        ok, msg=self._check_site_page()
        if not ok:
            return False, msg

        text=self.page.edit()
        if text.strip()=="":
            return False, 'Page does not exist'
        return True, text

    def write(self, text, summary='uploaded from script', append=False, separator='\n'):
        """
        Write to a page on the wiki.

        :param text: the text to write.
        :param summary: edit-summary on wiki. Default: ``uploaded from script``.
        :param append: Append to existing text if ``True``, overwrite if ``False``. Default: ``False``.
        :param separator: Only used if ``Append=True``. Separator between existing text and appended text. Default: ``'\\n'``

        :return: ``False, msg`` if something failes(not logged in, page cannot be opened). ``True, msg`` if ok.
        """
        ok, msg=self._check_site_page()
        if not ok:
            return False, msg

        value=''
        if append:
            try:
                value=self.page.edit()
            except:
                return False, 'Failed to open page'
            value+='{}{}'.format(separator, text)
        else:
            value=text

        status=None
        try:
            self.page.save(value, summary=summary)
        except ValueError:
            status='No page with that name found. Created new page.'
        else:
            status='Saved to page'

        return True, status

    def clear_page(self):
        """
        clears all content on the page.

        :return: ``False, msg`` if not logged in. ``True, msg`` if ok.
        """
        ok, msg=self._check_site_page()
        if not ok:
            return False, msg

        text='== Medlemsliste ==\n'
        try:
            self.page.save(text, summary='Cleared page from script')
        except:
            return False, 'No page to clear'

        return True, 'cleared page'


    def _check_site_page(self):
        """
        check if a user is logged in and the chosen page is accesible.

        :return: ``False, msg`` if not logged in or page cannot be opened. ``True, 'ok'`` if ok.
        """
        if not self.site:
            return False, 'Not logged in!'

        if not self.page:
            try:
                self.page=self.site.Pages[self.pagename]
            except:
                return False, 'Failed to open page'

        return True, 'ok'

    def dict_to_table(self, values, keys, lifetime=False, idindex=0):
        """
        Takes a dict as param and gives a wiki-formated table back.

        :param values: the dictionary to be parsed. Format: ``{id:{key:val, key:val, ...}, id:{key:val, key:val, ...}, ...}``.
        :param keys: a list of keys from the dictionary to write to table.
        :param lifetime: if ``True`` only lifetime members are read from dictionary, if ``False`` only non-lifetime members are read. Default: ``False``.
        :param idindex: index in keys of the ``id`` of a user. This must be gived, as id is ignored in inner-dict. Default: ``0``.
        """
        if not values:
            return False, u'values not given'

        if not isinstance(values, dict):
            return False, u'values must be a dict'

        if not keys:
            return False, u'keys not given'

        if not isinstance(keys, list):
            return False, u'keys must be a list'

        for key, val in values.iteritems():
            for k in keys:
               if not k in val and k != 'id':
                    return False, u'key {} is not in values'.format(k)
            break


        tablestyle=u'{|class="wikitable" style="text-align:left;"\n'

        tablehead=u''
        for key in keys:
            tablehead+=u'!{}\n'.format(key.title())

        del(keys[idindex])

        tablecontent=''
        sorted_keys=sorted(values.iterkeys())
        for id in sorted_keys:
            val=values[id]
            if (lifetime and val['lifetime']=='y') or (not lifetime and val['lifetime']=='n'):
                tablecontent+=u'|-\n'
                if lifetime:
                    tablecontent+=u'|{}\n'.format(id.lower().replace('l', ''))
                else:
                    tablecontent+=u'|{}\n'.format(id)
                for k in keys:
                    tablecontent+=u'|{}\n'.format(val[k].title())

        table=u'{}{}{}|}}'.format(tablestyle, tablehead, tablecontent)
        return True, table

    def wikitable_to_dict(self, table=None, keys=None):
        """
        parse a wiki-formatted table and return a dictionary. for dict-format see :func:`dict_to_table()<wikilink.WikiLink.dict_to_table>`.

        use :func:`get_table_from_text()<wikilink.WikiLink.get_table_from_text>` to get the right values from a page.

        :param table: table returned by :func:`get_table_from_text`
        :param keys: keys returned by :func:`get_table_from_text`
        :return: ``True, dict`` if successful, ``False, errmsg`` if not. dict is formatted like retval from :func:`get_table_from_text()<wikilink.WikiLink.get_table_from_text>`
        """
        pre=None
        post=None
        if not table or not keys:
            ok, msg=self.get_table_from_keys()
            if not ok:
                return false, msg
            table=msg['table']
            keys=msg['keys']
            pre=msg['pre']
            post=msg['post']

        if table.strip()=='':
            return False, 'no table given'
        if keys.strip()=='':
            return False, 'no keys given'

        retval={}
        for tab in table:
            tab=tab.split('\n|')
            if len(tab)>1:
                id=tab[1].strip()
                val={}
                for i in xrange(2, len(keys)):
                    val[keys[i-1].strip()]=tab[i].strip()

                retval[id]=val

        return True, {'pre':pre, 'post':post, 'keys':keys, 'dict':retval}

    def get_table_from_text(self, text):
        """
        Separate a table from the rest of a wiki-formatted page.

        Use :func:`wikitable_to_dict()<wikilink.WikiLink.wikitable_to_dict>` to get a dictionary where table-headers are keys, and normal cells are values.

        returns: ``False, errmsg`` if something failes. ``True, dict`` if successful. Dict-format: {'pre': 'text before dict', 'post': 'text after dict', 'keys':'a list of table headers', 'table':'a list of table-cells'}.
        """
        try:
            text=text.lower()
            tmp=text.split('{')
            pre=tmp[0]
            tmp=tmp[1].split('}')
            post=tmp[1]

            table=tmp[0].split('\n|-')
            keys=table[0].split('\n!')
        except:
            return False, 'IndexError! Is the page formatted correctly?'

        return True, {'pre':pre, 'post':post, 'keys':keys, 'table':table}
