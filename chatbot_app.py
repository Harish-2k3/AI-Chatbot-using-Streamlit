import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import spacy
from difflib import get_close_matches

# Set page configuration
st.set_page_config(page_title="Calorie Calculator Chatbot", layout="centered")

# Custom CSS for styling
st.markdown("""
    <style>
    .main {
        background: url('/mnt/data/image.png') no-repeat center center fixed;
        background-size: cover;
        color: white;
        font-family: 'Arial', sans-serif;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stTextInput>div>div>input {
        border: 2px solid #ddd;
        padding: 10px;
        border-radius: 5px;
        background-color: rgba(255, 255, 255, 0.8);
        color: black;
    }
    .stNumberInput>div>div>input {
        border: 2px solid #ddd;
        padding: 10px;
        border-radius: 5px;
        background-color: rgba(255, 255, 255, 0.8);
        color: black;
    }
    .stMarkdown>div {
        padding: 10px;
        border-radius: 10px;
        background-color: rgba(0, 0, 0, 0.6);
        color: white;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Load the NLP model
nlp = spacy.load('en_core_web_sm')

# Load the datasets
file_path = "C:/Users/Harish S/Downloads/ChatApp"
data1 = pd.read_csv("C:/Users/Harish S/Downloads/ChatApp/TN_FastFood.csv")
data2 = pd.read_csv("C:/Users/Harish S/Downloads/ChatApp/fastfood_calories.csv")

# Combine the datasets
data1['source'] = 'dataset1'
data2['source'] = 'dataset2'
data = pd.concat([data1, data2], ignore_index=True)

# Convert relevant columns to lowercase for case-insensitivity
data['item'] = data['item'].str.lower()

# Column names based on your datasets
FOOD_ITEM_COLUMN = 'item'
CALORIES_COLUMN = 'calories'
CHOLESTEROL_COLUMN = 'cholesterol'
TOTAL_FAT_COLUMN = 'total_fat'
SODIUM_COLUMN = 'sodium'
TOTAL_CARBS_COLUMN = 'total_carb'
FIBER_COLUMN = 'fiber'
SUGAR_COLUMN = 'sugar'
CALCIUM_COLUMN = 'calcium'
PROTEIN_COLUMN = 'protein'

# Function to find the food item in the dataset
def find_food_item(food, data):
    mask = data[FOOD_ITEM_COLUMN].str.contains(food, case=False, na=False)
    result = data[mask]
    return result

# Extract food items and quantities using spaCy
def extract_food_items(text):
    doc = nlp(text)
    food_items = []
    quantities = []

    for token in doc:
        if token.pos_ == 'NUM':
            quantity = int(token.text)
            next_token = token.nbor(1)
            if next_token.pos_ in ['NOUN', 'PROPN']:
                food_item = next_token.text.lower()
                food_items.append(food_item)
                quantities.append(quantity)
        elif token.pos_ == 'NOUN' and token.dep_ == 'dobj':
            food_item = token.text.lower()
            if food_item not in food_items:
                food_items.append(food_item)
                quantities.append(1)

    return food_items, quantities

# Suggest similar food items if the entered item is not found
def suggest_similar_items(food, data):
    all_items = data[FOOD_ITEM_COLUMN].tolist()
    similar_items = get_close_matches(food, all_items, n=3, cutoff=0.6)
    return similar_items

# Harris-Benedict Equation for calculating BMR
def calculate_bmr(gender, weight, height, age):
    if gender == 'Male':
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    return bmr

# Activity multiplier
def calculate_daily_calories(bmr, activity_level):
    if activity_level == 'Sedentary':
        return bmr * 1.2
    elif activity_level == 'Lightly active':
        return bmr * 1.375
    elif activity_level == 'Moderately active':
        return bmr * 1.55
    elif activity_level == 'Very active':
        return bmr * 1.725
    else:
        return bmr * 1.9

# Application title
st.title("Caloric Intake and Nutritional Facts Tracker")

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = "welcome"
if "caloric_limit" not in st.session_state:
    st.session_state.caloric_limit = None

# Welcome page
if st.session_state.step == "welcome":
    st.markdown("### 👋 Hello champ! Welcome to the Calorie Calculator Chatbot!")
    if st.button("Daily Calorie Limit Calculator"):
        st.session_state.step = "daily_calorie_calculator"
    if st.button("Food Calorie Calculator"):
        if st.session_state.caloric_limit is None:
            st.session_state.step = "set_daily_calorie_limit"
        else:
            st.session_state.step = "food_calorie_calculator"

# Daily Calorie Limit Calculator
if st.session_state.step == "daily_calorie_calculator":
    st.markdown("### 🧑 Please enter your details to calculate your daily caloric limit:")
    gender = st.selectbox("Select your gender:", ["Male", "Female"])
    weight = st.number_input("Enter your weight (kg):", min_value=30, max_value=200, value=70, step=1)
    height = st.number_input("Enter your height (cm):", min_value=100, max_value=250, value=170, step=1)
    age = st.number_input("Enter your age:", min_value=10, max_value=100, value=30, step=1)
    activity_level = st.selectbox("Select your activity level:", ["Sedentary", "Lightly active", "Moderately active", "Very active", "Super active"])
    
    if st.button("Calculate Daily Calorie Limit"):
        bmr = calculate_bmr(gender, weight, height, age)
        caloric_limit = calculate_daily_calories(bmr, activity_level)
        
        st.session_state.caloric_limit = caloric_limit
        st.markdown(f"### 🤖 Your daily caloric limit is {caloric_limit:.2f} kcal")
        

# Set Daily Calorie Limit for Food Calorie Calculator
if st.session_state.step == "set_daily_calorie_limit":
    st.markdown("### 🧑 Please set your daily caloric limit:")
    caloric_limit = st.number_input("Enter your daily caloric limit (kcal):", min_value=100, max_value=5000, value=2000, step=50)
    
    if st.button("Set Daily Caloric Limit"):
        st.session_state.caloric_limit = caloric_limit
        st.session_state.step = "food_calorie_calculator"

# Food Calorie Calculator
if st.session_state.step == "food_calorie_calculator":
    st.markdown("### 🧑 Enter the food you ate:")
    food_input = st.text_input("E.g., 'I had 1 Chicken Burger, 1 Chicken Fries, and 4 Piece Chicken Nuggets at McDonald's'")
    
    if st.button("Calculate"):
        if food_input:
            food_items, quantities = extract_food_items(food_input)
            total_calories = 0
            total_cholesterol = 0
            total_fat = 0
            total_sodium = 0
            total_carbs = 0
            total_fiber = 0
            total_sugar = 0
            total_calcium = 0
            total_protein = 0
            
            for food, quantity in zip(food_items, quantities):
                food_item = find_food_item(food, data)
                
                if not food_item.empty:
                    item_data = food_item.iloc[0]
                    total_calories += quantity * item_data[CALORIES_COLUMN]
                    total_cholesterol += quantity * item_data[CHOLESTEROL_COLUMN]
                    total_fat += quantity * item_data[TOTAL_FAT_COLUMN]
                    total_sodium += quantity * item_data[SODIUM_COLUMN]
                    total_carbs += quantity * item_data[TOTAL_CARBS_COLUMN]
                    total_fiber += quantity * item_data[FIBER_COLUMN]
                    total_sugar += quantity * item_data[SUGAR_COLUMN]
                    total_calcium += quantity * item_data[CALCIUM_COLUMN]
                    total_protein += quantity * item_data[PROTEIN_COLUMN]
                else:
                    st.markdown(f"### 🤖 Sorry, I couldn't find the food item '{food}' in the dataset.")
                    suggestions = suggest_similar_items(food, data)
                    if suggestions:
                        st.markdown(f"### Did you mean: {', '.join(suggestions)}?")
            
            nutritional_data = {
                'Nutrient': ['Total Calories', 'Total Cholesterol', 'Total Fat', 'Total Sodium', 'Total Carbohydrates', 
                             'Total Fiber', 'Total Sugar', 'Total Calcium', 'Total Protein'],
                'Amount': [total_calories, total_cholesterol, total_fat, total_sodium, total_carbs, 
                           total_fiber, total_sugar, total_calcium, total_protein]
            }
            df_nutritional = pd.DataFrame(nutritional_data)
            st.table(df_nutritional)
            
            if st.session_state.caloric_limit is not None:
                if total_calories > st.session_state.caloric_limit:
                    st.markdown(f"### ⚠ Warning: You have exceeded your daily caloric limit by {total_calories - st.session_state.caloric_limit:.2f} kcal")
                else:
                    st.markdown(f"### ✅ You are within your daily caloric limit. You have {st.session_state.caloric_limit - total_calories:.2f} kcal remaining.")

             # Plot pie chart
            pie_labels = ['Total Cholesterol', 'Total Fat', 'Total Sodium', 'Total Carbohydrates', 
              'Total Fiber', 'Total Sugar', 'Total Calcium', 'Total Protein']
            pie_sizes = [total_cholesterol, total_fat, total_sodium, total_carbs, total_fiber, 
            total_sugar, total_calcium, total_protein]
            fig, ax = plt.subplots()
            wedges, texts, autotexts = ax.pie(pie_sizes, labels=pie_labels, autopct='%1.1f%%', startangle=180,labeldistance=1.1)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
            # Adding legend
            ax.legend(wedges, pie_labels, title="Nutrients", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            # Equal aspect ratio ensures that pie is drawn as a circle.
            st.pyplot(fig)
        else:
            st.markdown("### 🤖 Please enter the food you consumed.")

# Return to Welcome Page
if st.session_state.step != "welcome" and st.button("Return to Welcome Page"):
    st.session_state.step = "welcome"
