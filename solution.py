import json
import os
import numpy as np
from flask import Flask, jsonify

DATA_FOLDER = "sample_data"
ALERT_FILE = "alert_feed.json"


def load_data():
    data = []
    for file in sorted(os.listdir(DATA_FOLDER)):
        if file.endswith(".json"):
            with open(os.path.join(DATA_FOLDER, file)) as f:
                data.append(json.load(f))
    return data


def compute_baseline(data):
    baseline_days = data[:3]
    
    wellbeing = [d["wellbeing"] for d in baseline_days]
    social = [d["social_engagement"] for d in baseline_days]
    energy = [d["energy"] for d in baseline_days]

    baseline = {
        "wellbeing": np.mean(wellbeing),
        "wellbeing_std": np.std(wellbeing),
        "social": np.mean(social),
        "energy": np.mean(energy)
    }
    return baseline


def detect_anomalies(data, baseline):
    alerts = []
    drop_threshold = 20

    if baseline["wellbeing_std"] > 15:
        drop_threshold = 30

    consecutive_low = 0
    gaze_avoidance = 0
    absence = 0
    recovery_days = 0
    was_improving = False
    
    all_wellbeing = [d["wellbeing"] for d in data]
    class_avg = np.mean(all_wellbeing)
    class_std = np.std(all_wellbeing)
    peer_threshold = class_avg - (2 * class_std)

    for i, day in enumerate(data):
        
        current_diff = baseline["wellbeing"] - day["wellbeing"]
        
        if i > 0:
            prev_diff = baseline["wellbeing"] - data[i-1]["wellbeing"]
            if prev_diff > 0 and current_diff < prev_diff:
                recovery_days += 1
                if recovery_days >= 3:
                    was_improving = True
            elif was_improving and current_diff > 15:
                alerts.append({
                    "type": "REGRESSION",
                    "date": day["date"],
                    "severity": "HIGH",
                    "message": "Recovery followed by significant drop in wellbeing"
                })
                recovery_days = 0
                was_improving = False
            else:
                recovery_days = 0
                was_improving = False

        if baseline["wellbeing"] - day["wellbeing"] >= drop_threshold:
            delta = baseline["wellbeing"] - day["wellbeing"]
            severity = "HIGH" if delta > 35 else "MEDIUM"
            alerts.append({
                "type": "SUDDEN_DROP",
                "date": day["date"],
                "severity": severity,
                "message": f"Wellbeing dropped by {delta} points"
            })

        if day["wellbeing"] < 45:
            consecutive_low += 1
        else:
            consecutive_low = 0

        if consecutive_low >= 3:
            alerts.append({
                "type": "SUSTAINED_LOW",
                "date": day["date"],
                "severity": "HIGH",
                "message": "Wellbeing low for 3 consecutive days"
            })

        if (baseline["social"] - day["social_engagement"] >= 25 and 
            day["gaze_direction"] in ["downward", "side"]):
            alerts.append({
                "type": "SOCIAL_WITHDRAWAL",
                "date": day["date"],
                "severity": "MEDIUM",
                "message": "Social engagement dropped with averted gaze"
            })

        if day["energy"] >= baseline["energy"] + 40:
            alerts.append({
                "type": "HYPERACTIVITY_SPIKE",
                "date": day["date"],
                "severity": "MEDIUM",
                "message": "Energy spike detected"
            })

        if not day["gaze_contact"]:
            gaze_avoidance += 1
        else:
            gaze_avoidance = 0

        if gaze_avoidance >= 3:
            alerts.append({
                "type": "GAZE_AVOIDANCE",
                "date": day["date"],
                "severity": "MEDIUM",
                "message": "No eye contact for multiple days"
            })

        if not day["person_detected"]:
            absence += 1
        else:
            absence = 0

        if absence >= 2:
            alerts.append({
                "type": "ABSENCE_FLAG",
                "date": day["date"],
                "severity": "CRITICAL",
                "message": "Student absent for 2+ days"
            })

        if day["wellbeing"] < peer_threshold and day["wellbeing"] < baseline["wellbeing"]:
            alerts.append({
                "type": "PEER_COMPARISON",
                "date": day["date"],
                "severity": "MEDIUM",
                "message": f"Wellbeing 2 std dev below class average ({class_avg:.0f})"
            })

    return alerts


def generate_json(alerts):
    output = {
        "total_alerts": len(alerts),
        "alerts": alerts
    }
    with open(ALERT_FILE, "w") as f:
        json.dump(output, f, indent=4)


