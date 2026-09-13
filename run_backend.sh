#!/usr/bin/env bash
cd "$(dirname "$0")/backend"
python -m uvicorn main:app --reload
