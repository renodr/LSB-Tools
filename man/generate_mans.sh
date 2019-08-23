#!/bin/bash

./help2man -N -i lsb_release.include -s 1 -m LSB-Tools -v "--progver" lsb_release > lsb_release.1

./help2man -N -i install_initd.include -s 8 -m LSB-Tools -v "--progver" /usr/lib/lsb/install_initd > install_initd.8

./help2man -N -i remove_initd.include -s 8 -m LSB-Tools -v "--progver" /usr/lib/lsb/remove_initd > remove_initd.8

