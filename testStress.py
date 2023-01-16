import threading
import time
import requests

urls = ['http://localhost:7777/?password=123']
number_of_threads = 50

def load_url(url):
    response = requests.get(url)
    print(response.status_code)

# Create an empty list to store the threads
threads = []

# Create and start the threads
while True:
  for i in range(number_of_threads):
      for url in urls:
          t = threading.Thread(target=load_url, args=(url,))
          t.start()
          threads.append(t)


  # Wait for all threads to finish
  for t in threads:
      t.join()