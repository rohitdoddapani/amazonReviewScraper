from flask import Flask, redirect, url_for, render_template, request
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import math
import time

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

# Initialize the Flask application
app = Flask(__name__)

@app.route('/')
def index():
   return render_template('product_info.html')

@app.route('/loading',methods = ['POST', 'GET'])
def loadingFunc():
    if request.method == 'POST' and request.form['productUrl']!='':
        url = request.form['productUrl']
    return render_template('loading.html', my_data = url)

@app.route('/product') 
def getUrl():
    if request.args.to_dict(flat=False)['data'][0]:
        data = str(request.args.to_dict(flat=False)['data'][0])
        print(data)
        # url = request.form['productUrl']
        url = data
        response = requests.get(url,headers=headers)
        amz_link = response.url.split("/")[2]
        product_title = response.url.split("/")[3]
        asin = response.url.split("/")[5]
        print(product_title,asin)

        gen_l = "https://"+amz_link+"/"+product_title+"/product-reviews/"+asin+"?pageNumber=1"
        time.sleep(2)
        page1 = requests.get(gen_l,headers=headers)
        soupA = bs(page1.content,'html.parser')

        x=''
        y=''
        while(len(x)==0 or x=='None'):
            gen_l = "https://www.amazon.in/"+product_title+"/product-reviews/"+asin+"?pageNumber=1"
            time.sleep(2)
            page1 = requests.get(gen_l,headers=headers)
            soupA = bs(page1.content,'html.parser')
            reviewC = soupA.find("div",{"data-hook":"cr-filter-info-review-rating-count"})
            x=str(reviewC)
            print(gen_l,page1,x,len(x))
            x_sen = x.split('\n')
            try:
                y=x_sen[4][30:40]
            except IndexError:
                pass
            
        z=''
        for i in y:
            if(i.isdigit()):
                z+=i

        #pageCount = math.ceil(int(''.join(y.split(',')))/10)
        pageCount = int(z)
        print(pageCount)

        cust_name_main = []
        review_title = []
        rate_main = []
        review_content = []
        pageno=1
        d_l=0

        try:
            while(pageno<pageCount):
                #pageno=1
                if(pageno<1):
                    pageno=1
                #getting link page wise
                gen_link = "https://www.amazon.in/"+str(product_title)+"/product-reviews/"+str(asin)+"?pageNumber="+str(pageno)
                # print(gen_link)
                # time.sleep(2)
                page = requests.get(gen_link,headers=headers,verify=False)
                # print(page)
                soup = bs(page.content,'html.parser')
                #fetching customer names
                names = soup.find_all('span',class_='a-profile-name')
                cust_name = []
                for i in range(0,len(names)):
                    cust_name.append(names[i].get_text())
                #popping two names because of extra top rating on each page
                if(len(cust_name)!=0):
                    cust_name.pop(0)
                    cust_name.pop(0)
                
                cust_name_main.extend(cust_name)

                #fetching title of the review
                title = soup.find_all('a',class_='review-title-content')
                # review_title = []
                for i in range(0,len(title)):
                    review_title.append(title[i].get_text())

                review_title[:] = [titles.lstrip('\n') for titles in review_title]
                review_title[:] = [titles.rstrip('\n') for titles in review_title]
                
                #fetching rating for the review
                rating = soup.find_all('i',class_='review-rating')
                rate = []
                for i in range(0,len(rating)):
                    rate.append(rating[i].get_text())
                if(len(rate)!=0):
                    rate.pop(0)
                    rate.pop(0)
                rate_main.extend(rate)

                #fatching content(body) of the review
                review = soup.find_all("span",{"data-hook":"review-body"})
                # review_content = []
                for i in range(0,len(review)):
                    review_content.append(review[i].get_text())

                review_content[:] = [reviews.lstrip('\n') for reviews in review_content]
                review_content[:] = [reviews.rstrip('\n') for reviews in review_content]
                if(len(cust_name_main)==d_l):
                    pass
                else:
                    d_l = len(cust_name_main)
                    pageno+=1
                # print(len(cust_name_main))
                # print(len(review_title))
                # print(len(rate_main))
                # print(len(review_content))
                # time.sleep(1)

            df = pd.DataFrame()
            df['Customer Name']=cust_name_main
            df['Review title']=review_title
            df['Ratings']=rate_main
            df['Reviews']=review_content
            fileName = product_title+".csv"
            df.to_csv(fileName,index=True)
            print("done extracting!")
            return render_template('success.html', fileName = fileName)
            # return redirect(url_for('success'))

        except:
            df = pd.DataFrame()
            df['Customer Name']=cust_name_main
            df['Review title']=review_title
            df['Ratings']=rate_main
            df['Reviews']=review_content
            fileName = product_title+".csv"
            df.to_csv(fileName,index=True)
            print("done extracting with exception!")
            return render_template('success.html', fileName = fileName)
    else:
        return redirect(url_for('index'))   

# @app.route('/success')
# def success():

#    return 'csv file saved'
	
if __name__ == '__main__':
   app.run(debug = True)