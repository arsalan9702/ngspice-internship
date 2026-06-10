import numpy as np

with open('test_circuits/test_bjt_sweep.raw', 'rb') as f:
    raw = f.read()

header_end = raw.find(b'Binary:\n') + len(b'Binary:\n')
binary_data = raw[header_end:]

floats = np.frombuffer(binary_data, dtype=np.float64)
print(f"Total floats: {len(floats)}")
print(floats)