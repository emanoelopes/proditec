#!/bin/bash

# Default values
INTERVAL=""
DISABLE=0

# Help message
usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  --every-hours X   Run update every X hours"
    echo "  --disable         Remove the scheduled job"
    echo "  --help            Show this help message"
    exit 1
}

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --every-hours) INTERVAL="$2"; shift ;;
        --disable) DISABLE=1 ;;
        --help) usage ;;
        *) echo "Unknown parameter passed: $1"; usage ;;
    esac
    shift
done

# Define the command to run
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG_FILE="$PROJECT_DIR/data/cron_job.log"
# Use docker-compose to run the pipeline inside the container
CMD="cd $PROJECT_DIR && /usr/bin/docker-compose run --rm app python -m src.core.update_pipeline >> $LOG_FILE 2>&1"
COMMENT="# PRODITEC_AUTO_UPDATE"

# Backup current crontab
crontab -l > mycron.tmp 2>/dev/null

# Remove existing job
grep -v "$COMMENT" mycron.tmp > mycron_clean.tmp
mv mycron_clean.tmp mycron.tmp

if [ "$DISABLE" -eq 1 ]; then
    echo "Removing scheduled job..."
    crontab mycron.tmp
    rm mycron.tmp
    echo "Done."
    exit 0
fi

if [ -z "$INTERVAL" ]; then
    echo "Error: --every-hours argument is required unless disabling."
    rm mycron.tmp
    usage
fi

# Add new job
# e.g. "0 */4 * * * command" for every 4 hours
echo "0 */$INTERVAL * * * $CMD $COMMENT" >> mycron.tmp

# Install new crontab
crontab mycron.tmp
rm mycron.tmp

echo "Scheduled update every $INTERVAL hours."
echo "Command: $CMD"
