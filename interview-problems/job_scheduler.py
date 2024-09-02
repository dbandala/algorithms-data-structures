# Once worker is created it can be used as many times as I want
# Scheduler should pick worker with the lowest index
# Hint: use heap data structure to store the indexes of the workers beeing used

import heapq

class JobScheduler:
    def __init__(self, num_jobs, jobs_starting_time, jobs_duration):
        self.num_jobs = num_jobs
        self.jobs_starting_time = jobs_starting_time
        self.jobs_duration = jobs_duration
        self.workers = {}
        self.workers_in_use = []
        heapq.heapify(self.workers_in_use)

    def sort_jobs(self):
        starting_times_indexes = sorted(range(len(self.jobs_starting_time)), key=lambda k: self.jobs_starting_time[k])
        self.jobs_starting_time = [self.jobs_starting_time[i] for i in starting_times_indexes]
        self.jobs_duration = [self.jobs_duration[i] for i in starting_times_indexes]

    def get_end_time(self, job_start_time, duration):
        start_time_minutes = abs(job_start_time) % 100
        start_time_hours = int(str(job_start_time)[:-2]) if len(str(job_start_time))>2 else 0
        end_time_hours = start_time_hours
        end_time_minutes = start_time_minutes+duration
        if end_time_minutes>=60:
            end_time_hours += 1
            end_time_minutes -=60

        end_time = end_time_hours*100+end_time_minutes
        return end_time


    def launch_jobs(self):
        working_load = []
        for i in range(len(jobs_starting_time)):
            job_start = jobs_starting_time[i]
            job_duration = jobs_duration[i]
            job_end = self.get_end_time(job_start, job_duration)
            
            print("WORKERS_INDEXES: ", list(self.workers_in_use))

            flag_assigned = False
            for j in self.workers_in_use: # O(n*m)
                if (self.workers[j]["job_end_time"]<job_start):
                    self.workers[j] = {"job_index": i, "job_end_time": job_end}
                    working_load.append('J'+str(i)+' W'+str(j))
                    flag_assigned = True
                    break

            if len(self.workers)==0 or not flag_assigned:
                new_worker_index = len(self.workers)
                self.workers[new_worker_index] = {"job_index": i, "job_end_time": job_end} # assigns the time when it will be freed
                working_load.append('J'+str(i)+' W'+str(new_worker_index))
                heapq.heappush(self.workers_in_use, new_worker_index)

        return working_load
    



def print_solution(worker, working_load):
    print(len(worker))
    for wl in working_load:
        print(wl)
            



# Test cases

if __name__ == "__main__":
    in_file = open("sample_input.txt", "r+")
    n_jobs = int(in_file.readline().strip())
    jobs_starting_time = []
    jobs_duration = []
    for _ in range(n_jobs):
        line_data = in_file.readline().replace('\n','').split()
        if len(line_data)<1:
            exit(-1)
        jobs_starting_time.append(int(line_data[0]))
        jobs_duration.append(int(line_data[1]))

    # print("JOBS: ", jobs_starting_time)
    # print("DURATIONS: ", jobs_duration)

    jb = JobScheduler(n_jobs, jobs_starting_time, jobs_duration)
    jb.sort_jobs()
    load = jb.launch_jobs()

    # print(jb.workers)

    print_solution(jb.workers, load)
