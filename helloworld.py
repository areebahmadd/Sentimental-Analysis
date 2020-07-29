from flask import Flask, render_template, request
import os
import numpy as np
import re
import seaborn as sns
import tweepy
import time
from googletrans import Translator
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
global user_id, count
# Flask code -----------------------------------

# Flask code end here ---------------------------
analyser = SentimentIntensityAnalyzer()


def sentiment_analyzer_scores(text):
    translator = Translator()
    text = translator.translate(text).text
    # print(text)
    score = analyser.polarity_scores(text)
    lb = score['compound']
    # print(lb)
    if lb >= 0.5:
        return 1
    elif (lb > -0.5) and (lb < 0.5):
        return 0
    else:
        return -1


def remove_pattern(input_txt, pattern):
    r = re.findall(pattern, input_txt)
    for i in r:
        input_txt = re.sub(i, '', input_txt)
    return input_txt


def clean_tweets(lst):
    # remove twitter Return handles (RT @xxx:)
    lst = np.vectorize(remove_pattern)(lst, "RT @[\w]*:")
    # remove twitter handles (@xxx)
    lst = np.vectorize(remove_pattern)(lst, "@[\w]*")
    # remove URL links (httpxxx)
    lst = np.vectorize(remove_pattern)(lst, "https?://[A-Za-z0-9./]*")
    # remove special characters, numbers, punctuations (except for #)
    lst = np.core.defchararray.replace(lst, "[^a-zA-Z#]", " ")
    return lst

#Key and token for accessing twitter via twitter developer account
consumer_key = 'S2awhuGWYnCvOVZn8BnJyih7c'
consumer_secret = 'kdQCHWzwCeesmlluKfvzgcZ4eCw6lGo59l07WGDm5GiJNv9kjQ'
access_token = '1098892792330403840-fqYkYSKNQmAaxzxkU2yzlAEtZ2RVcJ'
access_token_secret = 'SZUerBXn7KmSVyY8Fctbu3SqFPFGfws9r6OIZu7HyZ8ME'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


def list_tweets(user_id, count, prt=False):
    tweets = api.user_timeline("@" + user_id, count=count, tweet_mode='extended')
    tw = []
    for t in tweets:
        tw.append(str(clean_tweets(t.full_text)))
        if prt:
            print(t.full_text)
            print()
    return tw


# user_id = 'realDonaldTrump'
# count = 10


def anl_tweets(lst, title):
    sents = []
    for tw in lst:
        try:
            st = sentiment_analyzer_scores(tw)
            sents.append(st)
        except:
            sents.append(0)
    ax = sns.distplot(
        sents,
        kde=False,
        bins=3)
    ax.set(xlabel='Negative             Neutral             Positive',
           ylabel='#Tweets',
           title="Tweets of @"+user_id)
    fig = ax.get_figure()
    fig.savefig("./static/output.png")
    return sents


# fahimkhan20148
#-------------- flask code starts here ----------------
app = Flask(__name__)


@app.route("/")
def home():
    return render_template('home.html')


@app.route('/', methods=['POST'])
def getValue():
    global user_id, count
    user_id = uname = request.form['username']
    count = ntweets = request.form['notweets']
    all_list = list_tweets(user_id, count)
    anl_tweets(all_list,user_id)
    return render_template('pass.html',u=uname,n=ntweets,tws= all_list)

# @app.route('/',methods=["GET"])
# def back():
#     if(request.form['back']):
#         os.remove('./static/output.png')
#     return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)

