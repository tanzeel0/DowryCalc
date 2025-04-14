from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
import joblib
import os

app = Flask(__name__)
CORS(app)

DATA_PATH = 'dahej_dataset.csv'

def load_data():
    df = pd.read_csv(DATA_PATH)
    return df

def get_model():
    model_path = 'dahej_model.joblib'
    encoder_path = 'encoder.joblib'

    if os.path.exists(model_path) and os.path.exists(encoder_path):
        model = joblib.load(model_path)
        encoder = joblib.load(encoder_path)
        return model, encoder

    df = load_data()

    X = df[['Income', 'Profession', 'EmploymentType', 'Land']]
    y = df['Dahej']

    # Encode categorical features
    categorical_features = ['Profession', 'EmploymentType']
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    encoded_cats = encoder.fit_transform(X[categorical_features])

    numeric_features = X[['Income', 'Land']].values
    X_processed = np.hstack([numeric_features, encoded_cats])

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_processed, y)

    joblib.dump(model, model_path)
    joblib.dump(encoder, encoder_path)

    return model, encoder

model, encoder = get_model()

@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.json

    income = float(data['income'])
    profession = data['profession']
    employment_type = data['employmentType']
    land = float(data['land'])

    input_df = pd.DataFrame({
        'Income': [income],
        'Profession': [profession],
        'EmploymentType': [employment_type],
        'Land': [land]
    })

    # Encode input
    categorical_features = ['Profession', 'EmploymentType']
    encoded_cats = encoder.transform(input_df[categorical_features])
    numeric_features = input_df[['Income', 'Land']].values
    X_processed = np.hstack([numeric_features, encoded_cats])

    prediction = model.predict(X_processed)[0]

    return jsonify({
        'prediction': int(round(prediction)),  # Nearest rupee
        'analysis': {
            'income_factor': round(income * 0.025, 2),
            'profession_impact': get_profession_impact(profession),
            'employment_impact': 'Positive correlation' if employment_type == 'Government' else 'Baseline',
            'land_impact': f'Increases expectation by approximately {land * 5}%'
        }
    })

def get_profession_impact(profession):
    impacts = {
        'Businessman': 'Moderate positive impact',
        'CA': 'Strong positive impact',
        'Doctor': 'Very strong positive impact',
        'Engineer': 'Strong positive impact',
        'Lawyer': 'Strong positive impact',
        'Teacher': 'Slight negative impact',
        'Other': 'Neutral impact'
    }
    return impacts.get(profession, 'Unknown impact')

@app.route('/api/data', methods=['GET'])
def get_data():
    df = load_data()

    summary = {
        'profession_avg': df.groupby('Profession')['Dahej'].mean().round(0).to_dict(),
        'employment_avg': df.groupby('EmploymentType')['Dahej'].mean().round(0).to_dict(),
        'land_avg': df.groupby('Land')['Dahej'].mean().round(0).to_dict(),
        'income_ranges': [
            {'range': '0-50000', 'avg': round(df[df['Income'] < 50000]['Dahej'].mean(), 0)},
            {'range': '50000-100000', 'avg': round(df[(df['Income'] >= 50000) & (df['Income'] < 100000)]['Dahej'].mean(), 0)},
            {'range': '100000-150000', 'avg': round(df[(df['Income'] >= 100000) & (df['Income'] < 150000)]['Dahej'].mean(), 0)},
            {'range': '150000+', 'avg': round(df[df['Income'] >= 150000]['Dahej'].mean(), 0)}
        ],
        'sample_data': df.sample(100).to_dict(orient='records')
    }

    return jsonify(summary)

if __name__ == '__main__':
    app.run(debug=True)
