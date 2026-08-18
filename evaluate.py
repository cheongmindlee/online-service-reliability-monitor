import pandas as pd
import numpy as np

def evaluate_detector(
    df: pd.DataFrame,
    detector_name: str,
) -> dict:
    """
    Evaluate one detector's row-level predictions against the ground truth.

    Any nonzero value in the incident column is treated as anomalous. The
    detector's predictions must be in a column named <detector>_prediction.

    Args:
        df: DataFrame containing ground-truth incidents and detector predictions.
        detector_name: Name of the detection algorithm to evaluate.

    Returns:
        A dictionary containing confusion-matrix counts, precision, recall,
        and F1 score for the detector.
    """
    prediction_column = f"{detector_name}_prediction"

    if prediction_column not in df.columns:
        raise ValueError(f"Missing column: {prediction_column}")
    
    actual = df["incident"].ne(0)
    predicted = df[prediction_column].astype(bool)

    anomalies = int (actual.sum())
    true_positives = int((actual & predicted).sum())
    false_positives = int((~actual & predicted).sum())
    true_negatives = int((~actual & ~predicted).sum())
    false_negatives= int((actual & ~predicted).sum())

    precision_denominator = true_positives + false_positives
    recall_denominator = true_positives + false_negatives

    precision = (
        true_positives / precision_denominator
        if precision_denominator
        else 0.0
    )

    recall = (
        true_positives / recall_denominator
        if recall_denominator
        else 0.0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall)
        else 0.0
    )

    return{
        "detector": detector_name,
        "anomalies": anomalies,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "true_negatives": true_negatives,
        "false_negatives": false_negatives,
        "precision": precision,
        "recall": recall,
        "f1_score": f1
    }

def evaluate_all_detectors(df: pd.DataFrame):
    """
    Discover and evaluate every detector represented in the DataFrame.

    Detector names are derived from columns ending in _prediction. Each
    discovered detector is evaluated with evaluate_detector.

    Args:
        df: DataFrame containing ground-truth incidents and detector predictions.

    Returns:
        A DataFrame indexed by detector name with one column per evaluation
        metric.
    """
    suffix = "_prediction"

    detector_names = [
        column.removesuffix(suffix)
        for column in df.columns
        if column.endswith(suffix)
    ]

    data = [
        evaluate_detector(df, name)
        for name in detector_names
    ]

    for detector in data:
        for key, value in detector.items():
            if isinstance(value, float):
                print(f"{key: <20}| {value:.2f}")
            else:
                print(f"{key:<20}| {value}")
        print()

    return pd.DataFrame(data).set_index("detector")


df = pd.read_csv("data/detection.csv")

results = evaluate_all_detectors(df)
results.to_csv("data/evaluation.csv")
