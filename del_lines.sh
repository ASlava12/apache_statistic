#!/bin/bash

mx=1;

for line in $(cat lines.txt)
do
	sed -i "s#$line#test$mx#g" test.log;
	mx=$(($mx+1));
	#echo $mx;
done

