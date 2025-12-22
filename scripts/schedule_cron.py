
import os
import sys
import argparse
from crontab import CronTab

def schedule_cron(interval_hours=None, at_time=None):
    # Get current user's cron
    cron = CronTab(user=True)
    
    # Define the command
    python_exec = sys.executable
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'core', 'update_pipeline.py'))
    
    # Ensure command runs with the project root in PYTHONPATH if needed, or rely on script setup
    # We will use python -m src.core.update_pipeline approach or direct script execution.
    # Given update_pipeline.py has path setup, direct execution is fine if shebang or python arg.
    # Let's use the venv python to execute the script
    
    command = f'cd {os.path.dirname(os.path.dirname(os.path.dirname(script_path)))} && {python_exec} {script_path}'
    comment = "Proditec_Auto_Update"

    # Remove existing job
    cron.remove_all(comment=comment)
    
    if interval_hours:
        job = cron.new(command=command, comment=comment)
        job.hour.every(interval_hours)
        print(f"Scheduled update every {interval_hours} hours.")
        cron.write()
    elif at_time:
        # Expected format "HH:MM"
        hour, minute = at_time.split(':')
        job = cron.new(command=command, comment=comment)
        job.hour.on(int(hour))
        job.minute.on(int(minute))
        print(f"Scheduled update daily at {at_time}.")
        cron.write()
    else:
        print("No schedule parameters provided. Existing jobs removed (if any).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Schedule Grade Updates via Cron")
    parser.add_argument('--every-hours', type=int, help='Run every X hours')
    parser.add_argument('--at', type=str, help='Run daily at HH:MM')
    
    args = parser.parse_args()
    
    schedule_cron(interval_hours=args.every_hours, at_time=args.at)
