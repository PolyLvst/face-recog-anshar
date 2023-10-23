#!/bin/bash
# export DISPLAY adalah agar tidak error pada qt.qpa.plugin
export DISPLAY=:0
script_directory="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo $(date)>>$script_directory/logs/logs_cron.txt
run_py="$script_directory/run.py"
lazy_attend="$script_directory/lazy_attend.py"
cd $script_directory
$run_py
echo "Closing, please wait [5s]"
echo "Uploading remaining students"
$lazy_attend
sleep 5s