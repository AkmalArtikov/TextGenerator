from os import listdir
import os.path
import pickle
import random

SMALL_LETTER_CODES = (ord('a'), ord('z'))
LARGE_LETTER_CODES = (ord('A'), ord('Z'))
FILE_NAMES = ("words_freq.pickle", "capital_words_freq.pickle", "sentences_length_freq.pickle",
              "markov_one_word_freq.pickle", "markov_two_word_freq.pickle")


def is_in_alphabet(char):
    # Check symbol in alphabet
    char_ord = ord(char)

    is_small = SMALL_LETTER_CODES[1] >= char_ord >= SMALL_LETTER_CODES[0]
    is_large = LARGE_LETTER_CODES[1] >= char_ord >= LARGE_LETTER_CODES[0]

    return is_small or is_large


def clean_word(word):
    # Clean word from trash symbols
    while True:
        if len(word) == 0:
            break

        if not is_in_alphabet(word[0]):
            word = word[1:]
        else:
            break

    iterator = len(word)
    while True:
        if len(word) == 0:
            break

        if not is_in_alphabet(word[iterator-1]):
            word = word[:-1]
            iterator -= 1
        else:
            break
    return word


def clean_words(input_text):
    # Clean words and count first words
    input_text = input_text.split()

    text = []
    for i in range(len(input_text)):
        text += input_text[i].split('\xe2\x80\x94')

    capital_words = []
    for i in range(len(text)):
        if len(text[i]) > 2 and LARGE_LETTER_CODES[1] >= ord(text[i][0]) >= LARGE_LETTER_CODES[0] and\
           SMALL_LETTER_CODES[1] >= ord(text[i][1]) >= SMALL_LETTER_CODES[0] and\
           i > 0 and len(text[i-1]) > 2 and text[i-1][-1] in ('.', '!', '?'):
            capital_words.append(clean_word(text[i]))

    for i in range(len(text)):
        text[i] = clean_word(text[i])

    words = []
    for i in range(len(text)):
        if len(text[i]) != 0:
            words.append(text[i].lower())

    return words, capital_words


def update_sentences_probabilities(text, sentences_probabilities):
    # Update sentence length probabilities
    sentences = []
    text_without_points = text.split('.')
    for part in text_without_points:
        text_without_exclamations = part.split('!')
        for sub_part in text_without_exclamations:
            text_without_questions = sub_part.split('?')
            for sentence in text_without_questions:
                if len(sentence) > 1:
                    sentences.append(sentence)

    for sentence in sentences:
        words = sentence.split()
        length = len(words)
        if length < len(sentences_probabilities):
            sentences_probabilities[length] += 1


def read_corpus(dir_name):
    # Read corpus and clean words
    words = []
    capital_words = []
    sentences_probabilities = [0] * 1000

    path = os.path.dirname(os.path.abspath(__file__)) + "\\" + dir_name
    for dir in listdir(path):
        new_path = path + "\\" + dir
        for file in listdir(new_path):
            with open(new_path + "\\" + file, 'r') as input_file:
                text = input_file.read()

                new_words, new_capital_words = clean_words(text)
                words += new_words
                capital_words += new_capital_words

                update_sentences_probabilities(text, sentences_probabilities)

    return words, capital_words, sentences_probabilities


def words_frequency(words):
    # Count words frequency
    words_freq = {}

    for word in words:
        if word in words_freq:
            words_freq[word] += 1
        else:
            words_freq[word] = 1

    for word in words_freq:
        words_freq[word] = (words_freq[word] + 0.0) / len(words)

    return words_freq


def sentences_length_frequency(sentences_probabilities):
    # Count sentences length frequency
    sum = 0
    for length in xrange(len(sentences_probabilities)):
        sum += sentences_probabilities[length]

    for length in xrange(len(sentences_probabilities)):
        sentences_probabilities[length] = (sentences_probabilities[length] + 0.0) / sum

    return sentences_probabilities


def markov_one_word_frequency(words):
    # Count words frequency after another words
    markov_one_word_freq = {}

    for i in xrange(len(words) - 1):
        if words[i] in markov_one_word_freq:
            if words[i+1] in markov_one_word_freq[words[i]]:
                markov_one_word_freq[words[i]][words[i+1]] += 1
            else:
                markov_one_word_freq[words[i]][words[i+1]] = 1
        else:
            markov_one_word_freq[words[i]] = {}
            markov_one_word_freq[words[i]][words[i+1]] = 1

    for first_word in markov_one_word_freq:
        sum = 0
        for second_word in markov_one_word_freq[first_word]:
            sum += markov_one_word_freq[first_word][second_word]

        for second_word in markov_one_word_freq[first_word]:
            markov_one_word_freq[first_word][second_word] = \
                (markov_one_word_freq[first_word][second_word] + 0.0) / sum

    return markov_one_word_freq


