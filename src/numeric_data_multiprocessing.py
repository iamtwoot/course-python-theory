import random
import time
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, cpu_count
from multiprocessing import Process, Queue
import json
import matplotlib.pyplot as plt


def generate_data(n: int) -> list[int]:
    return [random.randint(1, 1000) for _ in range(n)]


def process_number(number):
    factorial = 1
    for i in range(1, number + 1):
        factorial *= i
    return factorial


# 1. Sequential
def run_sequential(numbers: list[int]) -> tuple[list[int], float]:
    start = time.perf_counter()
    results = [process_number(n) for n in numbers]
    elapsed = time.perf_counter() - start
    return results, elapsed


# 2. Using threading pool with concurrent.futures
def run_thread_pool(numbers: list[int], max_workers: int = 5) -> tuple[list[int], float]:
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_number, numbers))
    elapsed = time.perf_counter() - start
    return results, elapsed


# 3. Using process pool with multiprocessing.Pool
def run_process_pool(numbers: list[int]) -> tuple[list[int], float]:
    start = time.perf_counter()
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(process_number, numbers)
    elapsed = time.perf_counter() - start
    return results, elapsed


# 4. Using multiprocessing.Process and  multiprocessing.Queue
def get_chunks(numbers: list, n_chunks: int) -> list[list[int]]:
    step = len(numbers) // n_chunks
    chunks = []
    position = 0
    for i in range(n_chunks):
        if i == n_chunks - 1:
            chunk = numbers[position:]
        else:
            chunk = numbers[position:position + step]
        chunks.append(chunk)
        position += step
    return chunks


def worker(index: int, numbers: list[int], q: Queue) -> None:
    results = [process_number(n) for n in numbers]
    q.put((index, results))


def run_process_queue(numbers: list[int]) -> tuple[list[int], float]:
    start = time.perf_counter()

    chunks = get_chunks(numbers, cpu_count())
    q = Queue()
    processes = []

    for index, chunk in enumerate(chunks):
        p = Process(target=worker, args=(index, chunk, q))
        processes.append(p)
        p.start()

    results_by_index = {}
    for _ in processes:
        index, chunk_results = q.get()
        results_by_index[index] = chunk_results

    for p in processes:
        p.join()

    results = []
    for index in sorted(results_by_index):
        results.extend(results_by_index[index])

    elapsed = time.perf_counter() - start
    return results, elapsed


def save_results(numbers: list[int], results: list[int], file_path: str) -> None:
    with open(file_path, "w") as f:
        for number, result in zip(numbers, results):
            f.write(json.dumps({"number": number, "factorial": result}) + "\n")


def plot_speedup(results_table: list[tuple[str, float]], seq_time: float) -> None:
    names = [name for name, _ in results_table]
    speedups = [seq_time / elapsed for _, elapsed in results_table]

    plt.bar(names, speedups)
    plt.axhline(y=1.0, color="gray", linestyle="--")  # линия "уровень Sequential"
    plt.ylabel("Ускорение (x к Sequential)")
    plt.title("Ускорение параллельной обработки")
    plt.savefig("speedup.png")


if __name__ == "__main__":
    numbers = generate_data(500000)

    results_table = []

    seq_results, seq_time = run_sequential(numbers)
    results_table.append(("Sequential", seq_time))

    thread_results, thread_time = run_thread_pool(numbers)
    results_table.append(("Thread Pool", thread_time))

    process_results, process_time = run_process_pool(numbers)
    results_table.append(("Process Pool", process_time))

    queue_results, queue_time = run_process_queue(numbers)
    results_table.append(("Process+Queue", queue_time))

    assert seq_results == thread_results == process_results == queue_results

    # save_results(numbers, seq_results, "results.jsonl")
    plot_speedup(results_table, seq_time)

    for name, elapsed in results_table:
        speedup = seq_time / elapsed
        print(f"{name:15s}: {elapsed:8.4f}s    (x{speedup:.2f} к Sequential)")
