
================================================================================
                    PART II: LITERATURE REVIEW
================================================================================


================================================================================
CHAPTER 2    LITERATURE REVIEW
================================================================================
                                                                        Page 12

2.1  OVERVIEW OF THE RESEARCH DOMAIN
────────────────────────────────────────────────────────────────────────────────

The research domain for this project spans three intersecting fields:
geophysical disaster prediction, deep learning for time-series
classification, and Internet of Things (IoT) for emergency alert systems.
This literature review examines the state of the art in each area, with
particular emphasis on work directly relevant to tsunami early warning
in the Indian Ocean context.

Tsunami science has evolved substantially since the discipline's early
focus on post-event geological surveys. Modern tsunami research
encompasses four interrelated domains: (1) seismological source
characterization, which seeks to identify the earthquake parameters
(magnitude, depth, focal mechanism, rupture dynamics) that determine
tsunamigenic potential; (2) numerical propagation modeling, which
simulates wave propagation across ocean basins using shallow water
equations; (3) inundation modeling, which predicts run-up heights and
inland flooding; and (4) warning system engineering, which designs
operational systems for timely alert dissemination [Synolakis and
Bernard, 2006].

The intersection of artificial intelligence with tsunami prediction
represents a relatively recent but rapidly growing area of investigation.
Early approaches applied statistical methods such as logistic regression
and decision trees to seismic parameter databases [Heidarzadeh et al.,
2009]. The advent of deep learning has enabled more sophisticated
spatiotemporal pattern recognition, with convolutional architectures
extracting spatial features from seismic waveforms and recurrent
architectures capturing temporal dependencies in multi-sensor time
series [Romano et al., 2021].

                                                                        Page 13

The IoT dimension of this research draws on the broader field of
sensor-network-based environmental monitoring and disaster response.
The proliferation of low-cost microcontrollers and WiFi-enabled modules
has made distributed sensor and alert networks economically feasible,
shifting the paradigm from centralized institutional warning systems
to community-level participatory monitoring [Poslad et al., 2015].

                              [Figure 2.1]
    ┌─────────────────────────────────────────────────────────┐
    │              TSUNAMI GENERATION MECHANISM               │
    │                                                         │
    │  ─────── Sea Surface ──────────────────────────────     │
    │                ↑                                        │
    │    ~~~~~│ Vertical │ ~~~~~                               │
    │         │ Displace │                                     │
    │         │  -ment   │                                     │
    │  ───────┴──────────┴──────── Ocean Floor ──────────     │
    │       ┌──────┐                                          │
    │       │Thrust│   ← Overriding Plate                     │
    │       │Fault │                                           │
    │    ───┘      └────── Subducting Plate ──────────→       │
    │                                                         │
    │  Earthquake at shallow depth (<70 km) along             │
    │  subduction zone displaces water column vertically      │
    └─────────────────────────────────────────────────────────┘
              Figure 2.1: Tsunami generation mechanism
                    at a subduction zone


2.2  FOUNDATIONAL THEORIES AND FRAMEWORKS
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 14

This section establishes the theoretical foundations upon which the
proposed system is built.

2.2.1  Shallow Water Wave Theory

Tsunami propagation in deep ocean is governed by the linear shallow water
equations, which describe long-wavelength gravity waves in a fluid layer
whose depth is much smaller than the wavelength. The phase velocity of a
tsunami wave is given by:

    c = sqrt(g × h)

where g is gravitational acceleration (9.81 m/s²) and h is the ocean
depth in meters. At a typical deep-ocean depth of 4,000 meters, this
yields a propagation speed of approximately 198 m/s or 713 km/h —
comparable to the speed of a commercial jet aircraft [Titov et al., 2005].
This relationship is critical to the arrival time estimation algorithm
implemented in the risk assessment module of the proposed system.

2.2.2  Convolutional Neural Networks (CNN)

CNNs are a class of deep neural networks that apply learnable convolutional
filters to extract hierarchical spatial features from input data. First
proposed by LeCun et al. (1998) for digit recognition, CNNs have become
the dominant architecture for image classification, object detection, and,
more recently, time-series feature extraction. A convolutional layer
applies K filters of size F×F to an input tensor, producing K feature maps
that capture local patterns at progressively higher levels of abstraction
through stacking [Goodfellow et al., 2016].

In the context of this project, Conv2D layers extract spatial patterns from
the 24×32 input matrix, where each row represents a timestep and each
column represents a seismic or oceanographic feature. This formulation
treats the multisensor time series as a two-dimensional "image" whose
spatial structure encodes cross-feature correlations.

                                                                        Page 15

2.2.3  Long Short-Term Memory (LSTM) Networks

