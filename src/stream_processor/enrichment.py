import nltk
from nltk.corpus import wordnet

nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

def enrich(text: str):
    """
    Enrich the text by adding synonyms to key words.
    """
    words = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(words)
    
    enriched = []
    for word, tag in tagged:
        enriched.append(word)
        if tag.startswith('NN'):  # If the word is a noun
            synsets = wordnet.synsets(word)
            if synsets:
                synonyms = []
                for syn in synsets:
                    for lemma in syn.lemmas():
                        if lemma.name() != word:
                            synonyms.append(lemma.name())
                if synonyms:
                    enriched.append(f"(synonym: {synonyms[0]})")
    
    return ' '.join(enriched)
