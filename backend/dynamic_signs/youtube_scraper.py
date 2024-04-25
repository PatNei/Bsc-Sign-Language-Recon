import csv
import json
from pathlib import Path
import shutil
import string
import sys
from pytube import YouTube
import enchant
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from dynamic_signs.landmark_extractor import DynamicLandmarkExtractor
import re

class YouTubeScraper():
    num_hands: int

    def __init__(self,common_words_path_csv:Path, text_id_path:Path, common_words_path_txt=Path('dynamic_signs/common_words.txt'), num_hands=1) -> None:
        self.text_id_path = text_id_path
        self.common_words_path_csv = common_words_path_csv
        self.common_words_path_txt = common_words_path_txt
        self.num_hands = num_hands

    def get_video_signs(self, max=0, seconds_per_clip=1):
        dynamic_landmark_extractor = DynamicLandmarkExtractor(out_path="dynamic_signs/new_youtube.csv",num_hands=self.num_hands)
        captions = self.extract_captions(max=max, only_common_words=True).items()
        if max == 0:
            max = len(captions)
        i = -1
        for video_id, captions in captions:
            i = i + 1
            print(f"Step 2: {round(i / max * 100, 2)}%")
            yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
            video = yt.streams.get_highest_resolution()
            if video is None:
                continue
            try:
                video.download(output_path=f"dynamic_signs/videos/{video_id}", filename=f"{video_id}.mp4")
            except:
                continue
            
            for start_time, text in captions.items():
                with open(f"./dynamic_signs/videos/{video_id}/{text}.mp4", "w") as clip:
                    ffmpeg_extract_subclip(f"./dynamic_signs/videos/{video_id}/{video_id}.mp4", start_time / 1000, start_time / 1000 + seconds_per_clip, targetname=clip.name)
                    dynamic_landmark_extractor.process_video_frames(text, video_id, base_path=f"./dynamic_signs/videos/{video_id}/", video_path=clip.name)
            shutil.rmtree(f"./dynamic_signs/videos/{video_id}")

    def extract_captions(self, max=0, only_common_words=False):
        cap_num_of_words = max != 0
        common_words = []
        if only_common_words:
            with open(self.common_words_path_csv) as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    common_words.append(row['word'])
        
        res = {}
        i = -1
        with open(self.text_id_path) as video_ids:
            lines = video_ids.readlines()
            if not cap_num_of_words:
                max = len(lines)
            for video_id in lines:
                i = i+1
                print(f"Step 1: {round(i / max * 100, 2)}%")
                video_id = video_id.strip()
                if cap_num_of_words and i >= max:
                    break
                
                yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
                        
                try:        
                    yt.bypass_age_gate()
                    title = yt.title.lower()
                    desc = yt.description.lower()
                    keywords = "".join(yt.keywords).lower()
                    is_asl = "asl" in title or "american" in title or "asl" in desc or "american" in desc or "asl" in keywords or "american" in keywords


                    # Don't download videos with a length of more than 15 minutes
                    if yt.length > 15 * 60 or not is_asl:
                        continue
                except:
                    continue
                
                if "auto" in str(yt.captions.keys()):
                    continue

                keys = []
                for key in yt.captions.keys():
                    if key is None:
                        continue
                    key = key.code
                    if ('en' in key or 'ase' in key) and 'asr' not in key:
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
                            if not re.match(r"^[a-zA-Z]+$", text) or len(text.split(" ")) > 1:
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
        return res
        
    def find_common_words(self, max=0, min_occurances=3):
        words = {}
        for video_id, captions in self.extract_captions(max=max, only_common_words=False).items():
            for time, caption in captions.items():
                clip = (video_id, time)
                if caption in words:
                    existing = words[caption]
                    clips = existing["clips"]
                    count = existing["count"]
                    clips.append(clip)
                    words[caption] = dict(count=count + 1, clips=clips)
                else:
                    words[caption] = dict(count=1, clips=[clip])
        

        with open(self.common_words_path_csv, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['word', 'count', 'clips'])
            writer.writeheader()
            for word, info in words.items():
                clips = ""
                for clip in info["clips"]:
                    clips += f"{clip[0]}:{clip[1]}#"
                if (info["count"] >= min_occurances):
                    writer.writerow({'word': word, 'count': info["count"], 'clips': clips[:-1]})
                    
    def write_common_words(self):
        with open(self.common_words_path_csv, 'r') as common_words:
            with open(self.common_words_path_txt, 'w') as common_words_txt:
                reader = csv.DictReader(common_words)
                res = ""
                for row in reader:
                    word = row["word"]
                    clips = row["clips"]
                    res = res + f"{word}?{clips},"
                common_words_txt.write(res[:-1])

if __name__ == "__main__":
    yt = YouTubeScraper(Path("dynamic_signs/common_words_new.csv"), Path("dynamic_signs/video_ids.txt"), num_hands=2)
    yt.find_common_words(min_occurances=100, max=0)
    yt.get_video_signs(max=0, out_path="youtube_with_asl_in_title.csv",seconds_per_clip=1)
    # yt.get_video_signs(max=0,seconds_per_clip=1)
    # yt.find_common_words(min_occurances=50, max=0)
    # yt.find_common_words(min_occurances=0, max=20)
    # yt.write_common_words()
