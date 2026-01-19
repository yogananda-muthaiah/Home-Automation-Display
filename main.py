import network
import urequests
import time
import machine
import ujson
from machine import Pin, I2C
import ssd1306

# WiFi Configuration
WIFI_SSID = "your_wifi_ssid"
WIFI_PASSWORD = "your_wifi_password"

# GitHub Configuration
GITHUB_USER = "your_username"
GITHUB_REPO = "your_repository"
GITHUB_FILE = "path/to/your/file.md"  # Path to markdown file with table
GITHUB_TOKEN = "your_github_token"  # Optional: for higher rate limits

# Display Configuration (adjust for your display)
i2c = I2C(0, scl=Pin(5), sda=Pin(4))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

def connect_to_wifi():
    """Connect to WiFi network"""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('Waiting for connection...')
        time.sleep(1)
    
    if wlan.status() != 3:
        raise RuntimeError('WiFi connection failed')
    else:
        print('Connected to WiFi')
        status = wlan.ifconfig()
        print('IP = ' + status[0])
        return True

def fetch_github_markdown():
    """Fetch markdown content from GitHub"""
    headers = {}
    if GITHUB_TOKEN:
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # Get file metadata
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{GITHUB_FILE}"
    response = urequests.get(url, headers=headers)
    file_info = ujson.loads(response.text)
    response.close()
    
    # Get file content
    content_response = urequests.get(file_info['download_url'], headers=headers)
    markdown_content = content_response.text
    content_response.close()
    
    return markdown_content

def parse_markdown_table(markdown):
    """Parse markdown table into headers and rows"""
    lines = markdown.split('\n')
    
    # Find the table header separator (---)
    header_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith('|') and '---' in line:
            header_idx = i
            break
    
    if header_idx is None:
        return None
    
    # Extract headers
    headers = [cell.strip() for cell in lines[header_idx-1].split('|')[1:-1]]
    
    # Extract data rows
    data = []
    for line in lines[header_idx+1:]:
        if line.strip().startswith('|'):
            row = [cell.strip() for cell in line.split('|')[1:-1]]
            data.append(row)
    
    return headers, data

def display_table(headers, data):
    """Display table on OLED"""
    oled.fill(0)
    
    # Calculate column widths
    col_widths = []
    for i, header in enumerate(headers):
        max_width = len(header)
        for row in data:
            if i < len(row):
                max_width = max(max_width, len(row[i]))
        col_widths.append(min(max_width, oled.width // len(headers)))
    
    # Display headers
    x = 0
    for i, header in enumerate(headers):
        # Truncate if too long
        if len(header) > col_widths[i]:
            header = header[:col_widths[i]-1] + "..."
        oled.text(header, x, 0)
        x += col_widths[i]
    
    # Display data
    y = 10
    for row in data:
        x = 0
        for i, cell in enumerate(row):
            # Truncate if too long
            if len(cell) > col_widths[i]:
                cell = cell[:col_widths[i]-1] + "..."
            oled.text(cell, x, y)
            x += col_widths[i]
        y += 8
        if y >= oled.height - 8:
            break
    
    oled.show()

def main():
    try:
        # Connect to WiFi
        connect_to_wifi()
        
        # Main loop
        while True:
            try:
                # Fetch and display table
                markdown = fetch_github_markdown()
                table_data = parse_markdown_table(markdown)
                
                if table_data:
                    headers, data = table_data
                    display_table(headers, data)
                    print("Table updated successfully")
                else:
                    oled.fill(0)
                    oled.text("No table found", 0, 0)
                    oled.show()
                
                # Check for updates every 5 minutes
                print("Waiting for next update...")
                time.sleep(300)
                
            except Exception as e:
                print("Error:", e)
                oled.fill(0)
                oled.text("Error: " + str(e)[:20], 0, 0)
                oled.show()
                time.sleep(60)  # Wait before retrying
                
    except Exception as e:
        print("Fatal error:", e)
        oled.fill(0)
        oled.text("Fatal error", 0, 0)
        oled.show()

if __name__ == "__main__":
    main()
