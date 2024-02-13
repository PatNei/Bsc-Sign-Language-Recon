#!/bin/sh
poetry run uvicorn backend.sign.main:app --reload
# cd frontend && npm run dev
# cd ..