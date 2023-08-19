from os import listdir
import subprocess
import argparse
from concurrent.futures import ThreadPoolExecutor

class jadx: 
    
    def __init__(self, apks):
        self.system_path = True
        self.apk_dir = apks
 
    def decompile_single(self, file):
        print(f"Decompiling {file} ... ")
        result = subprocess.run(
            ["jadx", self.apk_dir + '/' + file, "-d", "./jadx_results/" + file.replace('.apk', '')]
        )
        print(f"Finished decompiling {file}")

    def decompile(self):
        print(self.apk_dir)
        files = [f for f in listdir(self.apk_dir)]
        print("Starting decompilation process")
        
        with ThreadPoolExecutor() as executor:
            executor.map(self.decompile_single, files)
        
        print(f"✅ Finished Decompiling {len(files)} apps")

def main():
    parser = argparse.ArgumentParser(description="Batch Decompile Directory of APK's")
    # parser.add_argument('--jadxPath', help='path to jadx')
    parser.add_argument('--apks', help='path to apks')

    args = parser.parse_args()
    apk_dir = args.apks
    jadx_obj = jadx(apk_dir)
    jadx_obj.decompile()

if __name__ == "__main__":
    main()
