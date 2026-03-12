import time

def benchmark():
    start = time.time()
    time.sleep(0.1)
    print(f"Benchmark completed in {time.time() - start:.2f}s")

if __name__ == "__main__":
    benchmark()
