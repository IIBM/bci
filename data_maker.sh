#!/bin/bash
unzip data_part.zip
for i in {1..9}
do
   cat data_part >> data_test
done
