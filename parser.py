# the HTML parser
from html.parser import HTMLParser


class SOSParser(HTMLParser):
    header_list = []
    parse_header = False
    parse_title = False
    parse_summary = False
    summary = ''
    title = ''

    def clear(self):
        self.header_list = []
        self.title = ''
        self.summary = ''

    def handle_starttag(self, tag, attrs):
        # if the tag is the title, trigger grabbing the title
        if tag == "title":
            self.parse_title = True
        else:
            self.parse_title = False

        # if the tag is a div, check whether the class name contains propName,
        # in order to parse the summary
        if tag == "div":
            for attr in attrs:
                if attr[0] == "class":
                    if attr[1].find('propName') > 0:
                        self.parse_summary = True

        # if the tag is an header, trigger grabbing the header
        if tag == "h2":
            self.parse_header = True
        else:
            self.parse_header = False

    def handle_data(self, data):
        data = data.strip()
        if self.parse_header:
            if len(data) > 0:
                self.header_list.append(data)
                # if parse summary is on (i.e., the div this h2 tag is sitting
                # in is of class "propName", it is the summary
                if self.parse_summary:
                    # the summary contains many attributes, but let's take the
                    # first one

                    self.summary = data.split(".")[0].lower().capitalize()

        if self.parse_title:
            data = data.replace(" | Official Voter Information Guide | California Secretary of State", "")
            data = data.replace("Prop ", "")
            data = data.replace("Proposition ", "")
            prop_num = data.split(" ")[0]
            text_type = " ".join(data.split(" ")[1:])
            if len(data) > 0:
                self.title = [prop_num, text_type]

    def handle_endtag(self, tag):
        if tag == 'div':
            self.parse_summary = False