import csv
import string
from pytube import YouTube
import enchant

def extract_captions(max, only_common_words=False):
    common_words = []
    if only_common_words:
        with open("common_words.csv") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                common_words.append(row['word'])
    
    res = {}
    with open("dynamic_signs/video_ids.txt") as video_ids:
        i = 0
        for video_id in video_ids.readlines():
            if i >= max:
                break
            yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
            try:        
                yt.bypass_age_gate()
            except:
                continue
            
            keys = []
            for key in yt.captions.keys():
                if key is None:
                    continue
                key = key.code
                if 'en' in key or 'ase' in key:
                    keys.append(key)
            
            if keys == []:
                continue

            length = 0
            current_key = ""
            for key in keys:
                caption = yt.captions[key]
                current_key = key if length < len(caption.json_captions) else current_key
                length = len(caption.json_captions)
                
            captions = yt.captions[current_key].json_captions
            
            caption_dict = {}
            for caption in captions["events"]:
                    try:
                        segs = caption['segs']
                    except:
                        continue
                    
                    for seg in segs:
                        text = seg['utf8'].lower().translate(str.maketrans('', '', string.punctuation)) 
                        if text == "" or len(text.split(" ")) > 1:
                            continue
                        
                        d = enchant.Dict("en_US")
                        if (text in common_words or not only_common_words) and d.check(text):
                            time = caption["tStartMs"]
                            try:
                                time = time + seg["tOffsetMs"]
                            except:
                                caption_dict[time] = text

            if len(caption_dict):
                res[video_id] = caption_dict
                i = i+1
    return res
    
def find_common_words(max, min_occurances=3):
    words = {}
    for captions in extract_captions(max).values():
        for caption in captions.values():
            if caption in words:
                words[caption] = words[caption] + 1
            else:
                words[caption] = 1
    with open('common_words.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['word', 'count'])
        writer.writeheader()
        for word, count in words.items():
            if (count >= min_occurances):
                writer.writerow({'word': word, 'count': count})

find_common_words(3, 3)