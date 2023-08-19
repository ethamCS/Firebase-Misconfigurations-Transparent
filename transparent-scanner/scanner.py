import os
import re
import hashlib
import concurrent.futures
import requests

#TODO: finalize regex/pattern matching for generalizability

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

pii_patterns = {
    'username_column': r'(?i)\b(username|user[_ ]?name|user|uname)\b',
    'first_name_column': r'(?i)\b(first[_ ]?name|given[_ ]?name|forename|fname)\b',
    'last_name_column': r'(?i)\b(last[_ ]?name|surname|lname)\b',
    'dob_column': r'(?i)\b(date[_ ]?of[_ ]?birth|dob|birthdate)\b',
    'email_column': r'(?i)\b(email|e[_ ]?mail)\b',
    'phone_column': r'(?i)\b(phone[_ ]?number|phone|cell[_ ]?phone|mobile[_ ]?number)\b',
    'address_column': r'(?i)\b(address|addr)\b',
    'ssn_column': r'(?i)\b(ssn|social[_ ]?security[_ ]?number)\b',
    'id_column': r'(?i)\b(id|identifier)\b',
    'passport_number_column': r'(?i)\b(passport[_ ]?number)\b',
    'bank_account_column': r'(?i)\b(bank[_ ]?account[_ ]?number)\b',
    'credit_card_column': r'(?i)\b(credit[_ ]?card[_ ]?number)\b',
    'driver_license_column': r'(?i)\b(driver[_ ]?license)\b',
    'ip_address_column': r'(?i)\b(ip[_ ]?address)\b',
    'employee_id_column': r'(?i)\b(employee[_ ]?id)\b',
    'medical_record_column': r'(?i)\b(medical[_ ]?record)\b',
    'vehicle_id_column': r'(?i)\b(vehicle[_ ]?id)\b',
}
pii_set = set(pii_patterns.keys())

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

    print(f'Testing {file} ...\n')
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
            print("Project does not exist: " + project_name, "NA")
        else:
            keys = response.json().keys()
            out = parse(response.json(), attributes)
            out = set(out)
            pii = detect_pii(out)
            print("Misconfigured Firebase Instance Found: " +
                  project_name, "INSECURE")
            return pii


def main():
    parent_directory = './decompiler/jadx_results/'
    apk_files = [f for f in os.listdir('./decompiler/jadx_results/')]

    for apk in apk_files:
        firebase_projects = find_firebase_project_names_parallel(
            parent_directory, apk)
        if len(firebase_projects) < 0:
            continue
        pii_found = scan_firebase_projects(firebase_projects)
        print(pii_found)


if __name__ == "__main__":
    main()
