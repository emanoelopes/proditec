import pandas as pd
import click
import logging
import time
import sys
import os
from datetime import datetime
from datetime import datetime
from bot import WhatsAppBot
import json
import random
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

@click.command()
@click.option('--csv', required=True, type=click.Path(exists=True), help='Path to the CSV file containing contacts.')
@click.option('--message', required=False, help='Message to send. Use {name} for personalization if the CSV has a "name" column.')
@click.option('--message-file', required=False, type=click.Path(exists=True), help='Path to a text file containing the message.')
@click.option('--messages-json', required=False, type=click.Path(exists=True), help='Path to a JSON file containing a list of messages.')
@click.option('--batch-size', default=50, help='Number of messages to send before pausing (to avoid bans).')
@click.option('--batch-pause', default=60, help='Pause time in seconds between batches.')
@click.option('--phone-col', default='phone', help='Column name for phone numbers in the CSV.')
@click.option('--name-col', default='name', help='Column name for names (optional) for personalization.')
def main(csv, message, message_file, messages_json, batch_size, batch_pause, phone_col, name_col):
    """
    WhatsApp Mass Messenger Bot.
    
    Reads contacts from a CSV file and sends a message to each number.
    requires a CSV with at least a phone number column.
    """
    
    # Check if CSV exists (redundant with click.Path exists=True but good practice)
    if not os.path.exists(csv):
        click.echo(f"Error: CSV file '{csv}' not found.")
        sys.exit(1)

    if messages_json:
        try:
            with open(messages_json, 'r', encoding='utf-8') as f:
                messages_list = json.load(f)
                if not isinstance(messages_list, list) or len(messages_list) == 0:
                     click.echo(f"Error: JSON file must contain a non-empty list of strings.")
                     sys.exit(1)
        except Exception as e:
            click.echo(f"Error reading messages JSON: {e}")
            sys.exit(1)
    else:
        messages_list = None 

    if message_file:
        try:
            with open(message_file, 'r', encoding='utf-8') as f:
                message = f.read()
        except Exception as e:
            click.echo(f"Error reading message file: {e}")
            sys.exit(1)

    # Validate message source
    if not message and not message_file and not messages_list:
        click.echo("Error: You must provide --message, --message-file, or --messages-json.")
        sys.exit(1)

    try:
        df = pd.read_csv(csv)
    except Exception as e:
        click.echo(f"Error reading CSV: {e}")
        sys.exit(1)

    # Validate columns
    if phone_col not in df.columns:
        click.echo(f"Error: Column '{phone_col}' not found in CSV. Available columns: {list(df.columns)}")
        sys.exit(1)

    bot = WhatsAppBot()
    
    # --- RESUME LOGIC ---
    # Find all delivered_report_*.csv files
    sent_phones = set()
    import glob
    report_files = glob.glob("delivered_report_*.csv")
    if report_files:
        click.echo(f"Found {len(report_files)} previous report(s). Checking for already sent messages...")
        for rf in report_files:
            try:
                # Read only the phone column to save memory if files are huge
                # Assuming 'phone' column exists as per line 99/114 logic
                sent_df = pd.read_csv(rf, dtype=str) 
                if 'phone' in sent_df.columns:
                    sent_phones.update(sent_df['phone'].tolist())
            except Exception as e:
                click.echo(f"Warning: Could not read report {rf}: {e}")
        
        click.echo(f"Total unique contacts previously messaged: {len(sent_phones)}")
    
    # Filter the main dataframe
    if not sent_phones:
        df_to_process = df
    else:
        # Ensure phone column is string for comparison
        df[phone_col] = df[phone_col].astype(str)
        
        # Filter
        initial_count = len(df)
        
        # Helper to clean phone for comparison
        def clean_phone(p):
            return re.sub(r'\D', '', str(p))
            
        df['clean_phone'] = df[phone_col].apply(clean_phone)
        
        df_to_process = df[~df['clean_phone'].isin(sent_phones)]
        # cleanup temp column
        df.drop(columns=['clean_phone'], inplace=True)
        
        skipped_count = initial_count - len(df_to_process)
        
        if skipped_count > 0:
            click.echo(f"Skipping {skipped_count} contacts that were already found in previous reports.")
            # Permanently remove them from the source file as requested
            df_to_process.to_csv(csv, index=False)
            click.echo(f"Updated {csv} to remove these contacts permanently.")
        else:
            click.echo("No contacts skipped (none matched previous reports).")
            
    if len(df_to_process) == 0:
        click.echo("All contacts in the CSV have already been messaged. Exiting.")
        return # Exit gracefully
        
    df = df_to_process # Work with the filtered list
    # --- END RESUME LOGIC ---

    try:
        bot.start()
        
        click.echo(f"Starting to process {len(df)} contacts...")
        
        delivered_contacts = []
        indices_to_drop = []
        
        count_processed = 0

        for index, row in df.iterrows():
            # Batch Pause Logic
            if count_processed > 0 and count_processed % batch_size == 0:
                click.echo(f"Batch limit of {batch_size} reached. Pausing for {batch_pause} seconds...")
                time.sleep(batch_pause)
                click.echo("Resuming...")

            count_processed += 1

            phone = str(row[phone_col])
            
            # Robust phone cleaning and formatting
            # 1. Remove everything that is not a digit
            phone = re.sub(r'\D', '', phone)
            
            # 2. Brasil Phone Number Correction Logic
            # Case A: 8 digits (No DDD, no country code) -> Too risky to guess DDD, assume invalid or log warning.
            # Case B: 10 digits (DDD + 8 digits) -> Add country code + Add 9
            # Case C: 11 digits (DDD + 9 digits) -> Add country code
            # Case D: 12 digits (55 + DDD + 8 digits) -> Add 9
            # Case E: 13 digits (55 + DDD + 9 digits) -> OK
            
            # Logic implementation:
            if len(phone) == 10:
                # Assuming DDD + 8 digits. Add '55' and the '9' after DDD.
                # Format: PP NNNN NNNN -> 55 PP 9 NNNN NNNN
                ddd = phone[:2]
                number = phone[2:]
                phone = f"55{ddd}9{number}"
                logging.info(f"Auto-corrected phone (added 55 and 9): {phone}")
                
            elif len(phone) == 11:
                # Assuming DDD + 9 digits OR 55 + DDD + 8 digits? 
                # Usually if it starts with 55 and has 11 digits, it is 55 + DDD + 8 digits (old format without 9)
                # But it could be just DDD + 9 digits (new format without country code)
                
                # Check if starts with 55 (Brazil DDI)
                if phone.startswith('55'):
                     # Likely 55 + DDD + 8 digits (e.g. 55 11 9999 8888 -> 11 digits)
                     # We need to add the 9.
                     # Format: 55 PP NNNN NNNN -> 55 PP 9 NNNN NNNN
                     ddd = phone[2:4]
                     number = phone[4:]
                     phone = f"55{ddd}9{number}"
                     logging.info(f"Auto-corrected phone (added 9 to 55 number): {phone}")
                else:
                    # Likely DDD + 9 digits (e.g. 11 99999 8888). Add 55.
                     phone = f"55{phone}"
                     logging.info(f"Auto-corrected phone (added 55): {phone}")

            elif len(phone) == 12:
                # Likely 55 + DDD + 9 digits is 13 digits.
                # 55 + DDD + 8 digits is 12 digits? No, 2+2+8=12. 
                # If 12 digits, it is likely 55 + DDD + 8 digits. (e.g. 55 11 8888 7777)
                if phone.startswith('55'):
                    # Insert 9 after DDD
                    ddd = phone[2:4]
                    number = phone[4:]
                    phone = f"55{ddd}9{number}"
                    logging.info(f"Auto-corrected phone (added 9 to 12-digit number): {phone}")
            
            elif len(phone) == 8 or len(phone) == 9:
                 logging.warning(f"Phone number {phone} is too short. Skipping auto-correction, might fail.")
            
            # Case where it is already 13 digits (55 + DDD + 9 + 8 digits) -> Do nothing

            
            # Choose message
            if messages_list:
                msg_to_send = random.choice(messages_list)
            else:
                msg_to_send = message
            
            # Personalization
            if name_col in df.columns and pd.notna(row[name_col]):
                msg_to_send = msg_to_send.format(name=row[name_col])
            
            logging.info(f"[{index+1}/{len(df)}] Sending to {phone}...")
            
            success = bot.send_message(phone, msg_to_send)
            
            if success:
                logging.info("Status: Sent")
                delivered_contacts.append({
                    'name': row[name_col] if name_col in df.columns and pd.notna(row[name_col]) else 'N/A',
                    'phone': phone,
                    'date': datetime.now().strftime("%Y-%m-%d"),
                    'time': datetime.now().strftime("%H:%M:%S")
                })
                indices_to_drop.append(index)
            else:
                logging.error("Status: Failed")
            
            # The bot class already handles delays between actions
            
        click.echo("All messages processed.")

        if not delivered_contacts:
            click.echo("No messages were sent in this session.")
        
    except KeyboardInterrupt:
        click.echo("\nInterrupted by user.")
    except Exception as e:
        click.echo(f"An error occurred: {e}")
    finally:
        # Save progress if there are delivered contacts
        if 'delivered_contacts' in locals() and delivered_contacts:
            click.echo("Saving delivery report and updating contacts file...")
            report_filename = f"delivered_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            report_df = pd.DataFrame(delivered_contacts)
            report_df.to_csv(report_filename, index=False)
            click.echo(f"Report generated: {report_filename}")

            # Update contacts CSV
            df_remaining = df.drop(indices_to_drop)
            df_remaining.to_csv(csv, index=False)
            click.echo(f"Updated contacts file: {csv} (Removed {len(indices_to_drop)} sent contacts)")
        
        bot.stop()

if __name__ == '__main__':
    main()
