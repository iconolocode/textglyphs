import streamlit as st
import spacy_streamlit
import spacy
from spacy import displacy


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

spacy_model = "en_core_web_sm"


st.title("Patterns in poetry")


#initialization
with st.form(key='text_form'):
    st.header("Input text")
    text = st.text_area("enter a text to analyze :",
                        DEFAULT_TEXT, height=400)
    submit_button = st.form_submit_button(label='analyze')

text = text.replace('      here is an example:', '')



#named ents
st.header("Named entities analysis")

ner = spacy.load(spacy_model)

text_ner = ner(text)
verses = [ner(verse) for verse in text.split('\n')]
#labels = labels or [ent.label_ for ent in doc.ents]

for verse in verses:
    html = displacy.render(
        verse,
        style="ent"
        #options={"ents": label_select, "colors": colors},
    )
    #displacy.render(verse, style='ent')
    wrapper = """<div style="background: white; overflow-x: auto; border: 0px; border-radius: 0.25rem; padding-left: 3em">{}</div>"""
    style = "<style>mark.entity { display: inline-block }</style>"
    html = html.replace('\n', ' ')
    st.write(f"{style}{wrapper.format(html)}", unsafe_allow_html=True)

st.text(f"Analyzed using spaCy model {spacy_model}")