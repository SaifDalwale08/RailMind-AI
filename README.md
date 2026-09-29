# 🚆 RailMind AI

### Predictive Railway Crowd Intelligence for Safer Passenger Movement

> **From detecting crowds to predicting crowd surges.**

RailMind AI is a predictive railway crowd-intelligence platform designed to help railway operators understand current crowd conditions, anticipate short-term crowd surges, identify spatial bottlenecks, and evaluate possible interventions.

The system combines **computer vision, AI/ML, crowd analytics, railway activity intelligence, forecasting, risk assessment, and an interactive command-center dashboard** into a single decision-support platform.

---

## 🎯 Problem

Railway stations experience rapidly changing passenger movement caused by:

- Train arrivals and departures
- Train delays
- Multiple simultaneous train movements
- Platform changes
- High passenger inflow
- Footbridge and gate congestion
- Sudden changes in passenger movement

Traditional monitoring can tell an operator **what is happening now**, but proactive crowd management requires understanding **what may happen next**.

### The key question:

> **How can we identify a potential crowd surge early enough to support preventive action?**

---

# 💡 Our Solution

RailMind AI follows a predictive decision-support approach:

```text
SEE → PREDICT → UNDERSTAND → IDENTIFY → SIMULATE → ACT

The platform processes railway video and operational context to provide:

Crowd Detection & Analytics
Short-Term Crowd Forecasting
Railway/Train Activity Intelligence
Spatial Bottleneck Identification
Risk Assessment
Intervention Simulation
Operator & Passenger Alerts
Multilingual Announcements
Post-Event Analytics
🧠 AI & Computer Vision
YOLO11n

RailMind uses a custom-trained YOLO11n (YOLOv11 Nano) model for person detection.

YOLO11n was selected as the computer-vision detection layer because its lightweight architecture is suitable for applications where efficient processing of multiple CCTV streams is important.

Model Specifications
Metric	Value
Model	YOLO11n
Parameters	~2.58 Million
GFLOPs	6.4
Task	Person Detection
Training Images	279
Validation Images	70
Validation Results
Metric	Result
Precision	0.780
Recall	0.816
mAP@50	0.870
mAP@50–95	0.580

These are validation results from the project's validation dataset and should not be interpreted as production deployment accuracy.

📊 Dataset

A key part of RailMind was working with real railway environment data collected at Pune Junction.

The dataset preparation included:

Real railway environment imagery
Person annotations
Pune-specific visual conditions
Training/validation split
Video-based crowd observations
Dataset Statistics
Original Images       : 437
Annotated/Matched     : 349
Training Images       : 279
Validation Images     : 70
Validation Instances  : 403

The Pune-specific dataset was used to develop and validate the person-detection component of RailMind.

⚙️ System Architecture
                RAILWAY CCTV / VIDEO
                         │
                         ▼
                  ┌──────────────┐
                  │    OpenCV    │
                  │Video Handling│
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
                  │   YOLO11n    │
                  │Person Detect.│
                  └──────┬───────┘
                         │
                         ▼
                 Person Detections
                         │
                         ▼
                Crowd Signal / Data
                         │
                         ▼
              ┌────────────────────┐
              │ Crowd Analytics    │
              │ Trend / Growth     │
              │ Acceleration       │
              └─────────┬──────────┘
                        │
                        ▼
              ┌────────────────────┐
              │ Short-Term Forecast│
              └─────────┬──────────┘
                        │
                        ▼
       ┌────────────────────────────────┐
       │      Railway Activity Layer    │
       │ Arrivals / Departures / Delays │
       │ Simultaneous Train Movements   │
       └───────────────┬────────────────┘
                       │
                       ▼
                ┌─────────────┐
                │Risk Analysis│
                └──────┬──────┘
                       │
              ┌────────┴─────────┐
              ▼                  ▼
       Bottleneck Analysis   Intervention
                             Simulation
              │                  │
              └────────┬─────────┘
                       ▼
              ┌─────────────────┐
              │   Dashboard     │
              │ Operator Alerts │
              │ Passenger Alerts│
              └─────────────────┘
🔬 Technical Workflow
1. Video Input

Railway CCTV/video footage is provided to the video-processing pipeline.

2. Person Detection

YOLO11n detects people within the video frames and provides bounding boxes and confidence scores.

3. Crowd Signal Generation

Person detections are converted into time-dependent observations that can be analyzed as a crowd signal.

4. Crowd Analytics

The system evaluates crowd conditions including:

Current crowd
Average crowd
Growth rate
Acceleration
Crowd trend
Movement/flow indicators
5. Short-Term Forecasting

Historical crowd observations are used to generate a short-term prediction of the expected crowd state.

The objective is not only to answer:

"How crowded is it now?"

but also:

"What could happen next?"

6. Railway Activity Intelligence

Crowd conditions are analyzed alongside railway activity such as:

Train arrivals
Train departures
Delays
Simultaneous train movements
Train pressure indicators

This provides operational context for the predicted crowd behavior.

7. Bottleneck Detection

Instead of relying only on station-wide crowd numbers, RailMind evaluates specific locations such as:

Platforms
Footbridges
Gates
Other defined station zones

This helps identify where passenger pressure is concentrated.

8. Risk Assessment

The system combines current and forward-looking signals to generate a risk assessment.

A moderate current crowd can still represent elevated future risk when the crowd trend is increasing and significant railway activity is approaching.

9. Intervention Simulation

RailMind provides decision-support interventions such as:

Gate Control
Platform Guidance
Gate Control + Platform Guidance

The intervention simulator estimates the potential effect of a selected intervention on crowd and risk conditions.

The simulated results represent modelled/projected outcomes and are not guarantees of real-world intervention effects.

10. Communication

The platform generates:

Operator alerts
Passenger alerts
English announcements
Hindi announcements
Marathi announcements
🖥️ Dashboard

RailMind provides an interactive railway intelligence dashboard containing modules such as:

📹 Live Monitoring

Monitor available railway video/camera information.

👥 Crowd Analytics

View current crowd conditions, trends, growth and movement indicators.

📈 Surge Forecast

View predicted crowd, expected increase, surge score and risk.

🚆 Train Intelligence

Analyze upcoming train activity and railway pressure.

📍 Bottlenecks

Identify locations experiencing higher passenger pressure.

🚨 Risk & Alerts

Provide operational awareness based on current and predicted conditions.

🧠 Intervention Simulator

Compare projected conditions under different intervention strategies.

📢 Passenger Communication

Generate multilingual passenger advisories.

📊 Post-Event Analytics

Review crowd and intervention-related statistics after an event.

🛠️ Technology Stack
Artificial Intelligence / Machine Learning
YOLO11n
Ultralytics
Computer Vision
Crowd Analytics
Time-Series Analysis / Forecasting
Computer Vision
OpenCV
Video processing
Frame analysis
Person detection pipeline
Backend
Python
FastAPI
REST APIs
JSON-based data exchange
OpenAPI / Swagger documentation
Frontend
HTML
CSS
JavaScript
Interactive dashboard
Development
Python
VS Code
Git / GitHub
🔌 API Architecture

The backend exposes REST endpoints for different RailMind modules.

Example endpoints include:

GET  /api/health
GET  /api/dashboard
GET  /api/crowd/history
GET  /api/schedule
GET  /api/trains/next
GET  /api/interventions
GET  /api/announcements
GET  /api/station/state
GET  /api/passenger-alerts

POST /api/video/upload
POST /api/video/analyze
POST /api/demo/analyze

Swagger/OpenAPI documentation is available through the FastAPI backend.

📁 Project Structure
RailMindAI/
│
├── Backend/
│   └── api.py
│
├── data/
│   └── live/
│       ├── uploads/
│       └── analysis/
│
├── Dataset/
│   └── Pune_YOLO/
│
├── runs/
│   └── RailMind/
│       └── pune_person/
│           └── weights/
│               └── best.pt
│
├── fornend/
│   └── railmind-ai/
│
└── README.md
🚀 Running the Project
1. Clone the repository
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd RailMindAI
2. Create a virtual environment
python -m venv .venv
Windows
.venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
4. Start the backend
uvicorn Backend.api:app --reload

Backend:

http://127.0.0.1:8000

Swagger API documentation:

http://127.0.0.1:8000/docs

Health check:

http://127.0.0.1:8000/api/health
5. Start the frontend

Open another terminal:

cd fornend/railmind-ai
python -m http.server 5500

Open:

http://127.0.0.1:5500/
📹 Video Analysis Pipeline

RailMind supports uploading railway video for analysis.

Video Upload
     ↓
Video ID Generated
     ↓
Video Processing
     ↓
YOLO11n Person Detection
     ↓
Crowd Observations
     ↓
Time-Series Signal
     ↓
Crowd Analytics
     ↓
Dashboard

The current prototype demonstrates a video-analysis workflow. Production deployment would require further benchmarking for real-time multi-camera processing.

🌐 Future Scope

RailMind is designed as a foundation for future railway-scale deployment.

Potential improvements include:

Real-time multi-camera CCTV integration
Edge AI deployment
Larger and more diverse railway datasets
Multi-camera tracking
Station-specific camera calibration
More advanced temporal forecasting models
Live railway operational data integration
Automated camera-health monitoring
Improved passenger flow estimation
Integration with railway control-room systems
Large-scale field validation
🔐 Safety & Privacy Considerations

RailMind is designed as a decision-support system, not an autonomous railway control system.

The system does not require passenger facial identification for its crowd-intelligence objective.

In a production environment, privacy-aware deployment should prioritize:

Aggregate crowd information
Minimal retention of raw video
Edge processing where appropriate
Secure data transmission
Role-based access to operational systems

Final operational decisions should remain with authorized railway personnel.

🌍 Social Impact

RailMind is aligned with the broader goals of:

SDG 3 — Good Health & Well-Being

Supporting safer passenger movement and reducing the potential impact of crowd-related incidents.

SDG 9 — Industry, Innovation & Infrastructure

Applying AI and computer vision to railway infrastructure and operational intelligence.

SDG 11 — Sustainable Cities & Communities

Supporting safer, more resilient and better-managed public transportation environments.

🏆 Hackathon
INNOVATE 4 IMPACT: AI4SDG Global Hackathon 2026

Problem Statement:

Real-Time Railway Crowd-Surge Prediction and Control

RailMind AI was developed and presented as our solution during the hackathon.

The team successfully progressed through the initial rounds and reached the Grand Finale, held on 12 September 2026.

👥 Team RailMind AI

Built with teamwork, late-night debugging, testing and a lot of iteration.

Team Members
Saif Dalwale — Team Lead | AI/ML | Backend | System Architecture
Faizan — Frontend | Dashboard | UI/UX
[Member Name] — System Integration | Deployment | Testing
[Member Name] — Research | Data | Documentation | Validation
📜 Disclaimer

RailMind AI is an academic/hackathon prototype developed for demonstration and research purposes.

The current system has not been deployed as an operational system within Indian Railways.

Forecasts, risk scores and intervention projections are model outputs intended for decision support and should not be treated as guaranteed real-world outcomes.
