import os, subprocess, time, urllib.parse, json
import speech_recognition as sr
WA_RAW = os.path.expanduser("~/rec.m4a")
WA_WAV = os.path.expanduser("~/rec.wav")

def speak(text):
    print(f"\nJarvis: {text}")
    tts = text.replace("Sir Osaf Ali", "Sir Osaaaf Aliii").replace("Osaf Ali", "Osaaaf Aliii")
    os.system(f'termux-tts-speak "{tts}" 2>/dev/null')

def suno():
    print(f"\n[ Mic ON 5 sec bolo ]")
    if os.path.exists(WA_RAW): os.remove(WA_RAW)
    if os.path.exists(WA_WAV): os.remove(WA_WAV)
    subprocess.getoutput(f'termux-microphone-record -f {WA_RAW} -l 5 2>&1')
    time.sleep(6)
    subprocess.getoutput('termux-microphone-record -q 2>&1')
    if not os.path.exists(WA_RAW): return ""
    sz = os.path.getsize(WA_RAW)
    print(f"Raw Size: {sz} bytes")
    if sz < 500: return ""
    subprocess.getoutput(f'ffmpeg -y -i {WA_RAW} -ar 16000 -ac 1 -c:a pcm_s16le {WA_WAV} 2>&1')
    if not os.path.exists(WA_WAV): return ""
    print(f"WAV Size: {os.path.getsize(WA_WAV)} bytes")
    r = sr.Recognizer()
    try:
        with sr.AudioFile(WA_WAV) as source: audio = r.record(source)
        try: text = r.recognize_google(audio, language="ur-PK")
        except: text = r.recognize_google(audio, language="en-US")
        print(f"Tum ne bola: {text}"); return text
    except Exception as e:
        print(f"Google error: {e}"); return ""

def get_all_contacts_by_name(name):
    try:
        out = subprocess.getoutput('termux-contact-list 2>&1')
        contacts = json.loads(out)
        return [c for c in contacts if name.lower() in c.get('name','').lower() and c.get('number','')]
    except: return []

def open_dialer_with_number(number):
    clean = "".join([c for c in number if c.isdigit() or c=='+'])
    os.system(f'am start -a android.intent.action.DIAL -d "tel:{clean}" > /dev/null 2>&1')

def open_whatsapp_chat(number):
    clean = "".join([c for c in number if c.isdigit()])
    if clean.startswith("03"): clean = "92" + clean[1:]
    os.system(f'am start -a android.intent.action.VIEW -d "https://wa.me/{clean}" > /dev/null 2>&1')

def open_whatsapp_chat_with_message(number, message):
    clean = "".join([c for c in number if c.isdigit()])
    if clean.startswith("03"): clean = "92" + clean[1:]
    # ye message likh dega, send ka button user dabayega
    os.system(f'am start -a android.intent.action.VIEW -d "https://wa.me/{clean}?text={urllib.parse.quote(message)}" > /dev/null 2>&1')

def open_native(app_key, search_query=""):
    pkgs = {"tiktok":"com.zhiliaoapp.musically","youtube":"com.google.android.youtube","whatsapp":"com.whatsapp"}
    pkg = pkgs.get(app_key.lower())
    if not pkg: return
    if app_key=="youtube" and search_query:
        os.system(f'am start -a android.intent.action.VIEW -d "https://www.youtube.com/results?search_query={urllib.parse.quote(search_query)}" -p {pkg} > /dev/null 2>&1'); return
    os.system(f'monkey -p {pkg} -c android.intent.category.LAUNCHER 1 > /dev/null 2>&1')

def jawab_do(sawal):
    low = sawal.lower()
    if "kia hal hai" in low or "kya hal hai" in low or "how are you" in low:
        return "Me theek hun Sir Osaf Ali, aap sunao?"
    if "kia gal hai" in low or "kya gal hai" in low:
        return "Koi gal nahi Sir Osaf Ali, sab theek hai, batao kya kaam hai?"
    if "tum kon ho" in low or "kis ne banaya" in low:
        return "Mujhe Sir Osaf Ali ne banaya hai, mera naam Jarvis hai"
    if "time" in low:
        return f"Abhi time {time.strftime('%I:%M %p')} ho raha hai Sir Osaf Ali"
    if "hello" in low or "hi" in low:
        return "Hello Sir Osaf Ali, hukam karen"
    return f"Samajh gaya Sir Osaf Ali, aap ne kaha {sawal}, batao is pe kya karun?"

