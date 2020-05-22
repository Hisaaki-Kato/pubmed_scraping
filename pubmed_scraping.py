from bs4 import BeautifulSoup
import requests
import csv
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import time

#################################################################
APIkey = '&api_key=' + '--your api key--'
keyword = "yeast"
batch_max = 1000
batch_size = 100  # <10,000
search_start = 0
parallel = 4
#################################################################

EsearchURL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term="
ElinkURL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&db=pubmed&"
EfetchURL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed"

def get_soup(url):
    request = requests.get(url)
    soup = BeautifulSoup(request.content, 'html.parser')
    return soup

def get_data(retstart_num):

    search_url = EsearchURL + keyword + '&retstart=' + str(retstart_num) + '&retmax=' + str(batch_size) + '&usehistory=y' + APIkey
    soup = get_soup(search_url)
    ids = soup.find_all('id')
    querykey = soup.find('querykey').text
    webenv = soup.find('webenv').text

    efetch_url = EfetchURL + "&retmode=xml" + '&query_key=' + querykey + '&WebEnv=' + webenv + '&retmax=' + str(batch_size) + APIkey
    fetch_soup = get_soup(efetch_url)
    articles = fetch_soup.find_all('pubmedarticle')

    data_list = []
    for ID, article in zip(ids, articles):
        title = article.find('articletitle').text
        pubdate = article.find("daterevised").text.replace('\n', '')
        authors = ["{0} {1}".format(last.text,fore.text) for last,fore in zip(article.find_all('lastname'), article.find_all('forename'))]
        try:
            abstract = article.find("abstracttext").text
        except AttributeError:
            abstract = None
        data = [ID.text, title, pubdate, authors, abstract]
        data_list.extend(data)
        
    return data_list


def main():

    range_num = range(search_start,batch_max,batch_size)
    with ThreadPoolExecutor(parallel) as executor:
        results = [result for inner in list(executor.map(get_data, range_num)) for result in inner]
    results_arr = np.array(results)
    results_arr = results_arr.reshape([int(len(results_arr)/5), 5])
    
    with open('article_data.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(results_arr)

if __name__ == "__main__":
    start = time.time()
    main()
    print(time.time() - start)
