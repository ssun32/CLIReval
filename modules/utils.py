lcode2analyzer={
    "ar": "arabic",
    "hy":"armenian", 
    "eu":"basque", 
    "bn":"bengali", 
    "bg":"bulgarian", 
    "ca":"catalan", 
    "cs":"czech", 
    "da":"danish", 
    "nl":"dutch", 
    "en":"english", 
    "fi":"finnish", 
    "fr":"french", 
    "gl":"galician", 
    "de":"german", 
    "el":"greek", 
    "hi":"hindi", 
    "hu":"hungarian", 
    "id":"indonesian", 
    "ga":"irish", 
    "it":"italian", 
    "lv":"latvian", 
    "lt":"lithuanian", 
    "no":"norwegian", 
    "fa":"persian", 
    "pt":"portuguese", 
    "ro":"romanian", 
    "ru":"russian", 
    "es":"spanish", 
    "sv":"swedish", 
    "tr":"turkish", 
    "th":"thai", 
    "zh":"smartcn", 
    "ja":"kuromoji",
    "ko":"nori", 
    "pl":"stempel",
    "uk":"ukrainian"
}

def get_analyzer(lcode):
    if lcode not in lcode2analyzer:
        return "standard"
    return lcode2analyzer[lcode]
