import threading


class WaitCallbacks(object):
    _active = {}
    _active_lock = threading.Lock()
    _message = {}
    _message_lock = threading.Lock()

    

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
                


    @classmethod
    def erase_message(cls, u):
        with cls._message_lock:
            if u in cls._message:
                cls._message.pop(u)

    @classmethod
    def update_message(cls, u, msg):
        with cls._message_lock:
            cls._message.update({u:status})
    
    @classmethod
    def message_present(cls, u):
        with cls._message_lock:
            return u in cls._message
            
    @classmethod
    def get_message(cls, u):
        with cls._message_lock:
            if u in cls._message:
                return cls._message.get(u)
            else:
                return None
