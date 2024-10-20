import sys
import json
import asyncio
import websockets
import matplotlib
import pandas as pd
import matplotlib.pyplot as plt

from libs.logger.logger import get_colorful_logger

matplotlib.use("TkAgg")
logger = get_colorful_logger()

# Sample JSON data (replace this with your actual JSON data)
json_data = """
{
    "Meta Data": {
        "1. Information": "Daily Prices (open, high, low, close) and Volumes",
        "2. Symbol": "IBM",
        "3. Last Refreshed": "2024-10-02",
        "4. Output Size": "Compact",
        "5. Time Zone": "US/Eastern"
    },
    "Time Series (Daily)": {
        "2024-10-02": {
            "1. open": "218.3100",
            "2. high": "220.2000",
            "3. low": "215.7980",
            "4. close": "219.7300",
            "5. volume": "3343399"
        },
        "2024-10-01": {
            "1. open": "220.6300",
            "2. high": "221.1000",
            "3. low": "215.9000",
            "4. close": "219.3500",
            "5. volume": "3548374"
        },
        "2024-09-30": {
            "1. open": "220.6500",
            "2. high": "221.3200",
            "3. low": "219.0200",
            "4. close": "221.0800",
            "5. volume": "3544264"
        },
        "2024-09-27": {
            "1. open": "223.0000",
            "2. high": "224.1500",
            "3. low": "220.7700",
            "4. close": "220.8400",
            "5. volume": "3830335"
        },
        "2024-09-26": {
            "1. open": "222.1100",
            "2. high": "224.0000",
            "3. low": "221.3550",
            "4. close": "223.4300",
            "5. volume": "2673210"
        },
        "2024-09-25": {
            "1. open": "221.1700",
            "2. high": "221.8500",
            "3. low": "220.1600",
            "4. close": "221.2300",
            "5. volume": "2537751"
        },
        "2024-09-24": {
            "1. open": "219.7800",
            "2. high": "221.1900",
            "3. low": "218.1600",
            "4. close": "220.9700",
            "5. volume": "3184114"
        },
        "2024-09-23": {
            "1. open": "218.0000",
            "2. high": "220.6200",
            "3. low": "217.2700",
            "4. close": "220.5000",
            "5. volume": "4074755"
        },
        "2024-09-20": {
            "1. open": "214.3300",
            "2. high": "217.8500",
            "3. low": "213.7400",
            "4. close": "217.7000",
            "5. volume": "9958980"
        },
        "2024-09-19": {
            "1. open": "218.0100",
            "2. high": "218.4800",
            "3. low": "210.3700",
            "4. close": "213.8900",
            "5. volume": "5279559"
        },
        "2024-09-18": {
            "1. open": "214.1300",
            "2. high": "216.8600",
            "3. low": "213.5900",
            "4. close": "214.9400",
            "5. volume": "3482764"
        },
        "2024-09-17": {
            "1. open": "217.2500",
            "2. high": "218.8400",
            "3. low": "213.0000",
            "4. close": "214.1300",
            "5. volume": "5635210"
        },
        "2024-09-16": {
            "1. open": "215.8800",
            "2. high": "217.9000",
            "3. low": "215.5200",
            "4. close": "217.1600",
            "5. volume": "4176257"
        },
        "2024-09-13": {
            "1. open": "212.4800",
            "2. high": "216.0900",
            "3. low": "212.1300",
            "4. close": "214.7900",
            "5. volume": "4572344"
        },
        "2024-09-12": {
            "1. open": "210.0000",
            "2. high": "212.6500",
            "3. low": "208.2650",
            "4. close": "211.6100",
            "5. volume": "4616446"
        },
        "2024-09-11": {
            "1. open": "207.7600",
            "2. high": "210.1200",
            "3. low": "203.0400",
            "4. close": "209.8900",
            "5. volume": "5554309"
        },
        "2024-09-10": {
            "1. open": "204.2000",
            "2. high": "205.8300",
            "3. low": "202.8700",
            "4. close": "205.3200",
            "5. volume": "3070644"
        },
        "2024-09-09": {
            "1. open": "201.9400",
            "2. high": "205.0500",
            "3. low": "201.4300",
            "4. close": "203.5300",
            "5. volume": "3705004"
        },
        "2024-09-06": {
            "1. open": "202.3800",
            "2. high": "204.1000",
            "3. low": "199.3350",
            "4. close": "200.7400",
            "5. volume": "3304491"
        },
        "2024-09-05": {
            "1. open": "204.0800",
            "2. high": "205.9500",
            "3. low": "200.9600",
            "4. close": "202.5900",
            "5. volume": "3229345"
        },
        "2024-09-04": {
            "1. open": "200.7600",
            "2. high": "204.3600",
            "3. low": "200.5000",
            "4. close": "204.1100",
            "5. volume": "3111332"
        },
        "2024-09-03": {
            "1. open": "201.9100",
            "2. high": "204.7200",
            "3. low": "200.2100",
            "4. close": "201.2800",
            "5. volume": "3874697"
        },
        "2024-08-30": {
            "1. open": "199.1100",
            "2. high": "202.1700",
            "3. low": "198.7300",
            "4. close": "202.1300",
            "5. volume": "4750999"
        },
        "2024-08-29": {
            "1. open": "199.3000",
            "2. high": "201.1200",
            "3. low": "198.2700",
            "4. close": "198.9000",
            "5. volume": "2989594"
        },
        "2024-08-28": {
            "1. open": "199.0000",
            "2. high": "200.0000",
            "3. low": "197.4900",
            "4. close": "198.4600",
            "5. volume": "2645244"
        },
        "2024-08-27": {
            "1. open": "197.4400",
            "2. high": "199.4000",
            "3. low": "196.9700",
            "4. close": "198.7300",
            "5. volume": "2617229"
        },
        "2024-08-26": {
            "1. open": "196.0000",
            "2. high": "198.3450",
            "3. low": "195.9000",
            "4. close": "197.9800",
            "5. volume": "2567217"
        },
        "2024-08-23": {
            "1. open": "196.7900",
            "2. high": "197.3800",
            "3. low": "194.3900",
            "4. close": "196.1000",
            "5. volume": "2321961"
        },
        "2024-08-22": {
            "1. open": "197.2500",
            "2. high": "197.9200",
            "3. low": "195.5700",
            "4. close": "195.9600",
            "5. volume": "1969496"
        },
        "2024-08-21": {
            "1. open": "195.9700",
            "2. high": "197.3300",
            "3. low": "194.1150",
            "4. close": "197.2100",
            "5. volume": "2579343"
        },
        "2024-08-20": {
            "1. open": "194.5900",
            "2. high": "196.2100",
            "3. low": "193.7500",
            "4. close": "196.0300",
            "5. volume": "1790371"
        },
        "2024-08-19": {
            "1. open": "193.8400",
            "2. high": "195.5250",
            "3. low": "193.7150",
            "4. close": "194.7300",
            "5. volume": "2361378"
        },
        "2024-08-16": {
            "1. open": "193.5800",
            "2. high": "194.3500",
            "3. low": "192.8600",
            "4. close": "193.7800",
            "5. volume": "2494472"
        },
        "2024-08-15": {
            "1. open": "193.5100",
            "2. high": "194.2500",
            "3. low": "193.2800",
            "4. close": "193.9500",
            "5. volume": "2471985"
        },
        "2024-08-14": {
            "1. open": "191.1500",
            "2. high": "193.0900",
            "3. low": "190.7300",
            "4. close": "192.3200",
            "5. volume": "1895114"
        },
        "2024-08-13": {
            "1. open": "190.2900",
            "2. high": "191.3100",
            "3. low": "189.2100",
            "4. close": "190.9900",
            "5. volume": "2178862"
        },
        "2024-08-12": {
            "1. open": "191.2500",
            "2. high": "191.5761",
            "3. low": "189.0001",
            "4. close": "189.4800",
            "5. volume": "2290421"
        },
        "2024-08-09": {
            "1. open": "191.1800",
            "2. high": "192.6300",
            "3. low": "189.0400",
            "4. close": "191.4500",
            "5. volume": "2773706"
        },
        "2024-08-08": {
            "1. open": "187.5000",
            "2. high": "192.8800",
            "3. low": "187.0000",
            "4. close": "192.6100",
            "5. volume": "3712698"
        },
        "2024-08-07": {
            "1. open": "188.0800",
            "2. high": "189.8700",
            "3. low": "186.7000",
            "4. close": "186.8000",
            "5. volume": "3801942"
        },
        "2024-08-06": {
            "1. open": "184.7000",
            "2. high": "188.9000",
            "3. low": "183.6400",
            "4. close": "186.8000",
            "5. volume": "3632517"
        },
        "2024-08-05": {
            "1. open": "184.5500",
            "2. high": "185.2550",
            "3. low": "181.8100",
            "4. close": "183.3100",
            "5. volume": "4975002"
        },
        "2024-08-02": {
            "1. open": "188.7800",
            "2. high": "189.2600",
            "3. low": "185.7000",
            "4. close": "189.1200",
            "5. volume": "4548824"
        },
        "2024-08-01": {
            "1. open": "192.8100",
            "2. high": "193.6350",
            "3. low": "188.2900",
            "4. close": "189.6600",
            "5. volume": "4085354"
        },
        "2024-07-31": {
            "1. open": "191.0000",
            "2. high": "194.5499",
            "3. low": "189.9900",
            "4. close": "192.1400",
            "5. volume": "5558405"
        },
        "2024-07-30": {
            "1. open": "191.4800",
            "2. high": "192.7700",
            "3. low": "189.0900",
            "4. close": "191.0400",
            "5. volume": "3064978"
        },
        "2024-07-29": {
            "1. open": "193.1800",
            "2. high": "193.2900",
            "3. low": "189.1800",
            "4. close": "191.5000",
            "5. volume": "3336806"
        },
        "2024-07-26": {
            "1. open": "190.5100",
            "2. high": "193.5700",
            "3. low": "189.6220",
            "4. close": "191.7500",
            "5. volume": "4294875"
        },
        "2024-07-25": {
            "1. open": "186.8000",
            "2. high": "196.2600",
            "3. low": "185.3000",
            "4. close": "191.9800",
            "5. volume": "9532802"
        },
        "2024-07-24": {
            "1. open": "184.1400",
            "2. high": "185.0714",
            "3. low": "183.1450",
            "4. close": "184.0200",
            "5. volume": "6962071"
        },
        "2024-07-23": {
            "1. open": "184.3600",
            "2. high": "185.3800",
            "3. low": "183.0100",
            "4. close": "184.1000",
            "5. volume": "2180225"
        },
        "2024-07-22": {
            "1. open": "183.4000",
            "2. high": "184.9700",
            "3. low": "182.8600",
            "4. close": "184.1500",
            "5. volume": "2488525"
        },
        "2024-07-19": {
            "1. open": "186.3300",
            "2. high": "187.0000",
            "3. low": "181.9500",
            "4. close": "183.2500",
            "5. volume": "3816039"
        },
        "2024-07-18": {
            "1. open": "186.6400",
            "2. high": "189.4700",
            "3. low": "185.1000",
            "4. close": "185.2200",
            "5. volume": "3487808"
        },
        "2024-07-17": {
            "1. open": "185.4400",
            "2. high": "187.9400",
            "3. low": "185.0700",
            "4. close": "187.4500",
            "5. volume": "4225302"
        },
        "2024-07-16": {
            "1. open": "184.6700",
            "2. high": "186.6000",
            "3. low": "184.5200",
            "4. close": "185.8100",
            "5. volume": "3374526"
        },
        "2024-07-15": {
            "1. open": "183.3800",
            "2. high": "184.9000",
            "3. low": "182.6000",
            "4. close": "182.8800",
            "5. volume": "2925794"
        },
        "2024-07-12": {
            "1. open": "178.5600",
            "2. high": "184.1600",
            "3. low": "178.5000",
            "4. close": "182.8300",
            "5. volume": "4785565"
        },
        "2024-07-11": {
            "1. open": "177.6500",
            "2. high": "179.4400",
            "3. low": "176.6200",
            "4. close": "178.3100",
            "5. volume": "2807145"
        },
        "2024-07-10": {
            "1. open": "176.6000",
            "2. high": "178.2200",
            "3. low": "174.4500",
            "4. close": "177.8400",
            "5. volume": "3462182"
        },
        "2024-07-09": {
            "1. open": "177.6000",
            "2. high": "177.7000",
            "3. low": "175.5800",
            "4. close": "176.4800",
            "5. volume": "2513305"
        },
        "2024-07-08": {
            "1. open": "176.4100",
            "2. high": "178.5900",
            "3. low": "176.0100",
            "4. close": "177.6400",
            "5. volume": "2503038"
        },
        "2024-07-05": {
            "1. open": "175.7400",
            "2. high": "176.0900",
            "3. low": "173.9500",
            "4. close": "176.0200",
            "5. volume": "2085970"
        },
        "2024-07-03": {
            "1. open": "177.8800",
            "2. high": "177.9800",
            "3. low": "175.1700",
            "4. close": "175.7300",
            "5. volume": "1649049"
        },
        "2024-07-02": {
            "1. open": "174.8400",
            "2. high": "177.4850",
            "3. low": "174.3200",
            "4. close": "177.3000",
            "5. volume": "2883275"
        },
        "2024-07-01": {
            "1. open": "173.4500",
            "2. high": "176.4600",
            "3. low": "173.3800",
            "4. close": "175.1000",
            "5. volume": "3320961"
        },
        "2024-06-28": {
            "1. open": "170.8500",
            "2. high": "173.4600",
            "3. low": "170.5300",
            "4. close": "172.9500",
            "5. volume": "4193459"
        },
        "2024-06-27": {
            "1. open": "171.1200",
            "2. high": "172.5000",
            "3. low": "170.4800",
            "4. close": "170.8500",
            "5. volume": "2894001"
        },
        "2024-06-26": {
            "1. open": "171.2800",
            "2. high": "172.6800",
            "3. low": "170.4100",
            "4. close": "171.8700",
            "5. volume": "2779016"
        },
        "2024-06-25": {
            "1. open": "175.1400",
            "2. high": "175.7526",
            "3. low": "171.4200",
            "4. close": "172.6000",
            "5. volume": "4119267"
        },
        "2024-06-24": {
            "1. open": "175.0000",
            "2. high": "178.4599",
            "3. low": "174.1500",
            "4. close": "175.0100",
            "5. volume": "4864735"
        },
        "2024-06-21": {
            "1. open": "173.9700",
            "2. high": "174.9600",
            "3. low": "171.4000",
            "4. close": "172.4600",
            "5. volume": "10182025"
        },
        "2024-06-20": {
            "1. open": "174.0800",
            "2. high": "174.2800",
            "3. low": "171.2200",
            "4. close": "173.9200",
            "5. volume": "4723078"
        },
        "2024-06-18": {
            "1. open": "170.0000",
            "2. high": "170.7500",
            "3. low": "168.3800",
            "4. close": "170.5500",
            "5. volume": "3386442"
        },
        "2024-06-17": {
            "1. open": "168.7600",
            "2. high": "169.7200",
            "3. low": "167.5000",
            "4. close": "169.5000",
            "5. volume": "3239815"
        },
        "2024-06-14": {
            "1. open": "168.2900",
            "2. high": "169.4700",
            "3. low": "167.2300",
            "4. close": "169.2100",
            "5. volume": "2777717"
        },
        "2024-06-13": {
            "1. open": "169.0100",
            "2. high": "169.5900",
            "3. low": "168.3350",
            "4. close": "169.1200",
            "5. volume": "3525717"
        },
        "2024-06-12": {
            "1. open": "171.3500",
            "2. high": "172.4700",
            "3. low": "168.1010",
            "4. close": "169.0000",
            "5. volume": "3522698"
        },
        "2024-06-11": {
            "1. open": "169.9800",
            "2. high": "170.0000",
            "3. low": "166.8100",
            "4. close": "169.3200",
            "5. volume": "2951251"
        },
        "2024-06-10": {
            "1. open": "169.5500",
            "2. high": "170.7600",
            "3. low": "168.8800",
            "4. close": "170.3800",
            "5. volume": "3444684"
        },
        "2024-06-07": {
            "1. open": "168.1800",
            "2. high": "171.3050",
            "3. low": "168.0600",
            "4. close": "170.0100",
            "5. volume": "3475495"
        },
        "2024-06-06": {
            "1. open": "167.3800",
            "2. high": "168.4400",
            "3. low": "166.8000",
            "4. close": "168.2000",
            "5. volume": "2207263"
        },
        "2024-06-05": {
            "1. open": "166.4100",
            "2. high": "167.7900",
            "3. low": "165.7800",
            "4. close": "167.3800",
            "5. volume": "3049377"
        },
        "2024-06-04": {
            "1. open": "164.6000",
            "2. high": "166.4000",
            "3. low": "163.8800",
            "4. close": "165.8100",
            "5. volume": "2594203"
        },
        "2024-06-03": {
            "1. open": "166.5400",
            "2. high": "166.7800",
            "3. low": "163.5300",
            "4. close": "165.2800",
            "5. volume": "2776058"
        },
        "2024-05-31": {
            "1. open": "165.7000",
            "2. high": "166.9700",
            "3. low": "163.8400",
            "4. close": "166.8500",
            "5. volume": "4905002"
        },
        "2024-05-30": {
            "1. open": "165.5600",
            "2. high": "166.7300",
            "3. low": "164.2300",
            "4. close": "165.6300",
            "5. volume": "3852963"
        },
        "2024-05-29": {
            "1. open": "168.0000",
            "2. high": "168.6300",
            "3. low": "166.2100",
            "4. close": "167.0500",
            "5. volume": "4206576"
        },
        "2024-05-28": {
            "1. open": "170.4400",
            "2. high": "171.0850",
            "3. low": "168.6500",
            "4. close": "169.6600",
            "5. volume": "2629645"
        },
        "2024-05-24": {
            "1. open": "171.4800",
            "2. high": "172.0100",
            "3. low": "170.2100",
            "4. close": "170.8900",
            "5. volume": "2587829"
        },
        "2024-05-23": {
            "1. open": "175.3900",
            "2. high": "175.4600",
            "3. low": "170.4350",
            "4. close": "170.6700",
            "5. volume": "3341335"
        },
        "2024-05-22": {
            "1. open": "173.3900",
            "2. high": "174.9900",
            "3. low": "172.7600",
            "4. close": "173.6900",
            "5. volume": "3294900"
        },
        "2024-05-21": {
            "1. open": "169.9400",
            "2. high": "174.9700",
            "3. low": "169.9400",
            "4. close": "173.4700",
            "5. volume": "6459800"
        },
        "2024-05-20": {
            "1. open": "169.0000",
            "2. high": "170.1600",
            "3. low": "168.3800",
            "4. close": "169.9200",
            "5. volume": "2726261"
        },
        "2024-05-17": {
            "1. open": "168.9700",
            "2. high": "169.1100",
            "3. low": "167.3300",
            "4. close": "169.0300",
            "5. volume": "2956387"
        },
        "2024-05-16": {
            "1. open": "168.2600",
            "2. high": "169.6300",
            "3. low": "167.7900",
            "4. close": "168.9700",
            "5. volume": "3492267"
        },
        "2024-05-15": {
            "1. open": "167.9400",
            "2. high": "168.3500",
            "3. low": "167.3400",
            "4. close": "168.2600",
            "5. volume": "4468823"
        },
        "2024-05-14": {
            "1. open": "167.8600",
            "2. high": "168.1300",
            "3. low": "166.4800",
            "4. close": "167.3600",
            "5. volume": "2600967"
        },
        "2024-05-13": {
            "1. open": "167.5000",
            "2. high": "168.0600",
            "3. low": "166.7600",
            "4. close": "167.5600",
            "5. volume": "2414859"
        },
        "2024-05-10": {
            "1. open": "167.1300",
            "2. high": "168.0700",
            "3. low": "166.3200",
            "4. close": "167.1500",
            "5. volume": "2255370"
        }
    }
}
"""
csv_filename = "ibm_stock_data.csv"


