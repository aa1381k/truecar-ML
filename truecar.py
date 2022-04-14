import mysql.connector
import re
import requests
from bs4 import BeautifulSoup
from sklearn import tree, preprocessing
import numpy as np

x = []

connection = mysql.connector.connect(
    user="root",
    password="",
    host="localhost",
    database="test"
)
cursor = connection.cursor()


def add_database(name, year, km2, gearbox2, fuel, price):
    if km2 != "" and km2 != re.findall("\d+", str(km2)):
        query = ("""SELECT * from cars WHERE name='%s'and year='%s' and price='%s' """ %
                 (name, year, price))
        cursor.execute(query)
        car_status = cursor.fetchone()
        if car_status == None:
            query = ("""INSERT INTO cars value("%s","%s","%s","%s","%s","%s")""" % (
                name, year, km2, gearbox2, fuel, price))
            cursor.execute(query)
            connection.commit()

def ML():
    data2 = []
    data3 = []
    price2 = []
    query = "SELECT name , gearbox ,fuel FROM cars "
    cursor.execute(query)
    data = cursor.fetchall()

    query = "SELECT year , km FROM cars"
    cursor.execute(query)
    info = cursor.fetchall()

    query = "SELECT price FROM cars"
    cursor.execute(query)
    price = cursor.fetchall()

    for i in range(0, len(price)):
        price2.append(list(price[i]))

    array = np.array(price2)
    result = array.flatten()
    result = list(result)

    for i in range(len(result)):
        if result[i] != "":
            result[i] = int(result[i])

    for i in data:
        data2.append(list(i))
    le = preprocessing.LabelEncoder()

    for i in data2:
        le.fit(i)
        transform = le.transform(i)
        transform = list(transform)
        data3.append(transform)

    for i in range(len(info)):

        info2 = info[i]
        transform2 = data3[i]
        transform2.append(int(info2[0]))
        transform2.append(int(info2[1]))
        x.append(transform2)

    for i in range(len(result)):

        clf = tree.DecisionTreeClassifier()
        clf = clf.fit(x, result)
    return clf


car_name = input("enter your car name: ")

car_name = (
    "https://www.truecar.com/used-cars-for-sale/listings/%s/location-little-rock-ar" % car_name)
webpage = requests.get(car_name)
soup = BeautifulSoup(webpage.text, "html.parser")
link = soup.find_all(
    "a", attrs={"class": "linkable order-2 vehicle-card-overlay"})
link2 = []
for i in link:
    link2.append(re.findall(r"""(?<=href=").*?(?=")""", str(i)))

print("searching......")
# print(link2)


for i in range(len(link2)):
    link = link2[i]
    webpage = requests.get(("https://www.truecar.com"+link[0]))
    soup = BeautifulSoup(webpage.text, "html.parser")

    car = (soup.find("div", attrs={"class": "heading-2 margin-bottom-2"})).text
    car = car.split(' ')
    for i in range(1,len(car)):
        if car[i] != '':
            car_name += car[i]

    car_name = car_name.replace('https://www.truecar.com/used-cars-for-sale/listings/porsche/location-little-rock-ar','')
    car_name = car_name.lower()
    car_year = car[0]
    car_price = ((soup.find("div", attrs={"class": "heading-2 margin-top-1"}).text).replace('$','')).replace(',','')
    car_mile =( soup.find("p", {"class": "margin-top-1"}).text).replace(',','')
    car_info = soup.find_all("div", {"class": "margin-top-5 col-6 col-md-4 col-lg-3"})
    car_info_len = len(car_info)
    car_gearbox = car_info[car_info_len-1].text
    car_gearbox = car_gearbox.replace('Transmission','').lower()
    car_fuel = car_info[car_info_len-2].text
    car_fuel = car_fuel.replace('Fuel Type','').lower()

    # print(f'{car_name} \n{car_year} \n{car_mile} \n{car_fuel} \n{car_price} \n{car_gearbox}','\n')
    # print("-------------------------")
    add_database(car_name, car_year, car_mile, car_gearbox, car_fuel, car_price)
    car_name = ''


mashine = ML()

for i in range(2):
    car_name = input("Enter Car Name: ")
    car_gearbox = input("Enter Car Gearbox Type: ")
    car_fuel = input("Enter Car Fuel: ")
    car_year = input("Enter Car Year: ")
    car_km = input("Enter Car Km: ")
    data2 = ([car_name, car_gearbox, car_fuel])
    le = preprocessing.LabelEncoder()
    le.fit(data2)
    transform = le.transform(data2)
    transform = list(transform)
    transform.append(car_year)
    transform.append(car_km)
    for info in range(len(transform)):
        transform[info] = int(transform[info])
    per = mashine.predict([transform])
    per = per[0]
    print(per)

