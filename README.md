# Behavioral Anomaly & Early Distress Detection

## Executive Summary
Build personal baselines from historical behavioral data and alert when someone deviates significantly from their norm. This system adds the missing alert layer to Sentio Mind—detecting concerning patterns proactively without requiring new video processing pipelines.

## Problem Statement
Sentio Mind produces behavioral scores and visualization charts but lacks proactive alerting. Students can show signs of distress for days before anyone notices. This assignment bridges that gap with an alert layer that identifies anomalies against personal baselines, enabling early intervention by counsellors and support staff.

**Core Issue:** Reactive analytics  Proactive alerts

## Solution Overview
Analyze multi-day behavioral JSON data from \sample_data/\ or \Dataset_Assignment/\ folders, establish personal baselines from first 3 days, detect 7 anomaly categories, and generate two outputs:
- **alert_digest.html** — Counsellor-friendly report with sparklines (offline-compatible, no CDN)
- **alert_feed.json** — Machine-readable alert feed for Flask API integration

Integration point: \/get_alerts\ Flask endpoint returns alert_feed.json for automated ingestion. Zero modifications to existing analysis pipeline.

## Input Data Format

\\json
{
  "day": 1,
  "wellbeing": 75,
  "social_engagement": 80,
  "energy": 82,
  "gaze_avoidance": 5,
  "absence": false,
  "participation": 90
}

\\

## 7 Anomaly Categories to Detect

1. **SUDDEN_DROP** — wellbeing  20 points below personal baseline in single day
2. **SUSTAINED_LOW** — wellbeing < 45 for  3 consecutive days
3. **SOCIAL_WITHDRAWAL** — social_engagement  25 points down + gaze mostly downward
4. **HYPERACTIVITY_SPIKE** — combined energy metrics  40 points above baseline
5. **REGRESSION** — was improving 3+ consecutive days, then drops > 15 points
6. **GAZE_AVOIDANCE** — zero eye contact for  3 consecutive days
7. **ABSENCE_FLAG** — person not detected for 2+ consecutive days (welfare check required)

## Baseline Computation Rule
- Use first 3 days of data as personal baseline (or all data if fewer than 3 days available)
- Calculate mean and standard deviation for each metric
- **Adaptive Threshold:** If baseline standard deviation > 15, increase drop threshold by 50% (reduces false positives)

## Output Specifications

### 1. alert_digest.html
**Purpose:** Counsellor-friendly alert digest with visualizations
**Requirements:**
- Offline-compatible (NO external CDN dependencies)
- Include sparkline charts for trend visualization
- List all detected anomalies with severity (HIGH/MEDIUM/LOW)
- Timestamp and day-by-day breakdown
- Actionable recommendations for each alert

### 2. alert_feed.json
**Purpose:** Machine-readable alerts for API integration
**JSON Schema (MUST match exactly):**
\\\json
{
  "subject_id": "string",
  "report_date": "YYYY-MM-DD",
  "baseline": {
    "wellbeing_mean": number,
    "wellbeing_std": number,
    "social_engagement_mean": number,
    "energy_mean": number
  },
  "alerts": [
    {
      "day": number,
      "type": "SUDDEN_DROP|SUSTAINED_LOW|SOCIAL_WITHDRAWAL|HYPERACTIVITY_SPIKE|REGRESSION|GAZE_AVOIDANCE|ABSENCE_FLAG",
      "severity": "HIGH|MEDIUM|LOW",
      "metric": "wellbeing|social_engagement|energy|gaze|absence",
      "value": number,
      "baseline_value": number,
      "deviation_percent": number,
      "message": "string",
      "action_required": boolean
    }
  ],
  "summary": {
    "total_alerts": number,
    "high_severity_count": number,
    "recommendation": "string"
  }
}
\\\

## Deliverables (3 Files)

1. **solution.py** — Main anomaly detection engine
   - No OpenCV or camera processing needed
   - Pure data analysis with NumPy/Pandas
   - Generates both alert_digest.html and alert_feed.json
   - Flask endpoint: \/get_alerts\ returns alert_feed.json

2. **alert_digest.html** — Counsellor report
   - Sparklines (embedded SVG, no external libraries)
   - Alert timeline and severity breakdown
   - Offline functionality (all CSS/JS embedded)

3. **alert_feed.json** — API-ready alerts
   - Matches schema exactly (automated validation)
   - Returned by Flask \/get_alerts\ endpoint

## template.py Structure (Rules)
- Function signatures are **fixed** — do NOT rename stub functions
- Add helper functions as needed
- Clear TODO markers for implementation sections
- Skeleton structure provided; write logic to fill in detection algorithms

## Constraints & Rules
 **Python 3.9+ only** — No version compatibility with earlier Python
 **No Jupyter notebooks** as final submission (pure .py files only)
 **No external video processing** — Use existing Sentio JSON data
 **HTML must work offline** — No CDN, no external resources
 **JSON schema is fixed** — Do not modify integration contract
 **Zero pipeline changes** — Alert layer only, independent of existing code

## Tech Stack (Shared Library)
- opencv-python==4.9.0
- face_recognition==1.3.0
- mediapipe==0.10.14
- deepface==0.0.93
- mtcnn==0.1.1
- numpy==1.26.4
- Pillow==10.3.0
- scikit-image==0.22.0
- imagehash==4.3.1

## Repository & Branch Naming
**GitHub Repo:** https://github.com/Sentiodirector/sentio-poc-anomaly-detection.git
**Branch Format:** \[FirstName_LastName_RollNumber]\
**Example:** \Rajesh_Yadav_1047\
Push all code to your personal branch only (no direct commits to main).

## File Structure
\\\
sentio-poc-anomaly-detection/
 README.md                 # This file
 solution.py              # Anomaly detection engine
 template.py              # Skeleton with TODO markers (reference)
 requirements.txt         # Dependencies
 alert_digest.html        # Generated counsellor report
 alert_feed.json          # Generated alert feed
 sample_data/             # Input JSON files (day_1.json ... day_5.json)
 Dataset_Assignment/      # Alternative dataset source
\\\

## Getting Started
1. Clone repo and create branch: \[FirstName_LastName_RollNumber]\
2. Populate \sample_data/\ with daily JSON files (minimum 5 days)
3. Run: \python solution.py\
4. Output: \lert_digest.html\ and \lert_feed.json\
5. Test Flask endpoint: \GET /get_alerts\ returns JSON feed
6. Commit and push to your branch only

## Success Criteria
- [x] Detects all 7 anomaly categories accurately
- [x] Baseline computed correctly (first 3 days, adaptive thresholding)
- [x] JSON schema matches exactly (no deviations)
- [x] HTML renders offline with no errors
- [x] Flask endpoint functional and returns valid JSON
- [x] Python 3.9+ compatible, no Jupyter artifacts
- [x] All files committed to personal branch

---
**Assignment Status:** Proof of Concept (POC) - v1.0
**Target Audience:** Data Analysts, Python Engineers (no CV expertise required)
**Last Updated:** March 17, 2026
