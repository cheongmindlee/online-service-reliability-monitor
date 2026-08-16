# Online-Service-Reliability-Monitor
Feed in generated inputs to measure and detect service latency


# Early Steps and Software Architecture
generate.py -> events.csv -> detect.py -> predictions.csv -> evaluate.py -> results.csv

To begin I will generate latency data and records - with data which contains whether this event was a anomaly to be able to test whether my model can accurately predict and evaluate data.

events.csv will contain | incident_id, latency_ms, is_anomaly, incident_id, incident_type

Then detect.py will take in the data produced by generate.py and go one by one using CUSUM, and EWMA to determine whether a any point an event was an anomly

predicition.csv will output | incident_id, ewma_score, ewma_prediction, cusum_score, cusum_prediction | and will be able to be merged with events.csv to be evaluated

Then evalue.py will take the predictions detect.py returned and report the final findings in comparison to the actual values that they should've been. ex. How many false negatives were reported.

# Anomaly Injection Formulation

This generator models hte latency of a healthy service using a lognormal distribution. A log normal disribuion was chosen since latency is non negative and production latency comonly follows a right-skewed shape (as most requests are near the typical latency with a few outliers taking longer). 
The baseline ditribution has a target mean of 100 ms and a configurable standard distribution. Since NumPy's lognormal distribution takes parameters in logsapce we need to standardize our mean and standard deviation using 
    log_sigma² = ln(1 + (sd_ms / mean_ms)²)
    log_mu     = ln(mean_ms) - log_sigma² / 2
and samples are drawn from 
    LogNormal(log_mu, log_sigma)


The anomalies I want to test are isolated spikes, step increase, gradual drift incident

Isolated Spikes: Sudden increase inlatency for one specific request. These isolated spikes in latency can occur from a cache miss or a singular slow database recall. I will capture this by multiplying the latency at an instance by a predetermined factor. 

Step Increase: Sudden increase in latency for consecutive number of requests. This anomaly can occur from incidents such as consisten overload of server/service or a bad deployment. I will capture this by multiplying the latency at an instance by a predetermined factor for a determined duration.

Gradual Drift: Gradual increase in latency over a period of time. This anomly can occur from a memory leak or an increasing growing queue. I will capture this by multiplying the latency at an instance within a determined duration by a growing factor. 

The limitations to this prcoess, is that by mulltiplying latency by a factor for these incidents we are saying that latency is a directly proportional to original latency. Different causes for incidents could have different addition of latency. However, for now I choose multiplication as an intentional simlified model of proportional degradation.

# Possible Imporvements
In the future to improve this model I may add to certain latency incidents rather than multiplying them to reflect different cuases. 