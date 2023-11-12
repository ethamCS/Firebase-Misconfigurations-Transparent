# Firebase Misconfiguration Transparent

https://github.com/shivsahni/FireBaseScanner/blob/master/README.md extended to have updated multithreaded decompilation processes using jadx. Firebase updates to use multithreading when file searching for project names. Ported to modern python3.

PII searching through pattern-matching json object keys

Upcoming: options to save or delete decompiled files, csv saving/appending options.

## *jadx Decompilation Script*

This Python script is designed for batch decompilation of APK files using JADX.

## Prerequisites

Before using this script, make sure you have the following installed:

- [JADX](https://github.com/skylot/jadx): jadx is a command-line tool that can be used for decompiling Android applications.

## Usage

1. Run the script:

    ```bash
   python3 jadx_invoker.py --apks=/path/to/apks
    ```

   Replace `/path/to/apks` with the directory containing APK files.

## Script Explanation

The script utilizes the `jadx` tool to decompile APK files in a specified directory.

### Class: jadx

- `__init__(self, apks)`: Initializes the jadx object with the directory containing APK files.

- `decompile(self)`: Initiates the decompilation process for each APK file in the specified directory.

# jadx Multithreaded Decompilation Script

This Python script is designed for batch decompilation of APK files using JADX with multithreading.

## Usage

1. Run the script:

    ```bash
    python3 multi_threaded --apks /path/to/apks
    ```

   Replace `/path/to/apks` with the directory containing  APK files.

## Script Explanation

Parallelized using multithreading for improved performance.

### Class: jadx

- `__init__(self, apks)`: Initializes the jadx object with the directory containing APK files.

- `decompile_single(self, file)`: Initiates the decompilation process for a single APK file.

- `decompile(self)`: Initiates the multithreaded decompilation process for all APK files in the specified directory.


