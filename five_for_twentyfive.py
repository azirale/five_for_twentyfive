import timeit
from typing import List
from tqdm import tqdm


# to start timing the entire duration
full_program_start = timeit.default_timer()


# 'all five letter words' -- from ~~wordle~~ :: swapped to same original source as Matt Parker
input_words = []
with open('words_alpha.txt','r') as filereader: ## file from here :: https://github.com/dwyl/english-words
    for line in filereader:
        word = line.strip().lower()
        if len(word) != 5: continue
        input_words.append(word)

print(f"\nGot {len(input_words)} 5-letter words") #> 12497 for wordle ;; 15920 for words_alpha


# words with two of the same letter aren't helpful -- we want 25 from 5 so all letters must be unique within a word
distinct_letter_words = []
for word in input_words:
    if len(set(word))<5:continue
    distinct_letter_words.append(word)

print(f"\nGot {len(distinct_letter_words)} words with no duplicate letters") #> 8310 for wordle ;; 10175 for words_alpha


# remove anagrams -- words that are anagrams of each other provide no benefit, even for searching
# keep just the first one we find
unagram_lookup = {}
for word in distinct_letter_words:
    unagram = ''.join(sorted(word))
    if unagram in unagram_lookup: continue
    unagram_lookup[unagram] = word

print(f"\nGot {len(unagram_lookup)} words excluding anagrams") #> 5176 for wordle ;; 5977 for words_alpha


# swap the unagram lookup back to the actual word picked so it looks sensible
# turn it into a set for better operations later
useful_words = set([word for word in unagram_lookup.values()])


# reference of all letters
all_letters = [l for l in 'abcdefghijklmnopqrstuvwxyz']


# sets of words that contain each letter
words_with_letter = {l:set() for l in all_letters}
for word in useful_words:
    for l in word:
        words_with_letter[l].add(word)

print(f"\nLetter frequencies...")
for l,words in words_with_letter.items():
    print(f" - '{l}' : {len(words)} words")


# what words are still permitted by a given word (no common letters between them)
print("\nGenerating sets of non-conflicting words for each word")
words_permitted_by_word = {}
for word in tqdm(useful_words):
    permitted_words = set(useful_words)
    for l in word:
        permitted_words.difference_update(words_with_letter[l])
    words_permitted_by_word[word] = permitted_words


# ordering words by ascending number of words permitted by them -- faster set operations by doing smaller sets first
ordered_words = sorted([word for word in useful_words],key=lambda word: len(words_permitted_by_word[word]) )

# index lookup by word for easy and obvious reordering after set operations
word_index = {w:i for i,w in enumerate(ordered_words)}




# recursively search for new words given currently permitted words and the sequence of words being used
def recursive_permitted_words(existing_permitted_words:set,word_combo:List[str]):
    new_word = word_combo[-1]
    new_permitted_words = existing_permitted_words.intersection(words_permitted_by_word[new_word])
    # if nothing is left immediately return an empty list -- no possible complete results
    if len(new_permitted_words) == 0:
        return []
    # if the word combination has 4 words already then anything we found in the still permitted set is a valid 5th word
    # skip any final word earlier in the ordered list -- it would have been added previously
    if len(word_combo)==4:
        return [ word_combo+[last_word] for last_word in new_permitted_words if word_index[last_word]>word_index[new_word] ]
    # otherwise we loop through our remaining permitted words to gather more results
    # from our permitted words we pick out only those that are forward in the search order
    # -- anything earlier in the search order is already handled in a prior search, because we always search in the same order
    # we also sort the list to maintain that searching order, and also to go through the smallest combinations first
    # -- smallest combo first means we can knock out as many search words as possible as fast as possible
    # -- this reduces the size of the overall search set
    filtered_permitted_words = [permitted_word for permitted_word in new_permitted_words if word_index[permitted_word]>word_index[new_word]]
    sorted_permitted_words = sorted(filtered_permitted_words, key=lambda x: word_index[x])
    # generate results with recursive call on sorted list of remaining permitted words
    results = []
    for new_word in sorted_permitted_words:
        results.extend(recursive_permitted_words( new_permitted_words, word_combo+[new_word]))
    return results


# loop through the ordered words as initial seed words and use recursive function to search through all valid combinations from that seed word
print("Searching for five words with twentyfive unique letters...")
all_results = []
seed_permitted_words = set(useful_words)
#for i,seed_word in enumerate(ordered_words):
for seed_word in tqdm(ordered_words):
    # strip this seed word from permitted seed words -- now that we have it as seed we will not need it again
    seed_permitted_words.remove(seed_word)
    # now do the recursive search with this seed word
    results = recursive_permitted_words(seed_permitted_words,[seed_word])
    # add to our overall collected results
    all_results.extend(results)
    pass


# ordering and forward-only searching/filtering should make all results unique
print(f"\nGot {len(all_results)} results...")
for result in sorted([sortedresult for sortedresult in [sorted(result) for result in all_results]]):
    print(f" : {'-'.join(sorted(result))}")
    pass


full_program_end = timeit.default_timer()
elapsed_time = full_program_end-full_program_start
print(f"\nEntire process took {elapsed_time:.0f}s")
