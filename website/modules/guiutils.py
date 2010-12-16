import threading


class WaitCallbacks(object):
    _active = {}
    _active_lock = threading.Lock()
    

    @classmethod
    def is_pending(cls, u):
        with cls._active_lock:
            if u in cls._active:
                return cls._active.get(u) == 'pending'
            else:
                return False
            
    @classmethod
    def declare(cls, u):
        with cls._active_lock:
            while u in cls._active:
                pass
            cls._active.update({u:'pending'})
            
    @classmethod
    def free(cls, u):
        with cls._active_lock:
            if u in cls._active:
                cls._active.pop(u)

    @classmethod
    def update(cls, u, status):
        with cls._active_lock:
            cls._active.update({u:status})
            
            
    @classmethod
    def status(cls, u):
        with cls._active_lock:
            if u in cls._active:
                return cls._active.get(u)
            else:
                return None