LSTM networks, introduced by Hochreiter and Schmidhuber (1997), are a
variant of Recurrent Neural Networks (RNNs) designed to address the
vanishing gradient problem that limits standard RNNs' ability to learn
long-range temporal dependencies. An LSTM cell maintains a cell state
vector c_t that is updated through three gating mechanisms:

(a) Forget Gate:  f_t = σ(W_f · [h_{t-1}, x_t] + b_f)
(b) Input Gate:   i_t = σ(W_i · [h_{t-1}, x_t] + b_i)
(c) Output Gate:  o_t = σ(W_o · [h_{t-1}, x_t] + b_o)

The cell state is updated as:
    c_t = f_t ⊙ c_{t-1} + i_t ⊙ tanh(W_c · [h_{t-1}, x_t] + b_c)

And the hidden state (output) is:
    h_t = o_t ⊙ tanh(c_t)

where σ is the sigmoid activation, ⊙ denotes element-wise multiplication,
and W, b are learnable weight matrices and bias vectors [Hochreiter and
Schmidhuber, 1997].

In this project, LSTM layers process the features extracted by the CNN
layers to capture temporal evolution patterns in seismic sequences —
specifically, the progression of earthquake swarms, foreshock-mainshock
patterns, and evolving ocean conditions that may precede a tsunamigenic
event.

2.2.4  Focal Loss for Class Imbalance

Binary cross-entropy loss, the standard objective function for binary
classification, assigns equal importance to all training samples
regardless of classification difficulty. In datasets with extreme class
imbalance — such as tsunami events, where positive instances constitute
less than 5% of observations — this leads to the model being dominated
by the overwhelming majority of easy negative examples [Lin et al., 2017].

Focal Loss, proposed by Lin et al. (2017) for dense object detection
(RetinaNet), modifies the standard cross-entropy by introducing a
modulating factor:

    FL(p_t) = -α_t × (1 - p_t)^γ × log(p_t)

where p_t is the model's estimated probability for the correct class,
α_t is a balancing factor (α for positive class, 1-α for negative), and
γ is the focusing parameter. When γ = 0, FL reduces to standard
cross-entropy. As γ increases, the loss assigned to well-classified
examples (p_t >> 0.5) is strongly down-weighted, focusing training on
hard, misclassified examples [Lin et al., 2017].

In the proposed system, γ = 2.0 and α = 0.25 are used, meaning the
model aggressively focuses on difficult examples while relatively
down-weighting the abundant easy negative cases. This configuration
is critical for achieving high recall — the most important metric for
a warning system where missed detections can cost lives.


2.3  SURVEY OF RELATED WORK
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 16

2.3.1  Deep Learning for Seismic Event Detection

The application of deep learning to seismic event detection and
classification has grown substantially since 2017. Key contributions
include:

Perol et al. (2018) developed ConvNetQuake, a CNN architecture trained
to detect and locate seismic events from single-station waveform data.
Their model achieved 94.5% accuracy on the Oklahoma earthquake catalog,
demonstrating that deep learning can match or exceed traditional
seismological methods based on STA/LTA (Short-Term Average / Long-Term
Average) triggering algorithms. However, ConvNetQuake focused on
earthquake detection rather than tsunami potential assessment and did
not incorporate ocean data.

Mousavi et al. (2020) introduced EQTransformer, a multi-task deep
learning model based on the Transformer architecture that simultaneously
detects earthquakes, determines P-wave and S-wave arrival times, and
performs first-motion polarity classification. Trained on one million
labeled waveforms, EQTransformer achieved an F1 score of 0.95 for event
detection. The attention-based architecture represents the state of the
art in seismic processing; however, it processes individual seismograms
rather than multisource features relevant to tsunami prediction.

                                                                        Page 17

Ross et al. (2018) applied a generalized phase detection model (GPD)
using deep residual neural networks to seismic phase picking, achieving
superhuman performance on benchmark datasets. Their work demonstrated
that deep learning models can be trained once and applied across
different geographic regions without retraining — a principle echoed in
the "Global Training, Local Application" paradigm of the proposed system.

Makinoshima et al. (2021) conducted a comprehensive review of machine
learning applications in tsunami science, categorizing approaches into
four groups: (a) source parameter estimation, (b) propagation prediction,
(c) inundation forecasting, and (d) damage/risk assessment. They
identified CNN-LSTM hybrid architectures as particularly promising for
real-time forecasting applications due to their ability to capture both
spatial and temporal patterns simultaneously.

2.3.2  Tsunami Early Warning Systems
                                                                        Page 18

The evolution of tsunami early warning systems can be traced through
three generations:

