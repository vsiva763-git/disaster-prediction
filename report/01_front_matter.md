

================================================================================
                        FRANCIS XAVIER ENGINEERING COLLEGE
                          (An Autonomous Institution)
                   Affiliated to Anna University, Chennai
                      Tirunelveli – 627003, Tamil Nadu
================================================================================

                DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING

================================================================================

                            PROJECT REPORT

                                 On

       INDIA-SPECIFIC TSUNAMI EARLY WARNING SYSTEM USING
          ARTIFICIAL INTELLIGENCE AND INTERNET OF THINGS

================================================================================

       Submitted in partial fulfillment of the requirements
         for the award of the degree of

                     BACHELOR OF TECHNOLOGY
                              in
                COMPUTER SCIENCE AND ENGINEERING

================================================================================

       Submitted by:

       Name                          Register Number
       ─────────────────────────────────────────────
       [Student Name 1]              [Register No.]
       [Student Name 2]              [Register No.]
       [Student Name 3]              [Register No.]
       [Student Name 4]              [Register No.]

       Under the Guidance of:
       [Guide Name], [Designation]
       Department of Computer Science and Engineering
       Francis Xavier Engineering College

================================================================================

                          MARCH 2026

================================================================================
                                                                         Page i


================================================================================
                        BONAFIDE CERTIFICATE
================================================================================

This is to certify that the project titled "India-Specific Tsunami Early
Warning System Using Artificial Intelligence and Internet of Things" is the
bonafide work of the following students:

       Name                          Register Number
       ─────────────────────────────────────────────
       [Student Name 1]              [Register No.]
       [Student Name 2]              [Register No.]
       [Student Name 3]              [Register No.]
       [Student Name 4]              [Register No.]

who carried out the project work under my supervision during the academic
year 2025–2026. This project report has been submitted for the B.Tech degree
examination held on [Date] at Francis Xavier Engineering College.


Internal Guide:

Signature: ______________________________
Name: [Guide Name]
Designation: [Designation]
Department of Computer Science and Engineering


Head of the Department:

Signature: ______________________________
Name: [HOD Name]
Department of Computer Science and Engineering


Internal Examiner                          External Examiner
Signature: ______________                  Signature: ______________

                                                                        Page ii


================================================================================
                            DECLARATION
================================================================================

We hereby declare that the project titled "India-Specific Tsunami Early
Warning System Using Artificial Intelligence and Internet of Things"
submitted to the Department of Computer Science and Engineering, Francis
Xavier Engineering College, Tirunelveli, in partial fulfillment of the
requirements for the award of the degree of Bachelor of Technology in
Computer Science and Engineering, is a record of original work done by us
under the supervision and guidance of [Guide Name], [Designation],
Department of Computer Science and Engineering.

We further declare that this project work has not been submitted to any
other university or institution for the award of any other degree or
diploma.


Place: Tirunelveli
Date: [Date]

Signature                  Name                     Register Number
──────────────────────────────────────────────────────────────────────
_______________            [Student Name 1]          [Register No.]
_______________            [Student Name 2]          [Register No.]
_______________            [Student Name 3]          [Register No.]
_______________            [Student Name 4]          [Register No.]

                                                                       Page iii


================================================================================
                          ACKNOWLEDGEMENT
================================================================================

We would like to express our sincere gratitude to all those who have
contributed to the successful completion of this project.

First and foremost, we express our heartfelt thanks to God Almighty for
His blessings and guidance throughout this project.

We are deeply indebted to our beloved Chairman and the Management of
Francis Xavier Engineering College for providing excellent infrastructure
and a conducive learning environment.

We express our sincere thanks to our Principal, Dr. [Principal Name], for
his/her constant encouragement and support.

We extend our profound gratitude to the Head of the Department,
Dr. [HOD Name], Department of Computer Science and Engineering, for
providing the necessary facilities and guidance for this project work.

We are extremely grateful to our Project Guide, [Guide Name],
[Designation], Department of Computer Science and Engineering, for
his/her invaluable guidance, constant supervision, timely suggestions,
and motivation throughout the course of this project. His/her profound
knowledge and insightful feedback were instrumental in shaping this project.

We wish to express our thanks to all the Faculty Members of the Department
of Computer Science and Engineering for their encouragement and support
during the project.

We are thankful to our parents and family members for their unwavering
love, support, encouragement, and patience throughout our academic journey.

