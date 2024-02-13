#!/bin/sh
poetry run uvicorn backend.sign.main:app --reload