import threading
from collections import deque
from concurrent import futures

class WorkerPool:
    
    def __init__(self,max_workers,number_of_tasks,worker_task):
        """
        Initalises a pool of worker threads

        Parameters
        ----------
        max_workers : int
            The maximum number of threads to use.
        number_of_tasks : int
            The number of job batches in total.
        worker_task : function
            The task to run for each worker.

        Returns
        -------
        None.

        """
        self.worker_count = max_workers
        self.worker_task = worker_task
        self.number_of_tasks = number_of_tasks
        self.worker = worker_task
        
        #Set up thread objects
        self.work = deque()
        result = deque()
        self.finished = threading.Event()
        self.pool = futures.ThreadPoolExecutor(self.worker_count)
    
        #Add workers into pool
        for _ in range(self.worker_count):
            self.pool.submit(self.worker,self.work,result,self.finished)

    def run(self,task_list,start=0):
        """
        Starts the worker pool from the given start point.

        Parameters
        ----------
        start : int, optional
            The batch number to start on. The default is 0.

        Returns
        -------
        None.

        """
        #Add the tasks to the work queue
        for task in task_list[start:]:
           self.work.appendleft(task)
        
        #Indicate that the work queue is complete
        self.finished.set()
    
        #Shut down the pool after the final task is completed
        self.pool.shutdown()