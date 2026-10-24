# 🚦 TrafficIQ: AI-Based Traffic Signal Timing Optimization or TrafficIQ: AI-Based Adaptive Traffic Signal Control

An intelligent traffic management system that uses **Machine Learning and adaptive signal optimization** to allocate green-light durations based on predicted traffic demand.

🌐 **Live Demo:** https://smarttrafficiq.streamlit.app/

## ✨ Key Features

* **Traffic Simulation:** Interactive 4-way intersection with moving vehicles and traffic signals.
* **ML-Based Prediction:** Random Forest Regressor predicts traffic demand.
* **Adaptive Signal Optimization:** Dynamically allocates green-light durations based on predicted demand.
* **Performance Comparison:** Compares fixed-time and adaptive signal strategies.
* **Traffic Analytics:** Visualizes traffic demand, queue lengths, delays, and green-time allocation.
* **Scenario Analysis:** Supports seven predefined traffic scenarios.
* **Interactive Dashboard:** Five Streamlit tabs with Plotly visualizations.

## 🛠️ Tech Stack

* **Language:** Python
* **Machine Learning:** Scikit-learn, Random Forest Regressor
* **Web Framework:** Streamlit
* **Visualization:** Plotly, HTML5 Canvas
* **Data Processing:** Pandas, NumPy
* **Model Serialization:** Joblib

## 🤖 Machine Learning Model

* **Algorithm:** Random Forest Regressor
* **Dataset:** 6,000 synthetic traffic observations
* **Input Features:** Vehicle count, traffic density, queue length, average speed, road direction, and time-related features.
* **Prediction Target:** Traffic demand (PCU/hr)

### Model Performance

| Metric   |        Score |
| -------- | -----------: |
| MAE      | 21.72 PCU/hr |
| RMSE     | 27.06 PCU/hr |
| R² Score |       0.9945 |

*These metrics are based on the project's reported held-out test results.*

## 🚦 Signal Optimization

TrafficIQ uses demand-based proportional green-time allocation with configurable cycle lengths and minimum/maximum green-time constraints.

It compares adaptive signal timing against a fixed-time strategy using simulated traffic performance metrics.

## 🚀 Installation & Usage

**1. Clone the repository**

```bash
git clone https://github.com/sanikadange3/TrafficIQ.git
cd TrafficIQ
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Generate the dataset and train the model (optional)**

```bash
python data/generate_dataset.py
python models/train_model.py
```

**4. Run the application**

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.


## 🔮 Future Scope

* Integration with real-time traffic sensor data.
* Computer vision-based vehicle detection.
* Emergency vehicle prioritization.
* Deployment and testing at real-world intersections.


## 👩‍💻 Developer

**Sanika Dange**

GitHub: https://github.com/sanikadange3
