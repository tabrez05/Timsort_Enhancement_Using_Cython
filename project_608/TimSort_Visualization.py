import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
import numpy as np
import random

# TimSort Parameters
RUN = 32

def min_run_length(n):
    """Calculates the minimum run length for TimSort."""
    r = 0
    while n >= 64:
        r |= n & 1
        n >>= 1
    return n + r

def reverse_in_place(arr, left, right, frames, metrics):
    """Reverses elements in arr[left:right+1] in place."""
    while left < right:
        arr[left], arr[right] = arr[right], arr[left]
        metrics['swaps'] += 1
        frames.append((list(arr), left, right, "In-Place Reverse", metrics['comparisons'], metrics['swaps']))
        left += 1
        right -= 1

def insertion_sort(arr, left, right, frames, metrics):
    """Insertion sort with reverse detection for descending runs."""
    run_start = left
    descending = False
    for i in range(left + 1, right + 1):
        if arr[i] < arr[i - 1]:
            descending = True
        elif arr[i] > arr[i - 1] and descending:
            reverse_in_place(arr, run_start, i - 1, frames, metrics)
            descending = False
            run_start = i
        else:
            run_start = i

    # Regular insertion sort
    for i in range(left + 1, right + 1):
        key = arr[i]
        j = i - 1
        while j >= left:
            metrics['comparisons'] += 1
            frames.append((list(arr), j, j + 1, "Insertion Phase (Compare)", metrics['comparisons'], metrics['swaps']))
            if arr[j] > key:
                arr[j + 1] = arr[j]
                metrics['swaps'] += 1
                frames.append((list(arr), j, j + 1, "Insertion Phase (Swap)", metrics['comparisons'], metrics['swaps']))
                j -= 1
            else:
                break
        arr[j + 1] = key
        frames.append((list(arr), j + 1, i, "Insertion Phase (Insert)", metrics['comparisons'], metrics['swaps']))

def gallop_merge(arr, left_arr, right_arr, len1, len2, left, frames, metrics):
    """Merges two arrays using galloping optimization."""
    i, j, k = 0, 0, left
    while i < len1 and j < len2:
        metrics['comparisons'] += 1
        frames.append((list(arr), left + i, len1 + j, "Galloping Phase (Compare)", metrics['comparisons'], metrics['swaps']))
        if left_arr[i] <= right_arr[j]:
            arr[k] = left_arr[i]
            i += 1
        else:
            arr[k] = right_arr[j]
            j += 1
        k += 1
        metrics['swaps'] += 1
        frames.append((list(arr), k - 1, -1, "Galloping Phase (Merge)", metrics['comparisons'], metrics['swaps']))

    while i < len1:
        arr[k] = left_arr[i]
        i += 1
        k += 1
        metrics['swaps'] += 1
        frames.append((list(arr), k - 1, -1, "Galloping Phase (Copy Left)", metrics['comparisons'], metrics['swaps']))

    while j < len2:
        arr[k] = right_arr[j]
        j += 1
        k += 1
        metrics['swaps'] += 1
        frames.append((list(arr), k - 1, -1, "Galloping Phase (Copy Right)", metrics['comparisons'], metrics['swaps']))

def merge(arr, left, mid, right, frames, metrics):
    """Merges two sorted subarrays."""
    len1, len2 = mid - left + 1, right - mid
    left_arr = arr[left:left + len1]
    right_arr = arr[mid + 1:mid + 1 + len2]
    gallop_merge(arr, left_arr, right_arr, len1, len2, left, frames, metrics)

def tim_sort(arr):
    """TimSort implementation in Python."""
    n = len(arr)
    frames = [(list(arr), -1, -1, "Start", 0, 0)]
    metrics = {'comparisons': 0, 'swaps': 0}
    min_run = min_run_length(n)

    for start in range(0, n, min_run):
        end = min(start + min_run - 1, n - 1)
        insertion_sort(arr, start, end, frames, metrics)

    size = min_run
    while size < n:
        for left in range(0, n, 2 * size):
            mid = min(left + size - 1, n - 1)
            right = min(left + 2 * size - 1, n - 1)
            if mid < right:
                merge(arr, left, mid, right, frames, metrics)
        size *= 2

    return frames

