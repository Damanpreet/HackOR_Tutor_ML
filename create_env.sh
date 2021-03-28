#!/bin/bash

for line in $(cat requirement.txt)
do
  pip install $line
done
