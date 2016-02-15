import json
from datetime import datetime

import pandas as pd
import requests_cache
import toolz.curried as toolz
import pymongo

import meetup

requests_cache.install_cache('meetup_cache')

DB = pymongo.MongoClient('localhost', 27017)
API_KEY = "39137ef755b394a3bb7222b762d"

EPOCH = datetime.utcfromtimestamp(0)
def unix_time_millis(dt):
    return (dt - EPOCH).total_seconds() * 1000

def download_cities(api, npages, **kwargs):
    pages = [api.cities(), ]
    for page in xrange(npages):
        pages = api.cities(**kwargs)
    return meetup.unpaginate_results(pages)

def download_many_pages(api, endpoint, max_pages=float('inf'), **kwargs):
    results = []
    resp = api._get(endpoint, **kwargs)
    results.extend(resp['results'])
    page = 0
    while resp['meta']['next']:
        page += 1
        if page > max_pages:
            break
        resp = api._get(resp['meta']['next'])
        results.extend(resp['results'])
    return results

def download_groups_city(api, max_pages=float('inf'), **kwargs):
    results = []
    resp = api._get('/2/groups', **kwargs)
    page = 0
    while resp['meta']['next']:
        page += 1
        if page > max_pages:
            break
        resp = api._get(resp['meta']['next'])
        results.extend(resp['results'])
    return results

def unpack_response(response):
    return pd.DataFrame(response['results'])

API = meetup.MeetupApi(API_KEY)

cities_world = unpack_response(API.cities())
cities_gb = unpack_response(API.cities(country='gb'))

def download_groups():
    for city in cities_gb.city:
        city_groups = download_many_pages(API, endpoint='/2/groups', city=city, country='gb')
        groups_gb.extend(city_groups)
        DB.meetup.groups.insert_many(city_groups)


groups_gb = list(DB.meetup.groups.find({'country': 'GB'}))

seen_ids = frozenset(x['group']['id']
        for x in DB.meetup.events.find({'group': {'$exists':True}},
                                       {'_id': 0, 'group.id':1}))


# Generate comma-separated partitions of group ids
for i in xrange(1, 34):
    group_ids_parts = toolz.pipe(
        groups_gb,
        toolz.filter(lambda x: 'category' in x),
        toolz.filter(lambda x: x['category']['id'] == i), # Tech groups
        lambda group: (str(g['id']) for g in group if g['id'] not in seen_ids),
        toolz.partition_all(50),
        lambda partitions: (','.join(partition) for partition in partitions),
    )
    for group_ids_part in group_ids_parts:
        events = download_many_pages(API, "/2/events", status='past', 
                                     group_id=group_ids_part,
                                     after="01012014",
                                     before="01012016")
        if events:
            DB.meetup.events.insert_many(events)
