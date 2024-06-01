import time
import threading

class Cache():

    cache = {}

    @staticmethod
    def set(key, value):
        Cache.cache[key] = {}
        Cache.cache[key]["result"] = value
        Cache.cache[key]["time"] = time.time()

    @staticmethod
    def get(key):
        if key not in Cache.cache:
            return None
        Cache.cache[key]["time"] = time.time()
        return Cache.cache[key]["result"]

    @staticmethod
    def clear():
        Cache.cache = {}

    @staticmethod
    def __clear_expired():
        for key in list(Cache.cache.keys()):
            if time.time() - Cache.cache[key]["time"] > 600:
                del Cache.cache[key]
        threading.Timer(60, Cache.__clear_expired).start()

#Cache._Cache__clear_expired()