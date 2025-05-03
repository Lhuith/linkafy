from threading import Thread

# https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread
# thanks kindall
# not ganna lie, no idea what this does, but it works I think, im sure kindall explained it
#   NOTES: it was like 3 am ok
class NewThread(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        Thread.__init__(self, group, target, name, args, kwargs)

    def run(self):
        if self._target != None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return