def generate_datasets():
    size = 50
    random_data = random.sample(range(1, 200), size)
    reverse_sorted_data = sorted(random_data, reverse=True)
    partially_sorted_data = sorted(random_data[: size // 2]) + random_data[size // 2 :]
    already_sorted_data = sorted(random_data)
    return {
        "Random": random_data,
        "Reverse Sorted": reverse_sorted_data,
        "Partially Sorted": partially_sorted_data,
        "Already Sorted": already_sorted_data,
    }

def visualize_tim_sort():
    datasets = generate_datasets()
    dataset_names = list(datasets.keys())
    frames_by_dataset = {name: tim_sort(datasets[name].copy()) for name in dataset_names}

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    bar_rects = []
    phase_texts = []
    overall_texts = []

    for ax, name in zip(axes, dataset_names):
        ax.set_title(f"{name} Dataset")
        rects = ax.bar(range(len(datasets[name])), datasets[name], align="center", color="Skyblue")
        phase_text = ax.text(0.02, 0.9, "", transform=ax.transAxes, fontsize=10, color="blue")
        overall_text = ax.text(0.02, 0.85, "", transform=ax.transAxes, fontsize=10, color="red")
        bar_rects.append(rects)
        phase_texts.append(phase_text)
        overall_texts.append(overall_text)

    def update(frame_indices):
        for i, name in enumerate(dataset_names):
            arr, idx1, idx2, phase, comparisons, swaps = frames_by_dataset[name][frame_indices[i]]
            for j, rect in enumerate(bar_rects[i]):
                rect.set_height(arr[j])
                rect.set_color("skyblue")
            if idx1 != -1:
                bar_rects[i][idx1].set_color("red")  # Comparison
            if idx2 != -1:
                bar_rects[i][idx2].set_color("green")  # Swap
            phase_texts[i].set_text(f"Phase: {phase}")
            overall_texts[i].set_text(f"Comparisons: {comparisons}, Swaps: {swaps}")

    def start_animation(event):
        def generate_frames():
            max_steps = max(len(frames_by_dataset[name]) for name in dataset_names)
            for step in range(max_steps):
                yield [min(step, len(frames_by_dataset[name]) - 1) for name in dataset_names]

        global ani
        ani = animation.FuncAnimation(
            fig, update, frames=generate_frames, repeat=False, interval=0.2
        )
        plt.draw()

    ax_play = plt.axes([0.7, 0.02, 0.1, 0.05])
    btn_play = Button(ax_play, "Play")
    btn_play.on_clicked(start_animation)

    plt.show()

visualize_tim_sort()







# import matplotlib.pyplot as plt
# import matplotlib.animation as animation
# from matplotlib.widgets import Button
# import random

# # TimSort parameters
# RUN = 32

# def insertion_sort(arr, left, right, frames, overall_metrics):
#     comparisons = 0
#     for i in range(left + 1, right + 1):
#         key = arr[i]
#         j = i - 1
#         while j >= left and arr[j] > key:
#             comparisons += 1
#             overall_metrics['comparisons'] += 1
#             arr[j + 1] = arr[j]
#             j -= 1
#             frames.append((list(arr), i, j + 1, "Insertion", comparisons, overall_metrics['comparisons']))
#         comparisons += 1  # Final comparison
#         overall_metrics['comparisons'] += 1
#         arr[j + 1] = key
#         frames.append((list(arr), i, j + 1, "Insertion", comparisons, overall_metrics['comparisons']))

# def merge(arr, left, mid, right, frames, overall_metrics):
#     comparisons = 0
#     n1 = mid - left + 1
#     n2 = right - mid
#     left_arr = arr[left:left + n1]
#     right_arr = arr[mid + 1:mid + 1 + n2]
#     i, j, k = 0, 0, left

#     while i < n1 and j < n2:
#         comparisons += 1
#         overall_metrics['comparisons'] += 1
#         if left_arr[i] <= right_arr[j]:
#             arr[k] = left_arr[i]
#             i += 1
#         else:
#             arr[k] = right_arr[j]
#             j += 1
#         k += 1
#         frames.append((list(arr), k - 1, -1, "Merge", comparisons, overall_metrics['comparisons']))

#     while i < n1:
#         arr[k] = left_arr[i]
#         i += 1
#         k += 1
#         frames.append((list(arr), k - 1, -1, "Merge", comparisons, overall_metrics['comparisons']))

#     while j < n2:
#         arr[k] = right_arr[j]
#         j += 1
#         k += 1
#         frames.append((list(arr), k - 1, -1, "Merge", comparisons, overall_metrics['comparisons']))

# def tim_sort(arr):
#     n = len(arr)
#     frames = [(list(arr), -1, -1, "Start", 0, 0)]
#     overall_metrics = {'comparisons': 0}

#     for i in range(0, n, RUN):
#         insertion_sort(arr, i, min(i + RUN - 1, n - 1), frames, overall_metrics)

#     size = RUN
#     while size < n:
#         for left in range(0, n, 2 * size):
#             mid = min(n - 1, left + size - 1)
#             right = min(n - 1, left + 2 * size - 1)
#             if mid < right:
#                 merge(arr, left, mid, right, frames, overall_metrics)
#         size *= 2

#     return frames

# def generate_datasets():
#     size = random.randint(50, 60)
#     random_data = random.sample(range(1, 200), size)
#     reverse_sorted_data = sorted(random_data, reverse=True)
#     partially_sorted_data = sorted(random_data[: size // 2]) + random_data[size // 2 :]
#     already_sorted_data = sorted(random_data)
#     return {
#         "Random": random_data,
#         "Reverse Sorted": reverse_sorted_data,
#         "Partially Sorted": partially_sorted_data,
#         "Already Sorted": already_sorted_data,
#     }

# def visualize_tim_sort():
#     datasets = generate_datasets()
#     dataset_names = ["Random", "Reverse Sorted", "Partially Sorted", "Already Sorted"]
#     dataset_copies = {name: datasets[name].copy() for name in dataset_names}
#     all_frames = {name: tim_sort(dataset_copies[name]) for name in dataset_names}

#     fig, axes = plt.subplots(2, 2, figsize=(14, 10))
#     axes = axes.flatten()
#     bar_rects = []
#     texts = []
#     overall_texts = []
#     global ani  # To persist animation

#     for ax, name in zip(axes, dataset_names):
#         ax.set_title(f"{name} Dataset")
#         rects = ax.bar(range(len(datasets[name])), datasets[name], align="center", color="Skyblue")
#         text = ax.text(0.02, 0.9, "", transform=ax.transAxes, fontsize=10, color="black")
#         overall_text = ax.text(0.02, 0.85, "", transform=ax.transAxes, fontsize=10, color="blue")
#         bar_rects.append(rects)
#         texts.append(text)
#         overall_texts.append(overall_text)

#     def update_all(frame_indices):
#         for i, name in enumerate(dataset_names):
#             step = all_frames[name][frame_indices[i]]
#             frame, active_index, compare_index, phase, comparisons, overall_comparisons = step
#             for rect, height in zip(bar_rects[i], frame):
#                 rect.set_height(height)
#                 rect.set_color("skyblue")
#             if active_index != -1:
#                 bar_rects[i][active_index].set_color("red")
#             if compare_index != -1:
#                 bar_rects[i][compare_index].set_color("green")
#             texts[i].set_text(f"Phase: {phase}, Comparisons: {comparisons}")
#             overall_texts[i].set_text(f"Overall Comparisons: {overall_comparisons}")

#     def start_animation(event):
#         def gen_frames():
#             max_steps = max(len(all_frames[name]) for name in dataset_names)
#             for step in range(max_steps):
#                 yield [min(step, len(all_frames[name]) - 1) for name in dataset_names]
#         global ani
#         ani = animation.FuncAnimation(
#             fig, update_all, frames=gen_frames, repeat=False, interval=50, blit=False, save_count=500
#         )
#         plt.draw()

#     def reset(event):
#         nonlocal all_frames
#         for i, name in enumerate(dataset_names):
#             all_frames[name] = tim_sort(dataset_copies[name].copy())
#             for rect, height in zip(bar_rects[i], datasets[name]):
#                 rect.set_height(height)
#                 rect.set_color("skyblue")
#             texts[i].set_text("Phase: Start")
#             overall_texts[i].set_text("Overall Comparisons: 0")
#         plt.draw()

#     ax_play = plt.axes([0.7, 0.02, 0.1, 0.05])
#     btn_play = Button(ax_play, "Play")
#     btn_play.on_clicked(start_animation)

#     ax_reset = plt.axes([0.81, 0.02, 0.1, 0.05])
#     btn_reset = Button(ax_reset, "Reset")
#     btn_reset.on_clicked(reset)

#     plt.show()

# visualize_tim_sort()





