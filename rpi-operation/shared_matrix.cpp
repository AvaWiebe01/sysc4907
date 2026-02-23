#include <fcntl.h>
#include <sys/mman.h>
#include <semaphore.h>
#include <unistd.h>
#include <cstdlib> // For rand() and srand()
#include <ctime>   // For time()

class SharedMatrix
{

    private:
    
    struct dataStruct {
        float values[151][2]; //DO NOT CHANGE THIS
    };

    //DO NOT CHANGE THESE
    const char* shm_name = "shared_road_matrix";
    const char* sem_name = "access_matrix_sem";
    sem_t* semaphore;
    dataStruct* data;
    int shm_fd;
    

    public:

    SharedMatrix() {
        shm_fd = shm_open(shm_name, O_CREAT | O_RDWR, 0666);
        ftruncate(shm_fd, sizeof(dataStruct));
        data = (dataStruct*)mmap(0, sizeof(dataStruct), PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);    
        semaphore = sem_open(sem_name, O_CREAT, 0666, 1);
    }

    //Writes the new values to shared_memory
    void send_data(float matrix[151][2]) {
        sem_wait(semaphore);
        for(int i = 0; i <= 149; i++){
            data->values[i][0] = matrix[i][0];
            data->values[i][1] = matrix[i][1];
        }
        data->values[150][0] = 1; // update ready flag
        sem_post(semaphore);
    }

    void cleanup(){
        munmap(data, sizeof(dataStruct));
        close(shm_fd);
        shm_unlink(shm_name);
        sem_close(semaphore);
        sem_unlink(sem_name);
    }
};






