import os
import re
import hashlib
import concurrent.futures
import requests

pii_set = set([
    'full_name'
    'id'
    'ssn'
    'email',
    'full_name',
    'first_name',
    'last_name',
    'phone_number',
    'phone'
    'address',
    'username',
    'password',
    'date of birth',
    'gender',
    'nationality',
])


def parse(response, attributes):
    for key, value in response.items():
        # print(key)
        attributes.append(key)
        if type(value) == type(dict()):
            parse(value, attributes)
    return attributes


def detect_pii(attributes):
    matches = pii_set.intersection(attributes)
    print(matches)
    for match in matches:
        print(f"Match found: PII '{match}'")


def find_firebase_project_names_parallel(parent, file):

    print("Testing " + file + "...\n")
    firebase_project_list = []
    regex = 'https*://(.+?)\.firebaseio.com'

    src = os.path.join(parent, file)
    print(src)

    def process_file(fullpath):
        temp_list = []
        with open(fullpath, 'r', errors='ignore') as f:
            for line in f:
                temp = re.findall(regex, line)
                if len(temp) != 0:
                    temp_list.extend(temp)
                    print("Firebase Project Found")
        return temp_list

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_path = {executor.submit(process_file, os.path.join(dir_path, file_name)): os.path.join(dir_path, file_name)
                          for dir_path, _, file_names in os.walk(src)
                          for file_name in file_names}

        for future in concurrent.futures.as_completed(future_to_path):
            fullpath = future_to_path[future]
            try:
                temp = future.result()
                firebase_project_list.extend(temp)
            except Exception as exc:
                print("An error occurred while processing file:", exc)

    if not firebase_project_list:
        print("No Firebase Project Found")

    return firebase_project_list


def scan_firebase_projects(firebase_project_list):
    attributes = []
    print("Scanning Firebase Projects")
    for project_name in firebase_project_list:
        url = 'https://' + project_name + '.firebaseio.com/.json'
        print(url)
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            print("An error occurred while making the request:", err)
            continue

        if response.status_code == 401:
            print("Secure Firebase Instance Found: " + project_name, "SECURE")
        elif response.status_code == 404:
            print("Project does not exist: " + project_name, "OUTPUT_WS")
        else:
            keys = response.json().keys()
            out = parse(response.json(), attributes)
            out = set(out)
            if 'email' in out:
                print("TRUE")
            detect_pii(out)
            print("Misconfigured Firebase Instance Found: " +
                  project_name, "INSECURE_WS")


def main():
    parent_directory = '/Users/ethanmyers/Firebase-Misconfigurations-Transparent/decompliler/jadx_results/'
    apk_file = 'snorelab'

    firebase_projects = find_firebase_project_names_parallel(
        parent_directory, apk_file)
    firebase_projects.append('dailybreath-b4b40')
    print(firebase_projects)
    scan_firebase_projects(firebase_projects)


if __name__ == "__main__":
    main()
