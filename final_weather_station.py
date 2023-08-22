import serial
import requests
from twilio.rest import Client

phone_numbers = ["phno1", "phno2", "phno3"]

ser = serial.Serial('/dev/ttyUSB0', 9600)  # Replace with your serial port

THINGSPEAK_API_KEY = ""  # Replace with your ThingSpeak API Key
THINGSPEAK_UPDATE_URL = f"https://api.thingspeak.com/update?api_key={THINGSPEAK_API_KEY}"

OPENWEATHERMAP_API_KEY = ""  # Replace with your OpenWeatherMap API Key
OPENWEATHERMAP_CITY = "Kumbakonam, IN"  # Replace with the city and country code

# Initialize Twilio client
twilio_account_sid = ""
twilio_auth_token = ""
twilio_client = Client(twilio_account_sid, twilio_auth_token)

# Initialize state for alerts
temperature_alert_sent = False
humidity_alert_sent = False

while True:
    data = ser.readline().decode().strip()  # Read and decode data
    if data.startswith("H:"):
        data = data[2:]  # Remove the "H:" prefix
        humidity, temperature = data.split(",T:")

        # Get live weather data from OpenWeatherMap API
        weather_response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={OPENWEATHERMAP_CITY}&appid={OPENWEATHERMAP_API_KEY}")
        weather_data = weather_response.json()
        current_weather = weather_data["weather"][0]["description"]
        temperature_celsius = weather_data["main"]["temp"] - 273.15  # Convert Kelvin to Celsius

        # Check conditions for alerts
        temperature_alert = "Normal"
        humidity_alert = "Normal"
        
        if float(temperature) > 34:
            if not temperature_alert_sent:
                temperature_alert = "High Temperature Alert"
                # Send SMS notification with weather details
                sms_body = (
                    f"*** High Temperature Alert! ***\n"
                    f"\tTemperature is above 34°C.\n\n"
                    f"\tSensor Data:\n"
                    f"\t\tTemperature: {float(temperature):.2f} °C.\n"  # Corrected format
                    f"\t\tHumidity: {humidity} .\n\n"
                    f"\tNote Current Details:\n"
                    f"\t\tTemperature: {temperature_celsius:.2f} °C.\n"
                    f"\t\tWeather: {current_weather}."
                )
                twilio_client.messages.create(
                    to=phone_numbers,  # Replace with your mobile number
                    from_="",  # Your Twilio phone number
                    body=sms_body
                )
                temperature_alert_sent = True
        
        else:
            temperature_alert_sent = False
            
        if float(humidity) > 55:
            if not humidity_alert_sent:
                humidity_alert = "High Humidity Alert"
                # Send SMS notification with weather details
                sms_body = (
                    f"*** High Humidity Alert! ***\n"
                    f"\tHumidity is above 55.\n\n"
                    f"\tSensor Data:\n"
                    f"\t\tTemperature: {float(temperature):.2f} °C.\n"
                    f"\t\tHumidity: {humidity}.\n\n"  # Corrected format
                    f"\tNote Current Details:\n"
                    f"\t\tTemperature: {temperature_celsius:.2f} °C.\n"
                    f"\t\tWeather: {current_weather}."
                )
                twilio_client.messages.create(
                    to=phone_numbers,  # Replace with your mobile number
                    from_="",  # Your Twilio phone number
                    body=sms_body
                )
                humidity_alert_sent = True
        else:
            humidity_alert_sent = False

        # Send combined data to ThingSpeak
        payload = {
            "field1": humidity,
            "field2": temperature,
            "field3": current_weather,
            "field4": temperature_celsius,
            "field5": temperature_alert,
            "field6": humidity_alert
        }
        response = requests.get(THINGSPEAK_UPDATE_URL, params=payload)
        
        if response.status_code == 200:
            print("Data sent to ThingSpeak")
        else:
            print("Error sending data to ThingSpeak")

        print("Humidity:", humidity, "%")
        print("Temperature:", temperature, "°C")
        print("Current Weather:", current_weather)
        print("Temperature Celsius:", temperature_celsius, "°C")
        print("Temperature Alert:", temperature_alert)
        print("Humidity Alert:", humidity_alert)
