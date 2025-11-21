import requests
from datetime import datetime

def check_urls(input_file='web-urls.txt'):
    """
    Reads URLs from a file, checks their connection status, 
    and saves the results to separate files.
    """
    # Get the current timestamp to name the output files
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    ok_file_path = f"{timestamp}-ok.txt"
    failed_file_path = f"{timestamp}-failed.txt"

    # Headers to mimic a standard web browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        with open(input_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found. Please create it.")
        return

    print(f"Starting to check {len(urls)} URLs")

    # Open the output files to write the results
    with open(ok_file_path, 'w') as ok_file, open(failed_file_path, 'w') as failed_file:
        for url in urls:
            try:
                # Send the request with a 10-second timeout
                response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
                
                # Check the status code. 200 is OK. 3xx codes (like 301, 302) are redirects,
                # and the requests library follows them automatically, so the final 
                # response.status_code will be 200 on success.
                if response.status_code == 200:
                    status = "OK"
                    print(f"{url} -> {status}")
                    ok_file.write(url + '\n')
                else:
                    # Other cases (4xx, 5xx) are considered failures
                    status = f"FAILED (Status: {response.status_code})"
                    print(f"{url} -> {status}")
                    failed_file.write(f"{url} (Status: {response.status_code})\n")

            except requests.exceptions.Timeout:
                status = "FAILED (Timeout)"
                print(f"{url} -> {status}")
                failed_file.write(f"{url} (Timeout)\n")
            except requests.exceptions.RequestException as e:
                # Catch other exceptions like connection errors, DNS errors, etc.
                status = f"FAILED (Error: {type(e).__name__})"
                print(f"{url} -> {status}")
                failed_file.write(f"{url} (Error)\n")

    print("\nProcessing complete!")

if __name__ == "__main__":
    check_urls()