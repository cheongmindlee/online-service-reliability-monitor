import numpy as np
import pandas as pd
import argparse
parser = argparse.ArgumentParser(
    description = "Decides how much data + what kind of data"
)

def positive_int(number):

    number = int(number)

    if(number < 0):
        raise argparse.ArgumentTypeError(
            "Must bea  non negative integer"
        )
    return number

parser.add_argument(
    "--samples",
    type =positive_int,
    default = 1000,
    help = "Amount of data to generate"
)

parser.add_argument(
    "--seed",
    type = int,
    default = None,
    help = "Choose a seed for reproducible results"
)

count_arguments = [
    ("--spikes", 10, "Number of spike incidents"),
    ("--steps", 5, "Number of step incidents"),
    ("--drifts", 5, "Number of drift incidents")
]

for name, default, description in count_arguments:
    parser.add_argument(
        name,
        type = int,
        default = default,
        help = description,
    )

args = parser.parse_args()

# set variables for number of samples, seed, and number of anomalies from user input
rng = np.random.default_rng(seed = args.seed)
n = args.samples

numSpikes = args.spikes
numSteps = args.steps
numDrifts = args.drifts

minDuration = 10
maxDuration = 50

# Place the anomalies randomly along the data
anomalyTypes = [1] * numSpikes + [2] * numSteps + [3] * numDrifts
rng.shuffle(anomalyTypes)

# Use a log normal distribution to generate the latency values

mean_ms = 100
sd_ms = 10

log_sigma = np.sqrt(np.log(1 + (sd_ms / mean_ms) ** 2))
log_mu = np.log(mean_ms) - (log_sigma**2) / 2
latency = rng.lognormal(mean=log_mu, sigma=log_sigma, size=n)
incident = np.zeros(n, dtype=int)



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