from datetime import datetime

# -----------------------------
# GET DATASET TIME RANGE
# -----------------------------

def get_dataset_bounds(collection):

    results = collection.get(
        include=["metadatas"]
    )

    metadatas = results["metadatas"]

    timestamps = []

    for meta in metadatas:

        start_time = meta.get(
            "event_time_start"
        )

        if start_time:

            timestamps.append(
                int(start_time)
            )

    if len(timestamps) == 0:

        return None, None

    return (
        min(timestamps),
        max(timestamps)
    )

# -----------------------------
# HUMAN TIME -> UNIX
# -----------------------------

def convert_human_time_to_unix(
    time_string,
    reference_date=None
):

    """
    Example:
    "11:30"
    "15:45"
    """

    if reference_date is None:

        reference_date = datetime.now()

    parsed = datetime.strptime(
        time_string,
        "%H:%M"
    )

    combined = reference_date.replace(

        hour=parsed.hour,

        minute=parsed.minute,

        second=0,

        microsecond=0
    )

    return int(
        combined.timestamp()
    )

# -----------------------------
# RANGE CHECK
# -----------------------------

def validate_time_range(

    start_time,

    end_time,

    dataset_min,

    dataset_max
):

    if start_time < dataset_min:

        start_time = dataset_min

    if end_time > dataset_max:

        end_time = dataset_max

    return start_time, end_time