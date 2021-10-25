from datetime import datetime

from flask import Flask, jsonify, request, render_template, redirect, url_for
import socket
import base64
import requests

app = Flask(__name__)

clientId = "7c961bbf1210433fb38e99e1e5ee981e"
clientSecret = "EqR+cm2j+Mcbx4KJrfaSTi58x7KwSBAGfe2m3ZTHD32XRlUGDTgwbLSME4rdmVv4RguVQc2BcoTHfKj82v5Hew=="
clientData = f"{clientId}:{clientSecret}"
encodedData = str(base64.b64encode(clientData.encode("utf-8")), "utf-8")
authorizationHeaderString = f"Basic {encodedData}"

storage_list=[]


def update(max_price):
    r = requests.get("https://api.skinport.com/v1/items", headers={
        "authorization": authorizationHeaderString
    }, params={
        "app_id": 730,
        "currency": "DKK"
    }).json()
    higest_diffrences = []
    for i in range(0, len(r)):
        data = r[i]
        min = data["min_price"]
        mean = data["mean_price"]
        max = data["max_price"]
        suggested_price = data["suggested_price"]
        d = 0
        if min is not None and mean is not None and mean<max_price:
            calprofit = suggested_price - mean

            if calprofit > 12:
                my_suggested_price = round((suggested_price * (1 - 0.12)), 2)
                category = 12
            elif calprofit <= 12 and calprofit > 6:
                my_suggested_price = round((suggested_price * (1 - 0.06)), 2)
                category = 6
            elif calprofit <= 6 and calprofit > 3:
                my_suggested_price = round((suggested_price * (1 - 0.03)), 2)
                category = 3
            else:
                my_suggested_price = round((suggested_price * (1 - 0.01)), 2)
                category = 1
            my_price_profit = round((my_suggested_price * (1 - 0.12)), 2)
            diffrence = round(my_suggested_price - mean, 2)
            profit = round(my_price_profit - min, 2)
            if diffrence > 1 and profit > 1:
                if my_suggested_price < suggested_price:
                    higest_diffrences.append((data["market_hash_name"].replace(",","."), min, mean, max, diffrence, suggested_price, my_suggested_price,my_price_profit, profit, category,data["item_page"], data["quantity"]))
    return tuple(higest_diffrences)

@app.route('/')
def index():  # put application's code here
    return render_template("index.html")

@app.route('/data' , methods=['POST',"GET"])
def data():  # put application's code here
    dataresived = request.form.to_dict()
    print(dataresived)
    skin_data=update(float(dataresived["maxPrice"]))
    skin_data=sorted(skin_data, key=lambda tup: tup[8], reverse=True)
    headings = ("name", "min", "mean", "max", "diffrence", "suggested_price", "my_suggested_price", "my_suggested_price-12%","profit", "category", "quantity")
    return render_template("skindata.html", headings=headings, skin_data=skin_data)

@app.route('/storage', methods=["POST"])
def storage():
    item =request.form.to_dict()
    print(item)
    headings = (
        "ID" ,"name", "min", "mean", "max", "diffrence", "suggested_price", "my_suggested_price", "my_suggested_price-12%",
        "profit", "category", "quantity")
    if "data" in item:
        data=item["data"][1:-1].split(",")
        newData = []
        newData.append(len(storage_list))
        newData.append(data[0])
        newData.append(float(data[1]))
        newData.append(float(data[2]))
        newData.append(float(data[3]))
        newData.append(float(data[4]))
        newData.append(float(data[5]))
        newData.append(float(data[6]))
        newData.append(float(data[7]))
        newData.append(float(data[8]))
        newData.append(float(data[9]))
        newData.append(data[10])
        newData.append(float(data[11]))

        passed = False
        for i in storage_list:
            if i[1]==newData[1]:
                passed=True
        if not passed:
            print(newData)
            storage_list.append(newData)

    if "remove" in item:
        data = item["remove"][1:-1].split(",")
        newData = []
        print(data)
        newData.append(float(data[0]))
        newData.append(data[1])
        newData.append(float(data[2]))
        newData.append(float(data[3]))
        newData.append(float(data[4]))
        newData.append(float(data[5]))
        newData.append(float(data[6]))
        newData.append(float(data[7]))
        newData.append(float(data[8]))
        newData.append(float(data[9]))
        newData.append(float(data[10]))
        newData.append(data[11])
        newData.append(float(data[12]))


        for i in storage_list:
            if i[0] == newData[0]:
                storage_list.remove(i)

    total_price = 0
    total_profit = 0
    for i in storage_list:
        total_price += float(i[2])
        total_profit += float(i[9])
    if len(storage_list)==0:
        return redirect(url_for('index'))
    else:
        return render_template("storage.html", headings=headings, skin_data=tuple(storage_list), total_profit=total_profit, total_price=total_price)





if __name__ == '__main__':
    app.run()
