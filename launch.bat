@echo off
chcp 65001 >nul
title Daily Task Reminder
cd /d "%~dp0"
start "" python "%~dp0daily_tasks.py"
