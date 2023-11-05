from threading import Thread
from flask import current_app,url_for
from flask_mail import Message
from app import mail
from flask import render_template
import os
from config import Config



def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)
        print(True)

def user(app,text_body,receiver_u):
        with app.app_context():
            msg = Message(subject="Report", sender=current_app.config['ADMINS'][0], recipients=receiver_u)
            msg.body =text_body
            mail.send(msg)

def user_(app,sender_u,text_body,receiver_u):
        with app.app_context():
            msg = Message(subject="Report", sender=sender_u, recipients=receiver_u)
            msg.body =text_body
            mail.send(msg)

def _user_(app,sender_u,text_body):
        with app.app_context():
            msg = Message(subject="Report", sender=sender_u, recipients=current_app.config['ADMINS'][0])
            msg.body =text_body
            mail.send(msg)             

def send_email(app, recipients, text_body,
               attachments=None, sync=False):
    with app.app_context():
        msg = Message(subject="verification", sender="noreply@demo.com", recipients=recipients)
        msg.body = text_body
        #msg.html = html_body
        if attachments:
            for attachment in attachments:
                msg.attach(*attachment)
        if sync:
            mail.send(msg)
            print(True)
        else:
            Thread(target=send_async_email,
                args=(current_app._get_current_object(), msg)).start()

def skelet_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def Report(sender_u,text_body):
    Thread(target=_user_,
            args=(current_app._get_current_object(), sender_u,text_body)).start()


def invitation_email(token,email,sender,r):
    msg = Message('You have been invited to oodaay',
                  sender=sender,
                  recipients=[email])
    
    msg.body = f''' To join odaay,visit the following link:
                {r}
     
                if you did not make this request then simply ignore this email and no changes will be made
                '''
    mail.send(msg)

def verify_email(email,r):
    skelet_email('Verify your  odaaay account['+str(r)+']',
               sender='noreply@odaaay.com',
               recipients=[email],
               text_body=f''' To reset your odaaay account password,Input the code below back in the app,
                
                if you did not make this request then simply ignore this email and no changes will be made
                ''',
               html_body=render_template('verify_code.html',code=r)) #os.path.join(destination,'verifycode.html')

def welcome_email(email,N):
    skelet_email('Welcome to odaaay',
               sender='noreply@odaaay.com',
               recipients=[email],
               text_body=f''' To reset your odaaay account password,Input the code below back in the app,
                
                if you did not make this request then simply ignore this email and no changes will be made
                ''',
               html_body=render_template('welcome.html',name=N))

def reset_password(email,r):
    skelet_email('Reset your  odaaay account password',
               sender='noreply@odaaay.com',
               recipients=[email],
               text_body=f''' To reset your odaaay account password,visit the following link:  
     
                if you did not make this request then simply ignore this email and no changes will be made
                ''',
               html_body=render_template('password_change.html',code=r))

def delete_account(email,link):
    skelet_email('Delete Account ?',
               sender='noreply@odaaay.com',
               recipients=[email],
               text_body=f''' To delete your odaaay account password,visit the following link:  
     
                if you did not make this request then simply ignore this email and no changes will be made
                ''',
               html_body=render_template('delete_confirm.html',link=link))

def account_deleted(email):
    skelet_email('Your account has been deleted',
               sender='noreply@odaaay.com',
               recipients=[email], 
               text_body=f''' Your account has been deleted
                ''',
               html_body=render_template('delete_account.html'))

def subscription_message(email,image,subscribed_to):
    
    
    skelet_email('Thanks for subscribing',
               sender='noreply@odaaay.com',
               recipients=[email], 
               text_body=f''' You have subscribed to the following
                ''',
               html_body=render_template('subscription.html',subscribed_to=subscribed_to,image=image))
    





