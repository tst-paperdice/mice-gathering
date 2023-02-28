from ast import AsyncFunctionDef
import requests
import csv
import pdb
import datetime

websites = [host for _, host in csv.reader(open("docker/content/top-10k.csv", "r"))]

filtered_urls = []
failed = []

now = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S") + " GMT"

headers = {
    #'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    "User-Agent": "Mozilla 5.0",
    "Date": now,
    "Time": now[-12:-4],
}

NUM_URLS = 1000
websites = websites[:NUM_URLS]

for i, url in enumerate(websites):
    full_url = f"http://{url}"
    print(f"testing {full_url} {i}/{len(websites)}")
    try:
        r = requests.head(full_url, headers=headers, timeout=10)
        if r.status_code == 200:
            filtered_urls.append(full_url)
        elif r.status_code in [301, 302, 308, 418]:
            print(f"    Failed with {r.status_code}")
            if "Location" in r.headers:
                print(
                    f"    Trying Location from response headers = {r.headers['Location']}"
                )
                full_url = r.headers["Location"]
            else:
                print("    Trying HTTPS...")
                full_url = f"https://{url}"

            r = requests.get(full_url, headers=headers, timeout=10)
            if r.status_code == 200:
                filtered_urls.append(full_url)
            else:
                print(f"    {full_url} failed with {r.status_code}")
                failed.append((full_url, f"-{r.status_code}"))
            # failed.append((full_url, f'-{r.status_code}'))
        else:
            print(f"Invalid response. status: {r.status_code}")
            failed.append((full_url, f"-{r.status_code}"))

    except Exception as e:
        print(f"failed with exception: {e}")
        failed.append((full_url, e))


with open(f"docker/content/{NUM_URLS}_filtered.csv", "w") as outfile:
    for i, el in enumerate(filtered_urls[:-1]):
        outfile.write(f"{i+1},{el}\n")
    outfile.write(f"{i+2},{filtered_urls[-1]}")  # No trailing newline

with open(f"docker/content/{NUM_URLS}_failures.txt", "w") as outfile:
    for url, err in failed:
        outfile.write(f"{url}-{err}\n")

# https = [url for url in filtered_urls if url[:5] == 'https']
# http = [url for url in filtered_urls if url[:5] == 'http:']

# # breakpoint()

# print(https)
# print(http)
# print(failed)
