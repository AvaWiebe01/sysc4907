#include <fcntl.h>
#include <sys/mman.h>
#include <semaphore.h>
#include <unistd.h>
#include <cstdlib> // For rand() and srand()
#include <ctime>   // For time()
#include<iostream>

#define NOTREADY -1.0
using namespace std;
class SharedIRI
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
        -dataStruct stores a float array of size 3

        -the contents stored in float array should look like this:

        {time_interval, sensor_readings, condition_scale(1 - 5)}
    */
    
    struct dataStruct {
        float values[2]; //DO NOT CHANGE THIS
    };

    //DO NOT CHANGE THESE
    const char* shm_name = "shared_iri";
    const char* sem_name = "access_iri_sem";
    sem_t* semaphore;
    volatile dataStruct* data;
	int shm_fd;
    

    public:

    SharedIRI() {
        int shm_fd = shm_open(shm_name, O_CREAT | O_RDWR, 0666);
        ftruncate(shm_fd, sizeof(dataStruct));
        data = (dataStruct*)mmap(0, sizeof(dataStruct), PROT_READ | PROT_WRITE, MAP_SHARED, shm_fd, 0);    
        semaphore = sem_open(sem_name, O_CREAT, 0666, 1);
    }

    //Writes the new values to shared_memory
    float read_data() {
        float result = -1;
        sem_wait(semaphore);
		//cout<<"reading from python\n";
		//cout<<data->values[1];
        if(data->values[1] > 0.0){
            result = data->values[0]; 
			data->values[1] = NOTREADY;
        }
        sem_post(semaphore);
        return result;
    }
};






