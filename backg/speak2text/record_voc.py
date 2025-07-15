import requests
import json
import base64
import sounddevice as sd
import numpy as np

API_KEY = "rDBlDmdDGFfI2FQLO8J14979"
SECRET_KEY = "IKAvhjWnhiiKNOpPAtU2e6fsQrzv6Oqk"

def record_pcm(filename, duration=5, samplerate=16000):
    print(f"正在录音 {duration} 秒...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    audio = audio.flatten()
    audio.tofile(filename)
    print("录音完成，已保存为", filename)

def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

def record_and_recognize(duration=5):
    audio_file = "recorded.pcm"
    record_pcm(audio_file, duration=duration, samplerate=16000)

    url = "https://vop.baidu.com/server_api"
    with open(audio_file, 'rb') as f:
        speech_data = f.read()
    speech_base64 = base64.b64encode(speech_data).decode('utf-8')

    payload = json.dumps({
        "format": "pcm",
        "rate": 16000,
        "channel": 1,
        "cuid": "QxMdYWTn8BomDX2dbV550p7iHX7ocRpj",
        "token": get_access_token(),
        "speech": speech_base64,
        "len": len(speech_data)
    }, ensure_ascii=False)
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload.encode("utf-8"))
    try:
        result = response.json()
        if "result" in result:
            return result["result"][0]
        else:
            return result.get("err_msg", "识别失败")
    except Exception:
        return "解析返回内容失败"

if __name__ == '__main__':
    print(record_and_recognize())