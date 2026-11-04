# workload.py -- simulates the memory access pattern of a model training loop
#
# A real large language model is not used. Two large matrices stand in for the
# model weights and gradients, so the test exercises the OS memory subsystem
# rather than the model itself.
#
# Usage:  python workload.py [MATRIX_SIZE]
# Choose MATRIX_SIZE so the working set is about 70-75%, 100-110% or 150-160%
# of the VM's RAM for scenarios A, B and C (see README.md).
import sys
import time

import numpy as np

# Adjust this to control how much RAM the "model" consumes
MATRIX_SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 8000  # 8000 = ~512 MB per matrix at float64
print(f"Allocating working set (~{MATRIX_SIZE**2 * 8 / 1e6:.0f} MB per matrix)...")

# Simulates model weights + gradients (two large matrices)
weights = np.random.rand(MATRIX_SIZE, MATRIX_SIZE)
gradients = np.random.rand(MATRIX_SIZE, MATRIX_SIZE)

print("Starting simulated training loop...")
iteration_times = []

for i in range(20):  # 20 "epochs"
    start = time.perf_counter()

    # Simulate forward pass (matrix multiply = memory-intensive)
    activations = np.dot(weights, gradients)

    # Simulate backward pass (element-wise update)
    weights -= 0.01 * activations

    elapsed = time.perf_counter() - start
    iteration_times.append(elapsed)
    print(f"  Iteration {i+1:02d}: {elapsed:.4f}s")

avg = sum(iteration_times) / len(iteration_times)
print(f"\nAverage iteration time: {avg:.4f}s")
print(f"Min: {min(iteration_times):.4f}s | Max: {max(iteration_times):.4f}s")
