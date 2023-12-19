import csv
import os
import re
import hashlib
import concurrent.futures
import requests
import geolocation

#TODO: finalize regex/pattern matching for generalizability

output="firebaseProject.csv" #Name of the output csv file
outputNotFound="firebaseProjectNotFound.csv" #List of the not found firebase URLs

url_list = []
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
    regex_matches = pii_set.intersection(attributes)
    combined_matches = matches.union(regex_matches)
    for match in combined_matches:
        print(f"Match found: PII '{match}'")
    return combined_matches


def find_firebase_project_names_parallel(parent, file):

    print(f'\nTesting {file} ...\n')
    firebase_project_list = []
    regex = 'https*://(.+?)\.firebaseio.com'

    src = os.path.join(parent, file)

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


def scan_firebase_projects(firebase_project_list, apk):
    attributes = []
    print("Scanning Firebase Projects")
    for project_name in firebase_project_list:
        url = 'https://' + project_name + '.firebaseio.com/.json'
        print(url)

        regex_pattern = r'^[a-zA-Z0-9-]+$'
        if re.match(regex_pattern, project_name):
            url_list.append(url)
            # with open("url_list.txt", "a") as matching_file:
            #     matching_file.write(url + '\n')
        
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            # print("An error occurred while making the request:", err)
            # continue

            if response.status_code == 401:
                print("Secure Firebase Instance Found: " + project_name, "SECURE")
                with open(output, "a", newline="") as csvfile:
                    data = [apk, url, "SECURE"]
                    writer = csv.writer(csvfile, delimiter=",")
                    writer.writerow(data)
            elif response.status_code == 423:
                print("Project unidentified: " + project_name, "NA")
                with open(outputNotFound, "a", newline="") as csvfile:
                    data = [apk, url, "UNIDENTIFIED"]
                    writer = csv.writer(csvfile, delimiter=",")
                    writer.writerow(data)
            elif response.status_code == 404:
                print("Project does not exist: " + project_name, "NA")
                with open(outputNotFound, "a", newline="") as csvfile:
                    data = [apk, "N/A", "NOT EXISTS"]
                    writer = csv.writer(csvfile, delimiter=",")
                    writer.writerow(data)
            else:
                keys = response.json().keys()
                out = parse(response.json(), attributes)
                out = set(out)
                pii = detect_pii(out)
                print("Misconfigured Firebase Instance Found: " +
                    project_name, "INSECURE")
                with open(output, "a", newline="") as csvfile:
                    data = [apk, url, "INSECURE"]
                    writer = csv.writer(csvfile, delimiter=",")
                    writer.writerow(data)
                return pii


def main():
    # parent_directory = './decompiler/jadx_results/'
    # apk_files = [f for f in os.listdir('./decompiler/jadx_results/')]
    parent_directory = 'C:\\Users\\ansh1\\OneDrive\\Desktop\\GDPR\\Firebase-Misconfigurations-Transparent\\jadx_results\\'
    apk_files = [f for f in os.listdir('C:\\Users\\ansh1\\OneDrive\\Desktop\\GDPR\\Firebase-Misconfigurations-Transparent\\jadx_results\\')]

    # print(parent_directory, apk_files)

    for apk in apk_files:
        firebase_projects = find_firebase_project_names_parallel(
            parent_directory, apk)
        if len(firebase_projects) < 0:
            continue
        pii_found = scan_firebase_projects(firebase_projects, apk)
        print(pii_found)
    # print(url_list)
    geolocation.get_location_by_url(url_list)

if __name__ == "__main__":
    main()
