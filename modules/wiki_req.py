import requests
from datetime import date, datetime

url = "https://simple.wikipedia.org/w/api.php"
user_agent = "iui-wikipedia (https://github.com/yelouis/IUI_Wiki_Comp)"
query_base = query_params = {
    'action': 'query',
    'format': 'json',
}
headers = {
    'User-Agent': user_agent
}
rv_limit = 10


def get_article_properties(pageid):
    # Returns the article's current revision ID, parent revision ID, and the past rv_limit revision IDs
    query_params = query_base.copy()
    query_params['pageids'] = pageid
    query_params['rvprop'] = 'ids'
    query_params['rvlimit'] = rv_limit
    query_params['prop'] = 'revisions'

    request = requests.get(url=url, params=query_params, headers=headers).json()

    revisions = request['query']['pages'][str(pageid)]['revisions']

    revision_ids = [cell['revid'] for cell in revisions]

    cid = request['query']['pages'][str(pageid)]['revisions'][0]['revid']
    pid = request['query']['pages'][str(pageid)]['revisions'][0]['parentid']

    return revision_ids, cid, pid


def get_creation_date(pageid):
    # Returns a timestamp of the article's creation
    query_params = query_base.copy()
    query_params['pageids'] = pageid
    query_params['rvprop'] = 'timestamp'
    query_params['rvlimit'] = 1
    query_params['rvdir'] = 'newer'
    query_params['prop'] = 'revisions'

    request = requests.get(url=url, params=query_params, headers=headers).json()

    revisions = request['query']['pages'][str(pageid)]['revisions']

    timestamp = datetime.strptime(revisions[0]['timestamp'], "%Y-%m-%dT%H:%M:%SZ")

    return timestamp


def get_revision_date(revision_id, pageid):
    # Returns the timestamp of a given revision
    query_params = query_base.copy()
    query_params['revids'] = revision_id
    query_params['rvprop'] = 'timestamp|ids'
    query_params['prop'] = 'revisions'

    request = requests.get(url=url, params=query_params, headers=headers).json()

    revisions = request['query']['pages'][str(pageid)]['revisions']

    timestamp = datetime.strptime(revisions[0]['timestamp'], "%Y-%m-%dT%H:%M:%SZ")

    return timestamp


def get_text(pageid):
    # Returns plain text of the article's body
    query_params = query_base.copy()
    query_params['pageids'] = pageid
    query_params['prop'] = 'extracts'

    request = requests.get(url=url, params=query_params, headers=headers).json()

    text = request['query']['pages'][str(pageid)]['extract']

    return text


def get_images(pageid):
    # Returns a list of images in the article
    query_params = query_base.copy()
    query_params['pageids'] = pageid
    query_params['prop'] = 'images'
    
    request = requests.get(url=url, params=query_params, headers=headers).json()

    images = request['query']['pages'][str(pageid)]['images']

    return images


def get_external_links(pageid):
    # Returns list of external links within the article
    query_params = query_base.copy()
    query_params['pageids'] = pageid
    query_params['prop'] = 'extlinks'
    
    request = requests.get(url=url, params=query_params, headers=headers).json()

    extlinks = request['query']['pages'][str(pageid)]['extlinks']

    return extlinks


def get_internal_links(pageid):
    # Returns list of internal links within the article
    query_params = query_base.copy()
    query_params['pageids'] = pageid
    query_params['prop'] = 'links'

    request = requests.get(url=url, params=query_params, headers=headers).json()

    links = request['query']['pages'][str(pageid)]['links']

    return links


def get_contributors(pageid, admin=False):
    # Returns all contributors to the article. If admin is true then returns only the trusted editors.
    query_params = query_base.copy()
    query_params['pageids'] = pageid
    query_params['prop'] = 'contributors'

    if admin: query_params['pcgroup'] = 'bureaucrat'

    request = requests.get(url=url, params=query_params, headers=headers).json()

    contribs = request['query']['pages'][str(pageid)]['contributors']

    return contribs
