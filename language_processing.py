import streamlit as st
import spacy
from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Span
from spacytextblob.spacytextblob import SpacyTextBlob

detect_model = 'en_core_web_sm'

@st.cache(allow_output_mutation=True)
def detect_ner(text):
    ner_nlp = spacy.load(detect_model)
    full_text = ner_nlp(text)
    verses = [ner_nlp(verse) for verse in text.split('\n')]
    return {'text': full_text, 'lines': verses}


@st.cache(allow_output_mutation=True)
def detect_pos(text):
    pos_nlp = spacy.load(detect_model, disable=["ner"])
    full_text = pos_nlp(text)
    verses = [pos_nlp(verse) for verse in text.split('\n')]

    patterns = [
        [{'POS': 'ADJ'}],
        [{'POS': 'ADP'}],
        [{'POS': 'ADV'}],
        [{'POS': 'AUX'}],
        [{'POS': 'CONJ'}],
        [{'POS': 'DET'}],
        [{'POS': 'INTJ'}],
        [{'POS': 'NOUN'}],
        [{'POS': 'NUM'}],
        [{'POS': 'PART'}],
        [{'POS': 'PRON'}],
        [{'POS': 'PROPN'}],
        [{'POS': 'PUNCT'}],
        [{'POS': 'SYM'}],
        [{'POS': 'VERB'}],
        [{'POS': 'X'}],
        [{'POS': 'SPACE'}],
        [{'POS': 'CCONJ'}],
        [{'POS': 'SCONJ'}]
    ]

    matcher = Matcher(pos_nlp.vocab)
    for pattern in patterns:
        matcher.add(key=pattern[0]['POS'], patterns=[pattern])

    for verse in verses:
        matches = matcher(verse)
        for id, start, end in matches:
            new_ent = Span(verse, start, end, label=id)
            verse.ents = list(verse.ents) + [new_ent]
            
    matches = matcher(full_text)
    for id, start, end in matches:
        new_ent = Span(full_text, start, end, label=id)
        full_text.ents = list(full_text.ents) + [new_ent]

    return {'text': full_text, 'lines': verses}


@st.cache(allow_output_mutation=True)        
def detect_quantity(text):
    
    quantity_nlp = spacy.load(detect_model, disable=["ner"])
    full_text = quantity_nlp(text)
    verses = [quantity_nlp(verse) for verse in text.split('\n')]

    matcher = Matcher(quantity_nlp.vocab)
    
    for token in full_text:
        number = token.morph.get("Number")
        
        if number:
            label = number[0].upper()
            matcher.add(label, patterns=[[{'MORPH': str(token.morph)}]])
    
        
    for verse in verses:
        matches = matcher(verse)
        for match_id, start, end in matches:
            new_ent = Span(verse, start, end, label=match_id)
            verse.ents = list(verse.ents) + [new_ent]
            

    return {'text': full_text, 'lines': verses}


@st.cache(allow_output_mutation=True)        
def detect_persons(text):
    
    persons_nlp = spacy.load(detect_model, disable=["ner"])
    full_text = persons_nlp(text)
    verses = [persons_nlp(verse) for verse in text.split('\n')]

    matcher = Matcher(persons_nlp.vocab)
    
    text_to_num = {'first': '1', 'second': '2', 'third': '3',
                   'one': '1', 'two': '2', 'three': '3'}
    
    for token in full_text:
        person = token.morph.get('Person')
        number = token.morph.get('Number')
        
        if person and person[0].isalpha():
            person = [text_to_num[person[0].lower()]]
            

        if not person == []:
            label = ' '.join(person + number).upper()
            matcher.add(label, patterns=[[{'MORPH': str(token.morph)}]])
        
        
    for verse in verses:
        matches = matcher(verse)
        for match_id, start, end in matches:
            new_ent = Span(verse, start, end, label=match_id)
            verse.ents = list(verse.ents) + [new_ent]
            

    return {'text': full_text, 'lines': verses}


@st.cache(allow_output_mutation=True)
def detect_tenses(text):
    
    tenses_nlp = spacy.load(detect_model, disable=["ner"])
    full_text = tenses_nlp(text)
    verses = [tenses_nlp(verse) for verse in text.split('\n')]

    matcher = Matcher(tenses_nlp.vocab)
    
    for token in full_text:
        if token.pos_ == 'VERB':
            tense = token.morph.get("Tense")
            if tense:
                label = tense[0].upper()
                if label == 'PRES':
                    label = 'PRESENT'
                matcher.add(label, patterns=[[{'MORPH': str(token.morph)}]])
            else:
                matcher.add('OTHER', patterns=[[{'MORPH': str(token.morph)}]])
    
    for verse in verses:
        matches = matcher(verse)
        for match_id, start, end in matches:
            new_ent = Span(verse, start, end, label=match_id)
            verse.ents = list(verse.ents) + [new_ent]
            

    return {'text': full_text, 'lines': verses}


@st.cache(allow_output_mutation=True)        
def detect_sentiments(text):
    
    sentiments_nlp = spacy.load(detect_model, disable=["ner"])
    sentiments_nlp.add_pipe('spacytextblob')
    full_text = sentiments_nlp(text)
    verses = [sentiments_nlp(verse) for verse in text.split('\n')]

    matcher = Matcher(sentiments_nlp.vocab)
    
    for token in full_text:
        if token._.polarity != 0:
            label = str(round(token._.polarity, 1))
            matcher.add(key=label, patterns=[[{'TEXT': token.text}]])
        
    for verse in verses:
        matches = matcher(verse)
        for match_id, start, end in matches:
            new_ent = Span(verse, start, end, label=match_id)
            verse.ents = list(verse.ents) + [new_ent]

    return {'text': full_text, 'lines': verses}


@st.cache(allow_output_mutation=True)        
def detect_subjectivity(text):
    
    subjectivity_nlp = spacy.load(detect_model, disable=["ner"])
    subjectivity_nlp.add_pipe('spacytextblob')
    full_text = subjectivity_nlp(text)
    verses = [subjectivity_nlp(verse) for verse in text.split('\n')]

    matcher = PhraseMatcher(subjectivity_nlp.vocab)
    
    for line in full_text.sents:
        if line._.subjectivity:
            score = line._.subjectivity
            label = str(round(score, 1))
            text = line.text.replace('\n', '')
            matcher.add(key=label, docs=[subjectivity_nlp(text)])
        
        
    for verse in verses:
        matches = matcher(verse)
        for match_id, start, end in matches:
            new_ent = Span(verse, start, end, label=match_id)
            verse.ents = list(verse.ents) + [new_ent]

    return {'text': full_text, 'lines': verses}

