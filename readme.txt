# nslookup

## Description
`nslookup` is a command-line tool used for querying the Domain Name System (DNS) to obtain domain name or IP address mapping information. It is useful for troubleshooting DNS-related issues.

## Installation
To install `nslookup`, follow these steps:

2. **Linux:**
    - `nslookup` is part of the `dnsutils` package. Install it using the following command:
      ```
      sudo apt-get install dnsutils
      ```


## Running the Server
To run the server that provides a web interface for `nslookup`, `dig`, and `ping` commands, follow these steps:

1. **Install Dependencies:**
    Ensure you have Python and Flask installed. You can install Flask using pip:
    ```
    pip install Flask
    ```

2. **Start the Server:**
    Navigate to the directory containing your server script and run:
    ```
    python app.py
    ```

3. **Access the Web Interface:**
    Open your web browser and go to `http://localhost:5000`. You will be able to perform `nslookup`, `dig`, and `ping` commands through the web interface.