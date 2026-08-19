import http.client
import json

conn = http.client.HTTPSConnection("vyk6mm.api.infobip.com")
payload = json.dumps({
    "messages": [
        {
            "from": "447860088970",
            "to": "27825576310",
            "messageId": "4b77a3c6-041f-48bd-9a68-55eab1b63043",
            "content": {
                "templateName": "test_whatsapp_template_en",
                "templateData": {
                    "body": {
                        "placeholders": ["Graham"]
                    }
                },
                "language": "en"
            }
        }
    ]
})
headers = {
    'Authorization': 'App a5cb0f4aa1c5771cd875efdf558b7c1e-84fb31f6-dd21-4899-ba27-c7f59b12c934',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
conn.request("POST", "/whatsapp/1/message/template", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))