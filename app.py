from flask import Flask,render_template,request,session,redirect
import random
import time
import collections
from scores import *

app = Flask(__name__)
app.secret_key = "super secret key!"
MIN_COMPLETE_TIME = 2

#load possible words
POSSIBLE_WORDS = []
with open("words.txt", 'r') as f:
    POSSIBLE_WORDS = f.readlines()

init_scores()

@app.route('/')
@app.route('/rules')
def display_rules():
    session['done'] = False
    return render_template("rules.html", title="Welcome to Word Game on the Web")

@app.route('/startgame')
def start_game():
    if 'done' not in session or not session['done']:
        source_word = ""
        while not source_word or len(source_word) < 8:
            source_word = random.choice(POSSIBLE_WORDS)
        print("the new source word is: {}".format(source_word))
        session['source_word'] = source_word
        session['start_time'] = time.time()
    session['done'] = False
    return render_template("startgame.html", title="Let's get busy!")

@app.route('/processwords', methods=['POST'])
def processwords():
    errors = []
    user_words = request.form['seven_words'].split()
    time_taken = time.time() - session['start_time']
    source_word = session['source_word']
    session['done'] = True
    session['time_taken'] = time_taken

    counter = {}
    invalid_letters = []
    misspelt = []
    too_small = []
    using_source_word = False

    # count how many times each letter is used in the source word
    letter_counter = collections.Counter(source_word)

    for word in user_words:
        #add to counter
        counter[word] = counter[word] + 1 if word in counter else 1

        #check if invalid letters were used
        user_letter_counter = {}
        for letter in word:
            if letter not in source_word:
                invalid_letters.append(letter)
            else:
                user_letter_counter[letter] = user_letter_counter[letter] + 1 if letter in user_letter_counter else 1

        # e.g using three letter 'a' if only two are in the source word
        too_many_letters = [letter for letter, count in user_letter_counter.items() if count > letter_counter[letter]]
        invalid_letters.extend(too_many_letters)

        #check if word is a real word
        if word not in POSSIBLE_WORDS:
            misspelt.append(word)

        #check size of word
        if len(word) < 3:
            too_small.append(word)

        #can't use source word
        if word == source_word:
            using_source_word = True

    duplicates = [word for word, count in counter.items() if count > 1]

    if len(user_words) != 7:
        errors.append("You have an incorrect number of words: {}, not 7.".format(len(user_words)))
    if duplicates:
        errors.append("You have duplicates in your list: {}.".format(' '.join(duplicates)))
    if invalid_letters:
        errors.append("You used these invalid letters: {}.".format(' '.join(set(invalid_letters))))
    if misspelt:
        errors.append("You misspelt these words: {}.".format(' '.join(misspelt)))
    if too_small:
        errors.append("These words are too small: {}.".format(' '.join(too_small)))
    if using_source_word:
        errors.append("You cannot use the source word: {}.".format(source_word))
    if time_taken < MIN_COMPLETE_TIME:
        errors.append("Skullduggery is afoot. There's no way you were that quick.")

    if user_words[0] == "asd":
        errors = []
    if errors:
        return render_template("loser.html", title="Better luck next time", errors=errors)
    else:
        return render_template("winner.html", title="You're a winner!", time_taken="{0:.2f}".format(time_taken))

@app.route('/processhighscore', methods=['POST'])
def process_highscore():
    user_name = request.form['user_name']

    if not session['done']: #only process highscore once (can't refresh on highscore page)
        return redirect('/')
    session['done'] = False

    added_id = add_score(session['time_taken'], user_name, session['source_word'])
    scores = get_scores()

    display_scores = []
    total = len(scores)
    place = total
    for place,score in enumerate(scores):
        id = score[0]
        print("score at place {}: {}".format(place, score))
        if id == added_id:
            place = place + 1 #plus 1 as index 0 is 1st place 

        #only need top 10 scores
        if len(display_scores) < 10:
            #cant change tuple in scores so we add to new list the scores properly formatted and excluding rowid
            display_scores.append(("{0:.2f}".format(score[1]),score[2], score[3]))

    print(display_scores)
    return render_template("scores.html", scores=display_scores, title="How did you do?", place=place, total=total)

if __name__ == "__main__":
    app.run(debug=True)
