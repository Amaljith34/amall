from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from transformers import pipeline
import chromedriver_binary
from selenium.webdriver.common.by import By
from wordcloud import WordCloud 
import matplotlib.pyplot as plt
from io import BytesIO, StringIO
import base64


# flask object
app = Flask(__name__)
                    
# Twitter scraping function
def twitter_scrape(search_query):
    service = webdriver.chrome.service.Service(executable_path='C:/Users/chait/OneDrive/Desktop/twitter_deploy1/twitter_deploy/chromedriver-win64/chromedriver-win64/chromedriver.exe')
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Add this line to run Chrome in headless mode
    # options.add_argument("--disable-gpu")
    # options.add_argument("--window-size=1920x1080")
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get("https://twitter.com/explore")
    driver.maximize_window()
    time.sleep(3)

    # Login to Twitter (assuming the class names are correct)
    username = driver.find_element(By.CLASS_NAME, "r-1dz5y72.r-13qz1uu")
    username.send_keys("scrapy632356143")  
    time.sleep(3)
    next=driver.find_element(By.XPATH,'//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div')
    next.click()
    time.sleep(3)
    password = driver.find_element(By.CLASS_NAME,"r-deolkf.r-homxoj ")     
    # password.click()
    password.send_keys("scrapy673002")  
    time.sleep(3) 
    
    login=driver.find_element(By.XPATH,'//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div/div')
    login.click()
    time.sleep(4)

    # Go to Explore
    explore=driver.find_element(By.XPATH,'//*[@data-testid="AppTabBar_Explore_Link"]')
    explore.click()
    time.sleep(2)

    # Search for the given query
    search_xpath = '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[1]/div[1]/div[1]/div/div/div/div/div[1]/div[2]/div/div/div/form/div[1]/div/div/div/label/div[2]/div/input'

    # Find the search element and send keys
    search_element = driver.find_element(By.XPATH, search_xpath)
    search_element.send_keys(search_query)
    search_element.send_keys(Keys.ENTER)
    time.sleep(3)
    # Scroll down to load more tweets
    total_height = int(driver.execute_script("return document.body.scrollHeight"))
    for i in range(1, total_height, 5):
        driver.execute_script("window.scrollTo(0, {});".format(i))

    # Extract tweet data
    data = driver.find_elements(By.XPATH, '//*[@data-testid="tweetText"]')
    # twit1 = [d.text for d in data]
    twit1=[]
    for d in data:
        print(d.text)
        twit1.append(d.text)

    # Close the driver
    driver.quit()

    # Return tweet data
    return twit1

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    # Get search query from form
    search_query = request.form['search_query']

    # Scrape Twitter for the given query
    twit1 = twitter_scrape(search_query)

    # Create a DataFrame
    df = pd.DataFrame({'post': twit1})
    print('dataframe',df)
    # Sentiment analysis using transformers pipeline
    nlp_sentence = pipeline('sentiment-analysis')
    # df['post'] = df['post'].apply(lambda x: nlp_sentence(x)[0]['label'])
    df=df['post']
    def predict_toxicity(comment):
        sentiment = nlp_sentence(comment)
        return sentiment[0]['label']
    def count_toxicity(df):
        positive_count = 0
        negative_count = 0
        for comment in df:
            sentiment = predict_toxicity(comment)
            if sentiment == 'NEGATIVE':
                
                positive_count += 1
            else:
                negative_count += 1
    
        total_comments = positive_count + negative_count
        positive_percentage = (positive_count / total_comments) * 100
        negative_percentage = (negative_count / total_comments) * 100
        return positive_percentage, negative_percentage
    #get the analysis percentage
    positive_percentage_total, negative_percentage_total = count_toxicity(df)
    positive_percentage=(f"Percentage of Positive comments: {positive_percentage_total:.2f}%")
    negative_percentage=(f"Percentage of Negative comments: {negative_percentage_total:.2f}%")
    
    text = df.values 

    # Count positive and negative sentiment percentages
    # positive_percentage = (df[df['post'] == 'POSITIVE'].shape[0] / df.shape[0]) * 100
    # negative_percentage = 100 - positive_percentage

    # Translate posts to English (uncomment if needed)
    # translator = Translator()
    # df['post'] = df['post'].apply(lambda x: translator.translate(x, dest='en').text)

    # Generate Word Cloud
    # text = df['post'].values
    # wordcloud = WordCloud().generate(str(text))

    # # Convert Word Cloud image to base64
    # img = BytesIO()
    # wordcloud.to_image().save(img, format='PNG')
    # img.seek(0)
    # img_base64 = base64.b64encode(img.getvalue()).decode()

    # Generate Word Cloud
    wordcloud = WordCloud().generate(str(text))

    # Convert Word Cloud image to base64 to display in HTML
    img = BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    img.seek(0)
    img_base64 = base64.b64encode(img.getvalue()).decode()


    # Visualize sentiment analysis results
    labels = ['POSITIVE', 'NEGATIVE']
    counts = [positive_percentage_total, negative_percentage_total]

    plt.figure(figsize=(4, 3))
    plt.bar(labels, counts)
    plt.title('Positive vs. Negative Twitter Posts')

    # Save plot to a BytesIO object
    img_plot = BytesIO()
    plt.savefig(img_plot, format='png')
    img_plot.seek(0)

    # Convert the plot image to base64 encoding
    img_base64plot = base64.b64encode(img_plot.getvalue()).decode()
    
    plt.close()  # Close the plot to release memory

    return render_template('boot.html', positive_percentage=positive_percentage, negative_percentage=negative_percentage, img_base64=img_base64,img_base64plot=img_base64plot)

if __name__ == '__main__':
    app.run(debug=True)









# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium import webdriver
# import chromedriver_binary
# from urllib.request import urlopen
# from selenium.webdriver.support.select import Select
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium import webdriver as selenium_webdriver
# import time
# from selenium.webdriver.chrome.service import Service
# import pandas as pd
# from selenium.webdriver.common.by import By
# service = Service(executable_path=r'C:\Users\user\Desktop\amaljith\chromedriver.exe')
# options = webdriver.ChromeOptions()
# driver = webdriver.Chrome(service=service, options=options)
# driver.get("https://www.flipkart.com/search?q=iphone+13")
# driver.maximize_window()
# time.sleep(5)

# names=[]
# name=driver.find_elements(By.CLASS_NAME,'_4rR01T')
# # print(name.text)
# for i in name:
#     names.append(i.text)
# print(names)
# prices=[]
# price=driver.find_elements(By.CLASS_NAME,'_1_WHN1')
# for i in price:
#     prices.append(i.text)
# print(prices)
# data= pd.DataFrame({"Name":names,"price":prices})
# data.to_csv('flipkart.csv')      

