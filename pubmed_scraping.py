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
batch_size = 1000
search_start = 0
parallel = 4 #Up to 4, because API rate limit
#################################################################

EsearchURL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term="
ElinkURL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&db=pubmed&id="
EfetchURL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id="

def get_soup(url):
    request = requests.get(url)
    soup = BeautifulSoup(request.content, 'html.parser')
    return soup

def get_ref_ids(url):
    link_soup = get_soup(url)

    link_data = link_soup.find_all('linksetdb')
    references = [link.text.split('\n') for link in link_data if 'pubmed_pubmed_refs' in link.text]

    if len(references) == 0:
        ref_ids = 'None'
    else:
        ref_ids = references[0][4::2]

    return ref_ids

def get_fetch_data(url):
    fetch_soup = get_soup(url)

    title = fetch_soup.find('articletitle').text
    pubdate = fetch_soup.find("daterevised").text.replace('\n', '')
    authors = ["{0} {1}".format(last.text,fore.text) for last,fore in zip(fetch_soup.find_all('lastname'), fetch_soup.find_all('forename'))]
    try:
        abstract = fetch_soup.find("abstracttext").text
    except AttributeError:
        abstract = 'None'

    fetch_data = [title, pubdate, authors, abstract]

    return fetch_data


def main():

    start = time.time()

    id_list = []
    for retstart_num in range(search_start,batch_max,batch_size):
        search_url = EsearchURL + keyword + '&retstart=' + str(retstart_num) + '&retmax=' + str(batch_size) + APIkey
        ids = get_soup(search_url).find_all('id')
        id_list.extend(ids)
    id_list = [id.text for id in id_list]

    # print('id_list:' + str(time.time()-start))
    # step = time.time()
    elink_urls = [ElinkURL + id + "&retmode=xml" + APIkey for id in id_list]
    efetch_urls = [EfetchURL + id + "&retmode=xml" + APIkey for id in id_list]

    article_data = []
    with ThreadPoolExecutor(parallel) as executor:
        ref_ids_results = list(executor.map(get_ref_ids, elink_urls))

    with ThreadPoolExecutor(parallel) as executor:
        fetch_data_results = list(executor.map(get_fetch_data, efetch_urls))

    article_data.append([id_list, ref_ids_results, fetch_data_results])
    article_data_arr = np.array(article_data[0]).T

    # print('article_data_list:' + str(time.time()-step))
    # step = time.time()

    with open('article_data.csv', 'w', encoding='utf-8') as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerows(article_data_arr)

    # print('write:' + str(time.time()-step))
    # print('total:' + str(time.time()-start))

if __name__ == "__main__":
    main()
