import nltk
import re

# Ensure NLTK tokenizers are available
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/wordnet')
    nltk.data.find('corpora/wordnet')
    nltk.data.find('taggers/averaged_perceptron_tagger') # Needed for robust word tokenization in some cases
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)

from nltk.tokenize import sent_tokenize, word_tokenize

def count_syllables_heuristic(word):
    word = word.lower()
    if not word:
        return 0
    
    # Remove non-alphabetic characters at the end (e.g., punctuation)
    word = re.sub(r'[^a-z]+$', '', word)
    if not word: # if word becomes empty after stripping non-alpha
        return 0

    if len(word) <= 3 and word not in ['ion', 'ism']: # Short words are usually 1 syllable
        if re.search(r'[aeiouy]', word): # check if it has any vowel
             return 1
        else: # for words like 'rhythm' or 'gym'
             if 'y' in word: return 1 # treat y as vowel if no other vowel
             return 0 # should not happen for English words if pre-filtered

    syllable_count = 0
    vowels = "aeiouy"
    
    # 1. Count vowel groups
    if word[0] in vowels:
        syllable_count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index-1] not in vowels:
            syllable_count += 1
            
    # 2. Handle silent 'e' at the end
    if word.endswith("e") and syllable_count > 1 and word[-2] not in vowels and not word.endswith("le"): # 'le' can be a syllable like 'apple'
        syllable_count -= 1
    elif word.endswith("le") and len(word) > 2 and word[-3] not in vowels and word[-3] not in 'scz': # simple, apple vs sizzle
        # if 'le' is preceded by a consonant (not s,c,z which often make 'le' part of prior syllable) it might form its own
        pass # often 'le' forms a syllable, e.g. 'apple', 'simple'
        
    # 3. Handle specific endings
    if word.endswith("ed") and syllable_count > 1: # e.g. "jumped" (1) vs "needed" (2)
        # A more complex rule would check the preceding consonant sound
        # For simplicity, we might overcount here, or accept current count
        pass
    if word.endswith("es") and syllable_count > 1:
        # e.g. "cases" (2) vs "makes" (1)
        pass
        
    # Diphthongs and triphthongs are already handled by vowel grouping (e.g., "beautiful" -> eau counts as one group)

    # Minimum 1 syllable for any actual word.
    if syllable_count == 0 and len(word) > 0: # e.g. "rhythm"
        syllable_count = 1
        
    return syllable_count

def calculate_fog_index(text_content):
    # Remove Markdown image links and existing Fog Index line for calculation
    text_to_analyze = re.sub(r"!\[.*?\]\(.*?\)", "", text_content)
    text_to_analyze = re.sub(r"Readability - Gunning Fog Index:.*", "", text_to_analyze)
    text_to_analyze = re.sub(r"#+ .*", "", text_to_analyze) # Remove markdown headings
    text_to_analyze = text_to_analyze.strip()

    if not text_to_analyze:
        return 0

    sentences = sent_tokenize(text_to_analyze)
    words = [word for sentence in sentences for word in word_tokenize(sentence) if re.match(r'[a-zA-Z]+', word)] # Keep only actual words

    if not sentences or not words:
        return 0

    num_sentences = len(sentences)
    num_words = len(words)
    
    average_sentence_length = num_words / num_sentences
    
    complex_words_count = 0
    for word in words:
        syllables = count_syllables_heuristic(word)
        if syllables >= 3:
            complex_words_count += 1
            
    percentage_complex_words = (complex_words_count / num_words) * 100 if num_words > 0 else 0
    
    fog_index = 0.4 * (average_sentence_length + percentage_complex_words)
    
    # For debugging counts:
    # print(f"Num Sentences: {num_sentences}")
    # print(f"Num Words: {num_words}")
    # print(f"Avg Sentence Length: {average_sentence_length}")
    # print(f"Complex Words: {complex_words_count}")
    # print(f"Percentage Complex Words: {percentage_complex_words}")
    
    return fog_index

if __name__ == "__main__":
    markdown_filepath = "docs/Tesla_Case_Analysis.md"
    
    with open(markdown_filepath, 'r', encoding='utf-8') as f:
        original_content = f.read()

    # Remove the placeholder before calculating
    content_for_fog_calculation = original_content.replace("Readability - Gunning Fog Index: Placeholder", "")

    fog_value = calculate_fog_index(content_for_fog_calculation)
    
    # Replace the placeholder with the calculated value
    final_content = original_content.replace("Readability - Gunning Fog Index: Placeholder", f"Readability - Gunning Fog Index: {fog_value:.2f}")
    
    with open(markdown_filepath, 'w', encoding='utf-8') as f:
        f.write(final_content)
        
    print(f"Fog Index calculated: {fog_value:.2f}")
    print(f"Markdown file updated: {markdown_filepath}")
