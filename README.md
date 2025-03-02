# Temp Files Collector Script

## Overview
A Python 3 script that monitors a `tmp` folder (in a specified base directory)
and waits until it has at least **10 valid files**.  Once there are 10 or more than 10 files in the `tmp` folder, the script archives them into `files.tar.gz`, deletes the archived files from the `tmp` folder and then exits as per the requirement.

**Design Decisions**:
The below files will be ignored
- Hidden files (those starting with `.`)
- Swap files (`.swp`, `.swo`, `.swx`, etc.)

Once there are 10 valid files, the script:
1. Renames any existing archive (`files.tar.gz`) in the same directory to `files_<timestamp>.tar.gz`.
2. Creates a new `files.tar.gz` with the latest 10 (or more) valid files.
3. Removes the original files from `tmp`.
4. Prints `files collected` to stdout and exits.

Commmand-Line Arguments:
1. The script can take two commandline arguments `--base-dir` and `--log-level`.
2. `--base-dir` is used to pass the base directory where the script watches the `tmp` sub-directory.
3. If the `--base-dir` argument is not supplied, the script assumes present working directory.
4. `--log-level` is used to configure the python `logging` pcakged used in the script to log any information required to debug issues. Any exception while dealing with the os calls are caught and logged as error.
5. If the `--log-level` argument is not specified, ERROR level is assumed. `DEBUG, INFO, WARNING, ERROR` are the log levels supported.

Build and Package:
1. The script can be started manually or can be run as a systemd service. A `Makefile` added in the project to build and package the script as as debian package `tmp-files-collector_1.0.0.deb`. The debian package includes the `systemd` service configuration files to start it as a `systemd` service. 

## Files
- **tmp_files_collector.py**: The main script containing `TmpFileCollector` class.
- **tmp_files_collector.service**: A systemd service file to run the script in the backgroud as a `systemd` service.
- **Makefile**: Automates building a `.deb` package for Debian/Ubuntu-like systems.
- **debian/postinst**: A post-install script that enables and starts the service after install.

## Building and installing it as a debian package
```
   make all
   sudo dpkg -i tmp-files-collector_1.0.0.deb
```
This prompts the user for `base-dir`, `log-level` and launches the script as a systemd service.
```
Please enter the desired base directory for 'tmp' and archives.
Press [Enter] to use the default (/opt/collector).
/opt/collector/test
Please enter the desired logging level (DEBUG, INFO, WARNING, ERROR).
Press [Enter] to default to ERROR.
DEBUG
Created symlink /etc/systemd/system/multi-user.target.wants/tmp_files_collector.service → /lib/systemd/system/tmp_files_collector.service.
==================================================
tmp_files_collector service installed/started with:
  BASE_DIR=/opt/collector/test
  LOG_LEVEL=DEBUG
==================================================
``` 
```
$ systemctl status tmp_files_collector.service 
● tmp_files_collector.service - Temp File Collector Service
     Loaded: loaded (/lib/systemd/system/tmp_files_collector.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2025-03-03 00:07:44 IST; 17s ago
   Main PID: 1364710 (python3)
      Tasks: 1 (limit: 18722)
     Memory: 5.9M
        CPU: 31ms
     CGroup: /system.slice/tmp_files_collector.service
             └─1364710 /usr/bin/python3 /usr/local/bin/tmp_files_collector.py --base-dir /opt/collector/test --log-level DEBUG

Mar 03 00:07:44 arun-Inspiron-14-7430-2-in-1 systemd[1]: Started Temp File Collector Service.
```
Once the script exits after one iteration, it can be started again with the systemd restart command `systemctl restart tmp_files_collector.service` if required.

When it's run as a systemd service the logs are written to the below files as specified in the `systemd` service file.
```
StandardOutput=append:/var/log/tmp_files_collector.log
StandardError=append:/var/log/tmp_files_collector.err
```


## To run the script manually
1. To run the script in the background with default arguments,
```
nohup tmp_files_collector.py > output.log 2>&1 &
```
The output is written to `output.log`

2. To run the script in the foreground with default arguments,
```
python3 tmp_files_collector.py
```
The output is written to the console.