def generate_html(alerts):
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Behavioral Anomaly Report</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            font-size: 1.1em;
            opacity: 0.95;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }
        .summary-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        .summary-card .number {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        .summary-card .label {
            font-size: 0.95em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .alerts-section {
            padding: 30px;
        }
        .alerts-section h2 {
            color: #333;
            margin-bottom: 25px;
            font-size: 1.8em;
        }
        .alert-card {
            background: white;
            border-left: 5px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
        }
        .alert-card:hover {
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
            transform: translateY(-2px);
        }
        .severity-high {
            border-left-color: #dc3545;
            background: #fff8f8;
        }
        .severity-high .severity-badge {
            background: #dc3545;
        }
        .severity-medium {
            border-left-color: #ffc107;
            background: #fffbf0;
        }
        .severity-medium .severity-badge {
            background: #ffc107;
            color: #333;
        }
        .severity-low {
            border-left-color: #28a745;
            background: #f8fff9;
        }
        .severity-low .severity-badge {
            background: #28a745;
        }
        .severity-critical {
            border-left-color: #e63946;
            background: #ffe0e6;
        }
        .severity-critical .severity-badge {
            background: #e63946;
        }
        .alert-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .alert-type {
            font-size: 1.2em;
            font-weight: 600;
            color: #333;
        }
        .severity-badge {
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .alert-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
        }
        .detail-item {
            display: flex;
            flex-direction: column;
        }
        .detail-label {
            font-size: 0.85em;
            color: #999;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 5px;
        }
        .detail-value {
            font-size: 1em;
            color: #333;
            font-weight: 500;
        }
        .alert-message {
            background: rgba(0, 0, 0, 0.02);
            border-left: 3px solid #667eea;
            padding: 12px 15px;
            border-radius: 4px;
            color: #555;
            line-height: 1.6;
        }
        .footer {
            background: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            color: #999;
            font-size: 0.9em;
            border-top: 1px solid #e9ecef;
        }
        @media (max-width: 600px) {
            .header h1 {
                font-size: 1.8em;
            }
            .alert-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }
            .summary {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Behavioral Anomaly Report</h1>
            <p>Automated Detection System for Early Intervention</p>
        </div>

        <div class="summary">
            <div class="summary-card">
                <div class="number">""" + str(len(alerts)) + """</div>
                <div class="label">Total Alerts</div>
            </div>
            <div class="summary-card">
                <div class="number">""" + str(sum(1 for a in alerts if a['severity'] == 'CRITICAL')) + """</div>
                <div class="label">Critical</div>
            </div>
            <div class="summary-card">
                <div class="number">""" + str(sum(1 for a in alerts if a['severity'] == 'HIGH')) + """</div>
                <div class="label">High</div>
            </div>
            <div class="summary-card">
                <div class="number">""" + str(sum(1 for a in alerts if a['severity'] == 'MEDIUM')) + """</div>
                <div class="label">Medium</div>
            </div>
        </div>

        <div class="alerts-section">
            <h2>Detected Anomalies</h2>
"""

    for alert in alerts:
        severity_class = f"severity-{alert['severity'].lower()}"
        html += f"""
            <div class="alert-card {severity_class}">
                <div class="alert-header">
                    <div class="alert-type">{alert['type']}</div>
                    <span class="severity-badge">{alert['severity']}</span>
                </div>
                <div class="alert-details">
                    <div class="detail-item">
                        <span class="detail-label">Date</span>
                        <span class="detail-value">{alert['date']}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Type</span>
                        <span class="detail-value">{alert['type']}</span>
                    </div>
                </div>
                <div class="alert-message">
                    <strong>Details:</strong> {alert['message']}
                </div>
            </div>
"""

    html += """
        </div>

        <div class="footer">
            <p style="color: #555; font-weight: 500; margin-bottom: 8px;">
                Sentio Mind Behavioral Anomaly Detection
            </p>
            <p style="color: #999; font-size: 0.9em; margin-bottom: 10px;">
                Counselor Alert Digest Report
            </p>
            <p style="color: #888; font-size: 0.85em; border-top: 1px solid #ddd; padding-top: 10px;">
                Report Generated: <span id="timestamp"></span>
            </p>
        </div>
    </div>

    <script>
        document.getElementById("timestamp").textContent = new Date().toLocaleString();
    </script>
</body>
</html>
"""

    with open("alert_digest.html", "w") as f:
        f.write(html)


def run_pipeline():
    data = load_data()
    baseline = compute_baseline(data)
    alerts = detect_anomalies(data, baseline)
    
    print(f"Loaded {len(data)} days of data")
    print(f"Baseline computed")
    print(f"Detected {len(alerts)} anomalies")
    
    generate_json(alerts)
    generate_html(alerts)
    
    print("alert_feed.json generated")
    print("alert_digest.html generated")
    
    return alerts


app = Flask(__name__)


@app.route("/get_alerts")
def get_alerts():
    with open(ALERT_FILE) as f:
        return jsonify(json.load(f))


if __name__ == "__main__":
    run_pipeline()
    app.run(debug=True)