import os
import sys
from datetime import datetime, timedelta
from dateutil import parser
import pytz

# Add the current directory to sys.path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from google_integration import GoogleIntegration

def main():
    try:
        gi = GoogleIntegration()
        print("Buscando eventos...")
        events = gi.obter_eventos_calendario(max_results=50)
        
        # Define tomorrow's date range in local time (assuming user is in -03:00 based on metadata)
        # Actually, let's just look for events on 2025-12-09
        target_date_str = "2025-12-09"
        
        print(f"Filtrando eventos para {target_date_str} com 'PRODITEC' e 'Turma A'...")
        
        found_events = []
        for event in events:
            summary = event.get('summary', '')
            start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date'))
            
            if not start:
                continue
                
            # Check if event is on target date
            # Handle both dateTime (2025-12-09T14:00:00-03:00) and date (2025-12-09)
            event_date_str = start.split('T')[0]
            
            if event_date_str == target_date_str:
                if 'PRODITEC' in summary.upper() and 'TURMA A' in summary.upper():
                    found_events.append(event)

        if not found_events:
            print("Nenhum evento encontrado para amanhã com 'PRODITEC' e 'Turma A'.")
            # Let's print all events for tomorrow to help debug if needed
            print("\nOutros eventos encontrados para amanhã:")
            for event in events:
                start = event.get('start', {}).get('dateTime', event.get('start', {}).get('date'))
                if start and start.split('T')[0] == target_date_str:
                    print(f" - {event.get('summary', 'Sem título')}")
            return

        for event in found_events:
            print(f"\nEvento encontrado: {event.get('summary')}")
            print(f"Horário: {event.get('start', {}).get('dateTime', event.get('start', {}).get('date'))}")
            
            attendees = event.get('attendees', [])
            if attendees:
                print(f"Lista de Convidados ({len(attendees)}):")
                for attendee in attendees:
                    name = attendee.get('displayName', attendee.get('email'))
                    email = attendee.get('email')
                    status = attendee.get('responseStatus')
                    print(f" - {name} ({email}) - Status: {status}")
            else:
                print("Nenhum convidado listado neste evento.")

    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    main()
