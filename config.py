# email_utils.py

from flask_mail import Mail, Message
from flask import current_app

def send_order_confirmation_email(user_email, order_id, total_amount, address):
    mail = Mail(current_app._get_current_object())
    
    msg = Message('Order Confirmation', recipients=[user_email])
    msg.body = f"""
    Your order has been placed successfully!

    Order ID: {order_id}
    Total Amount: {total_amount} PKR
    Delivery Address: {address}

    Thank you for shopping with us!
    """
    
    mail.send(msg)

def send_payment_confirmation_email(user_email, order_id, total_amount, payment_method, user_fullname):
    mail = Mail(current_app._get_current_object())
    
    subject = f"Transaction Confirmation for Order #{order_id}"
    body = f"""
    <html>
    <body>
        <h2>Transaction Confirmation for Order #{order_id}</h2>
        <p>Dear {user_fullname},</p>
        <p>Your payment of Pkr{total_amount:.2f} has been successfully received for Order #{order_id}.</p>
        <h3>Order Details:</h3>
        <p><strong>Order ID:</strong> {order_id}</p>
        <p><strong>Total Amount:</strong> Pkr{total_amount:.2f}</p>
        <p><strong>Payment Method:</strong> {payment_method}</p>
        <p>Thank you for your order!</p>
    </body>
    </html>
    """
    
    msg = Message(subject, recipients=[user_email])
    msg.html = body
    mail.send(msg)
