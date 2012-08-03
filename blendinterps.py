import nltk, re, sys
stemmer = nltk.stem.PorterStemmer()

def longest_common_prefix(w1, w2):
    x = 0
    while x < len(w1) and x < len(w2) and w1[x] == w2[x]:
        x += 1
    return w1[:x]


def longest_common_suffix(w1, w2):
    # Reverse w1 and w2 to find LCS using LCP
    w1 = ''.join(list(reversed(w1)))
    w2 = ''.join(list(reversed(w2)))
    lcp = longest_common_prefix(w1, w2)
    lcp = ''.join(list(reversed(lcp)))
    return lcp


def has_compound_interp(word, lexicon):
    # Return True if word has a compound interpretation based on the
    # words in lexicon, and False otherwise
    for i in range(2,len(word)-2):
        a,b = word[:i],word[i:]
        if a in lexicon and b in lexicon:
            return True
    return False

# For nox suffixes are common inflectional suffixes for nouns and verbs
suffixes = ['s', 'ed', 'ing', 'en', 'ed']
def is_morpho_suffix(s):
    return s in suffixes

def has_many_repeated_chars(word):
    # Return True if word has a sequence of more than 3 consecutive
    # identical letters and False otherwise
    return re.search("([a-zA-Z])\\1{3,}", word)


def blend_interp_candidates(word, context_tokens):
    # Find candidate blend interpretations for word in context

    # We only want to consider cases where the target word actually occurs
    # in the context.  (This wouldn't happen if we were looking at data from
    # a corpus, but when using snippets from a search engine, sometimes the
    # search term isn't in the snippet...)
    if not word in context_tokens:
        return set()
    
    # Restrictions on candidate blends: 
    #
    # 1. Candidate blend must not have many repeated characters (Han
    #    and Baldwin use this heuristic in normalization; such words
    #    are probably non-standard forms.)
    #
    # 2. Candidate blend must be at least 6 characters long (Short
    #    words are more likely to have a blend interpretation and then
    #    the number of candidates goes up a lot.)
    #
    if has_many_repeated_chars(word) or len(word) <= 5:
        return set()

    word_stem = stemmer.stem_word(word)

    # Find candidate w1s and w2s
    # Restrictions: 
    #
    # 1. Candidate words must be all alphabetical (We want to find
    #    candidates that look like words, not non-standard forms
    #    involving digits or punctuation)
    #
    # 2. Candidate words must not be the target word (Blends combine
    #    two words to for a NEW word)
    #
    # 3. Candidate w1s must start with first 2 letters of target word
    #    (Heuristic used by Cook and Stevenson to prevent the number
    #    of candidates from becoming too large)
    #
    # 4. Candidate w2s must end with last 2 letters of target word
    #    (Same motivation as 3.)
    #
    # 5. Target word must not be a substring of w1 or w2 (There must
    #    be orthographic material in the blend that is not already in
    #    one of the source words.)
    #
    # 6. Target word or target word stem cannot be identical to
    #    candidate word or candidate word stem (The target word should
    #    not be morpholagically derivable from a source word.  Note
    #    that there are 4 cases---target word==candidate word, target
    #    stem==candidate word, target word==candidate stem, target
    #    stem==candidate stem---and that the first case does not
    #    involve stems and is covered by 2.)
    # 
    # 7. Candidate sws must not have many repeated characters (Similar
    #    to 1. from previous set of restrictions; if a candidate
    #    source word is an "ill-formed word" then it is unlikely to be
    #    a source word for a blend.  This could be problematic.  It is
    #    possible that an ill-formed word is being used as the source
    #    word for a blend, but this certainly doesn't seem to be
    #    common.
    #
    other_words = [x for x in context_tokens if \
                       # 1.
                   x.isalpha()\
                       # 2.
                   and not x == word \
                       # 6.
                   and not x == word_stem and not stemmer.stem_word(x) == word\
                       and not stemmer.stem_word(x) == word_stem  \
                       # 7.
                   and not has_many_repeated_chars(x)]

    # 3., 4.
    w1s = set([x for x in other_words if \
                   x.startswith(word[:2]) and not word in x])
    # 4., 5.
    w2s = set([x for x in other_words if \
                   x.endswith(word[-2:]) and not word in x])
    
    # Further restrictions:
    # 
    # 1. Common prefix of candidate w1 and target and common suffix of
    #    w2 and target must together be at least as long as the target
    #    word (All of the orthographic material in a candidate blend
    #    must be present in the source words.)
    #    
    #    Could relax this a bit to allow for blends like donkofant
    #    (donkey + elephant).  Maybe some heuristic like X% of the
    #    characters in the candidate blend must also appear in the
    #    sws...
    #
    # 2. A candidate w1 and w2 when concatenated cannot be the target
    #    word (This rule prevents compounds from being identified.
    #    Blends are not compounds.)
    #
    # 3. Candidate w1 and w2 must not be the same word.  (Blends
    #    combine two different source words.)
    # 
    # 4. w1 must not be a prefix of w2; w2 must not be a suffix of w1.
    #
    # 5. Suffix that w2 contributes must not be a common verbal or
    #    nominal inflectional suffix. (We don't want w2 to contribute
    #    something like 'ing' because this tends to find blend
    #    candidates like blogging = blogged + starting
    #
    candidate_pairs = []
    for w1 in w1s:
        lcp_w1_word = longest_common_prefix(w1, word)
        for w2 in w2s:
            lcs_w2_word = longest_common_suffix(w2, word)
            # 5.
            if is_morpho_suffix(lcs_w2_word):
                continue
            # 1., 2., 3
            if len(lcp_w1_word) + len(lcs_w2_word) >= len(word) \
                    and not w1 + w2 == word and not w1 == w2 \
                    and not w2.startswith(w1) and not w1.endswith(w2): # 4.
                candidate_pairs.append((w1,w2))
    return set(candidate_pairs)


def all_blend_interp_candidates(context_tokens, lexicon):
    # Return candidate blend interpretations for all out-of-vocabulary
    # (according to lexicon) words in context_tokens

    all_bics = set()
    oovs = [c for c in context_tokens if not c in lexicon]
    for o in oovs:
        bics = blend_interp_candidates(o, context_tokens)
        for b in bics:
            all_bics.add((o,b))
    return all_bics

