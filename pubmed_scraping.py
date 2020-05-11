from bs4 import BeautifulSoup
import requests
import csv
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import time

#################################################################
APIkey = '&api_key=' + 'cfbe775651d713e0d6e21194021827922d07'
keyword = "yeast"
batch_max = 1000
batch_size = 1000
search_start = 0
parallel = 10
#################################################################

EsearchURL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term="
ElinkURL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=pubmed&db=pubmed&id="
EfetchURL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id="

def get_soup(url):
    request = requests.get(url)
    soup = BeautifulSoup(request.content, 'html.parser')
    return soup

def get_data(id):
    id = id.text

    elink_url = ElinkURL + id + "&retmode=xml" + APIkey
    link_soup = get_soup(elink_url)
    link_data = link_soup.find_all('linksetdb')
    references = [link.text.split('\n') for link in link_data if 'pubmed_pubmed_refs' in link.text]

    if len(references) == 0:
        ref_ids = 'None'
    else:
        ref_ids = references[0][4::2]

    # time.sleep(0.05)

    efetch_url = EfetchURL + id + "&retmode=xml" + APIkey
    fetch_soup = get_soup(efetch_url)
    title = fetch_soup.find('articletitle').text
    pubdate = fetch_soup.find("daterevised").text.replace('\n', '')
    authors = ["{0} {1}".format(last.text,fore.text) for last,fore in zip(fetch_soup.find_all('lastname'), fetch_soup.find_all('forename'))]
    try:
        abstract = fetch_soup.find("abstracttext").text
    except AttributeError:
        abstract = 'None'

    data = [id, ref_ids, title, pubdate, authors, abstract]

    return data


def main():

    start = time.time()

    id_list = []
    range_num = range(search_start,batch_max,batch_size)
    for retstart_num in range_num:
        search_url = EsearchURL + keyword + '&retstart=' + str(retstart_num) + '&retmax=' + str(batch_size) + APIkey
        ids = get_soup(search_url).find_all('id')
        id_list.extend(ids)

    # print('id_list:' + str(time.time()-start))
    # step = time.time()
    
    with ThreadPoolExecutor(parallel) as executor:
        results = list(executor.map(get_data, id_list))
    results_arr = np.array(results)

    # print('article_data_list:' + str(time.time()-step))
    # step = time.time()

    np.save('article_data_.npy', results_arr)

    # print('write:' + str(time.time()-step))
    # print('total:' + str(time.time()-start))

if __name__ == "__main__":
    main()
