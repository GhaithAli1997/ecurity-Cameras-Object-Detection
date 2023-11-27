# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 18:37:53 2023

@author: ghait
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import torch

def send(tensor):
     txet=''
     class_dict = {0: "person", 2: 'car',3: 'motorcycle',5: 'bus',7: 'truck',15: 'cat',16: 'dog'}
     class_counts = {class_name: 0 for class_name in class_dict.values()}
     for item in tensor:
       class_name = class_dict.get(int(item), "unknown")
       if class_name != "unknown":
         class_counts[class_name] += 1
     for class_name, count in class_counts.items():
         txet+=f"{count} {class_name}s"
     sender_email = 'ghaith.a.ale@gmail.com'  # Your email address
     sender_password = 'dasddsaddfds'  # Your email password but you need to creat App passwerd then used it here
     recipient_email = 'ghaith.a.ale@gmail.com'  # Recipient's email address
     # Create a message object
     msg = MIMEMultipart()
     msg['From'] = sender_email
     msg['To'] = recipient_email
     msg['Subject'] = 'worrning'
     email_body = "There is denger in "+txet
     msg.attach(MIMEText(email_body, 'plain'))
     
     try:        
        server = smtplib.SMTP('smtp.gmail.com', 587,timeout=30)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())

        print("Email sent successfully!")
     except Exception as e:
        print(f"Error: {e}")
     finally:
        server.quit()
