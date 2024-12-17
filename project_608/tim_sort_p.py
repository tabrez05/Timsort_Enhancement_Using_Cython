# tim_sort_P.py

def min_run_length(n):
    r = 0
    while n >= 64:
        r|= n&1
        n>>=1
    return n + r

def insertion_sort(arr, left, right):
    for i in range(left + 1, right + 1):
        key = arr[i]
        j = i - 1
        while j >= left and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key

def merge(arr, left, mid, right):
    len1, len2 = mid - left + 1, right - mid
    left_arr, right_arr = arr[left:mid + 1], arr[mid + 1:right + 1]
    i = j = 0
    k = left
    while i < len1 and j < len2:
        if left_arr[i] <= right_arr[j]:
            arr[k] = left_arr[i]
            i += 1
        else:
            arr[k] = right_arr[j]
            j += 1
        k += 1
    while i < len1:
        arr[k] = left_arr[i]
        i += 1
        k += 1
    while j < len2:
        arr[k] = right_arr[j]
        j += 1
        k += 1

def tim_sort_py(arr):
    n = len(arr)
    min_run = min_run_length(n)
    for start in range(0, n, min_run):
        end = min(start + min_run - 1, n - 1)
        insertion_sort(arr, start, end)
    size = min_run
    while size < n:
        for left in range(0, n, 2 * size):
            mid = min(left + size - 1, n - 1)
            right = min(left + 2 * size - 1, n - 1)
            if mid < right:
                merge(arr, left, mid, right)
        size *= 2
