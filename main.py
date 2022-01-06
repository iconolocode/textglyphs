import streamlit as st
import subprocess
from language_processing import *
from visualizers import *


if 'textblob' not in st.session_state:
    subprocess.run(['python3', '-m', 'textblob.download_corpora'])
    st.session_state.textblob = True

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

if 'analyzed_text' not in st.session_state:
    st.session_state.analyzed_text = False


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


def opacity_ruler(max = 10, start = 5):
    opacity = st.sidebar.slider('--- Levels of annotation presence:', 0, max, start,
                                help='You can make the annotations more vivid or discrete '
                                ' to focus on them or to make them subtle when reading')
    return opacity


def main():
    meta_data()
    
    st.sidebar.info('This tool uses artificial intelligence to extract features of language')
    
    with st.sidebar.form(key='text_form'):
        #with st.expander('Text editor', expanded=True):
        st.session_state.text = st.text_area(label='1. Enter a text to analyze:',
                            value=st.session_state.text, height=100,
                            help='You can copy paste a text here '
                                'and collapse this box.')
        st.form_submit_button(label='Analyze',
                              help='Save the text in the box above.')
        st.session_state.analyzed_text = False

    menu = ['\N{Right-Pointing Magnifying Glass} search by word class',
            '\N{Jigsaw Puzzle Piece} syntax structure',
            '\N{Hourglass with Flowing Sand} tenses',
            '\N{Scales} quantities',
            '\N{Busts in Silhouette} persons',
            '\N{Paperclip} named or specfic things',
            '\N{Performing Arts} sentiments',
            '\N{Thought Balloon} subjectivity', 
            'plain text']
    
    current = st.sidebar.radio('2. Generate annotation filters:', menu)

    filters = (spacy_pos, spacy_ner, spacy_tenses, spacy_quantity,
               spacy_persons, spacy_sentiments, spacy_subjectivity)
    
    if not st.session_state.textblob:
        loading_bar = st.progress(0)
        for step, f in enumerate(filters):
            loading_bar.progress(1/len(filters) * step)
            f(st.session_state.text)
        st.session_state.analyzed_text = True
        loading_bar.empty()

    if current == '\N{Jigsaw Puzzle Piece} syntax structure':
        opacity = opacity_ruler()
        display_pos(spacy_pos(st.session_state.text), 'pattern', opacity)

    elif current == '\N{Right-Pointing Magnifying Glass} search by word class':
        opacity = opacity_ruler()
        display_pos(spacy_pos(st.session_state.text), 'search', opacity)

    elif current == '\N{Paperclip} named or specfic things':
        opacity = opacity_ruler(3, 2)
        display_ner(spacy_ner(st.session_state.text), opacity)
        
    elif current == '\N{Hourglass with Flowing Sand} tenses':
        opacity = opacity_ruler(3, 2)
        display_tenses(spacy_tenses(st.session_state.text), opacity)
        
    elif current == '\N{Scales} quantities':
        opacity = opacity_ruler()
        display_quantity(spacy_quantity(st.session_state.text), opacity)
        
    elif current == '\N{Busts in Silhouette} persons':
        opacity = opacity_ruler()
        display_persons(spacy_persons(st.session_state.text), opacity)
        
    elif current == '\N{Performing Arts} sentiments':
        opacity = opacity_ruler()
        display_sentiments(spacy_sentiments(st.session_state.text), opacity)
        
    elif current == '\N{Thought Balloon} subjectivity':
        opacity = opacity_ruler()
        display_subjectivity(spacy_subjectivity(st.session_state.text), opacity)
        
    else: 
        st.markdown(st.session_state.text.replace('\n\n', '\n---\n'
                                                  ).replace('\n', '\n\n'))


if __name__ == '__main__':
    main()