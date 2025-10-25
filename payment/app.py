from flask import Flask, render_template, redirect, url_for, request, jsonify
import stripe
import os

app = Flask(__name__)

# 🔑 Stripe configuration
stripe.api_key = "sk_test_51SLaU82MYkeS4aDcGx9d6xBvvLWZRkPpAXov1ZzBlnIncOlXY2LSnBVpBVvgE1uJfb2w9AlBsPRZGfwz1JMjISUN004yUlMVig"  # replace with your own secret key

YOUR_DOMAIN = "http://127.0.0.1:5000"

@app.route('/')
def home():
    return render_template('chatbot.html')

@app.route('/go-to-payment', methods=['POST'])
def go_to_payment():
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Premium Plan',
                    },
                    'unit_amount': 999,  # $9.99
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success',
            cancel_url=YOUR_DOMAIN + '/cancel',
        )
        return jsonify({'url': checkout_session.url})
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/cancel')
def cancel():
    return render_template('cancel.html')

if __name__ == '__main__':
    app.run(debug=True)
