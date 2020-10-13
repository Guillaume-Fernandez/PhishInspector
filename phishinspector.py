'''
   phishinspector.py
   fork from https://github.com/cybercdh/phishfinder
 '''
import custom_functions as phish #Best pratices => one function = only one reuseable action
import json
import time
import multiprocessing
from collections import Counter
from signal import signal, SIGINT


def main():
    ws=multiprocessing.Process(target=phish.web_server)
    ws.start()
    print ("Web Server started: http://localhost:8002")
    i=0
    phish.mkdir_p("./result/") #Create directories
    args = phish.check_args() #Check input arguments
    target_classement = list()
    failed_ip_country = 0
    try:
        os.remove("./map/maps/markers.js.tmp")
    except:
        open("./map/maps/markers.js.tmp", "w")
    phish.append_file("./map/maps/markers.js.tmp", "var markers = [")

    #Import URL source file or download it from phishtank
    if args.inputfile is not None:
        source_file = phish.use_local_file(args.inputfile)
        print (source_file)
    else:
        source_file = phish.dl_from_phishtank()
        print (source_file)

    with open(source_file) as json_file:
        data = json.load(json_file)
        json_len=len(data)
        for entry in data:
            try:
                new_line=phish.ip_to_country(entry["details"][0]["ip_address"],entry["phish_id"])
                phish.append_file("./map/maps/markers.js.tmp",new_line)
            except:
                failed_ip_country+=1
            phish.copy_file("./map/maps/markers.js.tmp","./map/maps/markers.js")
            target_classement.append(entry["target"])
            if phish.check_url(entry["url"]) == "without_interest":
                # print("This URL look like http://example.com (",entry["url"],"), there is no possibility for files scan.")
                pass
            else:
                while phish.child_process_count() > int(args.process):
                    time.sleep(0.1)
                    task1.join()
                task1 = multiprocessing.Process(target=phish.scan_entry, args=[entry])
                task1.start()
            i+=1
            print("Lines completed: ",i," / ",json_len)

    phish.finalization(Counter(target_classement),failed_ip_country)


if __name__ == "__main__":
    main()
