from multiprocessing import Process, Queue

# A general purpose class for producer consumer queues on a separate process
# stop the process by appending 'DONE' to the queue.
class ProcessorConsumerQueueProcess(Process):
    def __init__(self):
        Process.__init__(self)
        self.queue = Queue()
        # terminates this process when main process ends.
        self.daemon = True
        self.start()

    # put item from another process.
    def put_item(self, item):
        self.queue.put(item)

    def process_item(self, item):
        print item
        # this method should be overridden by inherited classes.
        pass

    def run(self):
        while True:
            try:
                item = self.queue.get(True, 1)
                if item == 'DONE':
                    return
                else:
                    self.process_item(item)
            except:
                # queue.get throws if there is no item after the timeout.
                # for us this is fine, we continue.
                pass
