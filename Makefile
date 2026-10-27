# Makefile for Equity Research Project
# Usage: make run  (reproduces all outputs from scratch)

PYTHON = .venv/Scripts/python.exe
SHELL = cmd

.PHONY: run test clean setup

setup:
	py -m venv .venv
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

run: 
	$(PYTHON) src/extract.py
	$(PYTHON) src/market_data.py
	$(PYTHON) src/drivers.py
	$(PYTHON) src/forecast.py
	$(PYTHON) src/quality.py
	$(PYTHON) src/scenarios.py
	$(PYTHON) src/sizing.py
	$(PYTHON) src/tripwires.py
	$(PYTHON) src/warroom.py
	$(PYTHON) src/verifier.py
	$(PYTHON) src/memo.py

test:
	$(PYTHON) -m pytest tests/ -v

clean:
	del /s /q data\processed\*.csv 2>nul
	del /s /q outputs\*.* 2>nul
	del /s /q memo\*.* 2>nul
