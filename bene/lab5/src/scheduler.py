import sched
import itertools

class Scheduler(object):
    def __init__(self):
        self.current = 0
        self.count = itertools.count()
        self.scheduler = sched.scheduler(self.current_time,self.advance_time)

    def reset(self):
        self.current = 0
    
    def current_time(self):
        return self.current

    def advance_time(self,units):
        # if ((float(self.current) - int(self.current)) == 0):
        #     events = self.scheduler.queue
        #     for event in self.scheduler.queue:
        #         print str(event).split("argument")[0]
        #     print
        #     print
        self.current += units

    def add(self,delay,event,handler):
        return self.scheduler.enter(delay,next(self.count),handler,[event])

    def cancel(self,event):
        self.scheduler.cancel(event)

    def run(self):
        self.scheduler.run()
