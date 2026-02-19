#include <fcntl.h>
#include <sys/mman.h>
#include <semaphore.h>
#include <unistd.h>
#include <cstdlib> // For rand() and srand()
#include <ctime>   // For time()

class SharedData
{
    /*
    Please include the following libraries to use this class:
    #include <fcntl.h>
    #include <sys/mman.h>
    #include <semaphore.h>
    #include <unistd.h>
    */

    private:

    /*
        -dataStruct stores a float array of size 4

        -the contents stored in float array should look like this:

        {time_interval, sensor_readings, condition_scale(1 - 5), exit_flag}
    */
    
    struct dataStruct {
        float values[4]; //DO NOT CHANGE THIS
    };

    //DO NOT CHANGE THESE
    const char* shm_name = "shared_sensor_readings";
    const char* sem_name = "access_readings_sem";
    sem_t* semaphore;
    dataStruct* data;
    int shm_fd;
    

    public:

    SharedData() {
        shm_fd = shm_open(shm_name, O_CREAT | O_RDWR, 0666);
        ftruncate(shm_fd, sizeof(dataStruct));
        data = (dataStruct*)mmap(0, sizeof(dataStruct), PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);    
        semaphore = sem_open(sem_name, O_CREAT, 0666, 1);
    }

    //Writes the new values to shared_memory
    void send_data(float time_interval, float sensor_readings, float road_rating) {
        sem_wait(semaphore);
        data->values[0] = time_interval;
        data->values[1] = sensor_readings;
        data->values[2] = road_rating;
        sem_post(semaphore);
    }

    bool exited(){
        bool flag = false;
        sem_wait(semaphore);
        flag = (data->values[3] == 1.0f);
        sem_post(semaphore);
        return flag;
    }

    void cleanup(){
        munmap(data, sizeof(dataStruct));
        close(shm_fd);
        shm_unlink(shm_name);
        sem_close(semaphore);
        sem_unlink(sem_name);
    }

};

/*
//This is a test program. You can delete main if you want, or just copy th class into another c++ file.
int main() {
    SharedData shared_variable = SharedData();

    std::srand(std::time(nullptr));

    while (shared_variable.exited() == false) {
        shared_variable.send_data(0.1f,(static_cast<float>(std::rand() % 41) - 20.0f), (static_cast<float>(std::rand() % 5) + 1));
        usleep(50000); // Sleep 0.05s
    }
    shared_variable.cleanup();
    return 0;
}
*/