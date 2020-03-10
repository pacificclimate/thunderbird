class LoadingBar:
    def __init__(self, response, start=0, end=0, num_processes=1):
        self.response = response
        self.start = start
        self.end = end
        self.progress = start
        self.increment = self.set_increment(num_processes)

    def set_increment(self, num_processes):
        if self.start >= self.end:
            raise (
                f"Starting percentage ({self.start}) must be smaller than ending percentage ({self.end})"
            )

        return (self.end - self.start) / num_processes

    def update_range(self, end, num_processes):
        self.start = self.end
        self.end = end
        self.increment = self.set_increment(num_processes)

    def update_status(self, status):
        self.progress += self.increment
        self.response.update_status(status, self.progress)

    def begin(self, status="Starting Process"):
        self.response.update_status(status, self.start)

    def finish_process(self, status="Process Completed"):
        self.response.update_status(status, 100)