Finally, we thank all our friends and well-wishers who have directly or
indirectly helped us in the successful completion of this project.



                                                  [Student Name 1]
                                                  [Student Name 2]
                                                  [Student Name 3]
                                                  [Student Name 4]

                                                                        Page iv


================================================================================
                              ABSTRACT
================================================================================

India's 7,516-kilometer coastline extends across thirteen states and union
territories, placing over 250 million coastal residents at direct risk from
tsunami events. The catastrophic 2004 Indian Ocean tsunami, which caused
approximately 230,000 fatalities globally — including an estimated 16,000 in
India — exposed fundamental deficiencies in the nation's early warning
infrastructure. Conventional tsunami warning systems depend on capital-intensive
deep-ocean sensor networks (Deep-ocean Assessment and Reporting of Tsunamis,
or DART buoys), extensive seismic monitoring stations, and manual expert
analysis, rendering widespread deployment economically impractical for
developing nations. Furthermore, existing global warning systems issue alerts
for all oceanic seismic events without accounting for India's specific
geographic vulnerabilities, resulting in a high false-alarm rate that erodes
public trust and contributes to warning fatigue among coastal populations.

This project presents the design, implementation, and evaluation of an
India-Specific Tsunami Early Warning System that leverages Artificial
Intelligence (AI) and Internet of Things (IoT) technologies to address these
challenges. The system introduces the "Global Training, Local Application"
paradigm — a globally-trained deep learning model combined with India-specific
geographic filtering — utilizing exclusively free public Application
Programming Interfaces (APIs) at zero infrastructure cost.

The core prediction engine employs a Convolutional Neural Network – Long Short-
Term Memory (CNN-LSTM) hybrid architecture trained with Binary Focal Loss
(gamma = 2.0, alpha = 0.25) to address the extreme class imbalance inherent in
tsunami event datasets. The model processes 24-timestep sequences of 32 seismic
and oceanographic features and achieves exceptional performance metrics on the
evaluation dataset: Area Under the Receiver Operating Characteristic Curve
(AUC) of 1.0, classification accuracy of 100%, recall of 100%, and precision
of 100%.

Real-time data ingestion is performed from five public sources: the United
States Geological Survey (USGS) for earthquake parameters, the National
Oceanic and Atmospheric Administration (NOAA) Tides and Currents service for
sea level anomaly detection, NOAA National Data Buoy Center (NDBC) for wave
buoy data, the Indian National Centre for Ocean Information Services (INCOIS)
for official tsunami advisories, and the General Bathymetric Chart of the
Oceans (GEBCO) for ocean bathymetry data. An India-specific filtering layer
evaluates earthquake epicenter proximity to India's coastline using the
Haversine distance formula, assesses wave propagation direction toward Indian
shores, identifies critical subduction zones (Andaman, Makran, Sumatra,
Arabian Sea), and determines potentially affected coastal regions across
thirteen states and union territories. This filtering achieves a reported
seventy-two percent reduction in false alarms compared with unfiltered global
alert dissemination.

The web-based dashboard, built upon the Flask microframework with Leaflet.js
for interactive cartographic visualization, provides real-time display of
earthquake events, risk assessments, and wave animations through four
interactive modes. The IoT alert subsystem extends warnings to physical
hardware devices — Arduino UNO microcontrollers with LCD display and piezo
buzzer connected to ESP8266 WiFi modules — enabling audible and visual alerts
in remote coastal communities. The system supports both direct HTTP push and
cloud polling communication modes for IoT devices, ensuring alerts propagate
reliably through network address translation (NAT) firewalls.

The complete system is containerized using Docker and deployable on free-tier
cloud platforms including Railway and Render, making it accessible to disaster
management authorities, academic researchers, and educational institutions
without financial barriers.

Keywords: Tsunami Early Warning System, CNN-LSTM, Focal Loss, Deep Learning,
Internet of Things, Arduino, ESP8266, India Coastline, USGS, NOAA, INCOIS,
Real-time Prediction, Flask, Disaster Management, Seismic Analysis

                                                                      Page v-vi


================================================================================
                         TABLE OF CONTENTS
================================================================================

BONAFIDE CERTIFICATE ................................................... ii
DECLARATION ........................................................... iii
ACKNOWLEDGEMENT ....................................................... iv
ABSTRACT .............................................................. v-vi
TABLE OF CONTENTS ..................................................... vii-ix
LIST OF FIGURES ....................................................... x-xi
LIST OF TABLES ........................................................ xii
LIST OF ABBREVIATIONS AND SYMBOLS ..................................... xiii-xiv

