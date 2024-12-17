# import numpy as np
# from tim_sort_p import tim_sort_py
# from tim_sort import timSort
# import time

# arr = np.random.randint(0, 5000000, size=5000000, dtype=np.int32)

# python_arr = arr.copy()
# start_time = time.time()
# tim_sort_py(python_arr)
# python_time =(time.time() - start_time) * 1000
# print("Time taken to sort with Python Tim Sort:", python_time, "ms")

# # Tim Sort in Cython
# cython_arr = arr.copy()
# start_time = time.time()
# timSort(cython_arr)
# cython_time = (time.time() - start_time) * 1000
# print("Time taken to sort with Cython Tim Sort:", cython_time, "ms")



# # Python's built-in sort
# built_in_arr = arr.copy()
# start_time = time.time()
# built_in_arr.sort()
# built_in_time = (time.time() - start_time) * 1000
# print("Time taken to sort with Python's built-in sort:", built_in_time, "ms")

# # Create a random array
# arr = np.random.randint(0, 5000000, size=5000000, dtype=np.int32)
# #print(arr)
# start_time = time.time()
# # Call timSort and record time
# timSort(arr)
# end_time = time.time()
# #print("Time taken to sort random", start_time)
# print("Time taken to sort random with timsort", (end_time-start_time) * 1000)

# start_time = time.time()
# # Call timSort and record time
# arr.sort()
# end_time = time.time()
# print("Time taken to sort random with inbuilt function", (end_time-start_time) * 1000)
# #print("After Sorting the array using tim sort algorithm")
# #print("Sorted array:", arr)

import numpy as np
import time
from tim_sort import timSort  # Updated Cython implementation
from tim_sort_p import tim_sort_py  # Python implementation

# Dataset Generators
def generate_datasets(size):
    random_data = np.random.randint(0, size, size=size).tolist()
    reverse_sorted_data = sorted(random_data, reverse=True)
    partially_sorted_data = sorted(random_data[: size // 2]) + random_data[size // 2 :]
    already_sorted_data = sorted(random_data)
    return {
        "Random": random_data,
        "Reverse Sorted": reverse_sorted_data,
        "Partially Sorted": partially_sorted_data,
        "Already Sorted": already_sorted_data,
    }

def benchmark_algorithms(size=500000):
    datasets = generate_datasets(size)
    print(f"Benchmarking for size={size}:")
    for name, data in datasets.items():
        print(f"\n{name} Dataset:")

        # Python TimSort
        py_data = data.copy()
        start_time = time.perf_counter()
        tim_sort_py(py_data)
        print(f"Python TimSort: {(time.perf_counter() - start_time) * 1000:.2f} ms")

        # Cython Optimized TimSort
        cy_data = np.array(data.copy(), dtype=np.int32)
        start_time = time.perf_counter()
        timSort(cy_data)
        print(f"Cython TimSort: {(time.perf_counter() - start_time) * 1000:.2f} ms")

       # Python Built-in Sort
        built_in_data = data.copy()
        start_time = time.perf_counter()
        built_in_data.sort()
        print(f"Python Built-in Sort: {(time.perf_counter() - start_time) * 1000:.2f} ms")

if __name__ == "__main__":
    benchmark_algorithms(size=1000000)
