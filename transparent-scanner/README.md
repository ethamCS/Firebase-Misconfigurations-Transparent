# Firebase Misconfigurations Scanner

This is designed to scan APK files for Firebase project names and check their configurations for potential security misconfigurations. It also checks for Personally Identifiable Information (PII) in the responses (keys) from the Firebase projects.


## Usage

1. Run the script:

    ```bash
    python3 scanner.py
    ```

   Make sure to set the `parent_directory` variable in the script to the directory containing your APK files.

## Script Explanation

The script performs the following tasks:

1. **Find Firebase Project Names:**
   - Uses regular expressions to find Firebase project names in APK files.

2. **Scan Firebase Projects:**
   - Checks the configuration of each Firebase project for security issues.
   - Identifies secure, insecure, and non-existing Firebase instances.

3. **PII Detection:**
   - Parses the responses keys from Firebase projects to detect Personally Identifiable Information (PII).
   - Outputs PII found in the responses.

### Functions:

- `find_firebase_project_names_parallel(parent, file)`: Finds Firebase project names in APK files in parallel using multithreading.

- `scan_firebase_projects(firebase_project_list)`: Scans Firebase projects for security misconfigurations.

- `scan_firebase_projects_test()`: A test function for scanning a single Firebase project.

### How to Run

To run the script, execute the `main()` function:

```bash
python firebase_misconfigurations_scanner.py
