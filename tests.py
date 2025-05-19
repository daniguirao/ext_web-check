import requests
import json
import sys

def test_web_service():
    try:
        # Realizar la petición al servicio
        response = requests.get('http://localhost:32111')
        
        # Verificar que el código de respuesta es 200 (OK)
        if response.status_code != 200:
            print(f"❌ Error: El servicio respondió con código {response.status_code}")
            sys.exit(1)
            
        # Convertir la respuesta a JSON
        data = response.json()
        
        # Lista de campos requeridos
        required_fields = [
            "error",
            "Public_IP",
            "Location",
            "Local_IP",
            "Interface",
            "Download-Speed",
            "Upload-Speed"
        ]
        
        # Verificar que todos los campos requeridos están presentes
        missing_fields = []
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ Error: Faltan los siguientes campos en la respuesta: {', '.join(missing_fields)}")
            sys.exit(1)
            
        # Verificar que el campo error es "0"
        if data["error"] != "0":
            print(f"❌ Error: El campo 'error' debería ser '0', pero es '{data['error']}'")
            sys.exit(1)
            
        print("✅ Todas las pruebas pasaron correctamente")
        sys.exit(0)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servicio. Asegúrate de que está ejecutándose en el puerto 32111")
        sys.exit(1)
    except json.JSONDecodeError:
        print("❌ Error: La respuesta no es un JSON válido")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_web_service()