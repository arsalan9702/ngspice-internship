import subprocess
import numpy as np
import os

import re

def replace_strings_1(src, dst, replacements):
    mapping = dict(replacements)

    with open(src) as f:
        content = f.read()

    content = re.sub(
        r"\$[A-Z_]+",
        lambda m: mapping.get(m.group(0), m.group(0)),
        content
    )
    content = content.replace('\r\n', '\n')
    with open(dst, "w") as f:
        f.write(content)

def run_ngspice(cir_path:str):  
    raw_path = cir_path.replace('.in', '.raw').replace('.cir', '.raw')
    result = subprocess.run(
        ['ngspice', '-b', '-r', raw_path, cir_path],
        capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode!=0:
        print(result.stderr)
        raise RuntimeError(f'ngspice failed on {cir_path}')
    return raw_path

def _parse_raw_binary(raw_path: str) -> dict:
    with open(raw_path, 'rb') as f:
        raw = f.read()

    split = raw.split(b'Binary:\n')
    header_text = split[0].decode('latin-1')
    binary_data = split[1]

    variables = []
    num_vars = 0
    num_points = 0
    in_vars = False

    for line in header_text.splitlines():
        line = line.strip()
        if line.startswith('No. Variables:'):
            num_vars = int(line.split(':')[1].strip())
        elif line.startswith('No. Points:'):
            num_points = int(line.split(':')[1].strip())
        elif line.startswith('Variables:'):
            in_vars = True
            continue
        elif in_vars and line:
            parts = line.split()
            if parts and parts[0].isdigit():
                variables.append(parts[1].lower())
     
    floats = np.frombuffer(binary_data, dtype=np.float64)
    matrix = floats[:num_vars * num_points].reshape((num_points, num_vars))

    data = {}
    for i, var in enumerate(variables):
        data[var] = matrix[:, i]

    return data

class slv:
    def __init__(self, cir_path:str):
        raw_path = cir_path.replace('.in', '.raw').replace('.cir', '.raw')
        if not os.path.exists(raw_path):
            raise FileNotFoundError(
                f'Raw file not found: {raw_path}. Run ngspice first'
            )
        self._data = _parse_raw_binary(raw_path)

    def get_array(self, name:str) -> np.ndarray:
        name = name.lower()
        if name in self._data:
            return self._data[name]
        
        matches = [k for k in self._data if name in k]
        if len(matches)==1:
            return self._data[matches[0]]
        if len(matches)>1:
            raise KeyError(f'Ambiguous: "{name}" matches {matches}')
        raise KeyError(f'"{name}" not found. Available: {list(self._data.keys())}')
    

    def variables(self):
        return list(self._data.keys())
        