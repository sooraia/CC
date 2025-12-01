from .api_client import get_active_rovers, get_last_telemetry, get_missions
import time

def main():
    while True:
        print("\n=== GROUND CONTROL ===")
        print("1. List Active Rovers")
        print("2. Show Last Telemetry")
        print("3. List Missions")
        print("4. Exit")
        
        choice = input("Select option: ").strip()
        
        try:
            if choice == '1':
                rovers = get_active_rovers()
                print_json("ACTIVE ROVERS", rovers)
                
            elif choice == '2':
                telemetry = get_last_telemetry()
                print_json("LAST TELEMETRY", telemetry)
                
            elif choice == '3':
                missions = get_missions()
                print_json("MISSIONS", missions)
                
            elif choice == '4':
                print("Exiting Ground Control...")
                break
            else:
                print("Invalid option")
                
        except Exception as e:
            print(f"Error: {e}")

def print_json(title, data):
    print(f"\n=== {title} ===")
    if data:
        for key, value in data.items():
            print(f"{key}: {value}")
    else:
        print("No data available")


if __name__ == "__main__":
    main()