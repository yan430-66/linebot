import requests
import yaml

class CurrencyConverter:
    def __init__(self, 
                 api_key: str,
                 base_url: str,):
        self.api_key = api_key
        self.base_url = base_url 

    def get_exchange_rate(self, from_currency: str, to_currency: str):
        # Build API URL
        url = f"{self.base_url}/latest/{from_currency.upper()}"
        
        # Make the API request
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            try:
                # Extract the exchange rate
                rate = data["conversion_rates"][to_currency.upper()]
                return rate
            except KeyError:
                raise Exception(f"KeyError: Currency {to_currency} not found in response.")
        else:
            raise Exception(f"Fail to get exchange rates: {response.status_code}, {response.text}")

    def convert_currency(self,
                         amount: float | int, 
                         from_currency: str,
                         a: str, 
                         to_currency: str,
                         ):
        try:
            # Get the exchange rate and calculate the converted amount
            rate = self.get_exchange_rate(from_currency, to_currency)
            converted_amount = round(amount * rate, 2)
            return "msg", f"{amount} {from_currency.upper()} is equivalent to {converted_amount} {to_currency.upper()}."
        except Exception as e:
            return "err", f"Error: {e}"

# Run the script with user input
if __name__ == "__main__":
    # Initialize the converter
    converter = CurrencyConverter(api_key="api key", base_url="api url")
    
    # Get user input in a single line
    user_input = input("Enter the amount and currency conversion (e.g., 100 USD to EUR): ").strip()

    try:
        # Split the input into components
        amount_str, from_currency, _, to_currency = user_input.split()
        amount = float(amount_str)  # Convert the amount part to a float

        # Perform the conversion and display the result
        result = converter.convert_currency(from_currency=from_currency, to_currency=to_currency, amount=amount)
        print(result)
    except ValueError:
        print("Invalid input. Please enter the amount followed by 'from_currency to_currency'.")
    except Exception as e:
        print(f"Error: {e}")
