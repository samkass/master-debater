from time import sleep


# Return a string of numbers to simulate a streaming chat service to help with testing
class ChatTestIterator:
    i = 0

    def __init__(self, count=10):
        self.count = count

    def __iter__(self):
        # pause 0.5 seconds and yield some numbers.
        for i in range(self.count):
            sleep(0.2)
            i += 1
            yield f"{i} "
