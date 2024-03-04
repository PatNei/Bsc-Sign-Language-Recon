#!/bin/bash
cd backend
poetry run uvicorn sign.main:app --reload
cd ..
