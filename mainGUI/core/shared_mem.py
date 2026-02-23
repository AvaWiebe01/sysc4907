import time
import numpy as np
import posix_ipc
import mmap
import os

SHM_NAME = "shared_sensor_readings"
SEM_NAME = "access_readings_sem"

class SharedDataArray:
    def __init__(self):
        while True:
            try:
                self.sem = posix_ipc.Semaphore(SEM_NAME)
                self.shm = posix_ipc.SharedMemory(name=SHM_NAME)
                size = os.fstat(self.shm.fd).st_size
                self.map = mmap.mmap(self.shm.fd, size)
                self.view = np.ndarray((4,), dtype=np.float32, buffer=self.map)
                break
            except (FileNotFoundError, posix_ipc.ExistentialError):
                print("Waiting for shared memory...")
                time.sleep(0.5)

    def read(self):
        self.sem.acquire()
        try:
            return np.copy(self.view)
        finally:
            self.sem.release()

    def set_exit_flag(self):
        self.sem.acquire()
        try:
            self.view[3] = 1.0
        finally:
            self.sem.release()

    def close(self):
        self.set_exit_flag()

        try: 
            self.map.flush()
        except Exception:
            pass

        try: 
            self.map.close()
        except Exception:
            pass

        try: 
            self.shm.close_fd()
        except Exception:
            pass

        try:
            self.sem.close()
        except Exception:
            pass
