import re
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

def process_file(file_name):
    """
    Reads the specified text file line by line and extracts datetime and weight data.

    :param file_name: Name of the text file to read
    :return: Dictionary with datetime as keys and weights as values
    """
    weight_data = {}

    try:
        with open(file_name, 'r') as file:
            current_date = datetime.min
            for line_number, line_text in enumerate(file, start=1):
                line_text = line_text.replace('\n', '')

                # Check if the line contains a date
                result, value = convert_to_datetime(line_text)
                if result:
                    current_date = value

                # Check if the line contains a weight entry
                result, value = parse_weight_entry(line_text)
                if result:
                    time_str, weight = value
                    hours, minutes = map(int, time_str.split(":"))
                    current_date = current_date.replace(hour=hours, minute=minutes)
                    weight_data[current_date] = weight

    except FileNotFoundError:
        print(f"Error: The file '{file_name}' was not found.")
    except IOError:
        print(f"Error: Could not read the file '{file_name}'.")

    return weight_data

def convert_to_datetime(date_text):
    """
    Converts a string to a datetime object if possible.

    :param date_text: The date string to convert
    :return: (True, datetime object) if conversion is successful, or (False, None) if unsuccessful
    """
    try:
        date_obj = datetime.strptime(date_text, "%a, %b %d, %Y")
        return True, date_obj
    except ValueError:
        return False, None

def parse_weight_entry(text):
    """
    Parses the input text to find the time and weight if the text includes "Weight".

    :param text: Input text to parse
    :return: (True, (time, weight)) if "Weight" is found, else (False, None)
    """
    if "Weight" in text:
        time_match = re.search(r'\b\d{2}:\d{2}\b', text)
        weight_match = re.search(r'Weight\s([\d.]+)kg', text)
        
        if time_match and weight_match:
            time = time_match.group()
            weight = float(weight_match.group(1))
            return True, (time, weight)
    
    return False, None


def plot_weight_data(weight_data):
    """
    Plots the weight data with datetime on the x-axis and weight on the y-axis,
    including a linear regression line and displays the slope (in kg/day) and intercept.
    """
    # Extract timestamps and weights from weight_data
    x = np.array([dt.timestamp() for dt in weight_data.keys()]).reshape(-1, 1)
    y = np.array(list(weight_data.values()))

    # Create and fit the linear regression model
    model = LinearRegression()
    model.fit(x, y)

    # Calculate the slope and intercept
    slope_per_second = model.coef_[0]  # kg per second
    slope_per_day = slope_per_second * 86400  # Convert to kg per day
    intercept = model.intercept_

    # Generate data for the regression line
    x_range = np.linspace(x.min(), x.max(), 100).reshape(-1, 1)
    y_range = model.predict(x_range)

    # Plotting
    plt.figure(figsize=(10, 6))
    plt.scatter([datetime.fromtimestamp(ts[0]) for ts in x], y, label="Data points", color="blue")
    plt.plot([datetime.fromtimestamp(ts[0]) for ts in x_range], y_range, label="Regression line", color="red")

    # Display slope (kg/day) and intercept on the plot
    plt.text(0.05, 0.95, f"Slope: {slope_per_day:.6f} kg/day",
             transform=plt.gca().transAxes, fontsize=10, verticalalignment='top', color="darkgreen")

    # Formatting the plot
    plt.xlabel("Datetime")
    plt.ylabel("Weight (kg)")
    plt.title("Weight Data with Linear Regression Line")
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("weight_data_plot.png")


def main():
    # Specify the name of the file to process
    file_name = "log/[PiyoLog]Nov.txt"
    # Process the file and get weight data
    weight_data = process_file(file_name)

    #init data
    # intercept_date = datetime(2024, 10, 27, 17, 1)
    # weight_data[intercept_date] = 3.00

    # Plot the weight data
    plot_weight_data(weight_data)

# Call main() only if the script is executed directly
if __name__ == "__main__":
    main()
