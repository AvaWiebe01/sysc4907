import numpy as np
import math 
import scipy  
import argparse
import os
import matplotlib.pyplot as plt
import iriCalculator
import numpy as np

SHM_NAME = "shared_road_matrix"
SEM_NAME = "access_matrix_sem"

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
        try:
            return np.copy(self.view)
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

    def write(self, result):
        self.sem.acquire()
        try:
            self.view[0] = result
            self.view[1] = 1.0 #Sets changed flag to true
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
    #sharedIri = SharedResult() 
    #sharedMemRoadMatrix = SharedRoadMatrix()
    
    
    while(True):
        readings = sharedMemRoadMatrix.read()
       # j = 0
        #readings = [[0 for _ in range(2)] for _ in range(151)]
        
        """while  j <= 149:
            #readings[j][0] = j* 1.1000001

            
            if (j % 2) == 0:
                readings[j][1] = j*0.0003
            else:
                readings[j][1] = j*-0.0001
            j+=1
        """
        #readings[150][0] = 1.0

        if (readings[150][0] == 1.0):
            segmentLength = readings[149][0]
            result = iriCalculator.iri(np.array(readings[0:150]), segmentLength, readings[0][0], step=0, box_filter=False, method=2)
            #print(result[0,2])
            sharedIri.write(result[0,2])
            result = iriCalculator.iri(readings[0:149],0,0)
            sharedIri.write(result)
    
