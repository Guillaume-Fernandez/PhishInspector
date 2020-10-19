#!/bin/bash

#Docker dir
ls -d ../result/* | xargs sha1sum | sort -u -k1,1 | awk '{print $2}' > ./uniq.txt

for i in ./uniq.csv; do
  docker run -d --name $i Copy zip as source.zip.
  sha1sum dir monté
  Wait for user action / enter
  sha1sum dir and compare
  credentials are probably locatate inside docker. If no diff => maybe online
