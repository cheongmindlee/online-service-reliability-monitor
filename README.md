# Online-Service-Reliability-Monitor
Feed in generated inputs to measure and detect service latency


# Early Steps and Software Architecture
generate.py -> events.csv -> detect.py -> predictions.csv -> evaluate.py -> results.csv

To begin I will generate latency data and records - with data which contains whether this event was a anomaly to be able to test whether my model can accurately predict and evaluate data.

events.csv will contain | incident_id, latency_ms, is_anomaly, incident_id, incident_type

Then detect.py will take in the data produced by generate.py and go one by one using CUSUM, and EWMA to determine whether a any point an event was an anomly

predicition.csv will output | incident_id, ewma_score, ewma_prediction, cusum_score, cusum_prediction | and will be able to be merged with events.csv to be evaluated

Then evalue.py will take the predictions detect.py returned and report the final findings in comparison to the actual values that they should've been. ex. How many false negatives were reported.