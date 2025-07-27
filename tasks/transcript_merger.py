from prefect import task

@task
def merge_segments(all_segments: list, output_path: str):
    flat = [s for sublist in all_segments for s in sublist]
    flat.sort(key=lambda x: x["start"])

    with open(output_path, "w", encoding="utf-8") as f:
        for s in flat:
            ts = f"{s['start']:.2f}-{s['end']:.2f}"
            f.write(f"[{ts}] {s['speaker']}: {s['text']}\n")
