import streamlit as st
import openai
import re
from dataclasses import dataclass
from typing import List

# Replace this with your actual OpenAI API key
api_key = st.secrets["OPENAI_API_KEY"]
# Initialize OpenAI client
openai.api_key = api_key

@dataclass
class Word:
    german: str
    polish: str

class Flashcard:
    def __init__(self, words: List[Word]):
        self.words = words

    def get_word(self, index: int) -> Word:
        return self.words[index]

    def total_words(self) -> int:
        return len(self.words)

def parse_word_list(word_list: str) -> List[Word]:
    words = []
    for line in word_list.strip().split('\n'):
        line = re.sub(r'^\d+\.\s*', '', line.strip().replace('*', ''))
        if ' - ' in line:
            german, polish = map(str.strip, line.split(' - '))
            if german and polish:
                words.append(Word(german=german, polish=polish))
    return words

def create_flashcards(word_list: str) -> None:
    words = parse_word_list(word_list)
    if words:
        st.session_state.flashcard = Flashcard(words)
        st.session_state.current_index = 0
        st.session_state.show_input = False
    else:
        st.error("Nie znaleziono poprawnie sformatowanych słów.")

def display_flashcard() -> None:
    flashcard = st.session_state.flashcard
    current_word = flashcard.get_word(st.session_state.current_index)
    st.markdown(f"<h2>{current_word.german}</h2>", unsafe_allow_html=True)
    if st.button("Pokaż odpowiedź", key="show_answer"):
        st.markdown(f"<h3>{current_word.polish}</h3>", unsafe_allow_html=True)

    if st.button("Następne słowo", key="next_word"):
        st.session_state.current_index = (st.session_state.current_index + 1) % flashcard.total_words()
        st.experimental_rerun()

def generate_word_list(topic: str) -> str:
    prompt = f"Wygeneruj listę 10 słów w języku niemieckim związanych z tematem '{topic}' wraz z ich polskimi tłumaczeniami. Format: niemieckie słowo - polskie tłumaczenie. Pamiętaj, aby przed niemickimi rzeczownikami umieścić właściwe przedrostki. Nie pisz niczego poza samą listą."
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message['content']

def main() -> None:
    st.set_page_config(
        page_title="Fiszkomat",
        page_icon=":books:",
        layout="wide",
    )

    st.title("Fiszkomat")

    # Initialize application state
    if 'show_input' not in st.session_state:
        st.session_state.show_input = True
    if 'word_list' not in st.session_state:
        st.session_state.word_list = ""
    if 'flashcard' not in st.session_state:
        st.session_state.flashcard = None
    if 'current_index' not in st.session_state:
        st.session_state.current_index = 0

    # Interface for generating word list
    if st.session_state.show_input:
        topic = st.text_input(
            "Podaj temat, z którego chcesz się uczyć słówek:",
            help="Np. pogoda, jedzenie, podróże"
        )

        if st.button("Generuj listę słów", key="generate_word_list"):
            with st.spinner("Generowanie listy słów..."):
                try:
                    st.session_state.word_list = generate_word_list(topic)
                    st.success("Lista słów została wygenerowana!")
                except Exception as e:
                    st.error(f"Wystąpił błąd podczas generowania listy słów: {str(e)}")

        if st.session_state.word_list:
            st.subheader("Wygenerowana lista słów:")
            st.text_area("", st.session_state.word_list, height=200)
            if st.button("Utwórz fiszki", key="create_flashcards"):
                create_flashcards(st.session_state.word_list)
    else:
        # Interface for working with flashcards
        if st.session_state.flashcard:
            display_flashcard()

        if st.button("Nowa lista słów", key="new_word_list"):
            st.session_state.show_input = True
            st.session_state.word_list = ""
            st.session_state.flashcard = None
            st.experimental_rerun()

if __name__ == "__main__":
    main()

