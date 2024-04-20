#!/bin/bash



# Get the current date
current_date=$(date +%F_%H)
project_path="/home/fs/work/Scraper/public"

# activate conda env
source /home/fs/work/Scraper/screnv/bin/activate

cd "$project_path"
# Run Scrapy 
scrapy crawl news -o "$project_path/Output/raw/news_data_$current_date.csv"

# cleaner.py and analyze.py take a filename as an argument
python cleaner.py "$project_path/Output/raw/news_data_$current_date.csv"
python analyzer.py "$project_path/Output/cleaned/news_data_$current_date.csv" 

cd ".."
#python google_upload.py