PART I: INTRODUCTION

CHAPTER 1  INTRODUCTION ............................................... 1
  1.1  Background and Motivation ...................................... 1
  1.2  Problem Statement .............................................. 4
  1.3  Research Objectives ............................................ 5
  1.4  Research Questions ............................................. 6
  1.5  Scope and Limitations .......................................... 7
  1.6  Significance of the Study ...................................... 8
  1.7  Technologies Used .............................................. 9
  1.8  Document Organization .......................................... 11

PART II: LITERATURE REVIEW

CHAPTER 2  LITERATURE REVIEW .......................................... 12
  2.1  Overview of the Research Domain ................................ 12
  2.2  Foundational Theories and Frameworks ........................... 14
  2.3  Survey of Related Work ......................................... 16
       2.3.1  Deep Learning for Seismic Event Detection ............... 16
       2.3.2  Tsunami Early Warning Systems ........................... 18
       2.3.3  IoT in Disaster Management .............................. 20
  2.4  Comparison of Existing Approaches .............................. 22
  2.5  Identified Research Gaps ....................................... 25
  2.6  Summary ........................................................ 28

PART III: METHODOLOGY AND SYSTEM DESIGN

CHAPTER 3  SYSTEM ARCHITECTURE AND TECHNOLOGY STACK ................... 30
  3.1  Overview of the System Architecture ............................ 30
  3.2  Component Interaction and Data Flow ............................ 33
  3.3  Technology Stack and Design Rationale .......................... 35
  3.4  Third-Party Libraries and Dependencies ......................... 38
  3.5  Infrastructure and Deployment Environment ...................... 39

CHAPTER 4  DATA SOURCES AND DATA PIPELINE ............................. 41
  4.1  Data Collection Strategy ....................................... 41
  4.2  USGS Earthquake Data Collector ................................. 43
  4.3  NOAA Tides and Currents Collector .............................. 45
  4.4  NOAA NDBC Buoy Data Collector .................................. 47
  4.5  INCOIS Advisory Collector ...................................... 49
  4.6  GEBCO Bathymetry Loader ....................................... 50
  4.7  Data Preprocessing and Transformation .......................... 51
  4.8  Data Schema and Storage Design ................................. 53

CHAPTER 5  CORE ALGORITHMS AND LOGIC .................................. 54
  5.1  Algorithm 1: Binary Focal Loss Function ........................ 54
  5.2  Algorithm 2: Haversine Distance Calculation .................... 56
  5.3  Algorithm 3: India Risk Score Computation ...................... 58
  5.4  Algorithm 4: Seismic Pattern Synthesis ......................... 60
  5.5  Algorithm 5: Tsunami Arrival Time Estimation ................... 62
  5.6  Algorithm 6: Wave Anomaly Detection ............................ 63
  5.7  Complexity Analysis Summary .................................... 64

CHAPTER 6  MODULE-BY-MODULE IMPLEMENTATION BREAKDOWN .................. 65
  6.1  Module A: CNN-LSTM Binary Model ................................ 65
  6.2  Module B: Multi-Modal CNN-LSTM Model ........................... 68
  6.3  Module C: Data Preprocessor .................................... 70
  6.4  Module D: Model Trainer ........................................ 72
  6.5  Module E: India Impact Filter .................................. 74
  6.6  Module F: Risk Assessor ........................................ 76
  6.7  Module G: Inference Engine ..................................... 78
  6.8  Module H: Flask Web Application ................................ 80
  6.9  Module I: IoT Hardware Integration ............................. 82
  6.10 Module J: Utility Modules ...................................... 84

CHAPTER 7  API DESIGN AND INTERFACES .................................. 85
  7.1  REST API Endpoint Specification ................................ 85
  7.2  Prediction API — Input/Output Specifications ................... 88
  7.3  IoT API — Device Management and Alerting ....................... 90
  7.4  Error Handling and Edge Cases .................................. 92

CHAPTER 8  STORAGE, SECURITY, AND SCALABILITY ......................... 93
  8.1  In-Memory Data Storage Design .................................. 93
  8.2  Security and Authentication .................................... 94
  8.3  Scalability and Performance Considerations ..................... 95
  8.4  Testing Strategy ............................................... 96
  8.5  Reproducibility and Setup Guide ................................ 98
  8.6  Known Bugs, Limitations, and Technical Debt .................... 99