speak("Me Jarvis hun, mujhe Sir Osaf Ali ne banaya hai")
voice_mode = True
fail = 0
while True:
    if voice_mode:
        cmd = suno()
        if not cmd:
            fail += 1
            print(f"Fail: {fail}/3")
            if fail >= 3:
                voice_mode = False
                speak("Mic se awaz sahi nahi aa rahi, typing pe aa gaya hun Sir Osaf Ali")
                continue
            else: continue
        else: fail = 0
    else:
        cmd = input("\nAap (mic on likho to mic on): ")
    if not cmd: continue
    low = cmd.lower()

    if "mic on" in low: voice_mode = True; speak("Mic on ho gaya Sir Osaf Ali"); continue
    if "mic off" in low: voice_mode = False; speak("Mic off ho gaya Sir Osaf Ali"); continue

    # ===== YAHAN SARA CONTACT / WHATSAPP RULE EK SATH FIX KIA HAI =====

    # 1. WhatsApp CALL Rule - "whatsapp pe Ali ko call kar"
    if "whatsapp" in low and "call" in low:
        tmp = low.replace("whatsapp pe","").replace("whatsapp","").replace("ko call","").replace("call kar","").replace("call","").replace("ko","").strip()
        matched = get_all_contacts_by_name(tmp)
        if matched:
            open_whatsapp_chat(matched[0]['number'])
            speak(f"{matched[0]['name']} ki WhatsApp chat khol di hai, call ka button aap dabayen Sir Osaf Ali")
        else:
            speak(f"{tmp} ka number nahi mila Sir Osaf Ali")
        continue

    # 2. WhatsApp MESSAGE LIKHNA Rule - "Ali ko message likho hello" / "whatsapp pe Ali ko message likho hello"
    # Isme sirf likhega, send user karega
    if ("message" in low or "likho" in low) and ("ko" in low or "whatsapp" in low):
        # message ka text nikalo
        msg_text = ""
        name_part = low
        if "message likho" in low:
            parts = low.split("message likho")
            name_part = parts[0]
            msg_text = parts[1] if len(parts)>1 else ""
        elif "likho" in low:
            parts = low.split("likho")
            name_part = parts[0]
            msg_text = parts[1] if len(parts)>1 else ""
        elif "message" in low:
            parts = low.split("message")
            name_part = parts[0]
            msg_text = parts[1] if len(parts)>1 else ""

        # name saaf karo
        for w in ["whatsapp pe","whatsapp","ko","message","likho","kar","pe"]:
            name_part = name_part.replace(w,"")
        name_part = name_part.strip()
        msg_text = msg_text.replace("kar","").strip()
        if not msg_text: msg_text = "Hi"

        matched = get_all_contacts_by_name(name_part)
        if matched:
            open_whatsapp_chat_with_message(matched[0]['number'], msg_text)
            speak(f"{matched[0]['name']} ke liye message likh diya hai, send aap karen Sir Osaf Ali")
        else:
            speak(f"{name_part} ka number nahi mila Sir Osaf Ali")
        continue

    # 3. NUMBER NIKAL Rule (Unified) - WhatsApp + Normal
    if "number" in low or "contact" in low:
        is_whatsapp = "whatsapp" in low
        name = low
        for w in ["whatsapp pe","whatsapp","ka number nikal","ka number","number nikal","number dhundo","number","contact nikal","contact","nikal","ka","pe","ko"]:
            name = name.replace(w,"")
        name = name.strip()
        if not name: continue
        matched = get_all_contacts_by_name(name)
        if matched:
            if is_whatsapp:
                # WhatsApp bola to chat kholo
                open_whatsapp_chat(matched[0]['number'])
                speak(f"{matched[0]['name']} ki WhatsApp chat khol di Sir Osaf Ali")
            else:
                # Normal bola to dialpad
                open_dialer_with_number(matched[0]['number'])
                speak(f"{matched[0]['name']} ka number dialpad pe laga diya Sir Osaf Ali")
        else:
            speak(f"{name} ka number nahi mila Sir Osaf Ali")
        continue

    if "youtube" in low:
        q = low.replace("youtube pe","").replace("youtube","").replace("search kar","").replace("khol","").strip()
        open_native("youtube", q); speak(f"YouTube pe {q} search Sir Osaf Ali"); continue
    if "tiktok" in low: open_native("tiktok"); speak("TikTok khol diya Sir Osaf Ali"); continue
    if "whatsapp" in low and len(low.strip()) < 20: open_native("whatsapp"); speak("WhatsApp khol diya Sir Osaf Ali"); continue

    ans = jawab_do(cmd)
    speak(ans)
