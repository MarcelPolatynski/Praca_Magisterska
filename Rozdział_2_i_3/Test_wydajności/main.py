import psutil
import time
import GPUtil

def monitor_systemu():
    # Pobieranie informacji o CPU
    cpu_percent = psutil.cpu_percent(interval=1)

    print(f"Użycie CPU: {cpu_percent}%")

    # Pobieranie informacji o RAM
    ram = psutil.virtual_memory()
    ram_used = ram.used // (1024 * 1024) 


    print(f"Użycie RAM: {ram_used} MB")

    # Pobieranie informacji o GPU
    try:
        gpus = GPUtil.getGPUs()
        for gpu in gpus:
            print(f"Użycie GPU: {gpu.load * 100}%")
            print(f"Wykorzystanie pamięci GPU: {gpu.memoryUsed} MB")
    except ImportError:
        print("Biblioteka GPUtil nie jest zainstalowana. Pominięto informacje o GPU.")

if __name__ == "__main__":
    while True:
        monitor_systemu()
        time.sleep(0.5)
