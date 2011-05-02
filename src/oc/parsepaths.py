f = open("paths.dat",'r')

current_path = ""
count = 4 
for line in f:
    if line == "@@@\n":
        print "found delimiter"
        out = open("paths/path" + str(count) + ".dat", 'w')
        out.write(current_path)
        out.close()
        current_path = ""
        count += 1
    else:
        current_path += line

if(current_path != ""):
    out = open("paths/path" + str(count) + ".dat",'w')
    out.write(current_path)
    out.close()