def markov_two_word_frequency(words):
    # Count words frequency after pair of another words
    markov_two_word_freq = {}

    for i in xrange(len(words) - 2):
        chain = words[i] + "." + words[i+1]
        if chain in markov_two_word_freq:
            if words[i+2] in markov_two_word_freq[chain]:
                markov_two_word_freq[chain][words[i+2]] += 1
            else:
                markov_two_word_freq[chain][words[i+2]] = 1
        else:
            markov_two_word_freq[chain] = {}
            markov_two_word_freq[chain][words[i+2]] = 1

    for first_word in markov_two_word_freq:
        sum = 0
        for second_word in markov_two_word_freq[first_word]:
            sum += markov_two_word_freq[first_word][second_word]

        for second_word in markov_two_word_freq[first_word]:
            markov_two_word_freq[first_word][second_word] = \
                (markov_two_word_freq[first_word][second_word] + 0.0) / sum

    return markov_two_word_freq


def count_and_save_statistic(words, capital_words, sentences_probabilities):
    # Count statistics and serialize it
    words_freq = words_frequency(words)
    with open(FILE_NAMES[0], 'wb') as f:
        pickle.dump(words_freq, f)

    capital_words_freq = words_frequency(capital_words)
    with open(FILE_NAMES[1], 'wb') as f:
        pickle.dump(capital_words_freq, f)

    sentences_length_freq = sentences_length_frequency(sentences_probabilities)
    with open(FILE_NAMES[2], 'wb') as f:
        pickle.dump(sentences_length_freq, f)

    markov_one_word_freq = markov_one_word_frequency(words)
    with open(FILE_NAMES[3], 'wb') as f:
        pickle.dump(markov_one_word_freq, f)

    markov_two_word_freq = markov_two_word_frequency(words)
    with open(FILE_NAMES[4], 'wb') as f:
        pickle.dump(markov_two_word_freq, f)


def choose_sentence_length(sentence_length_freq):
    # Get sentence length from distribution
    random_value = random.random()
    cumulative_sum = 0.0

    for i in xrange(len(sentence_length_freq)):
        cumulative_sum += sentence_length_freq[i]
        if random_value < cumulative_sum:
            return i

    return len(sentence_length_freq)


def choose_first_word(capital_words_freq):
    # Get first word from distribution
    random_value = random.random()
    cumulative_sum = 0.0

    for word in capital_words_freq:
        cumulative_sum += capital_words_freq[word]
        if random_value < cumulative_sum:
            return word

    return capital_words_freq.keys()[-1]


def choose_second_word(word, markov_one_word_freq):
    # Get next word from distribution
    random_value = random.random()
    cumulative_sum = 0.0

    if word in markov_one_word_freq:
        for next_word in markov_one_word_freq[word]:
            cumulative_sum += markov_one_word_freq[word][next_word]
            if random_value < cumulative_sum:
                return next_word

    return markov_one_word_freq.keys()[-1]


def choose_other_words(pre_last_word, last_word, markov_one_word_freq, markov_two_word_freq):
    # Get word after the pair of words from distribution
    random_value = random.random()
    cumulative_sum = 0.0
    chain = pre_last_word + "." + last_word

    if chain in markov_two_word_freq:
        for next_word in markov_two_word_freq[chain]:
            cumulative_sum += markov_two_word_freq[chain][next_word]
            if random_value < cumulative_sum:
                return next_word
    else:
        return choose_second_word(last_word, markov_one_word_freq)


def generate_text(min_words_number):
    # Deserialize statistics and generate text
    with open(FILE_NAMES[0], 'rb') as f:
        words_freq = pickle.load(f)

    with open(FILE_NAMES[1], 'rb') as f:
        capital_words_freq = pickle.load(f)

    with open(FILE_NAMES[2], 'rb') as f:
        sentences_length_freq = pickle.load(f)

    with open(FILE_NAMES[3], 'rb') as f:
        markov_one_word_freq = pickle.load(f)

    with open(FILE_NAMES[4], 'rb') as f:
        markov_two_word_freq = pickle.load(f)

    text = ''
    words_number = 0

    title_size = random.randint(1, 5)
    length = 0
    last_word = ''
    while length < 3:
        last_word = choose_first_word(words_freq)
        length = len(last_word)
    text += last_word.upper() + " "
    for i in xrange(1, title_size):
        last_word = choose_second_word(last_word.lower(), markov_one_word_freq)
        text += last_word.upper() + " "
    text += "\n\n"

    while words_number < min_words_number:
        sentences_in_paragraph = int(random.gauss(10, 3))
        if sentences_in_paragraph < 1:
            sentences_in_paragraph = 1

        for i in xrange(sentences_in_paragraph):
            length = choose_sentence_length(sentences_length_freq)

            pre_last_word = ''
            last_word = ''
            for j in xrange(length):
                if j == 0:
                    last_word = choose_first_word(capital_words_freq)
                    text += last_word
                elif j == 1:
                    pre_last_word = last_word
                    last_word = choose_second_word(last_word.lower(), markov_one_word_freq)
                    text += last_word
                else:
                    new_word = choose_other_words(pre_last_word.lower(), last_word.lower(), markov_one_word_freq,
                                                  markov_two_word_freq)
                    text += new_word
                    pre_last_word = last_word
                    last_word = new_word

                if j != length - 1:
                    text += ' '

            words_number += 1
            text += '. '

        text += '\n\n'

    return text

words, capital_words, sentences_probabilities = read_corpus('corpus')
count_and_save_statistic(words, capital_words, sentences_probabilities)
text = generate_text(10000)

with open("generated_text.txt", 'w+') as file:
    file.write(text)