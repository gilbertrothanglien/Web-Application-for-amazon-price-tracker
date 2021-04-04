from bs4 import BeautifulSoup
import requests
import sqlite3
import datetime
import smtplib

db = sqlite3.connect("database.db", check_same_thread=False)

def track(url):
    req = requests.get(url, headers={
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.87 Safari/537.36"})
    soup = BeautifulSoup(req.content, 'html5lib')

    pr = soup.find('span', id=lambda x: x and x.startswith('priceblock_')).text
    con_pr = pr[1:]
    converted_price = con_pr.strip()
    newprice = ''
    for con in converted_price:
        if con != ',':
            newprice = newprice + con
    newprice = float(newprice)
    return newprice


def mail(m_mail, pro_name, cu_price, url):
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login('cs50pricetracker@gmail.com', 'cs50trackprice')
        body = f"The price of your product {pro_name} has dropped to {cu_price}. Please visit the url to check your product! \n {url}"
        msg = f"Subject: The price has dropped \n\n {body} \n CS50Pricetracker.com"
        smtp.sendmail('cs50pricetracker@gmail.com', m_mail, msg)


def main():
    while True:
        p_url = db.execute("SELECT product_url FROM track ")
        uid = db.execute("SELECT user_id FROM track ")
        p_price = db.execute("SELECT price FROM track")
        p_name = db.execute("SELECT product_name FROM track")
        t_time = db.execute("SELECT track_time FROM track")

        url = []
        u_id = []
        price = []
        product_name = []

        for p in p_price:
            price.append(p[0])

        for u in p_url:
            url.append(u[0])

        for n in p_name:
            product_name.append(n[0])

        for i in uid:
            u_id.append(i[0])

        for i in range(len(url)):
            try:
                cu_price = track(url[i])
            except:
                pass
            u_mail = ''
            if price[i] > cu_price or price[i] == cu_price:
                try:
                    umail = db.execute("SELECT email FROM users WHERE id = ?", (u_id[i],))
                    for m in umail:
                        u_mail = m[0]
                    mail(u_mail, product_name[i], cu_price, url[i])
                    db.excute("DELETE FROM track WHERE product_url=?",(url[i],))
                    print("success")
                except:
                    pass
            else:
                pass


main()
