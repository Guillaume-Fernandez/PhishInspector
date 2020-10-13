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

from geoip import geolite2, open_database
from urllib.parse import urlparse, urljoin, unquote

def hello_world(num):
    print("hello", num)
    time.sleep(10)
    print("world", num)

class bcolors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ENDC = '\033[0m'

def child_process_count(): #Then use if > 20 then .wait() process to
    current_process = psutil.Process()
    children = current_process.children(recursive=True)
    return len(children)

def thread_count(): #Then use if > 20 then .wait() process to
    threading.active_count()
    children = current_process.children(recursive=True)
    print(len(children))
    return len(children)

def scan_entry(entry):
    scan = search_files(entry["url"])
    # print (scan)
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
    return parser.parse_args()


def mkdir_p(path):
  try:
      os.makedirs(path)
  except OSError as exc: # Python >2.5
      if exc.errno == errno.EEXIST and os.path.isdir(path):
          pass
      else: raise

def dl_from_phishtank_old():
  # it does take a min or so to parse the json
  sys.stdout.write('[+]  Parsing URLs from phishtank, this may take a minute...')
  sys.stdout.flush()
  phishtank_url = "http://data.phishtank.com/data/online-valid.json"
  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
  }
  try:
    r = requests.get(phishtank_url, allow_redirects=True, timeout=5, stream=True, headers=headers)
  except requests.exceptions.RequestException:
    print(bcolors.WARNING + "[!]  An error occurred connecting to phishtank. Please try again." + bcolors.ENDC)
    sys.exit()

  if not r.ok:
    print(bcolors.WARNING + "[!]  An error occurred connecting to phishtank. Please try again." + bcolors.ENDC)
    sys.exit()
  parsed_json = r.json()
  urls = parsed_json['url'].strip()
  urls = unquote(urls)
  return urls, print(bcolors.OKGREEN + "done." + bcolors.ENDC)

def check_url(url):
    parts = urlparse(url)
    if (url[-1] == "/" and len(parts.path) == 1) or (len(parts.path) == 0):
        return "without_interest"
    else:
        return "with_interest"


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
        var = guess_file(phish_url,path_end,path_len,"zip")
        if var is not None:
            l.append(var)
        var = guess_file(phish_url,path_end,path_len,"tar.gz")
        if var is not None:
            l.append(var)
        var = guess_file(phish_url,path_end,path_len,"tar.xz")
        if var is not None:
            l.append(var)
    return l
        # try:
        #     l.append(guess_file(phish_url,"tar.gz"))
        # except:
        #     pass
        # try:
        #     l.append(guess_file(phish_url,"tar.xz"))
        # except:
        #     pass

def download_file(url,path):
    myfile = requests.get(url)
    filename = url.rsplit('/')[-1]
    open(path + "-" +  filename, 'wb').write(myfile.content)

def guess_file(phish_url,path_end,path_len,file_format):
  # append .zip to the current path, and see if it works!
    guess_url = phish_url + "." + file_format
    # print("[+]  Guessing: {}".format(guess_url))

    try:
      g = requests.head(guess_url, allow_redirects=False, timeout=2, stream=True)
      if not 'content-type' in g.headers:
        return

      # if the content-type isn't a zip, ignore
      if not file_format in g.headers.get('content-type'):
        return

      # hopefully we're working with a .zip now...
      print(bcolors.OKGREEN + "[!]  Successful guess! Potential kit found at {}".format(guess_url) + bcolors.ENDC)
      # download_file(guess_url)
      return guess_url

    except requests.exceptions.RequestException:
      # print("[!]  An error occurred connecting to {}".format(guess_url))
      return


def go_phishing(phishing_url):
  # parts returns an array including the path. Split the paths into a list to then iterate
  # e.g. ParseResult(scheme='https', netloc='example.com', path='/hello/world/foo/bar', params='', query='', fragment='')
  parts = urlparse(phishing_url)
  paths = parts.path.split('/')[1:]
  # iterate the length of the paths list
  for i in range(0, len(paths)):

    # traverse the path
    # phish_url = '{}://{}/{}/'.format(parts.scheme, parts.netloc,'/'.join(paths[:len(paths) - i]).encode('utf-8'))
    phish_url = '{}://{}/{}/'.format(parts.scheme, parts.netloc,'/'.join(paths[:len(paths) - i]))

    # guess each path with .zip extension
    go_guessing(phish_url)

    # request each path
    try:
      r = requests.get(phish_url, allow_redirects=False, timeout=2)
    except requests.exceptions.RequestException:
      print("[!]  An error occurred connecting to {}".format(phish_url))
      return

    if not r.ok:
      return
def use_local_file(f):
  # check the file exists
  if not os.path.isfile(f):
    print(bcolors.WARNING + "[!]  {} is not a valid file. Please retry".format(f) + bcolors.ENDC)
    sys.exit()
  return f

  # # parse the urls and go phishing
  # print(bcolors.WARNING + "[+]  Checking URLs from {}".format(f) + bcolors.ENDC)
  # with open (f) as inputfile:
  #   urls = inputfile.readlines()
  # return urls

def ip_to_country(ip):
    match = geolite2.lookup(ip)
    if match is not None:
        country = str(match.country)
        timezone = str(match.timezone)
        lat = str(match.location[0])
        long = str(match.location[1])
        new_line = str('{"name":"' + country + '","city":"' + timezone + '","lat":' + lat + ',"lng":' + long + ',},')
        return new_line
        # append_file("./map/maps/markers.js.tmp",new_line)
    else:
        return -1
    # return lat, long, print (ip,"is located at", match.country, match.timezone)

def append_file(file,line):
    map_source = open(file,'a')
    map_source.write(line)
    map_source.close()
