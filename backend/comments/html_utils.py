from html.parser import HTMLParser

import bleach


class TagBalanceParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.error = None

    def handle_starttag(self, tag, attrs):
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.error = f'Invalid or unclosed tag structure near </{tag}>'
            return
        self.stack.pop()

    def error_message(self):
        if self.error:
            return self.error
        if self.stack:
            return f'Unclosed tag(s): {", ".join(self.stack)}'
        return None


def sanitize_comment_html(value: str) -> str:
    parser = TagBalanceParser()
    parser.feed(value)
    parser.close()
    msg = parser.error_message()
    if msg:
        raise ValueError(msg)

    return bleach.clean(
        value,
        tags=['a', 'code', 'i', 'strong'],
        attributes={'a': ['href', 'title']},
        strip=True,
    )
