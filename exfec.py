
import uvicorn
from fastapi import FastAPI,Request
import os
import torch
from openvoice import se_extractor
from openvoice.api import ToneColorConverter
import nltk
nltk.download('averaged_perceptron_tagger_eng')


app = FastAPI()
ckpt_converter = 'checkpoints_v2/converter'
base_speakers = 'checkpoints_v2/base_speakers'
device="cuda:0" if torch.cuda.is_available() else "cpu"
print(device)
tone_color_converter = ToneColorConverter(f'{ckpt_converter}/config.json', device=device)
tone_color_converter.load_ckpt(f'{ckpt_converter}/checkpoint.pth')

app.state.resold=""

from melo.api import TTS


@app.get("/")
async def get_state():
    return {"state": "ok"}

@app.get("/language")
async def get_language():
    return ['EN_NEWEST', 'EN', 'ES', 'FR', 'ZH', 'JP', 'KR']


@app.post("/mdvoice")
async def mdvoice(request: Request):
    try:
        voicemodel = await request.json()
        print(voicemodel)
    except Exception as e:
        print(f"JSON decode error: {e}")
        return {"error": "Invalid JSON"}, 400
    texts = voicemodel["texts"]
    speed=voicemodel["speed"]
    output_dir = voicemodel['output_dir']
    os.makedirs(output_dir, exist_ok=True)

    src_path = f'{output_dir}/tmp.wav'
    save_pathlst=[]

    reference_speaker = voicemodel["reference_speaker"]  # This is the voice you want to clone
    if app.state.resold != reference_speaker:
        target_se, audio_name = se_extractor.get_se(reference_speaker, tone_color_converter, target_dir='processed',vad=True)
        app.state.resold=reference_speaker
    for language, text in texts.items():
        model = TTS(language=language, device=device)
        speaker_ids = model.hps.data.spk2id

        for speaker_key in speaker_ids.keys():
            speaker_id = speaker_ids[speaker_key]
            speaker_key = speaker_key.lower().replace('_', '-')
            source_se = torch.load(f'{base_speakers}/ses/{speaker_key}.pth', map_location=device)
            model.tts_to_file(text, speaker_id, src_path, speed=speed)
            save_path = f'{output_dir}/output_v2_{speaker_key}.wav'
            save_pathlst.append(save_path)
            # Run the tone color converter
            encode_message = "@MyShell"
            tone_color_converter.convert(
                audio_src_path=src_path,
                src_se=source_se,
                tgt_se=target_se,
                output_path=save_path,
                message=encode_message)

    return {"state": "ok","save_path":save_pathlst}



if __name__ == "__main__":
    uvicorn.run("exfec:app", host="127.0.0.1", port=8001)