import pandas as pd
import click
import logging
import sys
import os
from datetime import datetime
from bot import WhatsAppBot

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

@click.command()
@click.option('--csv', required=True, type=click.Path(exists=True), help='Path to the CSV file containing contacts.')
@click.option('--message', required=True, help='Message to send. Use {name} for personalization if the CSV has a "name" column.')
@click.option('--phone-col', default='phone', help='Column name for phone numbers in the CSV.')
@click.option('--name-col', default='name', help='Column name for names (optional) for personalization.')
def main(csv, message, phone_col, name_col):
    """
    WhatsApp Mass Messenger Bot.
    
    Reads contacts from a CSV file and sends a message to each number.
    requires a CSV with at least a phone number column.
    """
    
    # Check if CSV exists (redundant with click.Path exists=True but good practice)
    if not os.path.exists(csv):
        click.echo(f"Error: CSV file '{csv}' not found.")
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
    
    try:
        bot.start()
        
        click.echo(f"Starting to process {len(df)} contacts...")
        
        delivered_contacts = []
        indices_to_drop = []

        for index, row in df.iterrows():
            phone = str(row[phone_col])
            
            # Simple cleaning of phone numbers (remove spaces, etc if needed)
            # This expects numbers to be in international format or close to it.
            # You might want to add more robust cleaning here.
            
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

        # Generate Report
        if delivered_contacts:
            report_filename = f"delivered_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            report_df = pd.DataFrame(delivered_contacts)
            report_df.to_csv(report_filename, index=False)
            click.echo(f"Report generated: {report_filename}")

            # Update contacts CSV
            df_remaining = df.drop(indices_to_drop)
            df_remaining.to_csv(csv, index=False)
            click.echo(f"Updated contacts file: {csv} (Removed {len(indices_to_drop)} sent contacts)")
        else:
            click.echo("No messages were sent, so no report or CSV update needed.")
        
    except KeyboardInterrupt:
        click.echo("\nInterrupted by user.")
    except Exception as e:
        click.echo(f"An error occurred: {e}")
    finally:
        bot.stop()

if __name__ == '__main__':
    main()
