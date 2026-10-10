import requests

from config import GROQ_API_KEY, BUSINESS_CONTEXT


class AIServiceError(Exception):
    """Yapay zekâ servisiyle ilgili hatalar."""
    pass


class AIService:
    def yanit_uret(self, mesaj, gecmis=None):
        # API anahtarı yoksa demo yanıtı ver
        if not GROQ_API_KEY:
            return "CHARÉN AI Tea Sommelier şu anda demo modunda."

        # Önce asistanın rolü, sonra sohbet geçmişi
        messages = [
            {"role": "system", "content": BUSINESS_CONTEXT}
        ]

        if gecmis:
            messages.extend(gecmis)

        messages.append({
            "role": "user",
            "content": mesaj
        })

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "openai/gpt-oss-20b",
                    "messages": messages
                },
                timeout=30
            )

            print("Groq HTTP durumu:", response.status_code)
            print("Groq hata detayı:", response.text[:500])

            response.raise_for_status()

            return response.json()["choices"][0]["message"]["content"]

        except (requests.RequestException, KeyError, IndexError, TypeError) as error:
            raise AIServiceError(
                "Yapay zekâ servisine şu anda ulaşılamıyor."
            ) from error


ai_service = AIService()