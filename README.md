# pubmed_scraping

This is the application to scrape paper data from PubMed WebAPI.

## Requirement

* python 3.7

Install below libraries using pip.

* beautifulsoup 4.9.0
* requests 2.18.4
* numpy 1.18.2

## Usage
1. Clone this repository to your directory, and move to that directory.
```bash
$ git clone git@github.com:Hisaaki-Kato/pubmed_scraping.git
$ cd pubmed_scraping
```
2. Comment out line 9 and 10 of pubmed_scraping.py
```python
#from apikey import apikey   
#APIkey = apikey()  
```
3. Set your API key if you want. (What is API key? See this page. [Entrez Programming Utilities Help](https://www.ncbi.nlm.nih.gov/books/NBK25499/))
```python
APIkey = '&api_key= --your api key--'  #Set your API key
```
4. Input the keyword you want to search on pubmed.
```python
keyword = "--your keyword--"  #Defalut is 'yeast'
```
5. Run pubmed_scraping.py
```bash
$ python3 pubmed_scraping.py
```

## Note

By default, this app use 'multiprocessing' (see line 5). You can change this value from 0 to the number of CPU threads. 
※ Please note that if the number of accesses per second is too high, access will be denied by the API side (max value is 10 accesses per seconds).

## Author

Hisaaki-Kato