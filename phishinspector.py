'''
   phishinspector.py
   fork from https://github.com/cybercdh/phishfinder
 '''
import custom_functions as phish #Best pratices => one function = only one reuseable action
import json
import time
import multiprocessing
import threading
from collections import Counter

def main():
    i=0
    phish.mkdir_p("./result/zip/") #Create directories
    args = phish.check_args() #Check input arguments
    target_classement = list()
    failed_ip_country = 0
    try:
        os.remove("./map/maps/markers.js")
    except:
        open("./map/maps/markers.js", "w")
    phish.append_file("./map/maps/markers.js", "var markers = [")

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
            # print (entry["phish_id"],entry["url"],entry["details"][0]["country"],entry["target"])
            # append_country_map(entry["details"][0]["country"])
            try:
                new_line=phish.ip_to_country(entry["details"][0]["ip_address"],entry["phish_id"])
                phish.append_file("./map/maps/markers.js",new_line)
            except:
                failed_ip_country+=1
            target_classement.append(entry["target"])
            if phish.check_url(entry["url"]) == "without_interest":
                # print("This URL look like http://example.com (",entry["url"],"), there is no possibility for files scan.")
                pass
            else:
                while phish.child_process_count() > 3:
                    time.sleep(1)
                    task1.join()
                task1 = multiprocessing.Process(target=phish.scan_entry, args=[entry])
                task1.start()
            i+=1
            print("Lines completed: ",i," / ",json_len)

                # print("111111")
                # # t = Thread(target=phish.scan_entry(entry))
                # p=multiprocessing.Process(target=phish.test())
                # p.start()
                # print("222222")
                # Process(target=phish.scan_entry(entry))

            #     scan = phish.search_files(entry["url"])
            # # print (scan)
            #     if scan is not None:
            #         for scan_result in scan:
            #             phish.download_file(scan_result,"./result/" + entry["phish_id"])
            # if child process > 20 then :
            #     wait this loop pid
    print (Counter(target_classement))
    print("Failed ip resolv:",failed_ip_country)
    # json = json.loads(open(source_file).read())
    # for entry in json:
    #     url = json['url']
    #     print json['url']
    #     #resolv_url_to_ip(phishing_url)
    #     #ip_to_country(ip[0])
    #     exit()
    #     #go_phishing(phishing_url)

    phish.append_file("./map/maps/markers.jsp", "];")
    # phish.copyfile("./map/maps/markers.js.tmp","./map/maps/markers.js")


if __name__ == "__main__":
  main()

    #Initialisation of map source filename

    #For each urls in source file

    #If nb_worker < desired_nb_workers do:
