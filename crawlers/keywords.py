import spacy
import string
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import truecase

class KeywordExtractor:
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.stopwords = set(stopwords.words('english'))
        self.punct = set(string.punctuation + '’')
        self.translator = str.maketrans('', '', string.punctuation)

    def __call__(self, title: str, graf: str):
        return self.extract_keywords(title, graf)

    def remove_stopwords(self, phrase: str):
        new_phrase = []
        for word in phrase.split():
            if word not in self.stopwords | self.punct:
                word = word.translate(self.translator)
                new_phrase.append(word)
        
        if not new_phrase:
            return None
        else:
            return " ".join(new_phrase)

    def extract_keywords(self, title: str, graf: str):
        keywords = set([])
        location = None

        sents = [title] + sent_tokenize(graf)
        for sent in sents:
            doc = self.nlp(truecase.get_true_case(sent))
            for ent in doc.ents:
                if ent.label_ == "GPE" and not location:
                    location = ent.text
                phrase = self.remove_stopwords(ent.text.lower())
                if phrase:
                    keywords.add(phrase)
            for chunk in doc.noun_chunks:
                phrase = self.remove_stopwords(chunk.text.lower())
                if phrase:
                    keywords.add(phrase)
            
            if len(keywords) >= 10:
                break
            
        
        return keywords, location


# test
# extractor = KeywordExtractor()
# print(extractor("The state attorneys general in more than a dozen states are preparing to begin an antitrust investigation of the tech giants, according to two people briefed on the discussions, increasing pressure on the companies. The social media companies removed accounts and said they were sowing divisive messages about the Hong Kong protests."))