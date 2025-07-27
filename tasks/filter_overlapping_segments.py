from prefect import task

@task
def filter_overlapping_segments(segments_a, segments_b):
    """
    Filters segments_a to only include segments that overlap with any in segments_b.

    Parameters:
    - segments_a: List of dicts with 'start' and 'end'
    - segments_b: List of dicts with 'start' and 'end'

    Returns:
    - List of segments from segments_a that overlap with any in segments_b
    """
    filtered = []

    for seg_a in segments_a:
        a_start = seg_a["start"]
        a_end = seg_a["end"]

        for seg_b in segments_b:
            b_start = seg_b["start"]
            b_end = seg_b["end"]

            # Check for overlap
            if a_start < b_end and a_end > b_start:
                filtered.append(seg_a)
                break  # No need to check more once we found an overlap

    return filtered
