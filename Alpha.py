import streamlit as st
import re


class Flashcard:
    """Class to represent a flashcard for language learning."""

    def __init__(self, words):
        self.words = words

    def get_word(self, index):
        """Get the word at a specific index."""
        return self.words[index]

    def total_words(self):
        """Get the total number of words."""
        return len(self.words)


def parse_word_list(word_list):
    """
    Parse a list of words in the format 'german - polish'.

    Args:
        word_list (str): Multiline string with each line containing a German word and its Polish translation.

    Returns:
        list: List of dictionaries with 'german' and 'polish' keys.
    """
    words = []
    for line in word_list.split('\n'):
        line = line.strip()
        line = re.sub(r'^\d+\.\s*', '', line)
        line = line.replace('*', '')

        if ' - ' in line:
            german, polish = line.split(' - ')
            german = german.strip()
            polish = polish.strip()

            if german and polish:
                words.append({'german': german, 'polish': polish})
    return words


def create_flashcards(word_list):
    """Create flashcards from the provided word list."""
    words = parse_word_list(word_list)
    if words:
        st.session_state.flashcard = Flashcard(words)
        st.session_state.current_index = 0
        st.session_state.show_input = False  # Hide the input area after creating flashcards
        st.experimental_rerun()
    else:
        st.error("Nie znaleziono poprawnie sformatowanych słów.")


def display_flashcard():
    """Display the current flashcard."""
    flashcard = st.session_state.flashcard
    current_word = flashcard.get_word(st.session_state.current_index)

    st.markdown(f"<h3 style='text-align: center;'>{current_word['german']}</h3>", unsafe_allow_html=True)
    if st.button("Pokaż/Ukryj tłumaczenie", key='toggle_translation'):
        st.markdown(f"<h4 style='text-align: center; margin-top: 20px;'>{current_word['polish']}</h4>",
                    unsafe_allow_html=True)


def next_word():
    """Go to the next word in the flashcard set."""
    st.session_state.current_index = (st.session_state.current_index + 1) % len(st.session_state.flashcard.words)
    st.experimental_rerun()


def main():
    """Main function to run the Streamlit app."""
    st.title("Fiszki do nauki niemieckiego")

    if 'show_input' not in st.session_state:
        st.session_state.show_input = True

    if st.session_state.show_input:
        word_list = st.text_area(
            "Wprowadź listę słów (niemieckie - polskie):",
            height=200,
            help="Każde słowo w nowej linii, format: niemieckie_słowo - polskie_tłumaczenie"
        )

        if st.button("Utwórz fiszki"):
            create_flashcards(word_list)
    else:
        if 'flashcard' in st.session_state:
            display_flashcard()

            st.markdown(
                """
                <style>
                .fixed-footer {
                    position: fixed;
                    left: 0;
                    bottom: 0;
                    width: 100%;
                    background-color: white;
                    text-align: center;
                    padding: 10px;
                    box-shadow: 0 -1px 5px rgba(0, 0, 0, 0.1);
                }
                </style>
                <div class="fixed-footer">
                """,
                unsafe_allow_html=True
            )
            if st.button("Następne słowo", key='next_word'):
                next_word()


if __name__ == "__main__":
    main()
