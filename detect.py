import pandas as pd
import numpy as np
import argparse

def create_incident_ids(predictions):
    """
    Create an incident ID for each continuous sequence of anomaly predictions.

    Args:
        predictions: sequence of anomaly prediction values where 0 = normal, 1 = anomaly

    Returns:
        A NumPy array where 0 = normal and each positive integer identifies an incident.
    """
    predictions = np.asarray(predictions, dtype=bool)

    previous = np.concatenate(([False], predictions[:-1]))
    incident_starts = predictions & ~previous

    incident_ids = np.cumsum(incident_starts)

    return np.where(predictions, incident_ids, 0)


def cusum_detector(latencies: pd.Series) -> pd.DataFrame:
    scores = np.zeros(len(latencies))
    predictions = np.zeros(len(latencies), dtype=int)

    # k is the acceptable shift and h is the alarm threshold.
    k = 0.5
    h = 4

    # From how the latencies were generated, this is what we expect
    log_mu = 4.600195
    log_sigma = 0.099751
    positive_cusum = 0

    # Calculate each latency's z-score and accumulate evidence of an upward shift.
    for i, value in enumerate(latencies):
        log_latency = np.log(value)
        z_score = (log_latency - log_mu) / log_sigma

        positive_cusum = max(0, positive_cusum + z_score - k)
        scores[i] = positive_cusum

        # Check if the accumulated evidence goes beyond a threshold
        if positive_cusum > h:
            predictions[i] = 1

    return pd.DataFrame(
        {
            "cusum_score": scores,
            "cusum_prediction": predictions,
            "cusum_incident_id": create_incident_ids(predictions),
        },
        index=latencies.index,
    )

def ewma_detector(latencies: pd.Series) -> pd.DataFrame:
    scores = np.zeros(len(latencies))
    predictions = np.zeros(len(latencies), dtype = int)

    ewma_alpha = 0.2

    # Explain how warning_threshold is caluclated in README
    warning_coefficient = 2.5
    warning_threshold = warning_coefficient * np.sqrt((ewma_alpha/(2 - ewma_alpha)))
    log_mu = 4.600195
    log_sigma = 0.099751
    ewma_value = 0

    for i, value in enumerate(latencies):
        latency = np.log(value)
        z_score = (latency - log_mu) / log_sigma

        ewma_value = ewma_alpha * z_score + (1 - ewma_alpha) * ewma_value
        scores[i] = ewma_value
        if(ewma_value > warning_threshold):
            predictions[i] = 1
    return pd.DataFrame(
        {
            "ewma_score": scores,
            "ewma_prediction": predictions,
            "ewma_incident_id": create_incident_ids(predictions),
        },
        index=latencies.index,
        
    )


all_detectors = ["cusum", "ewma"]

parser = argparse.ArgumentParser(
    description = "Decide which detecting algorithms we should use"
)

parser.add_argument(
    "--detectors",
    nargs="+",
    choices=sorted(all_detectors),
    default=all_detectors,
    help="decide which algorithm to use for calculations"
)

args = parser.parse_args()
# Store which detectors we want to use.
enabled_detectors = args.detectors
DETECTORS = {
    "cusum": cusum_detector,
    "ewma": ewma_detector
}

df = pd.read_csv("data/latency_anomalies.csv")

# Run the chosen detectors and combine their results with the source data.
detector_results = [
    DETECTORS[name](df["latency"])
    for name in enabled_detectors
]

result_df = pd.concat([df, *detector_results], axis=1)
result_df.to_csv("data/detection.csv", index=False)

print(result_df.head())