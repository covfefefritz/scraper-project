#!/bin/bash

# Get the current date
current_date=$(date +%F)

# Run Scrapy 
scrapy crawl news -o "Output/raw/news_data_${current_date}.csv"

# Assuming cleaner.py and analyze.py take a filename as an argument
python cleaner.py "Output/raw/news_data_${current_date}.csv"
python analyzer.py "Output/cleaned/news_data_${current_date}.csv" #"_cleaned" statically defined in cleaner.py}


