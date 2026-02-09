#!/bin/bash

docker build -t pinterestboard .
docker run --rm -v ./images:/app/images -p 5000:5000 pinterestboard
