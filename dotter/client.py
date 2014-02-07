import json
import logging
import os
import time
import urllib

import requests


class GithubClient(object):

    GITHUB_API_ROOT = 'https://api.github.com/'

    def __init__(self, token=None):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.auth = (token, 'x-oauth-basic') if token else None
        self.session.headers.update({'User-Agent': 'Dotter'})
        self.ratelimit_remaining = 1
        self.ratelimit_reset = None

    def iter_repos(self, query, page=1, per_page=100):
        # Manual encode is easier than passing params all over the class
        results = self.get_page(self.GITHUB_API_ROOT + 'search/repositories?%s' %
                                urllib.urlencode({'q': query, 'page': page, 'per_page': per_page}))

        for repo in results['items']:
            yield repo['full_name'], repo['url']

    def iter_all_repos(self, queries):
        if isinstance(queries, basestring):
            queries = [queries]
        for query in queries:
            # Github only returns 1000 search results
            for page in range(1, 11):
                for repo in self.iter_repos(query, page=page, per_page=100):
                    yield repo

    def get_repo_contents(self, repo_url):
        return self.get_page(repo_url + '/contents/')

    def get_page(self, url):
        return self.api_call(url)

    def api_call(self, url):
        self.api_sleep()

        response = self.session.get(url)
        self.ratelimit_remaining = int(response.headers['X-RateLimit-Remaining'])
        self.ratelimit_reset = int(response.headers['X-RateLimit-Reset'])
        self.logger.debug('Retrieved page %s [%d remaining]', url, self.ratelimit_remaining)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            self.api_sleep()
            return self.api_call(url)

    def api_sleep(self):
        if self.ratelimit_remaining:
            return

        sleep_time = self.ratelimit_reset - time.time() + 1
        self.logger.debug("Sleeping for %ds...", sleep_time)
        time.sleep(sleep_time)


class GithubCachedClient(GithubClient):
    def __init__(self, cache_path=None, *args, **kwargs):
        super(GithubCachedClient, self).__init__(*args, **kwargs)
        self.cache = CacheStorage(cache_path=cache_path, site_root=self.GITHUB_API_ROOT)

    def get_page(self, url):
        if url in self.cache:
            self.logger.debug("Found %s in cache", url)
            return self.cache.get(url)
        else:
            self.logger.debug("Retrieving %s...", url)
            page = self.api_call(url)
            self.cache.save(url, page)
            return page


class CacheStorage(object):
    def __init__(self, cache_path='cache/', site_root=''):
        self.cache_path = cache_path
        self.site_root = site_root

    def cache_filename(self, page_url):
        filename = page_url.replace(self.site_root, '').rstrip('/').replace('/', '-')
        return os.path.join(self.cache_path, filename + '.json')

    def get(self, page_url):
        with open(self.cache_filename(page_url), 'r') as cached_page:
            return json.load(cached_page)

    def save(self, page_url, data):
        with open(self.cache_filename(page_url), 'w') as cache_file:
            json.dump(data, cache_file)

    def __contains__(self, page_url):
        return os.path.exists(self.cache_filename(page_url))
