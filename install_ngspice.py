import platform, subprocess, os, urllib.request
import py7zr   # pip install py7zr

def setup():
    system = platform.system()
    
    if system == 'Linux':
        print('Linux detected — installing ngspice via apt...')
        subprocess.run(['sudo', 'apt', 'install', '-y', 'ngspice'], check=True)
        print('Done!')

    elif system == 'Windows':
        print('Windows detected — downloading ngspice...')
        
        url      = 'https://sourceforge.net/projects/ngspice/files/ng-spice-rework/46/ngspice-46_64.7z'
        sz_path  = 'ngspice_win.7z'
        out_dir  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin')

        print('Downloading...')
        urllib.request.urlretrieve(url, sz_path)
        print('Extracting...')
        
        with py7zr.SevenZipFile(sz_path, mode='r') as z:
            z.extractall(path=out_dir)   # extracts Spice64/ folder inside bin/
        
        os.remove(sz_path)
        print(f'Extracted to {out_dir}/Spice64')
        print('Setup complete!')
    
    else:
        print(f'Unknown system: {system}')

if __name__ == '__main__':
    setup()