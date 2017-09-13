
import pandas as pd
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer

from incidents.models import knowledge
from .initialization import Initialize

import nltk


class Learner:
    classifier = None
    vectorizer = None

    def __init__(self):
        initialize = Initialize()
        self.knowledge_df = initialize.load_knowledge()

    # Construct a Document Term Matrix of Clean Data
    def lemmatization(self, text):
        std_tokenizer = CountVectorizer().build_tokenizer()
        tokens = std_tokenizer(text)
        lemmatizer = nltk.stem.WordNetLemmatizer()
        lemma_tokens = []
        for token in tokens:
            lemma_tokens.append(lemmatizer.lemmatize(token))
        return lemma_tokens

    def construct_dtm(self, df_clean):
        incident_desc = df_clean['summary']
        vectorizer = CountVectorizer(
            min_df=1, tokenizer=self.lemmatization, ngram_range=(1, 2))
        tf_dtm = vectorizer.fit_transform(incident_desc)
        self.vectorizer = vectorizer
        return tf_dtm

    # Get Knowledge_df and input_dtm from Main file
    def activate_classifier(self):
        knowledge_dtm = self.construct_dtm(self.knowledge_df)
        nb_clf = MultinomialNB().fit(knowledge_dtm, self.knowledge_df['label'])
        self.classifier = nb_clf

    # Get the Final predicted Labeled Dataframe
    # Can be used for Calculating Classifier Accuracy
    # Used for Unseen Inputs
    def predict_labels(self, df_input_clean):
        nb_clf = self.classifier
        vect = self.vectorizer
        dtm_input = vect.transform(df_input_clean['summary'])
        predictions = nb_clf.predict(dtm_input)
        df_output = df_input_clean
        df_output['Predicted'] = predictions
        return df_output

    def save_output(self, df_output, filename, id_col):
        cols = [id_col, 'Predicted']
        df_output.to_csv('output/' + filename, encoding='utf-8', columns=cols)

    # Process individual Incident for Training the Classifier

    def get_predictions_probs(self, inc_summary):
        nb_clf = self.classifier
        vect = self.vectorizer
        doc = [inc_summary]
        doc_tf = vect.transform(doc)
        predicted_probs = nb_clf.predict_proba(doc_tf)
        all_tags = nb_clf.classes_.tolist()
        tags_probs = [zip(all_tags, i) for i in predicted_probs]
        for entry in tags_probs:
            sorted_pred_list = sorted(entry, key=lambda t: t[1], reverse=True)
        return sorted_pred_list

    def process_single_incident(self, df_input_clean, incid_col):
        rows_iterator = df_input_clean.iterrows()
        data_display, row_iter = self.fetch_next_row(rows_iterator, incid_col)
        return data_display, row_iter

    def fetch_next_row(self, rows_iterator, incid_col):
        next_row = next(rows_iterator)
        incid_column = next_row[1][incid_col]
        description = next_row[1]['combined_desc']
        summary = next_row[1]['summary']
        pred_prob_list = self.get_predictions_probs(summary)
        return [incid_column ,description, summary, pred_prob_list], rows_iterator

    def enhance_knowledge(self, summary_text, pred_label):
        know_object = knowledge(summary=summary_text, label=pred_label)
        know_object.save()
