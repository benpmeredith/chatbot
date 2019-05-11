import speech_recognition as sr
import spacy
from spacy.lemmatizer import Lemmatizer
from spacy.lang.en import LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES
import pyttsx3
import logging

from s2t import speech2text
from nsv_query import Query

logging.getLogger(__name__).setLevel(logging.INFO)
logger = logging.getLogger(__name__)


class QueryBuilder:
    known_subjects = ["child", "son", "daughter", "nephew", "grandson", "granddaughter", "niece"]
    known_verbs = ["bully"]
    male_subjects = ["son", "nephew", "grandson"]
    female_subjects = ["daughter", "niece", "granddaughter"]

    def __init__(self):
        self.lemmatizer = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)
        self.engine = pyttsx3.init()
        self.engine.setProperty('voice', 'com.apple.speech.synthesis.voice.ava.premium')
        self.engine.setProperty('rate', self.engine.getProperty('rate') - 31.5)
        self.nlp = spacy.load("en_core_web_sm")
        self.recognizer = sr.Recognizer()

    def form_query(self, sentence=None):
        known_subjects = ["child", "son", "daughter", "nephew", "grandson", "granddaughter", "niece"]
        known_verbs = ["bully"]
        male_subjects = ["son", "nephew", "grandson"]
        female_subjects = ["daughter", "niece", "granddaughter"]

        lemmatizer = Lemmatizer(LEMMA_INDEX, LEMMA_EXC, LEMMA_RULES)

        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source)
            doc = self.nlp(sentence)

            noun_subjects = []
            for chunk in doc.noun_chunks:
                poss = False
                noun_subject = lemmatizer(chunk.root.text, u"NOUN")[0]
                for child in chunk.root.children:
                    if "poss" in child.dep_:
                        poss = child.text
                noun_subjects.append((noun_subject, poss))
            print(noun_subjects)

            root_verbs = [lemmatizer(token.head.text, u"VERB")[0] for token in doc if
                          token.dep_ == "ROOT" and token.head.pos_ == "VERB"]
            print(root_verbs)

            q = Query(self.engine, self.recognizer, source)

            for ns, poss in noun_subjects:
                if ns in known_subjects:
                    q.subject = ns
                    q.subject_poss = poss
                    break
                else:
                    print(f"Sorry, we don't support questions on {ns} yet")
                    return

            for ns, _ in noun_subjects:
                if ns in male_subjects:
                    q.subject_gender = "male"
                elif ns in female_subjects:
                    q.subject_gender = "female"
                    break

            for verb in root_verbs:
                if verb in known_verbs:
                    q.verb = verb
                    break

            print(q)
            q.get_missing_fields()
            print(q)


def main():
    qb = QueryBuilder()
    qb.form_query("My nephew is being bullied")


if __name__ == "__main__":
    main()