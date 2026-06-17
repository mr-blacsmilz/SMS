import datetime
import time
import serial  # Handles direct COM port communication from the Cat6 cables

# 1. HARDWARE PORT CONFIGURATION
# In the caterer's office, Lane 1 might be plugged into COM3 and Lane 2 into COM4
SCANNER_LANES = {
    "Lane_1": {"port": "COM3", "baudrate": 9600},
    "Lane_2": {"port": "COM4", "baudrate": 9600}
}

# 2. DEFINE SYSTEM MEAL WINDOWS (With Buffer Error Margins)
MEAL_WINDOWS = {
    "LUNCH": {
        "start": datetime.time(12, 30),
        "end": datetime.time(14, 00),
        "extended_end": datetime.time(14, 30)  # Handles kitchen delays
    },
    "SUPPER": {
        "start": datetime.time(18, 00),
        "end": datetime.time(19, 30),
        "extended_end": datetime.time(20, 00)
    }
}

def determine_active_meal_period(current_time, delay_mode_active=False):
    """Checks the server clock to see if a scan falls into a legal feeding window."""
    t = current_time.time()
    
    for meal, windows in MEAL_WINDOWS.items():
        end_limit = windows["extended_end"] if delay_mode_active else windows["end"]
        if windows["start"] <= t <= end_limit:
            return meal
    return None

def process_raw_scan(student_id, lane_name, database_df, delay_toggle=False):
    """Processes the string payload typed out by the Q300 scanner module."""
    student_id = student_id.strip()  # Clean up trailing spaces or newlines
    now = datetime.datetime.now()
    current_date_str = now.strftime("%A")  # e.g., 'Monday'
    
    # Check if student exists in the 1,700-student database
    if student_id not in database_df["Student ID"].values:
        return {"status": "REJECTED", "msg": "🚫 Invalid Card: Student ID not found."}
        
    # Check if a valid feeding window is active
    active_meal = determine_active_meal_period(now, delay_toggle)
    if not active_meal:
        return {"status": "REJECTED", "msg": "⏳ Denied: Access closed outside meal times."}
        
    # Generate the column string matching the database format (e.g., 'Monday_Lunch')
    db_column = f"{current_date_str}_{active_meal.capitalize()}"
    
    # Fetch row index of the student
    student_idx = database_df[database_df["Student ID"] == student_id].index[0]
    current_status = database_df.at[student_idx, db_column]
    
    # DOUBLE-DIPPING PROTECTION: Check if they already ate
    if current_status == "Scanned":
        return {"status": "REJECTED", "msg": "🚨 Fraud Alert: Card already scanned for this meal!"}
        
    # SUCCESS: Update database ledger record
    database_df.at[student_idx, db_column] = "Scanned"
    student_name = database_df.at[student_idx, "Name"]
    
    return {
        "status": "APPROVED", 
        "msg": f"✅ Approved: {student_name} ({database_df.at[student_idx, 'Class/Stream']})"
    }

def start_hardware_listener(lane_id, db_reference):
    """Background loop that monitors physical wire streams from the Q300 hardware."""
    config = SCANNER_LANES[lane_id]
    print(f"📡 Initializing {lane_id} background listener on {config['port']}...")
    
    try:
        # Open serial link down the Cat6 wire line
        ser = serial.Serial(port=config["port"], baudrate=config["baudrate"], timeout=1)
        time.sleep(2) # Give hardware time to settle
        print(f"🚀 {lane_id} link online. Awaiting card scans...")
        
        while True:
            if ser.in_waiting > 0:
                # Read incoming binary data string from the Q300 module
                raw_data = ser.readline().decode('utf-8')
                
                # Execute database evaluation
                result = process_raw_scan(raw_data, lane_id, db_reference)
                
                # Command hardware response cues based on logic outcome
                if result["status"] == "APPROVED":
                    print(f"[{lane_id}] {result['msg']}")
                    # (Optional Hardware Trigger): Command physical buzzer to emit a single short beep
                    # ser.write(b'\x07') 
                else:
                    print(f"[{lane_id}] {result['msg']}")
                    # (Optional Hardware Trigger): Command physical buzzer to emit double failure tones
                    # ser.write(b'\x07\x07')
                    
            time.sleep(0.1) # Prevents CPU overheating
            
    except serial.SerialException:
        print(f"❌ Connection Error: Hardware disconnected on {config['port']}. Check Cat6 wiring splitters.")
