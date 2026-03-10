import time
import numpy as np
import posix_ipc
import mmap
import os
import iriCalculator

SHM_NAME = "shared_road_matrix"
SEM_NAME = "access_matrix_sem"

#define constants
READY = 1.0
NOTREADY = -1.0

class SharedRoadMatrix:
    def __init__(self):
        while True:
            try:
                self.sem = posix_ipc.Semaphore(SEM_NAME)
                self.shm = posix_ipc.SharedMemory(name=SHM_NAME)
                size = os.fstat(self.shm.fd).st_size
                self.map = mmap.mmap(self.shm.fd, size)
                self.view = np.ndarray((151, 2), dtype=np.float32, buffer=self.map)
                break
            except (FileNotFoundError, posix_ipc.ExistentialError):
                print("Waiting for shared memory...")
                time.sleep(0.5)

    def read(self):
        self.sem.acquire()
        #print(self.view)
        try:
            if self.view[150, 0] > 0.0:
                #print("\nPython ack")
                returned = np.copy(self.view)
                self.view[150,0] = NOTREADY
                return returned
            else:
                #print("not ready \n")
                return np.zeros((151,2))
        finally:
            self.sem.release()


    def close(self):

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


SHMR_NAME = "shared_iri"
SEMR_NAME = "access_iri_sem"

class SharedResult:
    def __init__(self):
        while True:
            try:
                self.sem = posix_ipc.Semaphore(SEMR_NAME)
                self.shm = posix_ipc.SharedMemory(name=SHMR_NAME)
                size = os.fstat(self.shm.fd).st_size
                self.map = mmap.mmap(self.shm.fd, size)
                self.view = np.ndarray((2,), dtype=np.float32, buffer=self.map)
                break
            except (FileNotFoundError, posix_ipc.ExistentialError):
                print("Waiting for shared memory...")
                time.sleep(0.5)
        self.view[1] = 0
        """
        try:
            posix_ipc.unlink_shared_memory(SHMR_NAME)
        except (posix_ipc.ExistentialError):
            pass
            
        try:
            posix_ipc.unlink_semaphore(SEMR_NAME)
        except (posix_ipc.ExistentialError):
            pass
            
        self.size = 8 #for 2 floats
            
        self.sem = posix_ipc.Semaphore(SEMR_NAME, posix_ipc.O_CREAT, initial_value=1)
        self.shm = posix_ipc.SharedMemory(SHMR_NAME, posix_ipc.O_CREAT, size=self.size)
        self.map = mmap.mmap(self.shm.fd, self.size)
        self.shm.close_fd()
        self.view = np.ndarray((2,), dtype=np.float32, buffer=self.map)
"""
    def write(self, result):
        self.sem.acquire()
        try:
            print("write to shared mem")
            print(result)
            
            self.view[0] = result
            self.view[1] = 1.0 #Sets changed flag to true
            print(self.view )
        finally:
            self.sem.release()

    def close(self):
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
            
        try:
            posix_ipc.unlink_shared_memory(SHMR_NAME)
        except (posix_ipc.ExistentialError):
            pass
            
        try:
            posix_ipc.unlink_semaphore(SEMR_NAME)
        except (posix_ipc.ExistentialError):
            pass



if __name__ == "__main__":
    sharedIri = SharedResult() 
    sharedMemRoadMatrix = SharedRoadMatrix()
    
    while(True):

        readings = sharedMemRoadMatrix.read()
        if (readings[150][0] == 1.0):
            #readings[150][0] == 0;
            segmentLength = readings[149][0]
            result = iriCalculator.iri(np.array(readings[0:150]), segmentLength, readings[0][0], step=0, box_filter=False, method=2)
            result = result[0,2]
            print(result)
            if not isinstance(result, float): 
                result = -2.0
            sharedIri.write(result)
    
