
import pandas as pd
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer

from incidents.models import knowledge
from .initialization import Initialize

import nltk
import json
from pandas import ExcelWriter
import cython

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
            min_df=2, tokenizer=self.lemmatization, ngram_range=(1, 2))
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
        dtm_input = vect.transform(df_input_clean['machine_summary'])
        predictions = nb_clf.predict(dtm_input)
        df_output = df_input_clean
        df_output['Machine_Predicted_Label'] = predictions
        return df_output

    def save_output(self, df_output, filename):
        writer = pd.ExcelWriter(filename,  engine='xlsxwriter')
        df_output.to_excel(writer, 'Sheet1')
        writer.save()

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

    def get_prediction_stats(self, df_output, incident_id):
        all_stats = df_output.groupby('Machine_Predicted_Label').count()
        count_stats = all_stats[incident_id]
        return count_stats

    def get_predictions_probs_all(self, df_input_clean):
        nb_clf = self.classifier
        vect = self.vectorizer
        doc = list(df_input_clean['machine_summary'])
        doc_tf = vect.transform(doc)
        predictions = nb_clf.predict(doc_tf)
        df_input_clean['Machine_Predicted_Label'] = predictions
        predicted_probs = nb_clf.predict_proba(doc_tf)
        predicted_probs = [[round(float(i) * 100, 4) for i in nested_list]
                           for nested_list in predicted_probs]
        all_tags = nb_clf.classes_.tolist()
        tags_probs = [zip(all_tags, i) for i in predicted_probs]
        prediction_list = []
        for entry in tags_probs:
            sorted_pred_list = sorted(entry, key=lambda t: t[1], reverse=True)
            prediction_list.append(json.dumps(sorted_pred_list))

        df_input_clean['Machine_Predictions_Detail'] = prediction_list

        return df_input_clean

    def process_single_incident(self, df_input_clean, incid_col):
        rows_iterator = df_input_clean.iterrows()
        data_display, row_iter = self.fetch_next_row(rows_iterator, incid_col)
        return data_display, row_iter

    def fetch_next_row(self, rows_iterator, incid_col):
        next_row = next(rows_iterator)
        incid_column = next_row[1][incid_col]
        description = next_row[1]['machine_combined_desc']
        summary = next_row[1]['machine_summary']
        pred_prob_list = self.get_predictions_probs(summary)
        return [incid_column, description, summary, pred_prob_list], rows_iterator

    def enhance_knowledge(self, summary_text, pred_label):
        know_object = knowledge(summary=summary_text, label=pred_label)
        know_object.save()
