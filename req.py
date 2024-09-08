import json

import requests

data={
    "speed":1,
    "texts" : {
    'EN_NEWEST': "Did you ever hear a folk tale about a giant turtle?",  # The newest English base speaker model
    'EN': "Did you ever hear a folk tale about a giant turtle?",
    'ES': "El resplandor del sol acaricia las olas, pintando el cielo con una paleta deslumbrante.",
    'FR': "La lueur dorée du soleil caresse les vagues, peignant le ciel d'une palette éblouissante.",
    'ZH': "在这次vacation中，我们计划去Paris欣赏埃菲尔铁塔和卢浮宫的美景。每次看到哪些美景我心里都会觉得很愉快",
    'JP': "彼は毎朝ジョギングをして体を健康に保っています。",
    'KR': "안녕하세요! 오늘은 날씨가 정말 좋네요.",
},
    "output_dir":"outputs",
    "reference_speaker":"resources/source.mp3"
}
headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT)',
'Content-Type': 'application/json'
}
response=requests.post("http://127.0.0.1:8000/mdvoice",data=json.dumps(data),headers=headers)
print(response.status_code)
print(response.text)