def convert_json_to_data_frame():
    # Convert JSON to DataFrame
    data_dict = json.loads(json_data)
    time_series = data_dict["Time Series (Daily)"]
    # Prepare data for DataFrame
    data = []
    for date, values in time_series.items():
        data.append(
            {
                "Date": date,
                "Open": float(values["1. open"]),
                "High": float(values["2. high"]),
                "Low": float(values["3. low"]),
                "Close": float(values["4. close"]),
                "Volume": int(values["5. volume"]),
            }
        )
    # Create DataFrame
    df = pd.DataFrame(data)
    # Save DataFrame to CSV
    df.to_csv(csv_filename, index=False)


def load_csv_data_in_data_frame():
    # Load the data into a DataFrame from CSV
    data = pd.read_csv(csv_filename)
    # Convert the 'Date' column to datetime type for better plotting
    data["Date"] = pd.to_datetime(data["Date"])

    return data


def draw_visuals(data):
    # Set up a 2x2 grid of subplots
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))

    # 1. Plot Daily Closing Prices Over Time
    axs[0, 0].plot(data["Date"], data["Close"], color="blue", label="Closing Price")
    axs[0, 0].set_title("Daily Closing Prices Over Time")
    axs[0, 0].set_xlabel("Date")
    axs[0, 0].set_ylabel("Closing Price")
    axs[0, 0].legend()

    # 2. Plot Daily Highs and Lows
    axs[0, 1].fill_between(
        data["Date"], data["Low"], data["High"], color="lightgrey", alpha=0.6
    )
    axs[0, 1].plot(data["Date"], data["High"], color="green", label="High")
    axs[0, 1].plot(data["Date"], data["Low"], color="red", label="Low")
    axs[0, 1].set_title("Daily Highs and Lows")
    axs[0, 1].set_xlabel("Date")
    axs[0, 1].set_ylabel("Price")
    axs[0, 1].legend()

    # 3. Plot Volume Traded Over Time
    axs[1, 0].bar(data["Date"], data["Volume"], color="purple", width=0.5)
    axs[1, 0].set_title("Volume Traded Over Time")
    axs[1, 0].set_xlabel("Date")
    axs[1, 0].set_ylabel("Volume")

    # 4. Plot Daily Opening vs Closing Prices
    axs[1, 1].plot(data["Date"], data["Open"], color="orange", label="Opening Price")
    axs[1, 1].plot(data["Date"], data["Close"], color="blue", label="Closing Price")
    axs[1, 1].set_title("Daily Opening vs Closing Prices")
    axs[1, 1].set_xlabel("Date")
    axs[1, 1].set_ylabel("Price")
    axs[1, 1].legend()

    # Adjust layout to prevent overlap
    plt.tight_layout()

    # Show the plots
    plt.show()


async def websocket_client():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            print(f"Received: {message}")


if __name__ == "__main__":
    for arg in sys.argv:
        if arg == "visual":
            convert_json_to_data_frame()
            data = load_csv_data_in_data_frame()
            draw_visuals(data)
        elif arg == "websocket":
            asyncio.run(websocket_client())
        else:
            logger.info("python ./main.py [option]")
            logger.info("[option]::")
            logger.info("\t visual    -- visualizes the requested data")
            logger.info("\t websocket -- runs the websocket client")