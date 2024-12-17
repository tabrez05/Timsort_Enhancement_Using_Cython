# distutils: language = c++
# cython: boundscheck=False, wraparound=False, initializedcheck=False
# cython: cdivision=True
# cython: language_level=3

cimport cython
from cython.parallel import prange
from libc.stdlib cimport malloc, free

@cython.cfunc
@cython.inline
cdef int min_run_length(int n) noexcept:
    """Calculates the minimum run length for TimSort."""
    cdef int r = 0
    while n >= 64:
        r |= n & 1
        n >>= 1
    return n + r

@cython.boundscheck(False)
@cython.wraparound(False)
cdef void reverse_in_place(int[:] arr, int left, int right) noexcept:
    """Reverses elements in arr[left:right+1] in place."""
    cdef int temp
    while left < right:
        temp = arr[left]
        arr[left] = arr[right]
        arr[right] = temp
        left += 1
        right -= 1

@cython.boundscheck(False)
@cython.wraparound(False)
cdef void insertion_sort(int[:] arr, int left, int right) noexcept:
    """
    Optimized insertion sort:
    - Detects descending runs and reverses them in place.
    - Sorts the resulting runs using insertion sort.
    """
    cdef int i, j, key, run_start, descending

    # Detect runs and reverse descending ones
    run_start = left
    descending = 0
    for i in range(left + 1, right + 1):
        if arr[i] < arr[i - 1]:
            descending = 1
        elif arr[i] > arr[i - 1] and descending:
            # End of descending run: reverse it
            reverse_in_place(arr, run_start, i - 1)
            descending = 0
            run_start = i
        else:
            run_start = i

    # Final check for a descending run at the end of the range
    if descending:
        reverse_in_place(arr, run_start, right)

    # Perform regular insertion sort
    for i in range(left + 1, right + 1):
        key = arr[i]
        j = i - 1
        while j >= left and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key

@cython.boundscheck(False)
@cython.wraparound(False)
cdef void gallop_merge(int[:] arr, int left_arr[], int right_arr[], int len1, int len2, int left) noexcept:
    """Merges two sorted arrays into arr using galloping mode optimization."""
    cdef int i = 0, j = 0, k = left
    cdef int gallop_count = 0
    cdef int max_gallop = 4  # Start galloping after 4 consecutive elements

    # Merge with galloping optimization
    while i < len1 and j < len2:
        if left_arr[i] <= right_arr[j]:
            arr[k] = left_arr[i]
            i += 1
        else:
            arr[k] = right_arr[j]
            j += 1
        k += 1

        # Check for consecutive choices and enable galloping
        gallop_count += 1
        if gallop_count >= max_gallop:
            # Galloping Mode
            while i < len1 and left_arr[i] <= right_arr[j]:
                arr[k] = left_arr[i]
                i += 1
                k += 1
            while j < len2 and right_arr[j] < left_arr[i]:
                arr[k] = right_arr[j]
                j += 1
                k += 1
            gallop_count = 0  # Reset count

    # Copy remaining elements
    while i < len1:
        arr[k] = left_arr[i]
        i += 1
        k += 1
    while j < len2:
        arr[k] = right_arr[j]
        j += 1
        k += 1

@cython.boundscheck(False)
@cython.wraparound(False)
cdef void merge(int[:] arr, int left, int mid, int right) noexcept:
    """Merge two sorted subarrays with galloping mode."""
    cdef int i = 0, j = 0
    cdef int len1 = mid - left + 1
    cdef int len2 = right - mid
    
    cdef int* left_arr = <int*> malloc(len1 * sizeof(int))
    cdef int* right_arr = <int*> malloc(len2 * sizeof(int))

    try:
        # Copy data to temporary arrays
        for i in range(len1):
            left_arr[i] = arr[left + i]
        for j in range(len2):
            right_arr[j] = arr[mid + 1 + j]

        # Merge with galloping mode optimization
        gallop_merge(arr, left_arr, right_arr, len1, len2, left)
    finally:
        free(left_arr)
        free(right_arr)

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef void timSort(int[:] arr) noexcept:
    """
    TimSort algorithm:
    - Detects small chunks and sorts them using optimized insertion sort.
    - Merges sorted runs iteratively with galloping mode optimization.
    """
    cdef int n = arr.shape[0]
    cdef int min_run = min_run_length(n)
    cdef int start, end, size, left, mid, right

    # Step 1: Perform optimized insertion sort on small chunks
    for start in range(0, n, min_run):
        end = min(start + min_run - 1, n - 1)
        insertion_sort(arr, start, end)

    # Step 2: Iteratively merge sorted runs
    size = min_run
    while size < n:
        for left in prange(0, n, 2 * size, nogil=True):  # Parallel merging
            mid = min(left + size - 1, n - 1)
            right = min(left + 2 * size - 1, n - 1)
            if mid < right:
                merge(arr, left, mid, right)
        size *= 2
