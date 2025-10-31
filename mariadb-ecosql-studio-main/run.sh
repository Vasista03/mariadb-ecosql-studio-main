#!/bin/bash

echo "Starting backend server..."
cd backend
uvicorn app:app --reload &

sleep 2

echo "Starting Streamlit frontend..."
cd ../frontend
streamlit run app.py
