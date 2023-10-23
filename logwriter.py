#!/usr/bin/env python3
import logging
import time
import os

class write_some_log():
    def __init__(self,path,which_running) -> None:
        self.max_log_age = 3 # Day
        self.log_path = path
        self.whois_running = which_running
        self._check_old_logs()

    def Log_write(self,text,stat='info'):
        """available stat : \n info,warning,error,critical"""
        log_filename = self.log_path
        logging.basicConfig(filename=log_filename, format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
        text = text.replace('\n',' ')
        text = f'{text} [{self.whois_running}]'
        # Map the level string to a logging level constant
        level_map = {'debug': logging.DEBUG,
                        'info': logging.INFO,
                        'warning': logging.WARNING,
                        'error': logging.ERROR,
                        'critical': logging.CRITICAL}
        log_level = level_map.get(stat.lower(), logging.INFO)
        logging.log(log_level,text)

    def _check_old_logs(self):
        max_age_seconds = self.max_log_age * 24 * 60 * 60
        for file_path in os.listdir('./logs'):
            file_path = os.path.join('./logs',file_path)
            file_stat = os.stat(file_path)
            current_time = time.time()
            # Calculate the age of the file in seconds
            file_age_seconds = current_time - file_stat.st_mtime
            # Compare the age with the maximum allowed age
            if file_age_seconds > max_age_seconds:
                # File is older than 3 days, so delete it
                os.remove(file_path)
                print(f"{file_path} has been deleted as it's more than 3 days old.")

if __name__ == '__main__':
    logger = write_some_log('./logs/test.log','logwriter.py')
    logger.Log_write('Running .. ')