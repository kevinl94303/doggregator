pip3 install -r ./requirements.txt
python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
python3 -m spacy download en_core_web_sm