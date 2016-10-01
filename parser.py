# the HTML parser
from html.parser import HTMLParser


class SOSParser(HTMLParser):
    header_list = []
    parse_header = False
    parse_title = False
    title = ''
    def handle_starttag(self, tag, attrs):
        # if the tag is the title, trigger grabbing the title
        if tag == "title":
            self.parse_title = True
        else:
            self.parse_title = False

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
        if self.parse_title:
            data = data.replace(" | Official Voter Information Guide | California Secretary of State", "")
            data = data.replace("Prop ", "")
            data = data.replace("Proposition ", "")
            prop_num = data.split(" ")[0]
            text_type = " ".join(data.split(" ")[1:])
            if len(data) > 0:
                self.title = [prop_num, text_type]