import numpy as np
import pandas as pd


rng = np.random.default_rng(seed=1)

# Use a log normal distribution to generate the latency values
n = 1000
mean_ms = 100
sd_ms = 10

log_sigma = np.sqrt(np.log(1 + (sd_ms / mean_ms) ** 2))
log_mu = np.log(mean_ms) - (log_sigma**2) / 2
latency = rng.lognormal(mean=log_mu, sigma=log_sigma, size=n)
incident = np.zeros(n, dtype=int)

# Decide how many of each anomaly we want to curate
numSpikes = 10
numSteps = 5
numDrifts = 5

minDuration = 10
maxDuration = 50

anomalyTypes = [1] * numSpikes + [2] * numSteps + [3] * numDrifts
rng.shuffle(anomalyTypes)

for anomalyType in anomalyTypes:
    placed = False

    for attempt in range(1000):
        if anomalyType == 1:
            duration = 1
        else:
            duration = rng.integers(minDuration, maxDuration + 1)

        start = rng.integers(0, n - duration + 1)
        end = start + duration

        if np.any(incident[start:end] != 0):
            continue

        if anomalyType == 1:
            spikeCoef = rng.uniform(3, 5)
            incident[start] = 1
            latency[start] *= spikeCoef
        elif anomalyType == 2:
            stepCoef = rng.uniform(1.2, 1.8)
            incident[start:end] = 2
            latency[start:end] *= stepCoef
        else:
            driftCoef = rng.uniform(1.1, 2)
            incident[start:end] = 3
            drift = np.linspace(1, driftCoef, duration)
            latency[start:end] *= drift

        placed = True
        break

    # If there was no place to add the anomaly print what occured
    if not placed:
        print("Could not place anomaly type: ", anomalyType)

df = pd.DataFrame(
    {
        "time": np.arange(n),
        "latency": latency,
        "incident": incident,
    }
)

df.to_csv("data/latency_anomalies.csv", index=False)