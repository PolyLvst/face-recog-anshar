#!/bin/bash
VERS="1.0"
# Check if build-essential is installed
if ! dpkg -l | grep -q "build-essential"; then
    echo "build-essential is not installed. Installing..."
    sudo apt-get update
    sudo apt-get install -y build-essential
fi

# Check if python3-dev is installed
if ! dpkg -l | grep -q "python3-dev"; then
    echo "python3-dev is not installed. Installing..."
    sudo apt-get update
    sudo apt-get install -y python3-dev
fi

# Check if python3-tk is installed
if ! dpkg -l | grep -q "python3-tk"; then
    echo "python3-tk is not installed. Installing..."
    sudo apt-get update
    sudo apt-get install -y python3-tk
fi
# Check if cmake is installed
if ! dpkg -l | grep -q "cmake"; then
    echo "cmake is not installed. Installing..."
    sudo apt-get update
    sudo apt-get install -y cmake
fi

# Check if pip is installed
if ! dpkg -l | grep -q "python3-pip"; then
    echo "cmake is not installed. Installing..."
    sudo apt-get update
    sudo apt-get install -y python3-pip
fi

# Check if dos2unix is installed
if ! command -v dos2unix &>/dev/null; then
    echo "dos2unix is not installed. Installing..."
    sudo apt-get update
    sudo apt-get install -y dos2unix
fi

echo "Converting python to unix"
script_directory="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
if [ -d "$script_directory" ]; then
    # Convert from dos to unix
    find "$script_directory" -type f -name "*.py" -exec dos2unix {} \;
    echo "Conversion complete."
else
    echo "Directory not found: $script_directory"
fi

echo "Installing requirements"
pip install -r $script_directory/requirements.txt

echo "Refreshing bin"
python3 "$script_directory/multi_encode.py" -r
env_file="$script_directory/.env"

# Check if the .env file exists
if [ -f "$env_file" ]; then
    echo ".env file exist"
else
    echo "File $env_file does not exist."
fi
crontab_main="$script_directory/crontab.txt"
echo "Buka terminal lalu ketik crontab -e"> $crontab_main
echo "Copy & Paste :">> $crontab_main
# Change the path for run.py
echo "@reboot sleep 30;cd $script_directory;XDG_RUNTIME_DIR=/run/user/$(id -u) $script_directory/run.sh >> $script_directory/logs/logs_cron.txt 2>&1">> $crontab_main
# Change the path for lazy_attend.py
echo "*/5 * * * 1-6 cd $script_directory && $script_directory/lazy_attend.py >> $script_directory/logs/logs_cron.txt 2>&1">> $crontab_main
echo "Crontab.txt is ready to be copied by user"

find "$script_directory" -type f -name "*.py" -exec chmod +x {} \;
echo "Executing permission granted for all py file"
echo "Making desktop icon and shortcuts .. "
run_sh="$script_directory/run.sh"
desktop_entry="$script_directory/face-recog.desktop"
desktop_entry_temp="$script_directory/face-recog-$VERS.desktop"
cp $desktop_entry $desktop_entry_temp
icon_app="$script_directory/resources/desktop.png"
if [ -f "$desktop_entry_temp" ]; then
    sed -i "s|Exec=path|Exec=$run_sh|" "$desktop_entry_temp"
    sed -i "s|Icon=path|Icon=$icon_app|" "$desktop_entry_temp"
    if [ $? -eq 0 ]; then
        echo "$desktop_entry_temp updated."
    else
        echo "Failed to update $desktop_entry_temp."
    fi
else
    echo "File $desktop_entry_temp does not exist."
fi
chmod +x $run_sh
cd ~
cp $desktop_entry_temp "Desktop/"
cp $desktop_entry_temp ".local/share/applications/"
rm $desktop_entry_temp

chmod +x "Desktop/face-recog-$VERS.desktop"
chmod +x ".local/share/applications/face-recog-$VERS.desktop"
echo "All required packages are installed."
echo "Klik kanan shortcut desktop lalu klik allow launching"
echo "Bootstrap done .. dont forget to add the cron job inside the crontab.txt file"
