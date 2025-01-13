from datetime import datetime
import pytz

def get_current_time_ist():
    """
    Get the current date and time in Indian Standard Time (IST).

    Returns:
        str: Current date and time formatted as 'YYYY-MM-DD HH:MM:SS'.
    """
    # Define the timezone for India
    ist = pytz.timezone('Asia/Kolkata')
    
    # Get the current time in IST
    datetime_ist = datetime.now(ist)
    
    # Return the formatted date and time
    return datetime_ist.strftime("%d-%m-%Y %H:%M:%S")