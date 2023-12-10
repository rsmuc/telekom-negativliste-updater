# Telekom Negativliste Updater 
 
## Background 
 
My mother has been receiving a significant number of spam calls lately, and the built-in features of the Speedport router are not effective in blocking these calls. To address this issue, I have developed a Python script,  telekom_negativliste_updater.py , that scrapes a website listing the most active spam numbers in Germany for the last 24 hours. The script then updates the Telekom Negativliste, which is an online portal provided by Telekom, to block these spam numbers. Additionally, I have configured the Telefoniecenter to disallow unknown numbers from calling my mother altogether. 

## Status

Just a proof of concept. Currently it seems to work and to block most SPAM calls.
 
## Prerequisites 
 
- Python 3.9 or higher 
- Firefox web browser 
- Geckodriver for Firefox 
 
## Installation 
 
1. Clone this repository:
```shell
git clone https://github.com/rsmuc/telekom-negativliste-updater
```
2. Install the required Python packages:
```shell
pip install -r requirements.txt
```
3. Download and install Geckodriver for Firefox. You can find the latest version [here](https://github.com/mozilla/geckodriver/releases). 

## Installation of Geckodriver:

1. Visit the Geckodriver releases page on GitHub: [https://github.com/mozilla/geckodriver/releases](https://github.com/mozilla/geckodriver/releases) 
 
2. Scroll down to the latest release and find the appropriate version for your operating system. Geckodriver is available for Windows, macOS, and Linux. 
 
3. Download the Geckodriver executable file for your operating system. 
 
4. Extract the contents of the downloaded archive. 
 
5. Add the location of the extracted Geckodriver executable to your system's  PATH  environment variable. This step allows you to run Geckodriver from any directory in your command prompt or terminal. 
 
6. Verify the installation by opening a command prompt or terminal window and running the following command:
```shell
   geckodriver --version
```
If the installation was successful, you should see the version number of Geckodriver printed in the console. 
 
Please note that the exact steps for installing Geckodriver may vary depending on your operating system. Make sure to provide instructions specific to the operating system you are targeting in your README. 
 
Remember to include any additional details or troubleshooting steps that may be relevant to your specific use case.
 
## Usage 
 
The script supports the following command-line arguments: 
 
-  --username : Your Telekom username. 
-  --password : Your Telekom password. 
-  --phone_number : The phone number where the Negativliste shall be updated. As written in the dropdown when you login to the Telefoniecenter. e.g. "089 55555"
-  --number_source : The URL of the SPAM number source. e.g. notsocleverdialer.de 
-  --simulate : Enable simulation mode to simulate adding numbers without actually modifying the Negativliste. 
-  --interactive : Enable interactive mode to run firefox in foreground. 
 
To run the script, use the following command:
```shell
python telekom_negativliste_updater.py --username your_username --password your_password --phone_number your_phone_number --number_source notsocleverdialer.de
```
The script will log in to the Telekom Telefoniecenter, navigate to the Negativliste, and update it with the current most active spam numbers from the specified source. 

Please note that the specific source of the spam number list is not directly mentioned in this README, as scraping data from certain sources may not be allowed. You can configure the  --number_source  argument with a valid URL of a spam number source that complies with the terms of use and legal requirements. 
 
## Limitations 
 
- The Telekom Negativliste allows blocking up to 50 numbers. If the number of spam numbers exceeds this limit, only the first 50 will be blocked. 
- The script relies on the availability and accuracy of the number source website. If the website structure or content changes, the script may need to be updated accordingly. 
- Changes to the Telekom page structure or functionality may cause the script to stop working. Regular maintenance and updates may be required to keep the script functioning properly. 
 
## License 
 
This script is licensed under the [MIT License](LICENSE). 