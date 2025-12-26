#!/usr/bin/env bash

echo "# decision_games" >>README.md
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin git@github.com:thepseudocodeus/decision_games.git
git push -u origin main
