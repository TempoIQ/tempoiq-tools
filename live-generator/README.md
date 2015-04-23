TempoIQ Data Generator
======================

Python script for generating live realistic-looking random sensor data.

Usage:

    TIQ_HOST="my-env.backend.tempoiq.com"
    TIQ_KEY="my-key"
    TIQ_SECRET="my-secret"
    python ./single-device -d "device-key"

The script writes to the specified device in the backend defined
by the environment variables `TIQ_HOST`, `TIQ_KEY`, and `TIQ_SECRET`