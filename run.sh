#!/usr/bin/env bash

export $(grep -v '^#' .env | xargs)

uvicorn fip2dmp_importer:app --reload
