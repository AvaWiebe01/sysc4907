"""
Shared Memory Module
Provides a thread-safe interface for reading sensor data from POSIX shared memory.
Uses semaphores for synchronization to ensure safe concurrent access between
processes (e.g., sensor data producer and GUI consumer).
"""

import time
import numpy as np
import posix_ipc
import mmap
import os

# Name of the POSIX shared memory segment for sensor readings.
SHM_NAME = "shared_sensor_readings"
# Name of the POSIX semaphore for synchronizing access to shared memory.
SEM_NAME = "access_readings_sem"

class SharedDataArray:
    """
    Thread-safe wrapper for accessing sensor data stored in POSIX shared memory.
    Provides synchronized read/write operations using a semaphore to prevent
    race conditions between the data producer (sensor process) and consumer (GUI).

    The shared memory contains a 4-element float32 array:
    - [0]: Timestamp of the reading
    - [1]: Road condition value (1-5 scale)
    - [2]: Raw sensor data
    - [3]: Exit flag (set to 1.0 to signal shutdown)

    Attributes:
        sem: POSIX semaphore for synchronizing access.
        shm: POSIX shared memory segment object.
        map: Memory-mapped view of the shared memory.
        view: NumPy array view of the shared memory data.
    """

    def __init__(self):
        """
        Initialize the shared memory interface.
        Attempts to connect to existing shared memory and semaphore.
        If not available, waits and retries until the shared memory is created
        by the sensor data producer process.
        """
        # Retry loop to wait for shared memory to be created by another process.
        while True:
            try:
                # Open the existing semaphore for synchronization.
                self.sem = posix_ipc.Semaphore(SEM_NAME)
                # Open the existing shared memory segment.
                self.shm = posix_ipc.SharedMemory(name=SHM_NAME)
                # Get the size of the shared memory segment.
                size = os.fstat(self.shm.fd).st_size
                # Create a memory-mapped view of the shared memory.
                self.map = mmap.mmap(self.shm.fd, size)
                # Create a NumPy array view of the memory-mapped data.
                # Assumes 4 float32 values: [timestamp, condition, raw_data, exit_flag]
                self.view = np.ndarray((4,), dtype=np.float32, buffer=self.map)
                # Successfully connected, exit the retry loop.
                break
            except (FileNotFoundError, posix_ipc.ExistentialError):
                # Shared memory or semaphore not yet created by producer process.
                print("Waiting for shared memory...")
                # Wait briefly before retrying.
                time.sleep(0.5)

    def read(self):
        """
        Thread-safe read operation for sensor data.
        Acquires the semaphore, copies the current data, then releases the semaphore.
        Returns a copy to prevent external modifications to the shared data.

        Returns:
            np.ndarray: Copy of the 4-element sensor data array.
        """
        # Acquire the semaphore to ensure exclusive access to shared memory.
        self.sem.acquire()
        try:
            # Return a copy of the data to prevent external modifications.
            return np.copy(self.view)
        finally:
            # Always release the semaphore, even if an exception occurs.
            self.sem.release()

    def set_exit_flag(self):
        """
        Set the exit flag in shared memory to signal shutdown.
        Thread-safe operation that sets the exit flag (index 3) to 1.0.
        Used to communicate shutdown requests to the sensor data producer.
        """
        # Acquire semaphore for thread-safe write operation.
        self.sem.acquire()
        try:
            # Set the exit flag to 1.0 to signal the producer to shut down.
            self.view[3] = 1.0
        finally:
            # Release semaphore to allow other processes to access shared memory.
            self.sem.release()

    def close(self):
        """
        Clean up shared memory resources.
        Sets the exit flag, then closes the memory map, shared memory segment,
        and semaphore. Includes error handling to ensure cleanup completes
        even if some resources are already closed.
        """
        # Set the exit flag to signal the producer process to terminate.
        self.set_exit_flag()

        # Flush any pending writes to the memory-mapped file.
        try:
            self.map.flush()
        except Exception:
            # Ignore errors if the map is already closed or invalid.
            pass

        # Close the memory-mapped view.
        try:
            self.map.close()
        except Exception:
            # Ignore errors if already closed.
            pass

        # Close the shared memory file descriptor.
        try:
            self.shm.close_fd()
        except Exception:
            # Ignore errors if already closed.
            pass

        # Close the semaphore.
        try:
            self.sem.close()
        except Exception:
            # Ignore errors if already closed.
            pass
