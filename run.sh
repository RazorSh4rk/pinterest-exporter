#!/bin/bash

docker build -t pinterestboard .
docker run --rm -p 5000:5000 pinterestboard
