# phishfinder

## Overview
This repository is a fork from https://github.com/cybercdh/phishfinder

Features:
1. Download last phishtank data
2. Parse each URL:
  - Look for directories and files (.zip, .txt, .tar.gz and .tar.xz). Detailed informations at "URL scan".
  - Download possibly phishing kits and victim logs
  - Resolve IP to country and create a HTML map (based on https://github.com/asmaloney/Leaflet_Cluster_Example)
  - Log result to a csv or html file
3. Generate and compare sha1sum for each files. It is useless to analyse the same phishing kit.
4. Run phishing kits on Docker and run script to automaticly detect the trap.


## Usage
Run the script without any arguments to use the latest URLs from http://data.phishtank.com/data/online-valid.json

    python3 phishfinder.py

Else, you can pass a list of URLs and specify the folder where you'd like to save results

    python3 phishfinder.py --input urls.txt --output /phishing/kit/folder

## Example

![phishfinder example](/../screenshots/render1551268365598.gif?raw=true "Phishfinder Example")

## Install
    $ pip3 install -r requirements.txt

## TODO

Updates planned include:

* ~~Brute-forcing for files using the directory as the filename~~
* Speed up the requests and use threading
* ~~Resolve issue where a successful guess downloads a file, followed by an Open Directory download~~
