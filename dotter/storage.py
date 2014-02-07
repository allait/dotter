COMMENT_STRINGS = {
    'vim': '"',
    'zsh': '#',
    'bash': '#',
    'tmux': '#',
    'git': '#',
}


class DotLineComments(object):
    def __init__(self, count=0, comments=None):
        self.count = count
        self.comments = comments or []

    def add_occurence(self, comment=None, source=None):
        self.count += 1
        if comment:
            self.add_comment(comment, source)

    def add_comment(self, comment, source):
        self.comments.append((comment, source))


class DotStorage(object):
    def __init__(self, dotfile_type, comment_string=None):
        self.file_type = dotfile_type
        self.lines = {}
        self.comment_string = comment_string or COMMENT_STRINGS.get(dotfile_type)

    def add(self, git_url_contents, source=None):
        if 'content' not in git_url_contents:
            return
        file_content = git_url_contents['content'].decode('base64')
        self.add_lines(file_content, source)

    def top_lines(self, n=50):
        line_counts = [(key, val.count) for key, val in self.lines.iteritems()]
        return sorted(line_counts, key=lambda x: x[1], reverse=True)[:n]

    def add_lines(self, file_content, source):
        for line, comment in self.lines_with_comments(file_content):
            self.add_line(line, comment, source)

    def add_line(self, line, comment=None, source=None):
        if line not in self.lines:
            self.lines[line] = DotLineComments()
        self.lines[line].add_occurence(comment, source)

    def lines_with_comments(self, file_content):
        comment = []
        for line in filter(None, file_content.split('\n')):
            # Skip indented lines for now
            if line[0].isspace():
                pass
            elif line.startswith(self.comment_string):
                comment.append(line.lstrip(self.comment_string))
            else:
                yield line.strip(), ('\n'.join(comment) or None)
                comment = []