First Generation (1949–2004): The Pacific Tsunami Warning Center (PTWC),
established after the 1946 Alaskan tsunami, relied on seismograph
networks and manual analysis. Alert criteria were based primarily on
earthquake magnitude and location, resulting in high false-alarm rates
exceeding 75% [Gonzalez et al., 2005].

Second Generation (2004–2015): Following the 2004 Indian Ocean disaster,
the DART buoy network was expanded, and real-time deep-ocean pressure
data was integrated with seismic analysis. The NOAA Center for Tsunami
Research developed the MOST (Method of Splitting Tsunami) numerical
model for real-time wave propagation forecasting [Titov et al., 2005].
India established ITEWC at INCOIS, integrating seismic networks, tide
gauges, and DART buoys for the Indian Ocean [Nayak and Kumar, 2008].

Third Generation (2015–Present): Recent systems incorporate machine
learning for automated alert generation. Japan's JMA tsunami warning
system, considered the most advanced globally, combines W-phase
centroid moment tensor analysis with pre-computed tsunami scenario
databases to issue warnings within three minutes of an earthquake
[Kamigaichi, 2009]. Germany's GFZ GITEWS (German-Indonesian Tsunami
Early Warning System) demonstrated GPU-accelerated tsunami simulation
for real-time forecasting [Behrens et al., 2010].

The proposed system aligns with the emerging fourth generation of
tsunami warning systems, characterized by AI-driven prediction, IoT-
enabled distributed alerting, and cloud-based deployment that eliminates
dependence on dedicated institutional infrastructure.

                                                                        Page 19

Recent research by Liu et al. (2021) explored using deep neural networks
to predict tsunami wave heights from seismic source parameters, achieving
mean absolute errors below 0.5 meters for near-field events. Their model,
trained on synthetic tsunami scenarios generated by finite-element
simulation, demonstrated that neural networks can approximate complex
hydrodynamic models at a fraction of the computational cost.

Maeda et al. (2015) proposed a data-driven approach using dense ocean-
bottom pressure gauge networks for tsunami prediction, achieving
forecasts within 3 minutes for the 2011 Tohoku event. While highly
accurate, this approach requires expensive instrumented seafloor
infrastructure — the exact constraint that the proposed system seeks
to overcome.

2.3.3  IoT in Disaster Management
                                                                        Page 20

The application of IoT technologies in disaster management spans several
domains:

Kodali and Patel (2016) developed a low-cost IoT-based weather
monitoring system using ESP8266 and various sensors, demonstrating that
WiFi-enabled microcontrollers could provide real-time environmental data
at a fraction of the cost of commercial weather stations. Their work
established the viability of ESP8266-based systems for environmental
monitoring in developing countries.

Poslad et al. (2015) surveyed IoT approaches for environmental
monitoring and disaster response, identifying key architectural patterns
including: (a) sensor-to-cloud direct communication, (b) edge gateway
aggregation, and (c) mesh sensor networks. They highlighted that
reliable, low-latency alert delivery remains the primary challenge in
IoT-based warning systems.

Shah et al. (2019) designed an IoT-based earthquake early warning
system using MEMS accelerometers and ESP32 modules, achieving detection
latencies under 2 seconds. Their system demonstrated that distributed
IoT sensors can complement institutional seismic networks, particularly
in regions with sparse instrumentation.

                                                                        Page 21

