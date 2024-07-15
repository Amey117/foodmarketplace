from datetime import time

temp = []
for h in range(0,24):
    print("h is ",h)
    for m in (0,30):
        print("m is",m)
        t = (time(h,m).strftime('%I:%M %p'),time(h,m).strftime('%I:%M %p'))
        temp.append(t)

print(temp)
