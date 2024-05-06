import logging


common_words_english_lower_case = [word.lower() for word in [
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for", "not", "on", "with", 
    "he", "as", "you", "do", "at", "this", "but", "his", "by", "from", "they", "we", "say", "her", "she", 
    "or", "an", "will", "my", "one", "all", "would", "there", "their", "what", "so", "up", "out", "if", "about", 
    "who", "get", "which", "go", "me", "when", "make", "can", "like", "time", "no", "just", "him", "know", 
    "take", "people", "into", "year", "your", "good", "some", "could", "them", "see", "other", "than", "then", 
    "now", "look", "only", "come", "its", "over", "think", "also", "back", "after", "use", "two", "how", 
    "our", "work", "first", "well", "way", "even", "new", "want", "because", "any", "these", "give", "day", 
    "most", "us", "is", "was", "are", "be", "have", "had", "were", "can", "said", "use", "do", "will", 
    "would", "make", "like", "has", "look", "write", "go", "see", "could", "been", "call", "am", "find", 
    "did", "get", "come", "made", "may", "take", "know", "live", "give", "think", "say", "help", "tell", 
    "follow", "came", "want", "show", "set", "put", "does", "must", "ask", "went", "read", "need", "move", 
    "try", "change", "play", "spell", "found", "study", "learn", "should", "add", "keep", "start", "thought", 
    "saw", "turn", "might", "close", "seem", "open", "begin", "got", "run", "walk", "began", "grow", "took", 
    "carry", "hear", "stop", "miss", "eat", "watch", "let", "cut", "talk", "being", "leave", # wiki list ends here
    
    "happy", "okay", "alright","bye","hi","why", "flower","wait","yes","bed","pasta","name","remember","food","cheese","egg","dinner","lunch","banana","apple","breakfast","lunch","juice","hey","gift","animal","sorry","smart","door","j","z","car","sky","wrong","oops","pizza","music","cry","student","child","doctor","church","dad","brother","lazy","old","mad","tomorrow","yesterday","pregnant","college","funeral","law","religion","golf","fishing","bath","clean","math","english","science","fun","funny","money","coronavirus","ghost","spider","smile","junior","senior","goodbye","full","half","drive","buy","cow","lion","trust","kitten","rabbit","hamster","pet","boring","strong","hello","he","be","we","it","in","again","if","j","z","wow","ready" # added by us
    ]
]
# Sourced from https://en.wikipedia.org/wiki/Most_common_words_in_English with some but is generated via bing pilot
