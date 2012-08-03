import json, tokeniser

class TweetsWithRE():
    def __init__(self, search_res, case_sensitive=False):
        self.tokeniser = tokeniser.MicroTokeniser()
        self.search_res = search_res
        self.case_sensitive = case_sensitive
    
    def search_line(self, line):
        if not self.case_sensitive:
            line = line.lower()
        str_to_search = ' '.join(self.tokeniser.tokenise(line))
        for sre in self.search_res:
            mo = sre.search(str_to_search)
            if mo:
                return mo

if __name__ == '__main__':
    import argparse, re, sys

    parser = argparse.ArgumentParser()
    parser.add_argument('--searchres', type=str, 
                        help="Filename for regexes to search, one regeex per line")
    args = parser.parse_args()

    search_res = [re.compile("\\b" + x.strip() + "\\b") for x in open(args.searchres)]
    twre = TweetsWithRE(search_res)

    for line in sys.stdin:
        try:
            line = line.decode('utf8')
            tweet = json.loads(line)
            if tweet.has_key('text'):
                tweet_text = tweet['text']
            else:
                continue
        except UnicodeDecodeError:
            continue
        except ValueError:
            continue
        result = twre.search_line(tweet_text)
        if result:
            print (result.group() + '\t' + line.strip()).encode('utf8')
