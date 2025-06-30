import spacy
from nltk.tokenize import word_tokenize


_nlp_cache = {}

def get_spacy_model(lang_code):
    if lang_code not in _nlp_cache:
        _nlp_cache[lang_code] = spacy.blank(lang_code)
    return _nlp_cache[lang_code]


def tokenize_text(text, lang='en'):
    """Tokenize text using nltk for English or spaCy for other languages."""
    if lang == 'en':
        tokens = word_tokenize(text)
    else:
        nlp = get_spacy_model(lang)
        doc = nlp(text)
        tokens = [token.text for token in doc]
    return tokens


def lemmatize_text(text, lang='en'):
    """Return lemmas for a given text using spaCy."""
    nlp = get_spacy_model(lang)
    doc = nlp(text)
    return [token.lemma_ for token in doc]