Ray et al. (2017) explored IoT-based flood warning systems for India,
noting the challenges of last-mile connectivity in rural areas. They
proposed a hybrid communication architecture combining WiFi, cellular,
and LoRa (Long Range) radio to ensure alerts reach communities lacking
reliable internet connectivity.

                              [Figure 2.7]
    ┌─────────────────────────────────────────────────────────┐
    │            IoT DISASTER WARNING ARCHITECTURE            │
    │                                                         │
    │  ┌─────────┐    ┌────────┐    ┌──────────────┐         │
    │  │ Sensors │───→│ Edge   │───→│ Cloud Server │         │
    │  │ (Seismic│    │Gateway │    │  (AI Engine) │         │
    │  │  Ocean) │    │(ESP8266│    │              │         │
    │  └─────────┘    └────────┘    └──────┬───────┘         │
    │                                      │                  │
    │           ┌──────────────────────────┐│                  │
    │           │                          ↓│                  │
    │  ┌────────┤    Alert Distribution    ├│                  │
    │  │        └──────────────────────────┘│                  │
    │  │                                    │                  │
    │  ↓              ↓              ↓      ↓                 │
    │ ┌────┐    ┌──────────┐  ┌─────────┐  ┌────────┐       │
    │ │LCD │    │Web Dash- │  │ Mobile  │  │  SMS   │       │
    │ │+Buz│    │  board   │  │  App    │  │Gateway │       │
    │ │zer │    └──────────┘  └─────────┘  └────────┘       │
    │ └────┘                                                  │
    └─────────────────────────────────────────────────────────┘
    Figure 2.7: IoT-based disaster warning reference architecture

The proposed system specifically addresses a gap identified across these
IoT studies: the integration of AI-driven prediction with physical
alert hardware in a single, cohesive system. While most IoT approaches
focus on either data collection or alert delivery independently, this
project unifies the complete pipeline from sensor data ingestion through
AI analysis to physical buzzer and LCD activation.


2.4  COMPARISON OF EXISTING APPROACHES
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 22

Table 2.1 presents a systematic comparison of existing tsunami warning
approaches against the proposed system across twelve evaluation criteria.

Table 2.1: Comparison of Existing Tsunami Warning Approaches

┌──────────────────┬──────────┬──────────┬──────────┬──────────┬──────────┐
│ Criterion        │ PTWC     │ INCOIS   │ GITEWS   │ JMA      │ Proposed │
│                  │ (USA)    │ (India)  │ (Germany)│ (Japan)  │ System   │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Detection        │ Seismic  │ Seismic  │ GPS +    │ Seismic  │ AI +     │
│ Method           │ + DART   │ + DART   │ Seismic  │ W-phase  │ Multi-   │
│                  │          │          │ + GPS    │          │ source   │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ AI/ML            │ Limited  │ No       │ No       │ No       │ CNN-LSTM │
│ Integration      │          │          │          │          │ Focal    │
│                  │          │          │          │          │ Loss     │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Infrastructure   │ Very     │ High     │ Very     │ Very     │ Zero     │
│ Cost             │ High     │          │ High     │ High     │          │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ False Alarm      │ ~75%     │ ~70%     │ ~45%     │ ~30%     │ ~20%*    │
│ Rate             │          │          │          │          │          │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Alert Latency    │ 10-15    │ 10-30    │ 5-15     │ 2-3 min  │ <2 min   │
│                  │ min      │ min      │ min      │          │          │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Region-Specific  │ Pacific  │ Indian   │ Indian   │ Japan    │ India-   │
│ Filtering        │ Basin    │ Ocean    │ Ocean    │ coast    │ specific │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ IoT Hardware     │ No       │ No       │ No       │ Yes      │ Yes      │
│ Alerts           │          │          │          │ (J-Alert)│(Arduino) │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Open Source      │ Partial  │ No       │ Partial  │ No       │ Yes      │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Cloud Native     │ No       │ No       │ No       │ No       │ Yes      │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Data Sources     │ Proprie- │ Proprie- │ Proprie- │ Proprie- │ Free     │
│                  │ tary     │ tary     │ tary     │ tary     │ APIs     │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Web Dashboard    │ Yes      │ Yes      │ Yes      │ Yes      │ Yes      │
├──────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┤
│ Replicability    │ No       │ No       │ No       │ No       │ Yes      │
│ (by students)    │          │          │          │          │          │
└──────────────────┴──────────┴──────────┴──────────┴──────────┴──────────┘

* Estimated based on India-specific filtering reducing unfiltered
  false alarms by 72%.

                                                                        Page 23

Analysis of Table 2.1:

Several observations emerge from this comparison:

(1) Cost Disparity: All existing operational systems require significant
    capital investment in sensor infrastructure (DART buoys, seismic
    networks, GPS receivers), placing them beyond the reach of individual
    institutions, educational organizations, or local government bodies.
    The proposed system eliminates this barrier entirely by leveraging
    free public APIs.

(2) AI Gap: Despite the demonstrated potential of deep learning for
    seismic analysis, none of the four operational systems surveyed
    incorporate CNN-LSTM or comparable deep learning architectures for
    automated tsunami prediction. The PTWC has explored machine learning
    in research settings but has not deployed it operationally as of 2024.

(3) IoT Integration: Only Japan's J-Alert system provides hardware-level
    alert delivery, but it operates through proprietary receivers
    integrated into consumer electronics. No existing system offers open-
    hardware IoT alert delivery comparable to the Arduino + ESP8266
    approach proposed here.

(4) Replicability: No existing system can be replicated by a student,
    researcher, or local authority without institutional access to
    sensor networks and specialized infrastructure. The proposed system
    is designed for full replicability using commodity hardware and free
    software.

                                                                        Page 24

(5) Alert Latency: The proposed system targets alert generation within
    two minutes of earthquake occurrence — comparable to Japan's JMA
    system, which is considered the fastest operational system globally.
    This is achieved by eliminating manual analysis and using pre-trained
    model inference, which executes in under two seconds on commodity
    hardware.

(6) India-Specificity: While INCOIS provides India-focused warnings, its
    alert criteria are largely borrowed from global thresholds and do not
    implement the fine-grained geographic filtering (critical subduction
    zone analysis, Haversine distance to specific coastal regions, wave
    propagation direction assessment) that the proposed system provides.


2.5  IDENTIFIED RESEARCH GAPS
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 25

Based on the literature survey presented in Sections 2.1 through 2.4,
the following specific research gaps are identified:

Gap 1: Absence of Zero-Cost AI-Based Tsunami Warning Systems

The literature reveals no existing system that combines deep learning
prediction with a zero-cost data infrastructure. All operational systems
and most research prototypes assume access to proprietary sensor networks.
The few AI-based approaches in the literature [Liu et al., 2021;
Makinoshima et al., 2021] are purely retrospective analyses without
operational deployment. The proposed system directly addresses this gap
by demonstrating a production-ready system built entirely on free APIs.

Gap 2: Lack of India-Specific Geographic Filtering in AI Models

While global tsunami models exist, no published work implements multi-
criteria geographic filtering specifically calibrated for India's
coastline. The critical factors — proximity to the Andaman subduction
zone (the source of the 2004 disaster), the Makran subduction zone
(threatening Gujarat and the western coast), wave channeling in the Bay
of Bengal, and the vulnerability of low-lying island territories — are
not systematically incorporated into any existing AI-based prediction
system.

                                                                        Page 26

Gap 3: No Integrated AI + IoT Tsunami Warning Pipeline

Existing literature treats AI-based prediction and IoT-based alerting
as separate research problems. No published work demonstrates a unified
pipeline where AI model output directly triggers physical hardware
alerts (buzzer, LCD display) through IoT communication. The proposed
system closes this gap by implementing automatic alert propagation from
CNN-LSTM prediction to Arduino-based hardware alerts via ESP8266 WiFi.

Gap 4: Focal Loss Not Applied to Tsunami Prediction

Focal Loss [Lin et al., 2017] has been extensively validated in computer
vision (object detection, medical imaging) but has not been applied to
geophysical disaster prediction in the published literature (as of the
survey date). The extreme class imbalance in tsunami datasets (positive
events constitute <5% of earthquakes) makes Focal Loss theoretically
ideal for this domain, yet this connection has not been explored.

Gap 5: Cloud-Native Disaster Management Systems

The literature on disaster warning systems assumes dedicated server
infrastructure. No existing warning system is designed for deployment
on free-tier cloud platforms (Railway, Render, Heroku), which would
enable educational institutions and local governments to host their own
instances without capital expenditure. The proposed system demonstrates
this deployment model.

Gap 6: Open-Hardware IoT Alert Devices for Tsunami Warning

While IoT has been applied to flood detection [Ray et al., 2017] and
earthquake monitoring [Shah et al., 2019], no published work provides
an open-hardware design for tsunami alert devices that can be assembled
from commonly available components (Arduino UNO, ESP8266, 16×2 LCD,
piezo buzzer) for under USD 10 per unit, with software downloadable
from the warning system's web interface.

                                                                        Page 27

2.6  SUMMARY
────────────────────────────────────────────────────────────────────────────────
                                                                        Page 28

This literature review has established the theoretical foundations
(shallow water wave theory, CNN, LSTM, Focal Loss) and surveyed the
current state of the art across three intersecting research domains:
deep learning for seismic event detection, tsunami early warning
systems, and IoT for disaster management.

The key finding of this review is that despite substantial progress in
each individual domain, no existing system or published research
combines all three into a unified, zero-cost, India-specific solution.
The six identified research gaps collectively define the contribution
space of the proposed system:

(a) Zero-cost AI prediction using free public APIs (Gap 1)
(b) India-specific multi-criteria geographic filtering (Gap 2)
(c) Integrated AI-to-IoT alert pipeline (Gap 3)
(d) Focal Loss for tsunami class imbalance (Gap 4)
(e) Cloud-native deployment on free platforms (Gap 5)
(f) Open-hardware alert devices under USD 10 (Gap 6)

The proposed system is designed to address all six gaps simultaneously,
representing a novel contribution at the intersection of AI, IoT, and
disaster management.

The following chapters (Part III) provide exhaustive technical
documentation of how each gap is addressed through specific
architectural decisions, algorithmic implementations, and engineering
choices. The methodology section constitutes the core of this report,
providing sufficient detail for complete replication of the system.

                                                                        Page 29

