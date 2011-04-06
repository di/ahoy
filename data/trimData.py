
filename = "AIS_probs.dat"

filein = open(filename,'r')
mainout = open("AIS_trimmed.dat",'w')
above = open("AIS_trimmed_north.dat",'w')
below = open("AIS_trimmed_south.dat",'w')

n = 1

for line in filein:
	l = line.rstrip('\n')
	data = l.split(':')
	fromlat = float((data[0].split(','))[0])
	tolat = float((data[1].split(','))[0])
	if(fromlat <= 40.0 and fromlat >= 39.82):
		mainout.write(line)
	elif(fromlat < 39.82):
		below.write(line)
	else:
		above.write(line)

	print str(n)
	n += 1
filein.close()
mainout.close()
above.close()
below.close()