PART IV: RESULTS AND ANALYSIS

CHAPTER 9  RESULTS AND ANALYSIS ....................................... 100
  9.1  Experimental Setup ............................................. 100
  9.2  Quantitative Results ........................................... 101
  9.3  Qualitative Analysis ........................................... 104
  9.4  Comparison with Baseline and Related Systems ................... 106
  9.5  Discussion of Findings ......................................... 108
  9.6  Unexpected Observations and Edge Cases ......................... 109

PART V: DISCUSSION

CHAPTER 10  DISCUSSION ................................................ 110
  10.1 Interpretation of Results in Context of Literature ............. 110
  10.2 Theoretical Implications ....................................... 112
  10.3 Practical Implications ......................................... 113
  10.4 Limitations of the Current Work ................................ 114
  10.5 Threats to Validity ............................................ 115

PART VI: CONCLUSION AND FUTURE WORK

CHAPTER 11  CONCLUSION AND FUTURE WORK ................................ 116
  11.1 Summary of Contributions ....................................... 116
  11.2 Conclusion ..................................................... 118
  11.3 Future Research Directions ..................................... 119
  11.4 Roadmap and Next Steps ......................................... 121

BACK MATTER

REFERENCES ............................................................ 122
APPENDIX A: Key Code Listings ......................................... 128
APPENDIX B: Supplemental Tables and Data .............................. 133
APPENDIX C: Glossary of Terms ......................................... 136

                                                                   Page vii-ix


================================================================================
                          LIST OF FIGURES
================================================================================

Figure No.    Title                                              Page No.
──────────────────────────────────────────────────────────────────────────
Fig. 1.1      2004 Indian Ocean Tsunami Propagation Map              2
Fig. 1.2      India's Coastline with 13 Coastal States/UTs          3
Fig. 1.3      System High-Level Overview Diagram                     5
Fig. 2.1      Tsunami Generation Mechanism at Subduction Zone       12
Fig. 2.2      DART Buoy System Architecture                         13
Fig. 2.3      CNN Architecture for Feature Extraction               16
Fig. 2.4      LSTM Cell Internal Structure                          17
Fig. 2.5      CNN-LSTM Hybrid Processing Pipeline                   18
Fig. 2.6      Focal Loss vs. Cross-Entropy Loss Comparison          19
Fig. 2.7      IoT-Based Disaster Warning Reference Architecture     21
Fig. 3.1      Five-Layer System Architecture Diagram                31
Fig. 3.2      Component Interaction and Data Flow Diagram           33
Fig. 3.3      Technology Stack Overview                             36
Fig. 4.1      Data Collection Pipeline Flow Diagram                 42
Fig. 4.2      USGS GeoJSON Response Structure                       44
Fig. 4.3      Sea Level Anomaly Detection Flow                      46
Fig. 4.4      Buoy Data Processing Pipeline                         48
Fig. 4.5      24×32 Feature Matrix Structure                        52
Fig. 5.1      Focal Loss Function Behavior at Various Gamma         55
Fig. 5.2      Haversine Great-Circle Distance Illustration          57
Fig. 5.3      India Risk Score Component Weights                    59
Fig. 5.4      Seismic Pattern Synthesis Process                     61
Fig. 6.1      Binary CNN-LSTM Model Architecture Diagram            66
Fig. 6.2      Multi-Modal CNN-LSTM Three-Branch Architecture        68
Fig. 6.3      Data Preprocessing Pipeline                           70
Fig. 6.4      Training Pipeline with Callbacks                      72
Fig. 6.5      India Coastal Filtering Zones Map                     74
Fig. 6.6      Risk Assessment Decision Flow                         77
Fig. 6.7      Inference Engine Monitoring Loop                      78
Fig. 6.8      Flask Application Route Architecture                  80
Fig. 6.9      Arduino + ESP8266 Circuit Diagram                     82
Fig. 6.10     IoT Communication Modes                               83
Fig. 7.1      REST API Endpoint Map                                 86
Fig. 7.2      Prediction API Request/Response Flow                  88
Fig. 7.3      IoT Alert Propagation Sequence                        91
Fig. 9.1      Training Loss vs. Epochs Curve                       101
Fig. 9.2      Training Accuracy vs. Epochs Curve                   102
Fig. 9.3      ROC Curve                                            102
Fig. 9.4      Confusion Matrix                                     103
Fig. 9.5      API Response Time Distribution                       105
Fig. 9.6      Live Dashboard Screenshot                            106
Fig. 9.7      Wave Animation — Four Modes                          107
Fig. 9.8      IoT Dashboard Screenshot                             107
Fig. 11.1     Future Enhancement Roadmap                           120

                                                                    Page x-xi


