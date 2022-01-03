import streamlit as st
import spacy
from spacy import displacy
from spacy.displacy.templates import TPL_ENT as default_template
from spacy.matcher import Matcher
from spacy.tokens import Span
from time import sleep

spacy_model = 'en_core_web_sm'

wrapper = """<div style="background: rgba(255, 255, 255, 0.3); op overflow-x: auto; border: 0px; border-radius: 0.7rem; padding-left: 3em">{}</div>"""
style = """<style>mark.entity { display: inline-block }</style>"""

if 'text' not in st.session_state:
    st.session_state.text = ('      here is an example:\n'
                            'A Drop Fell on the Apple Tree - \n'
                            'Another -  on the Roof - \n'
                            'A Half a Dozen kissed the Eaves - \n'
                            'And made the Gables laugh - \n'
                            '\n'
                            'A few went out to help the Brook\n'
                            'That went to help the Sea - \n'
                            'Myself Conjectured were they Pearls - \n'
                            'What Necklace could be - \n'
                            '\n'
                            'The Dust replaced, in Hoisted Roads - \n'
                            'The Birds jocoser sung - \n'
                            'The Sunshine threw his Hat away - \n'
                            'The Bushes -  spangles flung - \n'
                            '\n'
                            'The Breezes brought dejected Lutes - \n'
                            'And bathed them in the Glee - \n'
                            'Then Orient showed a single Flag,\n'
                            'And signed the Fete away - ')

def meta_data():
    st.set_page_config(
     page_title='Poetry Patterns',
     page_icon=':scroll:',
     layout='wide',
     initial_sidebar_state='expanded',
     menu_items={
         'Get Help': 'https://www.extremelycoolapp.com/help',
         'Report a bug': 'https://twitter.com/iconolocode',
         'About': 'TODO: add abstract here'
     }
 )

def main():
    meta_data()


    menu = ['home',
            '\N{Jigsaw Puzzle Piece} part of speech pattern view',
            '\N{Right-Pointing Magnifying Glass} part of speech search filter',
            '\N{Busts in Silhouette} named entities recognition',
            'plain text']

    
    st.sidebar.subheader('Generate annotations')
    current = st.sidebar.radio('Switch between filters', menu)

    if current == 'home':
        home()

    elif current == '\N{Jigsaw Puzzle Piece} part of speech pattern view':
        opacity = opacity_ruler()

        display_pos(spacy_pos(st.session_state.text),
                    opacity=opacity,
                    pos_style='pattern')

    elif current == '\N{Right-Pointing Magnifying Glass} part of speech search filter':
        opacity = opacity_ruler()

        display_pos(spacy_pos(st.session_state.text),
                    opacity=opacity,
                    pos_style='search')

    elif current == '\N{Busts in Silhouette} named entities recognition':
        display_ner(spacy_ner(st.session_state.text))
        
    else: 
        st.markdown(st.session_state.text.replace('\n\n', '\n---\n'
                                                  ).replace('\n', '\n\n'))

def home():
    st.title('Patterns in poetry tool')
    

    with st.form(key='text_form'):
        #with st.expander('Text editor', expanded=True):
        st.session_state.text = st.text_area(label='Enter a text to analyze:',
                            value=st.session_state.text, height=300,
                            help='You can copy paste a text here '
                                'and collapse this box.')
        st.form_submit_button(label='Analyze',
                              help='Save the text in the box above.')

    st.session_state.text = st.session_state.text.replace('      here is an example:', '')


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
            style="ent",
            options={'template': default_template.replace('border-radius: 0.35',
                                                          'border-radius: 0.8')}
        )

        html = html.replace('\n', ' ')
        st.write(f'{style}{wrapper.format(html)}', unsafe_allow_html=True)

    st.title('')
    st.caption(
        f'     Probability based annotations by spaCy model {spacy_model}')

    with st.expander('More information (click here to hide)', expanded=True):
        st.sidebar.info('This model extracts key information. It is trained mostly on'
                        'texts related to news, but also on conversations, weblogs,'
                        'religious texts.')

        st.sidebar.info('*Tips for interpretation:* Are the pieces of information '
                        'that are extracted important in the poem, or is their role '
                        'more of one of ornaments to add detail to a text?' '\n\n'
                        'If there are misclassifications, this could be due to the '
                        'model not being trained for poetry. But there could also be '
                        'other reasons that could have lead to this, such as the '
                        'sentence structure or lexical context. It may be interesting '
                        'to look at those, if they confuse the machine, what does '
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
            
    matches = matcher(full_text)
    for id, start, end in matches:
        new_ent = Span(full_text, start, end, label=id)
        full_text.ents = list(full_text.ents) + [new_ent]

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

    pos_pattern_styling = """<mark class="entity" style="background: {bg}; width: 65px; padding: 0.5em 0.4em; line-height: 1em; border-radius: 0.2em; box-decoration-break: clone; -webkit-box-decoration-break: clone">
    <span {text}, style="color: black; opacity: """ + str(1 - opacity/9)+"""">{label}</span></mark>"""

    pos_options = {"colors": pos_colors, 'template': pos_pattern_styling}

    if pos_style == 'search':
        pos_cat = {
            'nouns and pronouns': ['PROPN', 'NOUN', 'PRON'],
            'verbs and auxiliaries': ['VERB', 'AUX'],
            'adjectives, adverbs and adposition': ['ADJ', 'ADV', 'ADP'],
            'conjuctions and particles': ['CONJ', 'SCONJ', 'CCONJ', 'PART'],
            'determiners': ['DET'],
            'interjections': ['INTJ'],
            'punctuaction and extra spaces': ['PUNCT', 'SPACE'],
            'numerals and special characters': ['NUM', 'SYM']
            }
        
        search_bar = st.sidebar.selectbox('Select the parts to focus on:',
                                            options=pos_cat, index=0,
                                            format_func=lambda option: option +
                                            ' ' + str(sum([1 for ent
                                                in spacy_text['text'].ents
                                            if ent.label_ in pos_cat[option]])),
                                            help='TODO')

        if opacity >= 5:
            label_type = '{label}'
        elif opacity < 3:
            label_type = ''
        else:
            label_type = '{label[0]}'
    
        pos_search_styling = """<mark class="entity" style="background: linear-gradient(90deg, transparent """+str(100 - opacity*15)+"""%, {bg}); padding: 0.5em 0.4em; margin: 0 0.25em; line-height: 1em; border-radius: 0.2em; box-decoration-break: clone; -webkit-box-decoration-break: clone">
        <span style="font-weight: bold;">{text}</span><span style="font-size: """+str(0.5 + opacity/10/2)+"""em; font-family: sans-serif; color: white; margin-left: """+str(opacity/10/2)+"""rem;">"""+label_type+"""</span></mark>"""
            
        pos_options.update({'template': pos_search_styling})
        pos_options.update({'ents': pos_cat[search_bar]})

    for verse in spacy_text['lines']:
        html = displacy.render(
            verse,
            style="ent",
            options=pos_options
        )

        html = html.replace('\n', ' ')
        st.write(f'{style}{wrapper.format(html)}', unsafe_allow_html=True)

    st.title('')
    st.caption(f'Probability based annotations by spaCy model {spacy_model}')

    with st.expander('More information (click here to hide)', expanded=True):
        st.sidebar.info('*Tips for interpretation: TODO*')


def opacity_ruler():
    opacity = st.sidebar.slider('Annotation presence', 0, 10, 5,
                                help='You can make the annotations more vivid or discrete '
                                ' to focus on them or to make them subtle when reading')
    return opacity


if __name__ == '__main__':
    main()
