#!/bin/bash

#Idee: Django web site, PSQL, scan en python, analyser les fichiers avec python, map country + map mental

#Docker dir
ls -d ./result/* | xargs sha1sum | sort -u -k1,1 | awk '{print $2}' > ./uniq.txt
echo "./result/6796391-1and1.zip" > ./uniq.txt
docker network create --internal --subnet 10.1.1.0/24 no-internet

init_func(){
  #Init
  docker run --rm -d -t -p 8080:80 --name phis-launcher phis-launcher:latest
  #--net no-internet
  docker exec phis-launcher rm /var/www/html/index.html
  docker cp $1 phis-launcher:/tmp/source.zip
  docker exec phis-launcher mkdir /tmp/unzip
  docker exec phis-launcher unzip /tmp/source.zip -d /tmp/unzip/
  docker exec phis-launcher unzip /tmp/source.zip -d /var/www/html/
  docker exec phis-launcher service apache2 start
}

diff_func(){
  docker exec phis-launcher diff -r --new-file /tmp/unzip/ /var/www/html/ | grep '>'
  r=$(docker exec phis-launcher bash -c 'diff -r --new-file /var/www/html/ /tmp/unzip/ > /dev/null; echo $?') #With bash -c and $? do not use "", use ''
  if [ $r == "1" ]
  then
    echo "diff detected"
    return 1
  else
    echo "No diff detected"
    return 0
  fi
}

while read i ; do
  init_func $i


  web_files=$(docker exec phis-launcher bash -c "find /var/www/html/ -name '*.php*' -o -name '*.html*' -o -name '*.htm*' | sed 's|/var/www/html||g'") # => /dir1/dir2/file.php /dir/dir3/file2.html etc.
  for i in $web_files; do
    echo "http://localhost:8080$i"
    #Grep every var names insite this file
    #Get action dest.php
    #
    # docker exec phis-launcher bash -c "curl 'http://localhost:80'$i --data-raw 'email=toto%40gmail.com&password=totopass&user=toto'" #check -d for post and get ?
    # r=$(diff_func)
    # echo $r
    done
  sleep 10800
  docker stop phis-launcher
  exit 1
done < ./uniq.txt


# docker exec phis-launcher bash -c "echo 'user:azerty1234' > /var/www/html/r.txt"
# docker exec phis-launcher bash -c "echo 'TEST-TEST' > /var/www/html/Adobe1/Adobe1/login.php"
#



# r=$(docker exec phis-launcher bash -c "ls -d /var/www/html/*")
# if [ $($r | wc -w) == 1 ]
#   r=$(docker exec phis-launcher bash -c "type $r")
#   if [ $y == True ]
# then
#   echo "go recursiv"
# else
#   echo "test file there"
# fi
