# ========================= Refer to requirements.txt =================================================================================================================

import requests
import simplejson as json
from flask import Flask, render_template, request, url_for
import csv
from datetime import datetime
from requests_oauthlib import OAuth1
import os

try:
  from SimpleHTTPServer import SimpleHTTPRequestHandler as Handler
  from SocketServer import TCPServer as Server
except ImportError:
  from http.server import SimpleHTTPRequestHandler as Handler
  from http.server import HTTPServer as Server



# ========================= Port & App initialization ================================================================================================================

#Use the PORT environment variable in BlueMix environment; default to 8000
PORT = int(os.getenv('PORT', 8000))                        

app = Flask(__name__)                                     

              

# ========================= Function to handle requests to home page==================================================================================================

#Handle all requests to the home page via this function
@app.route('/')                                           
def form():
    #Serve the index.html web page; Caching of CSS, data prevented by using the nocache parameter in HTML
    return render_template('index.html')



# ========================= Function to process requests & return results ============================================================================================

#Process the input and serve the results as http://twitter-psychographics.mybluemix.net/results
@app.route('/results', methods=['POST'])
def results():
    #Grab the user input, sent to the server via POST
    twitter_handle = request.form['q']
    
    #Handle variations in input: @POTUS vs POTUS
    if(twitter_handle[0:1] == "@"):
      twitter_handle=twitter_handle[1:len(twitter_handle)]
    print(twitter_handle)

    #Initialize counters & variables
    tweet_count = 0
    texty=""
    d3input=""
    csv_init=""



    # ========================= Initialize Twitter & Watson API parameters ===========================================================================================

    #Using Twitter API GET statuses/user_timeline. Refer to https://dev.twitter.com/rest/reference/get/statuses/user_timeline
    twitter_url="https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=" + twitter_handle + "&count=1000&include_rts=1"

    #Using Watson Personality Insights API service. Refer to https://www.ibm.com/smarterplanet/us/en/ibmwatson/developercloud/doc/personality-insights/index.shtml
    watson_api_url="https://gateway.watsonplatform.net/personality-insights/api/v2/profile"
  
    watson_user_name=""                                               #Replace with your Watson API service user name
    watson_pass_word=""                                               #Replace with your Watson API service password

    twitter_consumer_key=""                                           #Replace with your consumer key 
    twitter_consumer_secret=""                                        #Replace with your consumer secret 
    twitter_access_token=""                                           #Replace with your access token 
    twitter_access_token_secret=""                                    #Replace with your access token secret 


    
    # ========================= Retrieve Tweets and log Twitter Handle ================================================================================================

    twitter_auth=OAuth1(twitter_consumer_key, twitter_consumer_secret, twitter_access_token, twitter_access_token_secret)
    tweet=requests.get(twitter_url, auth=twitter_auth).json()
    #Each Twitter API call returns 100-200 tweets. So, we loop to send sequential API requests
    #Limiting to ~3000 Tweets (15*200)
    for j in range(1,16):
        #Break loop if Twitter returns empty result set.
        if(len(tweet)>1):
            tweet_count = tweet_count + len(tweet)
            print("Extracted " + str(tweet_count) + " Tweets...")
            #Grab the text portion of the tweet and append to texty variable
            for i in range(0,len(tweet)):
              texty=texty+". "+tweet[i]['text'].encode('utf-8')
            #At the end of the for loop, i will point to the last tweet in the result set
            #By default, this tweet will be the oldest tweet with the lowest id value
            #Use this field as the input for the max_id field for the subsequent Twitter API call
            min_id = tweet[i]['id']
            url1 = twitter_url + "&max_id=" + str(min_id)
            #Send subsequent request to Twitter, using the modified URL  
            tweet=requests.get(url1, auth=twitter_auth).json()

    #Log the twitter handle we have made API calls onr
    k = open("static/InputLog.txt", "r+")
    #Set file pointer at the end of the file
    k.seek(1, 2)
    #Log the timestamp and the twitter handle on a new line
    twit_log = "\n" + str(datetime.now()) + " | " + twitter_handle
    k.write(twit_log)
    k.close()


    
    # ========================= Call Watson Personality Insights API service & parse results ==========================================================================
  
    #Request Watson to accept input in plain text format and the results to be sent back in csv format
    watson_headers={'Content-Type': 'text/plain', 'accept': 'text/csv'}

    #Send over the parsed compilation of Tweets from above as input
    watson_results=requests.post(watson_api_url, auth=(watson_user_name, watson_pass_word), data = texty, headers=watson_headers)

    csv_init = watson_results.content

    #Parse the CSV output file
    #Extract the main scores for the Big 5 Personality traits
    #To be used for generating the results summary
    csv_init = csv_init.split(",")
    s1 = int(float(csv_init[2])*100)        #Agreeableness
    s2 = int(float(csv_init[9])*100)        #Conscientiousness
    s3 = int(float(csv_init[16])*100)       #Extraversion
    s4 = int(float(csv_init[23])*100)       #Emotional Range
    s5 = int(float(csv_init[30])*100)       #Openness

    #Calculate weighted average of each one of the sub-component traits
    #To be used for constructing the stacked bar chart in d3.js
    t1 = float(csv_init[3])+float(csv_init[4])+float(csv_init[5])+float(csv_init[6])+float(csv_init[7])+float(csv_init[8])          #Agreeableness
    t2 = float(csv_init[10])+float(csv_init[11])+float(csv_init[12])+float(csv_init[13])+float(csv_init[14])+float(csv_init[15])    #Conscientiousness
    t3 = float(csv_init[17])+float(csv_init[18])+float(csv_init[19])+float(csv_init[20])+float(csv_init[21])+float(csv_init[22])    #Extraversion
    t4 = float(csv_init[24])+float(csv_init[25])+float(csv_init[26])+float(csv_init[27])+float(csv_init[28])+float(csv_init[29])    #Emotional Range
    t5 = float(csv_init[31])+float(csv_init[32])+float(csv_init[33])+float(csv_init[34])+float(csv_init[35])+float(csv_init[36])    #Openness

    #Store the parsed results in a CSV file
    #This will serve as the input for d3.js for constructing the stacked bar chart
    #Write the header/column list first
    d3in_txt = "trait, Attribute 1, Attribute 2, Attribute 3, Attribute 4, Attribute 5, Attribute 6"
    #Agreeableness - Sub-component traits
    #Altruism, Cooperation, Modesty, Morality, Sympathy, Trust 
    d3in_txt = d3in_txt + "\n" + "Agreeableness, " + str((float(csv_init[3])*s1)/t1) + ", " + str((float(csv_init[4])*s1)/t1) + ", " + \
                                                     str((float(csv_init[5])*s1)/t1) + ", " + str((float(csv_init[6])*s1)/t1) + ", " + \
                                                     str((float(csv_init[7])*s1)/t1) + ", " + str((float(csv_init[8])*s1)/t1)
    #Conscientiousness - Sub-component traits
    #Achievement striving, Cautiousness, Dutifulness, Orderliness, Self-discipline, Self-efficacy 
    d3in_txt = d3in_txt + "\n" + "Extroversion, " + str((float(csv_init[17])*s3)/t3) + ", " + str((float(csv_init[18])*s3)/t3) + ", " + \
                                                     str((float(csv_init[19])*s3)/t3) + ", " + str((float(csv_init[20])*s3)/t3) + ", " + \
                                                     str((float(csv_init[21])*s3)/t3) + ", " + str((float(csv_init[22])*s3)/t3)
    #Extraversion - Sub-component traits
    #Activity level, Assertiveness, Cheerfulness, Excitement-seeking, Friendliness, Gregariousness 
    d3in_txt = d3in_txt + "\n" + "Openness, " + str((float(csv_init[31])*s5)/t5) + ", " + str((float(csv_init[32])*s5)/t5) + ", " + \
                                                     str((float(csv_init[33])*s5)/t5) + ", " + str((float(csv_init[34])*s5)/t5) + ", " + \
                                                     str((float(csv_init[35])*s5)/t5) + ", " + str((float(csv_init[36])*s5)/t5)  
    #Emotional Range - Sub-component traits
    #Anger, Anxiety, Depression, Immoderation, Self-consciousness, Vulnerability 
    d3in_txt = d3in_txt + "\n" + "Conscientiousness, " + str((float(csv_init[10])*s2)/t2) + ", " + str((float(csv_init[11])*s2)/t2) + ", " + \
                                                     str((float(csv_init[12])*s2)/t2) + ", " + str((float(csv_init[13])*s2)/t2) + ", " + \
                                                     str((float(csv_init[14])*s2)/t2) + ", " + str((float(csv_init[15])*s2)/t2)
    #Openness - Sub-component traits
    #Adventurousness, Artistic interests, Emotionality, Imagination, Intellect, Liberalism 
    d3in_txt = d3in_txt + "\n" + "Emotional Range, " + str((float(csv_init[24])*s4)/t4) + ", " + str((float(csv_init[25])*s4)/t4) + ", " + \
                                                     str((float(csv_init[26])*s4)/t4) + ", " + str((float(csv_init[27])*s4)/t4) + ", " + \
                                                     str((float(csv_init[28])*s4)/t4) + ", " + str((float(csv_init[29])*s4)/t4)
    
    #Store the parsed results in a CSV file
    g = open("static/d3input.csv", "r+")
    #Truncate everything, before copying the results
    #Caching prevented by using the nocache parameter in HTML
    g.seek(0)
    g.truncate()
    g.write(d3in_txt)
    g.close()
               
    #Send over the final.html file as the output
    #Pass the twitter handle & main scores for the Big-5 personality traits as parameters
    #These will be used to update the web page dynamically
    return render_template('final.html', twit=twitter_handle, agreeable_val=s1, conscientious_val=s2, extraversion_val=s3, emotional_val=s4, openness_val=s5)


# ========================= Main Function to fire up the server =======================================================================================================

if __name__ == '__main__':
  #Start up the application on the localhost (i.e. on the BlueMix environment)
  app.run(host='0.0.0.0', port=int(PORT)) 
