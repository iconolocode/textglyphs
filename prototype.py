import streamlit as st
import spacy
from spacy import displacy
from spacy.matcher import Matcher
from spacy.tokens import Span
from time import sleep


default_text = """      here is an example:
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

text = 'error: no entered text'

spacy_model = 'en_core_web_sm'

wrapper = """<div style="background: rgba(255, 255, 255, 0.3); op overflow-x: auto; border: 0px; border-radius: 0.5rem; padding-left: 3em">{}</div>"""
style = """<style>mark.entity { display: inline-block }</style>"""


def main():
    st.sidebar.title('Patterns in poetry tool')

    with st.sidebar.form(key='text_form'):
        with st.expander('text editor', expanded=True):
            text = st.text_area(label='enter a text to analyze :',
                                value=default_text, height=300,
                                help='you can copy paste a text here')
        st.form_submit_button(label='analyze',
                                    help='save the text in the box above')

    text = text.replace('      here is an example:', '')

    menu = ['\N{Jigsaw Puzzle Piece} parts of speech pattern view',
            '\N{Right-Pointing Magnifying Glass} parts of speech search filter',
            '\N{Busts in Silhouette} named entities recognition']

    st.sidebar.subheader('generate annotation')
    current = st.sidebar.radio('switch between filters', menu)

    if current == '\N{Jigsaw Puzzle Piece} parts of speech pattern view':
        opacity = opacity_ruler()

        display_pos(spacy_pos(text),
                    opacity=opacity,
                    pos_style='pattern')

    if current == '\N{Right-Pointing Magnifying Glass} parts of speech search filter':
        opacity = opacity_ruler()

        display_pos(spacy_pos(text),
                    opacity=opacity,
                    pos_style='search')

    elif current == '\N{Busts in Silhouette} named entities recognition':
        display_ner(spacy_ner(text))


@st.cache(allow_output_mutation=True)
def spacy_ner(text):
    ner = spacy.load(spacy_model)
    full_text = ner(text)
    verses = [ner(verse) for verse in text.split('\n')]
    return {'text': full_text, 'lines': verses}


def display_ner(spacy_text):

    for verse in spacy_text['lines']:
        html = displacy.render(
            verse,
            style="ent"
        )

        html = html.replace('\n', ' ')
        st.write(f'{style}{wrapper.format(html)}', unsafe_allow_html=True)

    st.title('')
    st.caption(
        f'     probability based annotations by spaCy model {spacy_model}')

    with st.expander('More information (click here to hide)', expanded=True):
        st.sidebar.info('This model extracts key information. It is trained mostly on'
                        'texts related to news, but also on conversations, weblogs,'
                        'religious texts.')

        st.sidebar.info('*Tips for interpretation:* Are the pieces of information'
                        'that are extracted important in the poem, or is their role'
                        'more of one of ornaments to add detail to a text?' '\n\n'
                        'If there are misclassifications, this could be due to the'
                        'model not being trained for poetry. But there could also be'
                        'other reasons that could have lead to this, such as the'
                        'sentence structure or lexical context. It may be interesting'
                        'to look at those, if they confuse the machine, what does'
                        'this mean for us?')


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


def display_pos(spacy_text, pos_style='pattern', opacity=10):

    alpha = str(opacity / 10)

    pos_colors = {
        'ADJ': 'hsla(330, 80%, 60%, ' + alpha + ')',
        'ADP': 'hsla(280, 80%, 70%, ' + alpha + ')',
        'ADV': 'hsla(310, 90%, 70%, ' + alpha + ')',
        'AUX': 'hsla(100, 60%, 70%, ' + alpha + ')',
        'VERB': 'hsla(120, 80%, 60%, ' + alpha + ')',
        'CONJ': 'hsla(14, 90%, 70%, ' + alpha + ')',
        'CCONJ': 'hsla(14, 90%, 70%, ' + alpha + ')',
        'SCONJ': 'hsla(14, 90%, 70%, ' + alpha + ')',
        'DET': 'hsla(330, 50%, 90%, ' + alpha + ')',
        'PART': 'hsla(350, 70%, 80%, ' + alpha + ')',
        'INTJ': 'hsla(50, 100%, 60%, ' + alpha + ')',
        'PROPN': 'hsla(220, 100%, 60%, ' + alpha + ')',
        'NOUN': 'hsla(190, 100%, 40%, ' + alpha + ')',
        'PRON': 'hsla(190, 70%, 70%, ' + alpha + ')',
        'SPACE': 'hsla(360, 0%, 20%, ' + alpha + ')',
        'NUM': 'hsla(360, 0%, 50%, ' + alpha + ')',
        'SYM': 'hsla(130, 20%, 30% ' + alpha + ')',
        'PUNCT': 'hsla(360, 20%, 30%, ' + alpha + ')',
        'X': 'hsla(360, 100%, 100%, ' + alpha + ')'
    }

    pos_cat = {
        'nouns and pronouns': ['PROPN', 'NOUN', 'PRON'],
        'verbs and auxiliaries': ['VERB', 'AUX'],
        'adjectives, adverbs and adposition': ['ADJ', 'ADV', 'ADP'],
        'conjuctions and particles': ['CONJ', 'ŚCONJ', 'CCONJ', 'PART'],
        'determiners': ['DET'],
        'interjections': ['INTJ'],
        'punctuaction and extra spaces': ['PUNCT', 'SPACE'],
        'numerals and special characters': ['NUM', 'SYM']
    }

    pos_pattern_styling = """<mark class="entity" style="background: {bg}; width: 65px; padding: 0.5em 0.4em; line-height: 1em; border-radius: 0.2em; box-decoration-break: clone; -webkit-box-decoration-break: clone">
    <span {text}, style="color: black; opacity: """ + str(1 - opacity/9)+"""">{label}</span></mark>"""

    pos_search_styling = """<mark class="entity" style="background: linear-gradient(90deg, transparent, {bg}); padding: 0.45em 0.6em; margin: 0 0.25em; line-height: 1em; border-radius: 0.8em; box-decoration-break: clone; -webkit-box-decoration-break: clone">
    <span style="font-weight: bold">{text}</span><span style="color: white">{label}</span></mark>"""

    pos_options = {"colors": pos_colors, 'template': pos_pattern_styling}

    if pos_style == 'search':
        search_bar = st.sidebar.multiselect('select the parts to focus on:',
                                            pos_cat, default='nouns and pronouns',
                                            help='TODO')
        search_options = []
        if len(search_bar) > 1:
            for option in search_bar:
                search_options += pos_cat[option]
        elif len(search_bar) == 1:
            search_options = pos_cat[search_bar[0]]
        else:
            search_options = ['']
            sleep(1)
            st.sidebar.error('unvalid selection')
            st.error('unvalid selection')

        pos_options.update({'template': pos_search_styling})
        pos_options.update({'ents': search_options})

    for verse in spacy_text['lines']:
        html = displacy.render(
            verse,
            style="ent",
            options=pos_options
        )

        html = html.replace('\n', ' ')
        st.write(f'{style}{wrapper.format(html)}', unsafe_allow_html=True)

    st.title('')
    st.caption(f'probability based annotations by spaCy model {spacy_model}')

    with st.expander('More information (click here to hide)', expanded=True):
        st.sidebar.info('*Tips for interpretation: TODO*')


def opacity_ruler():
    opacity = st.sidebar.slider('Annotation presence', 0, 10, 5,
                                help='You can make the annotations more vivid or discrete '
                                'to focus on them or to make them subtle when reading')
    return opacity


if __name__ == '__main__':
    main()
