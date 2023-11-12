import os
import time
import ray
# 
# # Normal Python
# def fibonacci_local(sequence_size):
#     fibonacci = []
#     for i in range(0, sequence_size):
#         if i < 2:
#             fibonacci.append(i)
#             continue
#         fibonacci.append(fibonacci[i-1]+fibonacci[i-2])
#     return sequence_size

# Ray task


total = []

@ray.remote
def fibonacci_distributed(sequence_size):
    import time
    time.sleep(101)
    print("In this module printing")
    total.append("12334")
    return "9777"

def run_remote(sequence_size):
    # Starting Ray
    ray.init()
    start_time = time.time()
    results = ray.get([fibonacci_distributed.remote(sequence_size) for _ in range(os.cpu_count())])
    print(total)

    duration = time.time() - start_time
    print(type(results))
    print(results)
    print('Sequence size: {}, Remote execution time: {}'.format(sequence_size, duration))  
    print(total)

run_remote(1000)
#print(ray.get([fibonacci_distributed.remote(1000)]))