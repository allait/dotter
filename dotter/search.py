from .storage import DotStorage

FILE_TYPES = {
    'vim': ['vimrc', '.vimrc'],
    'zsh': ['zshrc', '.zshrc'],
    'bash': ['bashrc', '.bashrc'],
    'tmux': ['tmux.conf', '.tmux.conf'],
    'git': ['gitconfig', '.gitconfig'],
}

FILE_PATHS = {v: k for k in FILE_TYPES for v in FILE_TYPES[k]}

SEARCH_QUERIES = [
    'dotfiles',
    'dotfiles in:name stars:>3',
    'dotfiles in:name stars:3',
    'dotfiles in:name stars:2',
    'dotfiles in:name stars:1',
]


def find_files(contents):
    for item in contents:
        if item['path'] in FILE_PATHS:
            yield FILE_PATHS[item['path']], item['git_url']


def get_dotfiles(client, queries):
    dots = {}

    for repo, url in client.iter_all_repos(queries):
        repo_contents = client.get_repo_contents(url)

        if repo_contents:
            for dotfile_type, git_url in find_files(repo_contents):
                if dotfile_type not in dots:
                    dots[dotfile_type] = DotStorage(dotfile_type)
                dots[dotfile_type].add(client.get_page(git_url), git_url)

    return dots
