import os
import logging
import sys

import httpx


LOG = logging.getLogger(__name__)
DSW_API_URL = os.environ.get('DSW_API_URL', '')
DSW_API_KEY = os.environ.get('DSW_API_KEY', '')
PACKAGE_IDS = os.environ.get('PACKAGE_IDS', '')

if DSW_API_URL == '' or DSW_API_KEY == '':
    LOG.error('DSW_API_URL or DSW_API_KEY is not specified!')
    sys.exit(1)


_HEADERS = {
    'Authorization': f'Bearer {DSW_API_KEY}',
    'User-Agent': 'fip2dmp-importer/0.1.0',
}

async def get_projects(query: str, tags: str):
    params = {
        'page': 0,
        'size': 900,
        'sort': 'name',
        'isTemplate': 'false',
    }
    if query != '':
        params['q'] = query
    if tags != '':
        params['projectTags'] = tags
    if PACKAGE_IDS != '':
        params['packageIds'] = PACKAGE_IDS
    r = httpx.get(f'{DSW_API_URL}/questionnaires',
                  params=params, headers=_HEADERS)
    r.raise_for_status()
    return r.json()


async def get_project_tags(query: str, exclude: str):
    params = {
        'page': 0,
        'size': 900,
    }
    if query != '':
        params['q'] = query
    if exclude != '':
        params['exclude'] = exclude
    r = httpx.get(f'{DSW_API_URL}/questionnaires/project-tags/suggestions',
                  params=params, headers=_HEADERS)
    r.raise_for_status()
    return r.json()


async def get_project(project_uuid: str):
    r = httpx.get(f'{DSW_API_URL}/questionnaires/{project_uuid}',
                  headers=_HEADERS)
    r.raise_for_status()
    return r.json()
