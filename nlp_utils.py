# import spacy
# from spacy.matcher import Matcher
# from spacy_wordnet.wordnet_annotator import WordnetAnnotator
# import random

# def replace_word(nlp, initial_text, word_to_replace, synonym):

#     matcher = Matcher(nlp.vocab)
#     matcher.add(word_to_replace, [[{"LOWER": word_to_replace}]])
    
#     tok = nlp(initial_text)
#     text = ''
#     buffer_start = 0
#     for _, match_start, _ in matcher(tok):
#         if match_start > buffer_start:
#             text += tok[buffer_start: match_start].text + tok[match_start - 1].whitespace_
#         text += synonym + tok[match_start].whitespace_
#         buffer_start = match_start + 1
#     text += tok[buffer_start:].text
#     return text

# def replace_random_tokens(nlp, text, num_items):
#     doc = nlp(text)
#     noun_adj_list = [token for token in doc if token.pos_ in ['NOUN', 'ADJ', 'VERB']]

#     num_noun_adjs = len(noun_adj_list)
#     if num_items > num_noun_adjs:
#         num_items = num_noun_adjs

#     random_noun_adjs = random.sample(noun_adj_list, num_items)

#     for token_to_replace in random_noun_adjs:
#         # select random synset from list of synsets
#         synsets = token_to_replace._.wordnet.synsets()

#         # if word has synonyms, replace
#         if synsets:
#             synonyms = random.choice(synsets).lemma_names()
            
#             # select random synonym from synset list
#             synonym = random.choice(synonyms[1:]) if len(synonyms) > 1 else synonyms[0]
#             synonym = synonym.replace('_', ' ')
#             # synonyms[1] if len(synonyms) > 1 else synonyms[0]
            
#             word_to_replace = str(token_to_replace)
#             text = replace_word(nlp, text, word_to_replace, synonym)

#     return text
