import streamlit as st
import spacy
from spacy import displacy
from spacy.displacy.templates import TPL_ENT as default_template
from spacy.matcher import Matcher, PhraseMatcher
from spacy.tokens import Span
import subprocess
from spacytextblob.spacytextblob import SpacyTextBlob

spacy_model = 'en_core_web_sm'

if 'textblob' not in st.session_state:
    subprocess.run(['python3', '-m', 'textblob.download_corpora'])
    st.session_state.textblob = True

wrapper = """<div style="background: rgba(255, 255, 255, 0.3); op overflow-x: auto; border: 0px; border-radius: 0.7rem; padding-left: 3em">{}</div>"""
style = """<style>mark.entity { display: inline-block }</style>"""

if 'text' not in st.session_state:
    st.session_state.text = ('A Drop Fell on the Apple Tree - \n'
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
            '\N{Hourglass with Flowing Sand} tenses',
            'quantities',
            'persons',
            'sentiments',
            'subjectivity', 
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
        opacity = opacity_ruler(3, 2)
        
        display_ner(spacy_ner(st.session_state.text), opacity)
        
    elif current == '\N{Hourglass with Flowing Sand} tenses':
        opacity = opacity_ruler(3, 2)
        
        display_tenses(spacy_tenses(st.session_state.text), opacity)
        
    elif current == 'quantities':
        opacity = opacity_ruler()

        display_quantity(spacy_quantity(st.session_state.text),
                    opacity=opacity)
        
    elif current == 'persons':
        opacity = opacity_ruler()

        display_persons(spacy_persons(st.session_state.text),
                    opacity=opacity)
        
    elif current == 'sentiments':
        opacity = opacity_ruler()

        display_sentiments(spacy_sentiments(st.session_state.text),
                    opacity=opacity)
        
    elif current == 'subjectivity':
        opacity = opacity_ruler()
        
        display_subjectivity(spacy_subjectivity(st.session_state.text),
                    opacity=opacity)
        
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


@st.cache(allow_output_mutation=True)
def spacy_ner(text):
    ner_nlp = spacy.load(spacy_model)
    full_text = ner_nlp(text)
    verses = [ner_nlp(verse) for verse in text.split('\n')]
    return {'text': full_text, 'lines': verses}


def display_ner(spacy_text, opacity):
    template = default_template.replace('border-radius',
                    'border:0.1rem solid hsla(0, 0%, 0%, 0.2); border-radius')
    
    if opacity == 2:
        template = template.replace('background: {bg}', 'background: transparent').replace(
            'font-weight: bold', 'background: {bg}; font-family: sans-serif')
    
    elif opacity < 3:
        template = template.replace('background: {bg}', 'background: transparent').replace(
            'font-weight: bold', 'font-family: sans-serif')
    
    if opacity == 0:
        template = template[:template.find('<span style=')] + '</mark>'
    
    
    for verse in spacy_text['lines']:
        html = displacy.render(
            verse,
            style='ent',
            options={'template': template}
            )

        html = html.replace('\n', ' ')
        st.write(f'{style}{wrapper.format(html)}', unsafe_allow_html=True)

    st.title('')
    st.caption(
        f'     Probability based annotations by spaCy model {spacy_model}')

    with st.sidebar.expander('More information (click here to hide)', expanded=True):
        st.info('This model extracts key information. It is trained mostly on'
                        'texts related to news, but also on conversations, weblogs,'
                        'religious texts.')

        st.info('*Tips for interpretation:* Are the pieces of information '
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
    pos_nlp = spacy.load(spacy_model, disable=["ner"])
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
        'DET': 'hsla(330, 35%, 80%, ' + alpha + ')',
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
        pos_categories = {
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
                                            options=pos_categories,
                                            format_func=lambda option: option +
                                            ' ' + str(sum([1 for pos
                                                in spacy_text['text'].ents
                                            if pos.label_ in pos_categories[option]])),
                                            help='TODO')
        
        pos_selection = pos_categories[search_bar]
        
        if sum([1 for pos in spacy_text['text'].ents if pos.label_
                in pos_categories[search_bar]]) == 0:
            st.sidebar.warning('unvalid selection, no text to annotate found')
        
        if st.sidebar.checkbox('advanced selection:', help='TODO'):
            all_pos = set([pos.label_ for pos in spacy_text['text'].ents])
            extra_bar = st.sidebar.multiselect('Select the parts to focus on:',
                        all_pos,
                        default=list(set(pos_categories[search_bar])
                                     .intersection(all_pos)),
                        help='TODO')

            pos_selection = extra_bar
        
        
        if opacity >= 5:
            label_type = '{label}'
        elif opacity < 3:
            label_type = ''
        else:
            label_type = '{label[0]}'
    
        pos_search_styling = """<mark class="entity" style="background: linear-gradient(90deg, transparent """+str(100 - opacity*15)+"""%, {bg}); padding: 0.5em 0.4em; margin: 0 0.25em; line-height: 1em; border-radius: 0.2em; box-decoration-break: clone; -webkit-box-decoration-break: clone">
        <span style="font-weight: bold;">{text}</span><span style="font-size: """+str(0.5 + opacity/10/2)+"""em; font-family: sans-serif; color: white; margin-left: """+str(opacity/10/2)+"""rem;">"""+label_type+"""</span></mark>"""
            
        pos_options.update({'template': pos_search_styling})
        pos_options.update({'ents': pos_selection})

    for verse in spacy_text['lines']:
        html = displacy.render(
            verse,
            style='ent',
            options=pos_options
        )

        html = html.replace('\n', ' ')
        st.write(f'{style}{wrapper.format(html)}', unsafe_allow_html=True)

    st.title('')
    st.caption(f'Probability based annotations by spaCy model {spacy_model}')

    with st.expander('More information (click here to hide)', expanded=True):
        st.sidebar.info('*Tips for interpretation: TODO*')


@st.cache(allow_output_mutation=True)
def spacy_tenses(text):
    
    tenses_nlp = spacy.load(spacy_model, disable=["ner"])
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


def display_tenses(spacy_text, opacity):
    template = default_template.replace('padding: 0.45em 0.6em; margin: 0 0.25em;',
                                        'padding: 0.45em 0.6em; margin: 0;')
    
    if opacity == 0 or opacity == 2:
        template = template[:template.find('<span style=')] + '</mark>'

       
    if opacity <= 1:
        time_colors = {'OTHER': 'transparent',
                   'PAST': 'transparent',
                   'PRESENT': 'transparent'}
        
        template = template.replace('padding: 0.45em 0.6em;','padding: 0;').replace('margin-left: 0.5rem', '')
    else:
        time_colors = {'OTHER': 'linear-gradient(90deg, transparent, lightBlue)',
                   'PAST': 'linear-gradient(90deg, orange, transparent)',
                   'PRESENT': 'linear-gradient(0deg, yellow, transparent)'}
    

    for verse in spacy_text['lines']:
        html = displacy.render(
            verse,
            style='ent',
            options={'colors': time_colors, 'template':
                     template.replace('border-radius: 0.35',
                        'border-radius: 0.9').replace('{text}', '<span class="{label}">{text}</span>')}
            )

        html = html.replace('\n', ' ')
        html = html.replace('class="OTHER"', 'class="OTHER" style="font-style: italic;"')
        html = html.replace('class="PAST"', """class="OTHER" style="display: inline-block; -webkit-transform: skew(10deg,0deg); -moz-transform: skew(10deg,0deg); transform: skew(10deg,0deg);" """)
        
        st.write(f'{style}{wrapper.format(html)}', unsafe_allow_html=True)
        
        
@st.cache(allow_output_mutation=True)        
def spacy_quantity(text):
    
    quantity_nlp = spacy.load(spacy_model, disable=["ner"])
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


def display_quantity(spacy_text, opacity = 5):
    template = default_template.replace('border-radius: 0.35',
            'border-radius: 0').replace('padding: 0.45em 0.6em', 'padding: 0.1em')
    
    if opacity < 4:
        template = template[:template.find('<span style=')] + '</mark>'
    
    quantity_colors =  {'SING': f' transparent; border-bottom: {str(opacity / 5 / 6)}em solid hsl(120, 0%, 70%)',
                    'PLUR': f' transparent; border-bottom: {str(opacity / 5 / 3.5)}em double hsl(55, 95%, 50%)'}
  
    
    for verse in spacy_text['lines']:
        html = displacy.render(
            verse,
            style='ent',
            options={'colors': quantity_colors, 'template': template}
            )
  
        
        html = html.replace('\n', ' ')
        
        if opacity >= 4 and opacity < 8:
            html = html.replace('SING', 'SG').replace('PLUR', 'PL')
            
        st.write(f'{style}{wrapper.format(html)}', unsafe_allow_html=True)


@st.cache(allow_output_mutation=True)        
def spacy_persons(text):
    
    persons_nlp = spacy.load(spacy_model, disable=["ner"])
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


def display_persons(spacy_text, opacity = 5):
    template = default_template.replace('padding: 0.45em 0.6em', 'padding: 0.3em'
                            ).replace(' margin-left: 0.5rem', ' margin-left: 0.2rem')
    
    if opacity < 3:
        template = template[:template.find('<span style=')] + '</mark>'
    
    alpha = str(opacity / 10)
    
    pers_colors = {'SINGG': 'linear-gradient(0deg, hsla(120, 0%, 90%, '+ alpha +') 15%, transparent 20%)',
                   '1 SING': 'linear-gradient(0deg, hsla(120, 100%, 50%, '+ alpha +') 15%, transparent 20%)',
                    '2 SING': 'linear-gradient(0deg, hsla(200, 100%, 50%, '+ alpha +') 15%, transparent 20%)',
                    '3 SING': 'linear-gradient(0deg, hsla(220, 100%, 60%, '+ alpha +') 15%, transparent 20%)',
                    'PLUR': 'linear-gradient(0deg, hsla(55, 95%, 50%, '+ alpha +') 15%, transparent 20%)',
                    '1 PLUR': 'linear-gradient(0deg, hsla(40, 100%, 50%, '+ alpha +') 15%, transparent 20%)',
                    '2 PLUR': 'linear-gradient(0deg, hsla(0, 100%, 50%, '+ alpha +') 15%, transparent 20%)',
                    '3 PLUR': 'linear-gradient(0deg, hsla(310, 100%, 50%, '+ alpha +') 15%, transparent 20%)',
                    '2': 'linear-gradient(0deg, hsla(310, 0%, 50%, '+ alpha +') 15%, transparent 20%)'}
    
    for verse in spacy_text['lines']:
        html = displacy.render(
            verse,
            style='ent',
            options={'colors': pers_colors, 'template': template}
            )
        
        if opacity >= 3 and opacity < 8:
            html = html.replace('SING', 'SG').replace('PLUR', 'PL')
        
        html = html.replace('\n', ' ')
        st.write(f'{style}{wrapper.format(html)}', unsafe_allow_html=True)


@st.cache(allow_output_mutation=True)        
def spacy_sentiments(text):
    
    sentiments_nlp = spacy.load(spacy_model, disable=["ner"])
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


def display_sentiments(spacy_text, opacity = 5):
    template = default_template.replace('padding: 0.45em 0.6em', 'padding: 0.75em'
                            ).replace(' margin-left: 0.5rem', ' margin-left: 0.2rem'
                            ).replace('border-radius: 0.35em', 'border-radius: 1em')
    
    if opacity < 5:
        template = template[:template.find('<span style=')] + '</mark>'
    
    
    alpha = str(opacity / 5)
    
    sentiments_colors = {}

    for i in range(-10,11):
        if i > 0:
            sentiments_colors.update({str(round(i/10, 1)):
                                    f"linear-gradient(0deg, transparent {70 - opacity * 4}%, hsla(100, 100%, {80 - i * 5}%, {alpha}) {70 - opacity * 4}%, transparent)"})
        if i < 0:
            sentiments_colors.update({str(round(i/10, 1)): 
                                    f"linear-gradient(0deg, transparent, hsla({40 - abs(i) * 4}, 100%, {80 - abs(i) * 3}%, {alpha}) {30 + opacity * 4}%, transparent {30 + opacity * 4}%)"})
        
    for verse in spacy_text['lines']:
        html = displacy.render(
            verse,
            style='ent',
            options={'colors': sentiments_colors, 'template': template}
            )
        
        html = html.replace('\n', ' ')
        st.write(f'{style}{wrapper.format(html)}', unsafe_allow_html=True)


@st.cache(allow_output_mutation=True)        
def spacy_subjectivity(text):
    
    subjectivity_nlp = spacy.load(spacy_model, disable=["ner"])
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


def display_subjectivity(spacy_text, opacity = 5):
    alpha = str(0.2 + opacity / 5)
    
    subjectivity_colors = {}

    for i in range(0,11):
        subjectivity_colors.update({str(round(i/10, 1)):
                                f"radial-gradient(hsla({250 + i * 5}, 100%, {100 - i * 4}%, {alpha}), transparent {65 + opacity * 3}%)"})

    for verse in spacy_text['lines']:
        html = displacy.render(
            verse,
            style='ent',
            options={'colors': subjectivity_colors}
            )
        
        html = html.replace('\n', ' ')
        st.write(f'{style}{wrapper.format(html)}', unsafe_allow_html=True)




def opacity_ruler(max = 10, start = 5):
    opacity = st.sidebar.slider('Annotation presence', 0, max, start,
                                help='You can make the annotations more vivid or discrete '
                                ' to focus on them or to make them subtle when reading')
    return opacity


if __name__ == '__main__':
    main()
