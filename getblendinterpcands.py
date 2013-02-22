# Copyright Paul Cook 2012, distributed under the GPL.

import argparse, blendinterps, codecs, gzip, langid, json, sys, tokeniser
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

parser = argparse.ArgumentParser()
parser.add_argument('lexfname', type=str, 
                    help="Filename for lexicon, assumed to be gzipped")
args = parser.parse_args()

lexicon = set([x.strip().lower() for x in gzip.open(args.lexfname)])

# Twitter contains many non-standard usages of spelling, and "'" as in "'s"
# is often omitted, so we add to the lexicon a variant of any word containing
# "'" that omits "'".
#
# Also, g-clipping is very common in Twitter, so we for any word in the lexicon
# that ends in "ing" we add a variant ending in "in".
new_lexicon = set(lexicon)
for l in lexicon:
    new_lexicon.add(l.replace("'", ""))
    if l.endswith('ing'):
        new_lexicon.add(l.rstrip('g'))
lexicon=new_lexicon

mytokeniser = tokeniser.MicroTokeniser()

for line in sys.stdin:
    try:
        input_line = line.decode('utf8')
        re_str,tweet = line.split('\t')
        tweet = json.loads(tweet)
        if tweet.has_key('text'):
            line = tweet['text'].strip().replace('\n', ' ')
        else:
            continue
    except UnicodeDecodeError:
        continue
    except ValueError:
        continue

    # Run langid later to filter non-English tweets
    tokens = [x.lower() for x in mytokeniser.tokenise(line) if x.isalpha()]

    bics = blendinterps.all_blend_interp_candidates(tokens, lexicon)
    if bics and langid.classify(line.encode('utf8'))[0] == 'en':
        for b in bics:
            url = "https://twitter.com/%s/status/%s" % (tweet['user']['screen_name'],tweet['id_str'])
            s = u"{}\t{}\t{}\t{}\t{}\t{}".format(b[0],b[1][0],b[1][1],
                                                 re_str,url,line.strip())
            print s
