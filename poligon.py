import requests
import psutil
import platform
import socket
import time
import uuid
import speedtest
import GPUtil

def get_crypto_data(cryptos):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(cryptos)}&vs_currencies=usd"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Ошибка при получении данных.")
        return None

def get_device_info():
    device_info = {
        "device_name": platform.node(),
        "os": platform.system() + " " + platform.release(),
        "mac_address": ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1]),
        "ip_address": socket.gethostbyname(socket.gethostname()),
        "internet_speed": get_internet_speed(),
        "temperature": get_temperature(),
        "cpu_temperature": get_cpu_temperature(),
        "gpu_info": get_gpu_info()
    }
    return device_info

def get_internet_speed():
    st = speedtest.Speedtest()
    st.get_best_server()
    download_speed = st.download() / 1_000_000  # Конвертируем в Мбит/с
    upload_speed = st.upload() / 1_000_000  # Конвертируем в Мбит/с
    return f"Скорость загрузки: {download_speed:.2f} Мбит/с, Скорость выгрузки: {upload_speed:.2f} Мбит/с"

def get_temperature():
    if platform.system() == "Linux":
        try:
            temp = psutil.sensors_temperatures()["coretemp"][0].current
            return f"{temp} °C"
        except Exception:
            return "Не удалось получить температуру"
    return "Не поддерживается"

def get_cpu_temperature():
    return psutil.sensors_temperatures().get('coretemp', [])[0].current if 'coretemp' in psutil.sensors_temperatures() else None

def get_gpu_info():
    gpus = GPUtil.getGPUs()
    gpu_info = []
    for gpu in gpus:
        gpu_info.append({
            "name": gpu.name,
            "temperature": gpu.temperature
        })
    return gpu_info

def display_device_info(device_info):
    print("\nПолучение информации о устройстве...")
    for key, value in device_info.items():
        if key == "gpu_info":
            for gpu in value:
                print(f"Видеокарта: {gpu['name']}, Температура: {gpu['temperature']} °C")
        else:
            print(f"{key.replace('_', ' ').capitalize()}: {value}")

def start_mining(device_info):
    # Получаем нормальные температуры
    cpu_normal_temp = get_cpu_temperature()
    gpu_normal_temps = [gpu['temperature'] for gpu in device_info['gpu_info']]
    
    print("\nНачинаем процесс майнинга...")
    while True:
        current_cpu_temp = get_cpu_temperature()
        current_gpu_temps = [gpu['temperature'] for gpu in device_info['gpu_info']]
        
        print(f"\nПроцессор: {platform.processor()} - Прошлая температура: {cpu_normal_temp} °C (НОРМА) - Настоящая температура: {current_cpu_temp} °C - Предельная температура: 85 °C")
        
        for i, gpu in enumerate(device_info['gpu_info']):
            print(f"Видеокарта: {gpu['name']} - Прошлая температура: {gpu_normal_temps[i]} °C (НОРМА) - Настоящая температура: {current_gpu_temps[i]} °C - Предельная температура: 85 °C")
        
        if current_cpu_temp > 85 or any(temp > 85 for temp in current_gpu_temps):
            print("Внимание! Температура превышает предельную. Остановка майнинга.")
            break
        
        time.sleep(10)  # Задержка для симуляции процесса

def main():
    cryptos = ["bitcoin", "ethereum", "monero"]
    
    print("Получение данных о криптовалютах...")
    data = get_crypto_data(cryptos)
    
    if data:
        for crypto in cryptos:
            print(f"Текущая цена {crypto.capitalize()}: ${data[crypto]['usd']}")
    
    device_info = get_device_info()
    display_device_info(device_info)

    start_mining_choice = input("Вы хотите начать майнинг? (y/n): ")
    if start_mining_choice.lower() == 'y':
        start_mining(device_info)
    else:
        print("Майнинг не был запущен. Завершение программы.")

if __name__ == "__main__":
    main()
