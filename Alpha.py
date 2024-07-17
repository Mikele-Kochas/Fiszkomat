import streamlit as st
import random
import re
from dataclasses import dataclass
from typing import List

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
        st.session_state.quiz_results = []
    else:
        st.error("Nie znaleziono poprawnie sformatowanych słów.")

def display_flashcard() -> None:
    flashcard = st.session_state.flashcard
    current_word = flashcard.get_word(st.session_state.current_index)

    st.markdown(f"<h3>{current_word.german}</h3>", unsafe_allow_html=True)
    if st.button("Pokaż/Ukryj tłumaczenie"):
        st.markdown(f"<h4>{current_word.polish}</h4>", unsafe_allow_html=True)

    if st.button("Następne słowo"):
        st.session_state.current_index = (st.session_state.current_index + 1) % flashcard.total_words()
        st.experimental_rerun()

def take_quiz() -> None:
    if 'quiz_state' not in st.session_state:
        num_questions = st.number_input("Ile pytań chcesz w quizie?", min_value=1, max_value=20, value=5)
        if st.button("Rozpocznij quiz"):
            st.session_state.quiz_state = {
                'current_question': 0,
                'questions': [],
                'user_answers': [''] * num_questions,
                'correct_answers': 0,
                'num_questions': num_questions,
                'feedback': ''
            }
            flashcard = st.session_state.flashcard
            total_words = flashcard.total_words()
            st.session_state.quiz_state['questions'] = [
                flashcard.get_word(random.randint(0, total_words - 1))
                for _ in range(num_questions)
            ]
            st.experimental_rerun()
    else:
        st.subheader("Sprawdź swoją wiedzę")

        quiz_state = st.session_state.quiz_state
        current_word = quiz_state['questions'][quiz_state['current_question']]

        st.write(f"Pytanie {quiz_state['current_question'] + 1} z {quiz_state['num_questions']}")
        user_answer = st.text_input(
            f"Przetłumacz słowo: {current_word.german}",
            key=f"quiz_input_{quiz_state['current_question']}",
            value=quiz_state['user_answers'][quiz_state['current_question']]
        )

        if st.button("Sprawdź"):
            feedback_placeholder = st.empty()

            if user_answer.strip().lower() == current_word.polish.lower():
                feedback_placeholder.success("Poprawna odpowiedź!")
                quiz_state['correct_answers'] += 1
            else:
                feedback_placeholder.error(f"Niepoprawna odpowiedź. Poprawne tłumaczenie: {current_word.polish}")

            quiz_state['user_answers'][quiz_state['current_question']] = user_answer

        if st.button("Następne pytanie"):
            quiz_state['current_question'] += 1
            quiz_state['feedback'] = ''

            if quiz_state['current_question'] >= quiz_state['num_questions']:
                score = quiz_state['correct_answers'] / quiz_state['num_questions']
                st.session_state.quiz_results.append(score)
                st.write(
                    f"Koniec quizu! Uzyskałeś {quiz_state['correct_answers']} na {quiz_state['num_questions']} możliwych punktów.")
                del st.session_state.quiz_state
            else:
                st.experimental_rerun()

    if st.button("Powrót do fiszek"):
        if 'quiz_state' in st.session_state:
            del st.session_state.quiz_state
        st.experimental_rerun()

def display_statistics() -> None:
    st.subheader("Twoje statystyki")

    if 'flashcard' in st.session_state:
        flashcard = st.session_state.flashcard
        total_words = flashcard.total_words()
        st.write(f"Wprowadzono {total_words} słów.")

        if st.session_state.quiz_results:
            avg_score = sum(st.session_state.quiz_results) / len(st.session_state.quiz_results)
            st.write(f"Średni wynik quizu: {avg_score:.2%}")
    else:
        st.write("Brak danych do wyświetlenia statystyk.")

def main() -> None:
    st.set_page_config(
        page_title="Fiszkomat",
        page_icon=":books:",
        layout="wide",
    )

    st.title("Fiszkomat")

    if 'show_input' not in st.session_state:
        st.session_state.show_input = True

    if 'quiz_results' not in st.session_state:
        st.session_state.quiz_results = []

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
            tab1, tab2, tab3 = st.tabs(["Fiszki", "Quiz", "Statystyki"])

            with tab1:
                display_flashcard()

            with tab2:
                take_quiz()

            with tab3:
                display_statistics()

        if st.button("Nowa lista słów"):
            st.session_state.show_input = True
            if 'quiz_state' in st.session_state:
                del st.session_state.quiz_state

if __name__ == "__main__":
    main()
