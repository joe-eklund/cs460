testmap = {'a':1,'b':2,'c':2,'blah':5,'to':{'bob':'alice'}}
# testmap2 = {'a':1,'b':2,'c':2,'blah':5,'to':{'bob':'bob'}}
print testmap
for key in testmap.keys():
	print "key="+str(key) + " and value=" + str(testmap[key])

print testmap == testmap2