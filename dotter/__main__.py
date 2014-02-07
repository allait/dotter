import argparse
import logging
import os

from .client import GithubCachedClient, GithubClient
from .search import get_dotfiles, SEARCH_QUERIES


def parse_args():
    parser = argparse.ArgumentParser(description='Search github for common lines in dotfiles')
    parser.add_argument('-t', '--token-file', type=os.path.abspath,
                        help='path to file containing Github token')
    parser.add_argument('-c', '--cache-path', type=os.path.abspath,
                        help='path to cache directory')
    return parser.parse_args()


def main():
    args = parse_args()

    token = open(args.token_file).read().strip() if args.token_file else None

    if args.cache_path:
        client = GithubCachedClient(cache_path=args.cache_path, token=token)
    else:
        client = GithubClient(token=token)

    dots = get_dotfiles(client, queries=SEARCH_QUERIES)

    return dots


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    dots = main()

    for ftype in dots:
        print
        print ftype
        print '-' * 40
        print "\n".join("%s\t%d" % i for i in dots[ftype].top_lines())
