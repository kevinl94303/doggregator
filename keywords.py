import spacy
import string
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords

class KeywordExtractor():
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.stopwords = set(stopwords.words('english'))
        self.punct = set(string.punctuation)

    def __call__(self, graf: str):
        return self.extract_keywords(graf)

    def remove_stopwords(self, phrase: str):
        new_phrase = []
        for word in phrase.split():
            if word not in self.stopwords | self.punct:
                new_phrase.append(word)
        
        if not new_phrase:
            return None
        else:
            return " ".join(new_phrase)

    def extract_keywords(self, graf: str):
        keywords = []

        sents = sent_tokenize(graf)
        for sent in sents:
            doc = self.nlp(sent)
            for ent in doc.ents:
                phrase = self.remove_stopwords(ent.text.lower())
                if phrase:
                    keywords.append(phrase)
            for chunk in doc.noun_chunks:
                phrase = self.remove_stopwords(chunk.text.lower())
                if phrase:
                    keywords.append(phrase)
        
        return keywords


# test
extractor = KeywordExtractor()
print(extractor("The state attorneys general in more than a dozen states are preparing to begin an antitrust investigation of the tech giants, according to two people briefed on the discussions, increasing pressure on the companies. The social media companies removed accounts and said they were sowing divisive messages about the Hong Kong protests."))