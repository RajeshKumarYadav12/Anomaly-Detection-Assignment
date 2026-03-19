# 🧠 Behavioral Anomaly & Early Distress Detection

## 📌 Executive Summary
This project builds **personal behavioral baselines** from historical data and detects anomalies when a user deviates significantly from their normal pattern.  

It adds a **proactive alert layer** to SentioMind, enabling early detection of distress without requiring any new video processing pipeline.

---

## ❗ Problem Statement
SentioMind currently provides behavioral analytics but lacks **real-time alerting**.  

Students may show signs of distress for multiple days before intervention occurs.

> **Core Gap:** Reactive analytics → Proactive alerts

---

## 🚀 Solution Overview

| Component | Description |
|----------|------------|
| **Input Source** | Multi-day behavioral JSON data (`sample_data/` or `Dataset_Assignment/`) |
| **Baseline Computation** | First 3 days used to calculate mean & standard deviation |
| **Anomaly Detection** | Detects 7 behavioral anomaly categories |
| **Processing Type** | Pure data analysis (NumPy/Pandas, no CV required) |
| **Output 1** | `alert_digest.html` (human-readable report) |
| **Output 2** | `alert_feed.json` (machine-readable alerts) |
| **Integration** | Flask API endpoint `/get_alerts` |
| **Pipeline Impact** | No changes to existing system |

---

## 📥 Input Data Format

| Field | Type | Description | Example |
|------|------|------------|--------|
| `day` | Integer | Day number | 1 |
| `wellbeing` | Integer | Mental wellbeing score | 75 |
| `social_engagement` | Integer | Interaction level | 80 |
| `energy` | Integer | Energy/activity level | 82 |
| `gaze_avoidance` | Integer | Eye contact avoidance | 5 |
| `absence` | Boolean | Presence status | false |
| `participation` | Integer | Participation level | 90 |

---

## ⚠️ Anomaly Categories

| # | Type | Description |
|--|------|------------|
| 1 | **SUDDEN_DROP** | Wellbeing drops ≥ 20 points below baseline |
| 2 | **SUSTAINED_LOW** | Wellbeing < 45 for ≥ 3 consecutive days |
| 3 | **SOCIAL_WITHDRAWAL** | Social engagement drops ≥ 25 + gaze avoidance |
| 4 | **HYPERACTIVITY_SPIKE** | Energy increases ≥ 40 points above baseline |
| 5 | **REGRESSION** | Improvement followed by sharp drop (>15 points) |
| 6 | **GAZE_AVOIDANCE** | No eye contact for ≥ 3 days |
| 7 | **ABSENCE_FLAG** | Absent for ≥ 2 consecutive days |

---

## 📊 Baseline Computation Rules

- First 3 days → baseline
- If <3 days → use all available data
- Compute:
  - Mean
  - Standard Deviation

### 🔄 Adaptive Threshold
- If `std > 15` → increase threshold by **50%**
- Helps reduce false positives

---

## 📤 Output Specifications

### 1️⃣ alert_digest.html

| Feature | Description |
|--------|------------|
| Purpose | Counsellor-friendly report |
| Compatibility | Fully offline (no CDN) |
| Charts | Sparkline graphs (SVG-based) |
| Content | Alert list with severity |
| Timeline | Day-by-day breakdown |
| Recommendation | Actionable suggestions |
| Design | Embedded CSS & JS |

---

### 2️⃣ alert_feed.json

#### 🔹 Structure

| Field | Type | Description |
|------|------|------------|
| `subject_id` | String | Unique student ID |
| `report_date` | String | YYYY-MM-DD |
| `baseline` | Object | Mean & std values |
| `alerts` | Array | List of anomalies |
| `summary` | Object | Alert summary |

---

#### 🔹 Alerts Object

| Field | Type | Description |
|------|------|------------|
| `day` | Number | Day of anomaly |
| `type` | String | Anomaly type |
| `severity` | String | HIGH / MEDIUM / LOW |
| `metric` | String | Affected metric |
| `value` | Number | Current value |
| `baseline_value` | Number | Baseline |
| `deviation_percent` | Number | % change |
| `message` | String | Description |
| `action_required` | Boolean | Action needed |

---

#### 🔹 Summary

| Field | Type | Description |
|------|------|------------|
| `total_alerts` | Number | Total anomalies |
| `high_severity_count` | Number | Critical alerts |
| `recommendation` | String | Suggested action |

---

## 📁 Project Structure


sentio-poc-anomaly-detection/
│
├── README.md
├── solution.py
├── template.py
├── requirements.txt
├── alert_digest.html
├── alert_feed.json
│
├── sample_data/
│ ├── day_1.json
│ ├── day_2.json
│ └── ...
│
└── Dataset_Assignment/


---

## ⚙️ Tech Stack

- Python 3.9+
- NumPy
- Pandas
- Flask (for API)

---

## ▶️ Getting Started

```bash
# Clone repository
git clone https://github.com/Sentiodirector/sentio-poc-anomaly-detection.git

# Navigate
cd sentio-poc-anomaly-detection

# Run project
python solution.py
🌐 API Endpoint
GET /get_alerts

Returns:

alert_feed.json
📌 Constraints

Python 3.9+ only

No Jupyter notebooks

No video processing

HTML must work offline

JSON schema must not change

No modification to existing pipeline

✅ Success Criteria

 Detects all 7 anomalies

 Correct baseline computation

 Valid JSON schema

 Offline HTML working

 Functional API endpoint

 Clean and structured code

🔀 Branch Naming
[FirstName_LastName_RollNumber]

Example:

Rajesh_Yadav_1047
👨‍💻 Author

Rajesh Kumar Yadav
