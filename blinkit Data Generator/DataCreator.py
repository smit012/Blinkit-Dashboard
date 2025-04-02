import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from faker import Faker

# Set random seed for reproducibility
np.random.seed(150)
fake = Faker('en_IN')


def generate_complete_blinkit_data(num_orders=50000, start_date='2022-01-01', end_date='2025-12-31'):
    # Convert string dates to datetime
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    date_range_days = (end_date - start_date).days

    # 1. Customer Data
    customers = []
    for _ in range(num_orders // 2):  # Assuming each customer makes ~2 orders
        customer = {
            'customer_id': fake.unique.random_number(digits=8),
            'customer_name': fake.name(),
            'email': fake.email(),
            'phone': f"+91{fake.msisdn()[3:]}",
            'address': fake.address(),
            'area': fake.city_name(),
            'pincode': fake.postcode(),
            'registration_date': fake.date_between(start_date=start_date, end_date=end_date),
            'customer_segment': random.choice(['New', 'Regular', 'Premium', 'Inactive']),
            'total_orders': random.randint(1, 20),
            'avg_order_value': round(random.uniform(200, 2000), 2)
        }
        customers.append(customer)

    # 2. Product and Inventory Data
    categories = {
        'Fruits & Vegetables': {'margin': 0.25, 'shelf_life_days': 3},
        'Dairy & Breakfast': {'margin': 0.20, 'shelf_life_days': 7},
        'Snacks & Munchies': {'margin': 0.35, 'shelf_life_days': 90},
        'Cold Drinks & Juices': {'margin': 0.30, 'shelf_life_days': 180},
        'Instant & Frozen Food': {'margin': 0.40, 'shelf_life_days': 180},
        'Grocery & Staples': {'margin': 0.15, 'shelf_life_days': 365},
        'Household Care': {'margin': 0.25, 'shelf_life_days': 365},
        'Personal Care': {'margin': 0.35, 'shelf_life_days': 365},
        'Baby Care': {'margin': 0.30, 'shelf_life_days': 365},
        'Pet Care': {'margin': 0.35, 'shelf_life_days': 365},
        'Pharmacy': {'margin': 0.20, 'shelf_life_days': 365}
    }
    
    products = []
    inventory = []
    
    for cat, details in categories.items():
        num_products = random.randint(15, 30)
        for _ in range(num_products):
            price = round(random.uniform(10, 1000), 2)
            product_id = fake.unique.random_number(digits=6)
            
            product = {
                'product_id': product_id,
                'product_name': fake.word() + ' ' + fake.word(),
                'category': cat,
                'brand': fake.company(),
                'price': price,
                'mrp': round(price / (1 - details['margin']), 2),
                'margin_percentage': details['margin'] * 100,
                'shelf_life_days': details['shelf_life_days'],
                'min_stock_level': random.randint(10, 30),
                'max_stock_level': random.randint(50, 100)
            }
            products.append(product)
            
            # Generate inventory data for date range
            for day in range(date_range_days + 1):
                date = start_date + timedelta(days=day)
                inventory.append({
                    'product_id': product_id,
                    'date': date.date(),
                    'stock_received': random.randint(0, 30),
                    'damaged_stock': random.randint(0, 5),
                })

    # 3. Order Data
    orders = []
    order_items = []
    
    for _ in range(num_orders):
        customer = random.choice(customers)
        order_date = fake.date_time_between(start_date=start_date, end_date=end_date)
        promised_delivery = order_date + timedelta(minutes=random.randint(10, 20))
        
        delivery_scenario = random.random()
        if delivery_scenario < 0.7:
            actual_delivery = promised_delivery + timedelta(minutes=random.randint(-5, 5))
            delivery_status = 'On Time'
        elif delivery_scenario < 0.9:
            actual_delivery = promised_delivery + timedelta(minutes=random.randint(6, 15))
            delivery_status = 'Slightly Delayed'
        else:
            actual_delivery = promised_delivery + timedelta(minutes=random.randint(16, 30))
            delivery_status = 'Significantly Delayed'
            
        order_id = fake.unique.random_number(digits=10)
        num_items = random.randint(1, 8)
        order_products = random.sample(products, num_items)
        order_total = sum(p['price'] for p in order_products)
        
        order = {
            'order_id': order_id,
            'customer_id': customer['customer_id'],
            'order_date': order_date,
            'promised_delivery_time': promised_delivery,
            'actual_delivery_time': actual_delivery,
            'delivery_status': delivery_status,
            'order_total': round(order_total, 2),
            'payment_method': random.choice(['UPI', 'Card', 'Cash', 'Wallet']),
            'delivery_partner_id': fake.unique.random_number(digits=5),
            'store_id': fake.unique.random_number(digits=10)
        }
        orders.append(order)
        
        # Generate order items
        for product in order_products:
            order_items.append({
                'order_id': order_id,
                'product_id': product['product_id'],
                'quantity': random.randint(1, 3),
                'unit_price': product['price'],
                'total_price': product['price'] * random.randint(1, 3)
            })

    # 4. Delivery Performance Data
    delivery_performance = []
    for order in orders:
        delivery_time = (order['actual_delivery_time'] - order['promised_delivery_time']).total_seconds() / 60
        delivery_performance.append({
            'order_id': order['order_id'],
            'delivery_partner_id': order['delivery_partner_id'],
            'promised_time': order['promised_delivery_time'],
            'actual_time': order['actual_delivery_time'],
            'delivery_time_minutes': round(delivery_time, 2),
            'distance_km': round(random.uniform(0.5, 5), 2),
            'delivery_status': order['delivery_status'],
            'reasons_if_delayed': 'Traffic' if delivery_time > 0 else None
        })

    # 5. Customer Feedback Data
    feedback = []
    for order in orders:
        if order['delivery_status'] == 'On Time':
            rating = random.randint(4, 5)
            sentiment = 'Positive'
        elif order['delivery_status'] == 'Slightly Delayed':
            rating = random.randint(3, 4)
            sentiment = 'Neutral'
        else:
            rating = random.randint(1, 3)
            sentiment = 'Negative'
            
        feedback.append({
            'feedback_id': fake.unique.random_number(digits=7),
            'order_id': order['order_id'],
            'customer_id': order['customer_id'],
            'rating': rating,
            'feedback_text': fake.text(max_nb_chars=100),
            'feedback_category': random.choice(['Delivery', 'Product Quality', 'App Experience', 'Customer Service']),
            'sentiment': sentiment,
            'feedback_date': order['actual_delivery_time'] + timedelta(minutes=random.randint(10, 60))
        })

    # 6. Marketing Performance Data
    marketing_campaigns = [
        'New User Discount',
        'Weekend Special',
        'Festival Offer',
        'Flash Sale',
        'Membership Drive',
        'Category Promotion',
        'App Push Notification',
        'Email Campaign',
        'Referral Program'
    ]
    
    marketing_data = []
    for day in range(date_range_days + 1):
        date = start_date + timedelta(days=day)
        for campaign in marketing_campaigns:
            marketing_data.append({
                'campaign_id': fake.unique.random_number(digits=6),
                'campaign_name': campaign,
                'date': date.date(),
                'target_audience': random.choice(['All', 'New Users', 'Premium', 'Inactive']),
                'channel': random.choice(['App', 'Email', 'SMS', 'Social Media']),
                'impressions': random.randint(400, 1000),
                'clicks': random.randint(50, 300),
                'conversions': random.randint(10, 100),
                'spend': round(random.uniform(50, 100), 2),
                'revenue_generated': round(random.uniform(100, 500), 2),
                'roas': round(random.uniform(1.5, 4.0), 2)
            })

    # Convert to DataFrames
    return {
        'customers': pd.DataFrame(customers),
        'products': pd.DataFrame(products),
        'inventory': pd.DataFrame(inventory),
        'orders': pd.DataFrame(orders),
        'order_items': pd.DataFrame(order_items),
        'delivery_performance': pd.DataFrame(delivery_performance),
        'customer_feedback': pd.DataFrame(feedback),
        'marketing_performance': pd.DataFrame(marketing_data)
    }

def save_blinkit_data(data_dict, prefix='blinkit_'):
    """Save all generated DataFrames to CSV files"""
    for name, df in data_dict.items():
        df.to_csv(f'{prefix}{name}.csv', index=False)

# Generate and save the data with custom date range
data = generate_complete_blinkit_data(start_date='2023-01-01', end_date='2025-12-31')
save_blinkit_data(data)
