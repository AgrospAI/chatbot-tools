from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    parsed = urlparse(url)

    return parsed.scheme in ["http", "https"] and parsed.netloc


class URLField:
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        return obj.__dict__[self.name]

    def __set__(self, obj, value):
        if not is_valid_url(value):
            raise ValueError(f"Invalid URL: {value}")
        obj.__dict__[self.name] = value
