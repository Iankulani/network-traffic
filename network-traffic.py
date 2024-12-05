# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 05:54:47 2024

@author: IAN CARTER KULANI
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ping3 import ping

class NetworkMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Monitor Tool")
        self.root.geometry("800x600")
        
        self.ip_addresses = []
        self.latency_data = []
        self.network_data = []
        self.is_monitoring = False
        
        self.create_widgets()

    def create_widgets(self):
        # Input field to enter multiple IP addresses
        ttk.Label(self.root, text="Enter IP Addresses (comma-separated):").grid(row=0, column=0, padx=10, pady=5)
        self.ip_entry = ttk.Entry(self.root, width=50)
        self.ip_entry.grid(row=0, column=1, padx=10, pady=5)

        # Button to start/stop monitoring
        self.start_button = ttk.Button(self.root, text="Start Monitoring", command=self.toggle_monitoring)
        self.start_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        # Label to show the current status of network monitoring
        self.status_label = ttk.Label(self.root, text="Status: Not Monitoring")
        self.status_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

        # Matplotlib plot for network traffic statistics
        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.ax.set_title("Network Traffic Monitoring")
        self.ax.set_xlabel("Time (seconds)")
        self.ax.set_ylabel("Traffic (bytes)")

        self.canvas = FigureCanvasTkAgg(self.fig, self.root)
        self.canvas.get_tk_widget().grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Matplotlib pie chart for latency statistics
        self.pie_fig, self.pie_ax = plt.subplots(figsize=(4, 4))
        self.pie_ax.pie([0.5, 0.5], labels=['Low Latency', 'High Latency'], autopct='%1.1f%%', startangle=90)
        self.pie_ax.set_title("Latency Statistics")

        self.pie_canvas = FigureCanvasTkAgg(self.pie_fig, self.root)
        self.pie_canvas.get_tk_widget().grid(row=3, column=2, padx=10, pady=10)

    def toggle_monitoring(self):
        if self.is_monitoring:
            self.is_monitoring = False
            self.start_button.config(text="Start Monitoring")
            self.status_label.config(text="Status: Not Monitoring")
        else:
            self.is_monitoring = True
            self.start_button.config(text="Stop Monitoring")
            self.status_label.config(text="Status: Monitoring")
            threading.Thread(target=self.monitor_network).start()

    def monitor_network(self):
        # Start monitoring network traffic and pinging IPs
        self.latency_data = []
        self.network_data = []
        start_time = time.time()
        
        while self.is_monitoring:
            # Get list of IPs
            ips = self.ip_entry.get().split(',')
            for ip in ips:
                ip = ip.strip()  # Clean up any leading/trailing spaces
                latency = self.ping_ip(ip)
                if latency is not None:
                    self.latency_data.append(latency)
                
            # Monitor network traffic
            net_io = psutil.net_io_counters()
            self.network_data.append(net_io.bytes_sent + net_io.bytes_recv)

            # Update the visualizations
            self.update_pie_chart()
            self.update_network_traffic(start_time)
            time.sleep(2)  # Wait 2 seconds before the next ping or traffic check

    def ping_ip(self, ip):
        try:
            latency = ping(ip)
            if latency is not None:
                return round(latency * 1000)  # Convert latency to ms
        except Exception as e:
            print(f"Error pinging {ip}: {e}")
        return None

    def update_pie_chart(self):
        # Determine high vs low latency based on a threshold (e.g., 200 ms)
        low_latency_count = sum(1 for latency in self.latency_data if latency < 200)
        high_latency_count = len(self.latency_data) - low_latency_count

        # Calculate percentages
        total = len(self.latency_data)
        low_latency_percentage = (low_latency_count / total) * 100 if total else 0
        high_latency_percentage = (high_latency_count / total) * 100 if total else 0

        # Update pie chart
        self.pie_ax.clear()
        self.pie_ax.pie([low_latency_percentage, high_latency_percentage], 
                        labels=[f'Low Latency ({low_latency_percentage:.1f}%)', f'High Latency ({high_latency_percentage:.1f}%)'], 
                        autopct='%1.1f%%', startangle=90)
        self.pie_ax.set_title("Latency Statistics")
        self.pie_canvas.draw()

    def update_network_traffic(self, start_time):
        # Time elapsed
        elapsed_time = time.time() - start_time

        # Update the network traffic plot
        self.ax.clear()
        self.ax.set_title("Network Traffic Monitoring")
        self.ax.set_xlabel("Time (seconds)")
        self.ax.set_ylabel("Traffic (bytes)")
        self.ax.plot(range(len(self.network_data)), self.network_data, color='green')
        self.ax.set_ylim(0, max(self.network_data) * 1.1 if self.network_data else 1000)
        self.canvas.draw()

# Create the main window and run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkMonitorApp(root)
    root.mainloop()
