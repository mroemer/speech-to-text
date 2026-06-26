FILE=$1
PYTHONPATH=. python flows/combined_transcription_flow.py inputs/$FILE.zip \
    --whisper_model large-v3 \
    --output_dir outputs/$FILE \
  && python3 sum_speaking_time.py outputs/$FILE/*.json > outputs/$FILE/speaking_times.txt \
  && cp outputs/$FILE/final_transcript.txt outputs/${FILE}_final_transcript.txt \
  && cp outputs/$FILE/speaking_times.txt outputs/${FILE}_speaking_times.txt \
  && tar cfzv outputs/$FILE.tar.gz outputs/$FILE \
  && rm -rf outputs/$FILE