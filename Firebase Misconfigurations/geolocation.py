import json
import pprint
import re
import socket
import ssl
import subprocess
import sys
import dns.resolver

def get_location_by_url(hostname_list):
    
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ['8.8.8.8']

    for hostname in hostname_list:
    
        hostname_url = re.sub(r'^https://|(?<!\.)\/\.json$', '', hostname)

        try:
            answers = dns.resolver.resolve(hostname_url, 'A')
            ip = answers[0].to_text()
        except dns.resolver.NoAnswer:
            print(f"No DNS response for {hostname_url}")
            continue
    
        try:
            result = subprocess.run(
                ["powershell", "Invoke-RestMethod ipinfo.io/" + ip],
                capture_output=True, text=True  
            )

        except:
            print("Error Invoke-RestMethod failed")
            continue

        print(result.stdout)

        response_json = json.loads(result.stdout)

        country_name = response_json.get('country', 'N/A')
        print(f"Country for {hostname_url}: {country_name}")

        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(socket.socket(), server_hostname=hostname_url)
        s.connect((hostname_url, 443))
        cert = s.getpeercert()

        # pprint.pprint(cert)

        # Write geolocation info on a file
        # with open("loc_output.txt", "a") as f:
        #     f.write("URL      :  " + hostname_url)
        #     f.write(result.stdout)

        # Write certificate info on a text file
        # with open("certificate.txt", "a") as f:
        #     json.dump(cert, f, indent=4, sort_keys=True, separators=(" ", ": "))
        #     f.write("\n\n\n")

if __name__ == "__main__":
    url_list = ['https://com-loseit.firebaseio.com/.json', 'https://vernal-parser-760.firebaseio.com/.json', 'https://g6-store-us.firebaseio.com/.json', 'https://trident-d7d16.firebaseio.com/.json', 'https://x-component-production.firebaseio.com/.json', 'https://youper-9931b.firebaseio.com/.json']
    get_location_by_url(url_list)