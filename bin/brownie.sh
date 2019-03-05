#!/bin/bash

docker run -it -v $PWD:/usr/src brownie-local brownie $@
