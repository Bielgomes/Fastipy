import time

class Timer():
  def __init__(self):
    self.start = time.time()

  def end(self):
    self.end = time.time()

    elapsed_time = (self.end - self.start) * 1000
    print(f"Debug > Function execution time: {elapsed_time.__round__(2)} ms")