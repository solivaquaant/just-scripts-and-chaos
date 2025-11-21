import ftplib
import socket
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading


# Check connection to an IP before checking FTP
def check_connection(host, log_func, port=21, timeout=1):
    """Check raw TCP connection to a port."""
    try:
        socket.setdefaulttimeout(timeout)
        s = socket.socket()
        s.connect((host, port))
        s.close()
        return True
    except socket.error as err:
        log_func(f"Cannot connect to {host}: {err}")
        return False

def list_root_files(ftp, log_func):
    """
    List files and directories in the root directory of the FTP server.
    Returns a list of files/directories, or None if empty.
    """
    try:
        files = ftp.nlst()  # List files/directories in root
        if files:
            return files
        else:
            return None  # No files or directories
    except ftplib.error_perm as error:
        log_func(f"FTP error (permission denied): {error}")
        return None

def check_ftp(result, ip, log_func):
    """
    Check FTP on an IP and write results to an HTML file if data exists.
    Only lists files/directories in the root.
    """
    try:
        ftp = ftplib.FTP(ip, 'anonymous', '', timeout=1)
        ftp.encoding = 'latin-1'
        
        files = list_root_files(ftp, log_func)  # List root files/directories
        if files:
            log_func(f"--- Files found at {ip}! Writing to report...")
            result.write(f'<div style="border:1px solid black;padding:10px;margin-bottom:10px;">')
            result.write(f'<h2>IP/Host: {ip}</h2><ul>')
            
            for f in files:
                result.write(f'<li>{f}</li>')
            
            result.write('</ul></div>')
        else:
            log_func(f"No files or directories found at {ip}. Skipping...")
        
        ftp.quit()
    except ftplib.all_errors as error:
        log_func(f"FTP error at {ip}: {error}")
        pass

def try_open_file(filename, log_func):
    """Try opening a file with different encodings."""
    encodings = ['utf-8-sig', 'utf-16', 'latin-1']
    for encoding in encodings:
        try:
            with open(filename, encoding=encoding) as f:
                log_func(f"Successfully opened file with encoding {encoding}")
                return f.readlines()
        except UnicodeDecodeError as e:
            log_func(f"Failed to open with {encoding}: {e}")
    return None

