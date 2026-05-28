class Lifecycle:

    def __init__(self):

        self.running = False
        self.sleeping = False

    def start(self):

        self.running = True

    def stop(self):

        self.running = False

    def sleep(self):

        self.sleeping = True

    def wake(self):

        self.sleeping = False

    def is_running(self):

        return self.running

    def is_sleeping(self):

        return self.sleeping


lifecycle = Lifecycle()