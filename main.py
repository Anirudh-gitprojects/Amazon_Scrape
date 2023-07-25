from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import csv
from selenium.webdriver.support.wait import WebDriverWait as wait
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions
import pandas as pd

# initialize driver
driver=webdriver.Firefox()

# add IE
ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)

# get site url
driver.get("https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1")

count=0

#declare list variables
product_asin = []
product_name = []
product_price = []
product_ratings = []
product_ratings_num = []
product_link = []

p_description_arr=[]
product_manufacturer_arr=[]
description_arr=[]

#initialize fields for csv
fields = ['Name', 'Price', 'Rating', 'Reviews','URL', 'Description', 'ASIN', 'Product Description', 'Manufacturer']
filename = "amazon_scrape_list.csv"

with open(filename, 'w',encoding="utf-8") as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(fields)
    print('Scraping...')
    while(count<20):
        items = wait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "s-result-item s-asin")]')))
        for item in items:
        # find name
            name = item.find_element(By.XPATH, './/span[@class="a-size-medium a-color-base a-text-normal"]')
            product_name.append(name.text)

        # find ASIN
            data_asin = item.get_attribute("data-asin")
            product_asin.append(data_asin)

        # find Links
            link = item.find_element(By.CLASS_NAME,"a-link-normal")
            product_link.append(link.get_attribute("href"))

        # find price
            try:
                whole_price = item.find_element(By.XPATH, './/span[@class="a-price-whole"]')
                if whole_price!=[]:
                        product_price.append(whole_price.text)
                else:
                    whole_price=0
                    product_price.append(whole_price)
            except:
                product_price.append('0')

            ratings_box = item.find_elements(By.XPATH, './/div[@class="a-row a-size-small"]/span')

             # find ratings and reviews
            if ratings_box != []:
                ratings = ratings_box[0].get_attribute('aria-label')
                ratings_num = ratings_box[1].get_attribute('aria-label')
            else:
                ratings, ratings_num = 0, 0

            product_ratings.append(ratings)
            product_ratings_num.append(str(ratings_num))


            # write to csv
            csvwriter.writerows(

            [[name.text, whole_price.text, ratings, ratings_num, link.get_attribute('href')]])

        # Go to next page
        clickable = wait(driver, 10, ignored_exceptions=ignored_exceptions) \
        .until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "s-pagination-next")))
        clickable.click()
        count += 1

# Print for reference
#print(len(product_name))
#print(len(product_asin))
#print(len(product_price))
#print(len(product_ratings))
#print(len(product_ratings_num))
#print((product_link))


# Hit links from product_link list
for i in product_link[:200]:
    driver.get(i)
    # Get Manufacturer if exists else append UNKNOWN
    try:
        manufacturer=driver.find_elements(By.CSS_SELECTOR,"#detailBulletsWrapper_feature_div li span")
        product_desc=[m.text for m in manufacturer]
        first_match = next(
            (n for n in product_desc if n.startswith('Manufacturer')),
            'UNKNOWN'
        )
        product_manufacturer_arr.append(first_match[15:])
    except:
        product_manufacturer_arr.append('UNKNOWN')

    try:
        p_description=driver.find_element(By.CSS_SELECTOR,"#productDescription p>span")
        p_description_arr.append(p_description.text)
    except:
        p_description_arr.append('None')

    try:
        description=driver.find_element(By.CSS_SELECTOR,"#feature-bullets")
        description_arr.append(description.text)

    except:
        description_arr.append('None')

driver.close();

# Write to csv the above data
df = pd.read_csv('amazon_scrape_list.csv')
df['Manufacturer'] = product_manufacturer_arr
df['ASIN']=product_asin
df['Product Description']= p_description_arr
df['Description']= description_arr
df.to_csv('amazon_scrape_list.csv', index=False)