def create_gui():
    root = tk.Tk()
    root.title("FTP Anonymous Scanner")
    root.geometry("600x600")

    tab_control = ttk.Notebook(root)
    
    # Tab 1: Manual Testing
    tab1 = ttk.Frame(tab_control)
    tab_control.add(tab1, text='Manual Scan')
    
    frame_manual = ttk.LabelFrame(tab1, text="Single Target")
    frame_manual.pack(fill="x", expand=True, padx=10, pady=10)

    ttk.Label(frame_manual, text="IP/Host:").pack(pady=5)
    entry_manual_ip = ttk.Entry(frame_manual, width=50)
    entry_manual_ip.pack(pady=5, padx=10, fill="x")

    ttk.Label(frame_manual, text="Output (HTML File):").pack(pady=5)
    entry_manual_output = ttk.Entry(frame_manual, width=50)
    entry_manual_output.pack(pady=5, padx=10, fill="x")
    entry_manual_output.insert(0, "result_manual.html")

    btn_manual_scan = ttk.Button(frame_manual, text="Start Scan", 
                                 command=lambda: start_manual_scan_thread(
                                     entry_manual_ip.get(), 
                                     entry_manual_output.get()
                                 ))
    btn_manual_scan.pack(pady=10)

    # Tab 2: Automatic Testing
    tab2 = ttk.Frame(tab_control)
    tab_control.add(tab2, text='Automatic Scan')

    frame_auto = ttk.LabelFrame(tab2, text="Batch Targets")
    frame_auto.pack(fill="x", expand=True, padx=10, pady=10)

    # Input File
    frame_input = ttk.Frame(frame_auto)
    frame_input.pack(fill="x", padx=10, pady=5)
    ttk.Label(frame_input, text="Input File (IP list):").pack(side=tk.LEFT)
    entry_auto_input = ttk.Entry(frame_input, width=40)
    entry_auto_input.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
    btn_browse_input = ttk.Button(frame_input, text="Browse...",
                                  command=lambda: browse_file(entry_auto_input))
    btn_browse_input.pack(side=tk.LEFT)

    # Output File
    frame_output = ttk.Frame(frame_auto)
    frame_output.pack(fill="x", padx=10, pady=5)
    ttk.Label(frame_output, text="Output File (HTML report):").pack(side=tk.LEFT)
    entry_auto_output = ttk.Entry(frame_output, width=40)
    entry_auto_output.pack(side=tk.LEFT, fill="x", expand=True, padx=5)
    btn_browse_output = ttk.Button(frame_output, text="Save As...",
                                   command=lambda: save_file(entry_auto_output))
    btn_browse_output.pack(side=tk.LEFT)
    entry_auto_output.insert(0, "result_batch.html")

    btn_auto_scan = ttk.Button(frame_auto, text="Start Batch Scan",
                               command=lambda: start_auto_scan_thread(
                                   entry_auto_input.get(), 
                                   entry_auto_output.get()
                               ))
    btn_auto_scan.pack(pady=10)

    tab_control.pack(expand=1, fill="x", pady=5, padx=5)

    # Log area 
    frame_log = ttk.LabelFrame(root, text="Log Output")
    frame_log.pack(fill="both", expand=True, padx=10, pady=10)
    
    log_text = scrolledtext.ScrolledText(frame_log, width=70, height=20, wrap=tk.WORD)
    log_text.pack(fill="both", expand=True, padx=5, pady=5)
    
    def log_message(message):
        """Thread-safe logging to update Text widget."""
        log_text.insert(tk.END, message + "\n")
        log_text.see(tk.END)
        root.update_idletasks()
    
    def browse_file(entry_widget):
        """Open file dialog and update entry."""
        filename = filedialog.askopenfilename(
            title="Select Input File",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
        )
        if filename:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filename)

    def save_file(entry_widget):
        """Open save dialog and update entry."""
        filename = filedialog.asksaveasfilename(
            title="Save Report As",
            filetypes=(("HTML files", "*.html"), ("All files", "*.*")),
            defaultextension=".html"
        )
        if filename:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filename)
    
    def start_manual_scan_thread(target, result_name):
        """Wrap single scan function in a thread."""
        log_message("Starting single scan...")
        btn_manual_scan.config(state=tk.DISABLED)
        threading.Thread(target=run_manual_scan, args=(target, result_name), daemon=True).start()

    def run_manual_scan(target, result_name):
        """Single scan task (runs in thread)."""
        if not target:
            log_message("Error: Please enter IP/Host.")
            btn_manual_scan.config(state=tk.NORMAL)
            return

        try:
            if check_connection(target, log_message):
                log_message(f"Connected to {target}. Checking FTP...")
                with open(result_name, 'w+', encoding='utf-8') as result:
                    result.write('<html><head><title>FTP Scan Results</title></head><body>')
                    check_ftp(result, target, log_message)
                    result.write('</body></html>')
                log_message(f"Scan complete. Results saved to: {result_name}")
            else:
                log_message(f"Skipping {target} due to failed connection.")
        except Exception as e:
            log_message(f"Unexpected error occurred: {e}")
        finally:
            btn_manual_scan.config(state=tk.NORMAL)

    def start_auto_scan_thread(name, result_name):
        """Wrap batch scan function in a thread."""
        log_message("Starting batch scan...")
        btn_auto_scan.config(state=tk.DISABLED)
        threading.Thread(target=run_auto_scan, args=(name, result_name), daemon=True).start()

    def run_auto_scan(name, result_name):
        """Batch scan task (runs in thread)."""
        if not name or not result_name:
            log_message("Error: Please select input and output files.")
            btn_auto_scan.config(state=tk.NORMAL)
            return

        try:
            b = try_open_file(name, log_message)
            
            if b is not None:
                c = [x.strip().replace('\n', '') for x in b if x.strip()]
                log_message(f"Found {len(c)} IP/Host in the file.")

                with open(result_name, 'w+', encoding='utf-8') as result:
                    result.write('<html><head><title>FTP Scan Results</title></head><body>')

                    for ip in c:
                        log_message(f'\n--- Checking IP/Host: {ip} ---')
                        if check_connection(ip, log_message):
                            check_ftp(result, ip, log_message)
                        else:
                            log_message(f"Skipping {ip} due to failed connection.")
                    
                    result.write('</body></html>')
                log_message(f"Batch scan complete. Results saved to: {result_name}")
            else:
                log_message(f"Failed to open input file: {name}")
        except Exception as e:
            log_message(f"Unexpected error occurred: {e}")
        finally:
            btn_auto_scan.config(state=tk.NORMAL)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
