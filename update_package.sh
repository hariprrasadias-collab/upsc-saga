#!/bin/bash
sed -i 's/"build": "npm install && tsc -b && vite build"/"build": "pnpm install \&\& tsc -b \&\& vite build"/g' frontend/package.json
