from flask import Flask, jsonify
import requests
import socket
import netifaces
import speedtest

app = Flask(__name__)

def get_network_info():
    ip_info = requests.get('https://ipinfo.io/json').json()
    public_ip = ip_info.get('ip')
    location = ip_info.get('city', 'Unknown') + ", " + ip_info.get('country', 'Unknown')

    gateways = netifaces.gateways().get('default', {})
    iface_info = gateways.get(netifaces.AF_INET)

    if iface_info:
        iface = iface_info[1]
        local_ip = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']
    else:
        iface = 'Unavailable'
        local_ip = 'Unavailable'
    
    # Medir la velocidad de Internet
    st = speedtest.Speedtest()
    st.get_best_server()  # Elige el mejor servidor
    download_speed = st.download() / 1_000_000  # Convertir a Mbps
    upload_speed = st.upload() / 1_000_000  # Convertir a Mbps
    
    return {
        "error":"0",
        "Public_IP": public_ip,
        "Location": location,
        "Local_IP": local_ip,
        "Interface": iface,
        "Download-Speed": round(download_speed, 2),
        "Upload-Speed": round(upload_speed, 2)
    }

@app.route("/")
def index():
    try:
        data = get_network_info()
        return jsonify(data)
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=32111)
