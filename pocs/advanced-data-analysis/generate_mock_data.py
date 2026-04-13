import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from fpdf import FPDF

# Seed for reproducibility
np.random.seed(42)

def generate_complex_sales_data(output_path):
    print(f"Generating sales data at {output_path}...")
    
    dates = [datetime(2023, 1, 1) + timedelta(days=x) for x in range(365)]
    regions = ['South Delhi', 'North Delhi', 'West Delhi', 'Noida', 'Gurugram']
    products = ['Classic Potato Samosa', 'Paneer Tikka Samosa', 'Spicy Chicken Samosa', 'Chocolate Fusion Samosa']
    
    data = []
    
    for date in dates:
        # Seasonal factor (Samosas sell better in winter/monsoon)
        month = date.month
        seasonal_multiplier = 1.3 if month in [11, 12, 1, 7, 8] else 1.0
        
        # Weekend boost
        day_type_multiplier = 1.25 if date.weekday() >= 5 else 1.0
        
        for region in regions:
            # Regional preference boost
            region_pref = 1.2 if region == 'South Delhi' else 1.0
            
            for product in products:
                # Base units
                base_units = np.random.randint(50, 150)
                
                # Product specific traits
                if product == 'Chocolate Fusion Samosa':
                    # Niche product, lower volume, higher volatility
                    base_units = np.random.randint(5, 30)
                
                # Introduce a "Cannibalization Event"
                # If a promotion is running on Paneer, Classic dips slightly
                promo_active = np.random.random() > 0.9
                promo_multiplier = 1.5 if promo_active else 1.0
                
                # Weather factor
                is_raining = np.random.random() > 0.8
                weather_multiplier = 1.4 if is_raining else 1.0 # Chai-Samosa weather!
                
                # Calculate final units
                units = int(base_units * seasonal_multiplier * day_type_multiplier * region_pref * promo_multiplier * weather_multiplier)
                
                # Pricing
                base_price = {
                    'Classic Potato Samosa': 15,
                    'Paneer Tikka Samosa': 25,
                    'Spicy Chicken Samosa': 30,
                    'Chocolate Fusion Samosa': 45
                }[product]
                
                revenue = units * base_price
                
                # Competitor pricing (for complex analysis)
                comp_price = base_price + np.random.uniform(-5, 5)
                
                data.append({
                    'Date': date.strftime('%Y-%m-%d'),
                    'Region': region,
                    'Product': product,
                    'Units_Sold': units,
                    'Price_Point': base_price,
                    'Revenue': revenue,
                    'Competitor_Price': round(comp_price, 2),
                    'Weather': 'Rainy' if is_raining else 'Clear',
                    'Promotion_Active': promo_active
                })

    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print("Sales data generated successfully.")

def generate_strategy_pdf(output_path):
    print(f"Generating strategy PDF at {output_path}...")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Samosa Hub: 2024 Expansion Strategy (NCR Region)", ln=True, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=(
        "Executive Summary:\n"
        "Samosa Hub has established a dominant position in South Delhi. As we look towards 2024, "
        "the objective is to penetrate the Noida and Gurugram corporate sectors. Our data shows a "
        "significant correlation between rainy weather and sales spikes, which we aim to capitalize on "
        "via targeted 'Monsoon Bundles'.\n\n"
        "Key Challenges:\n"
        "1. Supply Chain Resilience: Sourcing local ingredients from Mandis during peak festive seasons.\n"
        "2. Cannibalization: Emerging data suggests that high-tier products like the 'Chocolate Fusion' "
        "interfere with 'Classic' sales in corporate hubs.\n"
        "3. Pricing Pressure: Competitors in North Delhi have aggressive pricing at the 12 INR price point.\n\n"
        "Strategic Pillars:\n"
        "- Quality Governance: Centralized spice control.\n"
        "- Local Pulse: Community-voted monthly flavors.\n"
        "- Digital Integration: Predictive inventory based on local weather forecasts."
    ))
    
    pdf.output(output_path)
    print("Strategy PDF generated successfully.")

if __name__ == "__main__":
    os.makedirs('data', exist_ok=True)
    generate_complex_sales_data('data/samosa_sales_complex.csv')
    generate_strategy_pdf('data/expansion_strategy.pdf')
