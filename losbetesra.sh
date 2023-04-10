#!/bin/bash
python3 losbetesra.py "$1" --generar-python > main.py
python3 main.py
