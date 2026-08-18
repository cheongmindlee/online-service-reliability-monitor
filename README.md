# Online-Service-Reliability-Monitor
Feed in generated inputs to measure and detect service latency


# Early Steps and Software Architecture
generate.py -> events.csv -> detect.py -> predictions.csv -> evaluate.py -> results.csv

To begin I will generate latency data and records with labels showing whether each event is an anomaly. This will make it possible to test whether the model can accurately predict and evaluate anomalous data.

events.csv will contain | time, latency_ms, is_anomaly, incident_id, incident_type

Then detect.py will take in the data produced by generate.py and go one by one using CUSUM and EWMA to determine whether any point is an anomaly.

predicition.csv will output | incident_id, ewma_score, ewma_prediction, cusum_score, cusum_prediction | and will be able to be merged with events.csv to be evaluated

Then evaluate.py will take the predictions detect.py returned and report the final findings in comparison to the actual values. For example, it can report how many false negatives occurred.

# Anomaly Injection Formulation

This generator models the latency of a healthy service using a lognormal distribution. A lognormal distribution was chosen because latency is non-negative and production latency commonly follows a right-skewed shape: most requests are near the typical latency, with a few outliers taking longer.
The baseline distribution has a target mean of 100 ms and a configurable standard deviation. Since NumPy's lognormal distribution takes parameters in log-space, we need to convert the target mean and standard deviation using:

    log_sigma² = ln(1 + (sd_ms / mean_ms)²)
    log_mu     = ln(mean_ms) - log_sigma² / 2

Samples are then drawn from:

    LogNormal(log_mu, log_sigma)

The anomalies I want to test are isolated spikes, step increases, and gradual drift incidents. For the MVP, incidents should not overlap so that the ground truth anomaly label can be compared cleanly with the detector predictions.

Isolated Spikes: Sudden increase in latency for one specific request. These isolated spikes can occur from a cache miss or a single slow database call. I will capture this by multiplying the latency at one instance by a factor within a predetermined range. Choosing from a range gives the synthetic data more variation than using a consistent factor.

Step Increase: Sudden increase in latency for consecutive number of requests. This anomaly can occur from incidents such as consistent overload of server/service or a bad deployment. I will capture this by multiplying the latency at an instance by a factor within a predetermined range for a random duration within a set range.

Gradual Drift: Gradual increase in latency over a period of time. This anomaly can occur from a memory leak or a growing queue. I will capture this by multiplying the latency across a randomly chosen duration by a growing factor that is also random and within a set range.

The limitation to this process is that by multiplying latency by a factor for these incidents, we are saying that anomalous latency is directly proportional to the original latency. Different causes for incidents could add latency instead. However, for now I chose multiplication as an intentionally simplified model of proportional degradation.

# Determining the number of anomalies and when they occur

For better control of the data, I decided to pick the number of times each anomaly will appear within the list. This allows for better testing and analysis because each generated dataset has a known number of isolated spikes, step increases, and gradual drifts.

Step increases and gradual drifts currently last for a random duration between 10 and 50 requests. This range can be changed later, but it gives each multi-request incident enough length for detection experiments. Isolated spikes last for one request.

To choose where an anomaly occurs, the generator first determines the duration of the incident. It then checks random start points in the incident list. If no other incident has occurred within the candidate duration, the anomaly is placed there. If another incident already exists in that window, the generator tries another random location. This prevents anomaly windows from overlapping.

# Possible Improvements
In the future, I may add latency for certain incidents rather than multiplying it to reflect different causes.

# Detection Algorithms
