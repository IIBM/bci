#!/bin/bash
unzip data_part.zip
for i in {1..20}
do
   cat data_part >> data_test
done
rm data_part
