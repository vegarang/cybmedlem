from storage import Storage

s=Storage(**{'fields':['name'], 'ident':'name'})

print 'start create'
retval=s.create(**{'name':'nisse', 'some':'stuff'})

if 'error' in retval:
    print retval['error']

if 'success' in retval:
    print retval['success']
    print retval['object']

print 'done create'

print 'start read'
retval=s.read(**{'id':0})
print retval
print 'done id-read'

retval=s.read(**{'name':'nisse'})
print retval
print 'done name-read'

print 'start faulty update'
print s.update(**{'name':'julenisse', 'extra':'awesome dude'})
print s.update(**{'id':20, 'name':'julenisse', 'extra':'awesome dude'})

print 'done faulty update'
print 'start update'
retval=s.update(**{'id':0, 'name':'julenisse', 'extra':'awesome dude'})
print retval
print 'done update'

print 'all done'
