import os
import django
import requests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'catering_company.settings')
django.setup()
from django.conf import settings


def test_yandex_api():

    api_key = settings.YANDEX_TRANSLATE_API_KEY
    folder_id = settings.YANDEX_FOLDER_ID

    url = "https://translate.api.cloud.yandex.net/translate/v2/translate"
    headers = {
        "Authorization": f"Api-Key {api_key}",
        "Content-Type": "application/json"
    }
    
    body = {
        "folderId": folder_id,
        "texts": ["Привет, мир!"],
        "targetLanguageCode": "en"
    }
    
    try:
        response = requests.post(url, headers=headers, json=body, timeout=10)
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.text[:200]}...")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Успех! Переведенный текст: {result['translations'][0]['text']}")
            return True
        elif response.status_code == 401:
            print("\n❌ Ошибка 401: Неверный API ключ")
        elif response.status_code == 403:
            print("\n❌ Ошибка 403: Нет доступа или неверный Folder ID")
        elif response.status_code == 400:
            print("\n❌ Ошибка 400: Неверный запрос. Проверьте тело запроса")
        else:
            print(f"\n❌ Ошибка {response.status_code}: {response.text}")
            
    except requests.exceptions.Timeout:
        print("\n❌ Таймаут: API не отвечает")
    except requests.exceptions.ConnectionError:
        print("\n❌ Ошибка соединения: Проверьте интернет")
    except Exception as e:
        print(f"\n❌ Неизвестная ошибка: {str(e)}")
    
    return False