================================================================================
                          LIST OF TABLES
================================================================================

Table No.     Title                                              Page No.
──────────────────────────────────────────────────────────────────────────
Table 1.1     Technologies and Frameworks Used                       9
Table 2.1     Comparison of Existing Tsunami Warning Approaches     23
Table 3.1     Python Library Dependencies                           38
Table 4.1     Data Sources and Collection Methods                   41
Table 4.2     32 Input Feature Descriptions                         52
Table 5.1     Tsunami Capability Assessment Matrix                  59
Table 5.2     Algorithm Complexity Summary                          64
Table 6.1     Binary CNN-LSTM Layer Configuration                   67
Table 6.2     Multi-Modal CNN-LSTM Layer Configuration              69
Table 6.3     Training Hyperparameters                              73
Table 6.4     India Coastal Region Boundaries                       75
Table 6.5     India Risk Score Weight Distribution                  76
Table 6.6     IoT Alert Levels and Buzzer Patterns                  83
Table 7.1     REST API Endpoint Specification                       86
Table 7.2     IoT API Endpoint Specification                        90
Table 7.3     Error Response Codes                                  92
Table 8.1     Hardware Requirements                                 93
Table 8.2     Software Requirements                                 93
Table 9.1     Model Performance Metrics Summary                    101
Table 9.2     Threshold Analysis Results                           103
Table 9.3     Comparison with Related Systems                      106
Table 9.4     API Performance Benchmarks                           105
Table 9.5     Test Case Summary                                    108
Table 11.1    Future Enhancement Roadmap Phases                    120
Table 11.2    Research Direction Priorities                         121

                                                                     Page xii


================================================================================
                 LIST OF ABBREVIATIONS AND SYMBOLS
================================================================================

ABBREVIATIONS
──────────────────────────────────────────────────────────────────────────

AI        Artificial Intelligence
ANN       Artificial Neural Network
API       Application Programming Interface
AUC       Area Under the Curve (Receiver Operating Characteristic)
CNN       Convolutional Neural Network
CORS      Cross-Origin Resource Sharing
CSS       Cascading Style Sheets
DART      Deep-ocean Assessment and Reporting of Tsunamis
DFD       Data Flow Diagram
DL        Deep Learning
ESP       Espressif Systems (ESP8266 WiFi Module)
GEBCO     General Bathymetric Chart of the Oceans
GeoJSON   Geographic JavaScript Object Notation
GPIO      General Purpose Input/Output
GPU       Graphics Processing Unit
HTML      Hypertext Markup Language
HTTP      Hypertext Transfer Protocol
HTTPS     HTTP Secure
INCOIS    Indian National Centre for Ocean Information Services
IOC       Intergovernmental Oceanographic Commission
IoT       Internet of Things
JSON      JavaScript Object Notation
LCD       Liquid Crystal Display
LSTM      Long Short-Term Memory
ML        Machine Learning
MLLW      Mean Lower Low Water
MSE       Mean Squared Error
NAT       Network Address Translation
NDBC      National Data Buoy Center
NDMA      National Disaster Management Authority
NetCDF    Network Common Data Form
NOAA      National Oceanic and Atmospheric Administration
PTWC      Pacific Tsunami Warning Center
REST      Representational State Transfer
RNN       Recurrent Neural Network
ROC       Receiver Operating Characteristic
SHAP      SHapley Additive exPlanations
SMOTE     Synthetic Minority Over-sampling Technique
UML       Unified Modeling Language
USGS      United States Geological Survey
UTC       Coordinated Universal Time
YAML      YAML Ain't Markup Language

SYMBOLS
──────────────────────────────────────────────────────────────────────────

Symbol    Description
γ         Focal Loss focusing parameter (gamma)
α         Focal Loss balancing factor (alpha)
σ         Standard deviation
φ         Latitude in radians (Haversine formula)
λ         Longitude in radians (Haversine formula)
Δ         Difference operator
ω         Angular frequency
π         Mathematical constant (3.14159...)
R         Earth's mean radius (6,371 km)
p_t       Model-predicted probability for class t
θ         Model parameters (weights and biases)

                                                                  Page xiii-xiv

