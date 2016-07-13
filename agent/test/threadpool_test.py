#!/usr/bin/env python 
import threadpool 
import time,random 


 
def hello(str): 
    time.sleep(1)
    print "1"
    return str 
 
def print_result(request, result): 
    print "the result is %s %r" % (request.requestID, result) 
 
data = [random.randint(1,10) for i in range(20)] 
print data
 
pool = threadpool.ThreadPool(5) 
i = 0
li = []
pool.wait() 
for it in data:
    i += 1
    if i%7 != 0:
        li.append(it)
    else:
        requests = threadpool.makeRequests(hello, li, print_result) 
        [pool.putRequest(req) for req in requests] 
        li = []
        
print "before wait"
#pool.wait()
print "after wait"
time.sleep(10)

