import errno
import os, os.path
import json
import sys
from argparse import ArgumentParser
import requests
import gzip
import shutil
import psutil
import time
import os
from http.server import HTTPServer, CGIHTTPRequestHandler# Make sure the server is created at current directory
from geoip import geolite2, open_database
from urllib.parse import urlparse, urljoin, unquote
from collections import Counter


class bcolors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'

# Create server object listening the port 80
def web_server():
    os.chdir('./map/')
    server_object = HTTPServer(server_address=('', 8002), RequestHandlerClass=CGIHTTPRequestHandler)
    server_object.serve_forever()

# Copy the contents of the file named file_in to a file named file_out.
def copy_file(file_in,file_out):
    shutil.copyfile(file_in, file_out)

# Append the string named line at the end of the file named file
def append_file(file,line):
map_source = open(file,'a')
map_source.write(line)
map_source.close()

# Print the number of element in the list target_c and print the String failed_ip_country and close the markers file
def finalization(target_c,failed_ip_country):
    print (Counter(target_c))
    print("Failed ip resolv:",failed_ip_country)
    append_file("./map/maps/markers.jsp.tmp", "];")


# Return the count the number of child process
def child_process_count(): #Then use if > 20 then .wait() process to
    current_process = psutil.Process()
    children = current_process.children(recursive=True)
    return len(children)

# Append the String phish_url and the String file_format and guess if the file exist, return it if yes and return NULL if not
def guess_file(phish_url,file_format):
    guess_url = phish_url + "." + file_format
    try:
      g = requests.head(guess_url, allow_redirects=False, timeout=2, stream=True)
      if not 'content-type' in g.headers:
        return
      # if the content-type isn't a file format, ignore
      if not file_format in g.headers.get('content-type'):
        return
      # hopefully we're working with a file format now...
      print(bcolors.OKGREEN + "[!]  Successful guess! Potential kit found at {}".format(guess_url) + bcolors.ENDC)
      # download_file(guess_url)
      return guess_url
    except requests.exceptions.RequestException:
      # print("[!]  An error occurred connecting to {}".format(guess_url))
      return

# Find if the String url got tar/zip/tar.gz files, return the list of the url's files or NULL
def search_files(url):
    # print("The URL is : ",url)
    parts = urlparse(url)
    if url[-1] == "/" and len(parts.path) > 1:
        url = url[:-1]
        # print(url)
    path_end = parts.path[-1]
    path_len = len(parts.path)
    paths = parts.path.split('/')[1:]
    if path_end == "/" and path_len == 1: # if http://url.com/ => exit function, can't try anything
        return
    l = list()
    for i in range(0, len(paths)):
        if paths[i] == "":
            return
        phish_url = '{}://{}/{}'.format(parts.scheme, parts.netloc,'/'.join(paths[:len(paths) - i]))
        var = guess_file(phish_url,"zip")
        if var is not None:
            l.append(var)
        var = guess_file(phish_url,"tar.gz")
        if var is not None:
            l.append(var)
        var = guess_file(phish_url,"tar.xz")
        if var is not None:
            l.append(var)
    return l


def scan_entry(entry):
    scan = search_files(entry["url"])
    if scan is not None:
        for scan_result in scan:
            download_file(scan_result,"./result/" + entry["phish_id"])


def dl_from_phishtank():
    url = 'http://data.phishtank.com/data/online-valid.json.gz'
    myfile = requests.get(url)
    open('online-valid.json.gz', 'wb').write(myfile.content)
    with gzip.open('online-valid.json.gz', 'rb') as f_in:
        with open('online-valid.json', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    return "online-valid.json"

def check_args():
    parser = ArgumentParser()
    parser.add_argument("-i", "--input", dest="inputfile", required=False, help="input file of phishing URLs", metavar="FILE")
    parser.add_argument("-o", "--output", dest="outputDir", default=".", help="location to save phishing kits and logs", metavar="FILE")
    parser.add_argument("-p", "--process", dest="process", default="10", help="Process number limit", metavar="INT")
    return parser.parse_args()


def mkdir_p(path):
  try:
      os.makedirs(path)
  except OSError as exc: # Python >2.5
      if exc.errno == errno.EEXIST and os.path.isdir(path):
          pass
      else: raise

def check_url(url):
    parts = urlparse(url)
    if (url[-1] == "/" and len(parts.path) == 1) or (len(parts.path) == 0):
        return "without_interest"
    else:
        return "with_interest"

def download_file(url,path):
    myfile = requests.get(url)
    filename = url.rsplit('/')[-1]
    open(path + "-" +  filename, 'wb').write(myfile.content)

def ip_to_country(ip,phishtank_id):
    match = geolite2.lookup(ip)
    if match is not None:
        country = str(match.country)
        timezone = str(match.timezone)
        lat = str(match.location[0])
        long = str(match.location[1])
        new_line = str('{"name":"' + country + '","city":"' + timezone + " | PhishTank:" + phishtank_id + '","lat":' + lat + ',"lng":' + long + ',},')
        return new_line
    else:
        return -1
