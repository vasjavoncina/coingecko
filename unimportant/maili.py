import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def email_alert(subject, body, to):
    user = "vasja.voncina123@gmail.com"
    password = "dyphwqvtshlbunmf"

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = user
    msg['To'] = to
    
    html = f'<html><body><p>Brt, buraz moj, nove linke mam za tbe:<br>{body}</p></body></html>'
    part2 = MIMEText(html, 'html')
    msg.attach(part2)
    server = smtplib.SMTP_SSL('smtp.gmail.com')
    server.login(user, password)
    server.sendmail(user, to, msg.as_string())
    print("Emails sent.")
    server.quit()


def send_mails_new_coins(coins):
    body = ''
    
    if len(coins) > 0:
        for coin in coins:
            body += coin.name + ": " + coin.gecko_link + "<br>"
    
        to = ["peter.peternik123@gmail.com"] #, "ozmec7@gmail.com", "julijan.gorensek@gmail.com"]
        for mail in to:
            email_alert("new coins", body, mail)
    else:
        print("No new links available.")