import streamlit as st
import spacy
from spacy import displacy
from spacy.matcher import Matcher
from spacy.tokens import Span


DEFAULT_TEXT = """      here is an example:
A Drop Fell on the Apple Tree - 
Another -  on the Roof - 
A Half a Dozen kissed the Eaves - 
And made the Gables laugh - 

A few went out to help the Brook
That went to help the Sea - 
Myself Conjectured were they Pearls - 
What Necklace could be - 

The Dust replaced, in Hoisted Roads - 
The Birds jocoser sung - 
The Sunshine threw his Hat away - 
The Bushes -  spangles flung - 

The Breezes brought dejected Lutes - 
And bathed them in the Glee - 
Then Orient showed a single Flag,
And signed the Fete away - """

spacy_model = 'en_core_web_sm'


st.title('Patterns in poetry')


#initialization
with st.form(key='text_form'):
    st.header('Input text')
    text = st.text_area(label='enter a text to analyze :',
                        value=DEFAULT_TEXT, height=400,
                        help='you can copy paste a text here')
    submit_button = st.form_submit_button(label='analyze',
                                help='click to pass the text to the analyzer')

text = text.replace('      here is an example:', '')


@st.cache(allow_output_mutation=True)
def spacy_ner(text):
    ner = spacy.load(spacy_model)
    full_text = ner(text)
    verses = [ner(verse) for verse in text.split('\n')]
    return {'text': full_text, 'lines': verses}

def display_ner(spacy_text):
    st.header('Named entities analysis')
    
    #labels = labels or [ent.label_ for ent in doc.ents]
    
    for verse in spacy_text['lines']:
        html = displacy.render(
            verse,
            style="ent"
            #options={"ents": label_select, "colors": colors},
        )
        #displacy.render(verse, style='ent')
        wrapper = """<div style="background: rgba(255, 255, 255, 0.3); op overflow-x: auto; border: 0px; border-radius: 0.25rem; padding-left: 3em">{}</div>"""
        style = """<style>mark.entity { display: inline-block }</style>"""
        html = html.replace('\n', ' ')
        st.write(f'{style}{wrapper.format(html)}', unsafe_allow_html=True)
    
    st.text(f"Analyzed using spaCy model {spacy_model}")
    
    with st.expander('More information (click here to hide)', expanded=True):
        st.info('This model extracts key information. It is trained mostly on'
                'texts related to news, but also on conversations, weblogs,'
                'religious texts.')
            
        st.info('*Tips for interpretation:* Are the pieces of information'
                'that are extracted important in the poem, or is their role'
                'more of one of ornaments to add detail to a text?' '\n\n'
                'If there are misclassifications, this could be due to the'
                'model not being trained for poetry. But there could also be'
                'other reasons that could have lead to this, such as the'
                'sentence structure or lexical context. It may be interesting'
                'to look at those, if they confuse the machine, what does'
                'this mean for us?')
    
display_ner(spacy_ner(text))

@st.cache(allow_output_mutation=True)
def spacy_pos(text):
    pos = spacy.load(spacy_model, disable=["ner"])
    full_text = pos(text)
    verses = [pos(verse) for verse in text.split('\n')]
    
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
    
    matcher = Matcher(pos.vocab)
    for pattern in patterns:
        matcher.add(key=pattern[0]['POS'], patterns=[pattern])
    
    for verse in verses:
        matches = matcher(verse)
        for id, start, end in matches:
            new_ent = Span(verse, start, end, label=id)
            verse.ents = list(verse.ents) + [new_ent]
    
    return {'text': full_text, 'lines': verses}    
    

def display_pos(spacy_text, opacity = 10):
    st.header('Part Of Speech analysis')
    
    alpha = str(opacity / 10)
    
    pos_colors = {'ADJ': 'hsla(330, 80%, 60%, '+ alpha +')',
            'ADP': 'hsla(280, 80%, 70%, '+ alpha +')',
            'ADV': 'hsla(310, 90%, 70%, '+ alpha +')',

            'AUX': 'hsla(100, 60%, 70%, '+ alpha +')',
            'VERB': 'hsla(120, 80%, 60%, '+ alpha +')',

            'CONJ': 'hsla(14, 90%, 70%, '+ alpha +')',
            'CCONJ': 'hsla(14, 90%, 70%, '+ alpha +')',
            'SCONJ': 'hsla(14, 90%, 70%, '+ alpha +')',

            'DET': 'hsla(330, 50%, 90%, '+ alpha +')',
            'PART': 'hsla(350, 70%, 80%, '+ alpha +')',
            'INTJ': 'hsla(50, 100%, 60%, '+ alpha +')',

            'PROPN': 'hsla(220, 100%, 60%, '+ alpha +')',
            'NOUN': 'hsla(190, 100%, 40%, '+ alpha +')',
            'PRON': 'hsla(190, 70%, 70%, '+ alpha +')',

            'SPACE': 'hsla(360, 0%, 20%, '+ alpha +')',
            'NUM': 'hsla(360, 0%, 50%, '+ alpha +')',
            'SYM': 'hsla(130, 20%, 30% '+ alpha +')',
            'PUNCT': 'hsla(360, 20%, 30%, '+ alpha +')',

            'X': 'hsla(360, 100%, 100%, '+ alpha +')'
            }
    
    pos_styling = """<mark class="entity" style="background: {bg}; padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1em; border-radius: 0.35em; box-decoration-break: clone; -webkit-box-decoration-break: clone">
    <span {text}, style="color: white">{label}</span></mark>"""
    
    #labels = labels or [ent.label_ for ent in doc.ents]
    
    for verse in spacy_text['lines']:
        html = displacy.render(
            verse,
            style="ent",
            options={"colors": pos_colors, 'template': pos_styling},
        )
        
        wrapper = """<div style="background: rgba(255, 255, 255, 0.3); op overflow-x: auto; border: 0px; border-radius: 0.25rem; padding-left: 3em">{}</div>"""
        style = """<style>mark.entity { display: inline-block }</style>"""
        html = html.replace('\n', ' ')
        st.write(f'{style}{wrapper.format(html)}', unsafe_allow_html=True)
    
    st.text(f"Analyzed using spaCy model {spacy_model}")
    
    with st.expander('More information (click here to hide)', expanded=True):
        st.info('*Tips for interpretation: TODO*')

opacity = st.slider('Annotation presence', 0, 10, 5,
                    help='You can make the annotations more vivid or discrete'
                    ' to focus on them or to make them subtle when reading')

display_pos(spacy_pos(text),
            opacity=opacity)






    