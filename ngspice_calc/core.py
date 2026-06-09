import subprocess
import numpy as np
import os

import re

def replace_strings_1(src, dst, replacements):
    mapping = dict(replacements)

    with open(src) as f:
        content = f.read()

    content = re.sub(
        r"\$[A-Za-z_][A-Za-z0-9_]*",
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

def _parse_header(header_text:str):
    variables = []
    num_vars = 0
    num_points = 0
    flags = 'real'
    plotname = ''
    in_vars = False

    for line in header_text.splitlines():
        line = line.strip()

        if line.startswith('Plotname:'):
            plotname = line.split(':', 1)[1].strip()
        elif line.startswith('Flags:'):
            flags = line.split(':', 1)[1].strip().lower()
        elif line.startswith('No. Variables:'):
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

    return variables, num_vars, num_points, flags, plotname

def _parse_op(binary_data, variables, num_vars, num_points):
    """
    DC operating point - single point, real values.
    """

    floats = np.frombuffer(binary_data, np.float64)
    data = {}

    for i,var in enumerate(variables):
        data[var] = np.array([floats[i]])

    return data

def _parse_tran(binary_data, variables, num_vars, num_points):
    """
    Transient -- multiple points, real values.
    Layout: [var0, var1, ..., varN] per point, float64.
    """
    floats = np.frombuffer(binary_data, dtype=np.float64)
    matrix = floats[:num_vars * num_points].reshape((num_points, num_vars))
    data = {}
    for i, var in enumerate(variables):
        data[var] = matrix[:, i]

    return data

def _parse_ac(binary_data, variables, num_vars, num_points):
    """
    AC - multiple points, complex values
    layout: [re0, im0, re1, im1, ..., ren, imn] per point, float
    frequence: only need real part
    """

    floats = np.frombuffer(binary_data, dtype=np.float64)
    matrix = floats[:2 * num_vars * num_points].reshape((num_points, 2 * num_vars))
    data = {}

    for i,var in enumerate(variables):
        real = matrix[:, 2*i]
        imag = matrix[:, 2 * i + 1]

        if var=="frequency":
            data[var] = real
        else:
            data[var] = real + 1j * imag
    
    return data


def _parse_all_plots(raw_path: str) -> dict:
    """
    Detects analysis type from header and dispatches to the right parser
    Returns list of dicts, one per plot
    each dict: {'plotname': str, 'data': {var: np.array}}
    Each plot is seperated by "Plotname:" in .raw file
    """
    with open(raw_path, 'rb') as f:
        raw = f.read()

    plot_positions = []
    search_start=0

    while True:
        pos = raw.find(b"Plotname:", search_start)
        if pos == -1:
            break
        plot_positions.append(pos)
        search_start = pos+1

    plots = []
    for idx,start in enumerate(plot_positions):
        end = plot_positions[idx + 1] if idx+1<len(plot_positions) else len(raw)
        chunk = raw[start:end]

        parts = chunk.split(b'Binary:\n')
        if len(parts)!=2:
            continue

        header_text = parts[0].decode('latin-1')
        binary_data = parts[1]

        variables, num_vars, num_points, flags, plotname = _parse_header(header_text)

        plotname_lower = plotname.lower()
        if 'operating' in plotname_lower:
            data = _parse_op(binary_data, variables, num_vars, num_points)
        elif 'transient' in plotname_lower:
            data = _parse_tran(binary_data, variables, num_vars, num_points)
        elif 'ac' in plotname_lower or flags == 'complex':
            data = _parse_ac(binary_data, variables, num_vars, num_points)
        else:
            data = _parse_tran(binary_data, variables, num_vars, num_points)

        plots.append({'plotname': plotname, 'data': data})

    return plots


    
class slv:
    def __init__(self, cir_path:str):
        raw_path = cir_path.replace('.in', '.raw').replace('.cir', '.raw')
        
        if not os.path.exists(raw_path):
            raise FileNotFoundError(
                f'Raw file not found: {raw_path}. Run ngspice first'
            )
        
        self._plots = _parse_all_plots(raw_path)

    def get_array(self, name:str, plot:int=0) -> np.ndarray:
        """
        get variable by name from specific plot (default 0).
        """

        data = self._plots[plot]['data']
        name = name.lower()

        if name in data:
            return data[name]
        matches = [k for k in data if name in k]

        if len(matches)==1:
            return data[matches[0]]
        if len(matches)>1:
            raise KeyError(f'Ambiguous: "{name}", matches {matches}')
        raise KeyError(
            f'"{name}" not found in plot. '
            f'Available: {list(data.keys())}'
        )
    

    def variables(self, plot:int=0):
        return list(self._plots[plot]['data'].keys())
    
    def num_plots(self):
        return len(self._plots)
    
    def plotname(self, plot:int=0):
        return self._plots[plot]['plotname']
    
    def analysis_type(self, plot: int = 0):
        first = list(self._plots[plot]['data'].values())[0]
        if np.iscomplexobj(first):
            return 'ac'
        elif len(first) == 1:
            return 'op'
        else:
            return 'tran'
    

        