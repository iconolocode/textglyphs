import streamlit as st
from spacy import displacy
from spacy.displacy.templates import TPL_ENT as default_template 

wrapper = """<div style="background: rgba(255, 255, 255, 0.3); op overflow-x: auto; border: 0px; border-radius: 0.7rem; padding-left: 3em">{}</div>"""
style = """<style>mark.entity { display: inline-block }</style>"""

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

  
    st.sidebar.markdown('##### 3. Interpret the poem with the annotations:')
    #with st.sidebar.expander('More information (click here to hide)', expanded=True):
    st.sidebar.info('This model extracts key information. It is trained mostly on '
            'texts related to news, but also on conversations, weblogs, '
            'and religious texts.')

    st.sidebar.info('**Tips for interpretation:** Are the pieces of information '
            'that are extracted important in the poem, or is their role '
            'more of one of ornaments to add detail to a text?' '\n\n'
            'If there are misclassifications, this could be due to the '
            'model not being trained for poetry. But there could also be '
            'other reasons that could have lead to this, such as the '
            'sentence structure or lexical context. It may be interesting '
            'to look at those, if they confuse the machine, what does '
            'this mean for us?')
    
    
def display_pos(spacy_text, pos_style, opacity):

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

    with st.expander('More information (click here to hide)', expanded=True):
        st.sidebar.info('*Tips for interpretation: TODO*')
        
        
def display_quantity(spacy_text, opacity):
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
        
    
def display_persons(spacy_text, opacity):
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
        
        
def display_sentiments(spacy_text, opacity):
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
        
        
def display_subjectivity(spacy_text, opacity):
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