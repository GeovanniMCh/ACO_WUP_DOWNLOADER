try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser


class VersionParser(HTMLParser):
    gui_data_set = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href":
                    if value.startswith("GeovanniMCh/ACO_WUP_DOWNLOADER") and value.endswith(".zip"):
                        self.gui_data_set.append(value)
