#!/bin/bash
docker build -t type_check -f type_check.Dockerfile .
docker run -it type_check 