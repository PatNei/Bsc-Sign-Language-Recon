import json
from pytube import YouTube

with open("dynamic_signs/video_ids.txt") as video_ids:
    for video_id in video_ids.readlines():
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
        
        caption_list = []
        
        for caption in captions["events"]:
            try:
                text = caption['segs'][0]['utf8']
                if len(text.split(" ")) > 1:
                    continue
                print(text)
                caption_list.append(caption)
            except:
                continue
        
        # print(captions)
        # break
        # if video_details is None:
        #     continue
        # print(video_details.keys())
        # print(video_details.get("title") or "")