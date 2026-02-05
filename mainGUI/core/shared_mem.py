import time
import numpy as np
import posix_ipc
from multiprocessing import shared_memory

SHM_NAME = "shared_sensor_readings"
SEM_NAME = "access_readings_sem"

class SharedDataArray:
    def __init__(self):
        while True:
            try:
                self.sem = posix_ipc.Semaphore(SEM_NAME)
                self.shm = shared_memory.SharedMemory(name=SHM_NAME)
                self.view = np.ndarray((3,), dtype=np.float32, buffer=self.shm.buf)
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

    def close(self):
        try:
            self.shm.close()
        except Exception:
            pass
