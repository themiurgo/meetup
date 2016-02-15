SHELL = /bin/bash

all: countries.csv worldcitiespop.csv

countries.csv:
	wget https://github.com/datasets/country-list/raw/master/data.csv -P data -O countries.csv

#worldcitiespop.csv:
#	wget http://download.maxmind.com/download/worldcities/worldcitiespop.txt.gz -P data
#

mongostart:
	mongod --dbpath ./data/mongodb


notebook:
	jupyter notebook Analysis.ipynb

data/cities1000.csv :
	cat data/cities1000.headers <(csvformat -e utf8 -t data/cities1000.txt -q @) > data/cities1000.csv

data/nuts_rg_60m_2010_lvl_1.geojson:
	wget -P data https://raw.github.com/datasets/geo-nuts-administrative-boundaries/master/data/nuts_rg_60m_2010_lvl_1.geojson
	# See http://data.okfn.org/data/core/geo-nuts-administrative-boundaries for more info
