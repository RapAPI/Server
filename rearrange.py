import re
import pronouncing
from random import shuffle

def parse_cmu(cmufh):
    """Parses an incoming file handle as a CMU pronouncing dictionary file.
        Returns a list of 2-tuples pairing a word with its phones (as a string)"""
    pronunciations = list()
    for line in cmufh:
        line = line.strip()
        if line.startswith(';'): continue
        word, phones = line.split("  ")
        word = re.sub(r'\(\d\)$', '', word.lower())
        phones_list = phones.split(" ")
        pronunciations.append((word.lower(), phones))
    return pronunciations 

pronunciations = parse_cmu(open('cmudict-0.7b'))

def syllable_count(phones):
    return sum([phones.count(i) for i in '012'])

def phones_for_word(find):
    """Searches a list of 2-tuples (as returned from parse_cmu) for the given
        word. Returns a list of phone strings that correspond to that word."""
    matches = list()
    for word, phones in pronunciations:
        if word == find:
            matches.append(phones)
    return matches

def rhyming_part(phones):
    """Returns the "rhyming part" of a string with phones. "Rhyming part" here
        means everything from the vowel in the stressed syllable nearest the end
        of the word up to the end of the word."""
    idx = 0
    phones_list = phones.split()
    for i in reversed(range(0, len(phones_list))):
        if phones_list[i][-1] in ('1', '2'):
            idx = i
            break
    return ' '.join(phones_list[idx:])

def search(pattern):
    """Searches a list of 2-tuples (as returned from parse_cmu) for
        pronunciations matching a given regular expression. (Word boundary anchors
        are automatically added before and after the pattern.) Returns a list of
        matching words."""
    matches = list()
    for word, phones in pronunciations:
        if re.search(r"\b" + pattern + r"\b", phones):
            matches.append(word)
    return matches

def rhymes(word):
    """Searches a list of 2-tuples (as returned from parse_cmu) for words that
        rhyme with the given word. Returns a list of such words."""
    all_rhymes = list()
    all_phones = phones_for_word(word)
    for phones_str in all_phones:
        part = rhyming_part(phones_str)
        rhymes = search(part + "$")
        all_rhymes.extend(rhymes)
    return [r for r in all_rhymes if r != word]

def wordsRhyme(strWordA, strWordB):
    rhymes_A = pronouncing.rhymes(strWordA)
    for rhyming_word in rhymes_A:
        if rhyming_word == strWordB:
            return True
    return False


def groupingAlgorithm(arrstrVerses):
    arrtupVerses = []
    arrUnmatchedVerses = []
    arrstrFinalLyrics = []
    i = 0
    while (i < len(arrstrVerses)):
        if (i + 1) < len(arrstrVerses):
            wordA = arrstrVerses[i].split()[-1]
            wordB = arrstrVerses[i + 1].split()[-1]
            if wordsRhyme(wordA, wordB):
                t = arrstrVerses[i], arrstrVerses[i + 1]
                arrtupVerses.append(t)
                i = i + 2
            else:
                arrUnmatchedVerses.append(arrstrVerses[i])
                i = i + 1
        else:
            arrUnmatchedVerses.append(arrstrVerses[i])
            i = i + 1
    shuffle(arrtupVerses)
    for pair in arrtupVerses:
        arrstrFinalLyrics.append(pair[0])
        arrstrFinalLyrics.append(pair[1])

    for verse in arrUnmatchedVerses:
        arrstrFinalLyrics.append(verse)

    return arrstrFinalLyrics

def rearrange_text(stdin):
    import sys, operator;

    word_group = list()
    line_lengths = list()
    for line in stdin:
        line = line.strip()
        words = line.split()
        word_group.append(words)
        line_lengths.append(len(words))
        print(words)
    median_line_length = sorted(line_lengths)[int(len(sorted(line_lengths))/2)]

    print("Median Line Lenght", median_line_length)

    print("Pre-split line count", len(word_group))

    w = 0
    while w < len(word_group):
        words = word_group[w]
        if len(words) > 5/3 * median_line_length:
            new_line_first = list(words[:int(len(words)/2)])
            new_line_second = list(words[int(len(words)/2):])
            word_group[w] = new_line_first
            #w -= 1
            if(w == len(word_group)):
                word_group.append(new_line_second)
                continue
            word_group.insert(w+1, new_line_second)
            continue
        w+=1
            
    print("post-split line number", len(word_group))

    rhymes_list = dict()
    line_num = 0
    text = list()
    rubbish = list()
    for words in word_group:
        if (len(words) < 1 or len(phones_for_word(words[-1])) < 1):
            continue
        #print(phones_for_word(words[-1]))
        #raw_text = raw_text_file.readlines()
        ph = phones_for_word(words[-1])[0]
                
        phones_list = rhyming_part(ph).split(' ')
        if(rhymes_list.get(''.join(list(reversed(phones_list)))) == None):
            rhymes_list[''.join(list(reversed(phones_list)))] = list()
        rhymes_list[''.join(list(reversed(phones_list)))].append(line_num)
        print(line_num, ' '.join(words))
        line_num += 1
        text.append(' '.join(words))
        #print (list(reversed(phones_list)))

    #helper = [(key, len(rhymes_list[key])) for key in rhymes_list.keys()]
    #helper.sort(key=lambda x: x[1])
    #print(rhymes_list[helper[0][0]])
    #print(sorted((rhymes_list), key=operator.itemgetter(1, 2, 3, 4)))
    #print(sorted((rhymes_list)))
    print(list(sorted((rhymes_list))))
    values = list(sorted((rhymes_list)))
    line_order = list()
    for v in values:
        for r in rhymes_list[v]:
            line_order.append(r)
    print(line_order)
    print(len(line_order))

    output_text = list()
    for l in line_order:
        output_text.append(text[l])

    print(output_text)

    output_text += rubbish

    print('\n'.join(output_text))
    print('\n')

    output_text = [s for s in output_text if len(s) > 0]
    output_text = groupingAlgorithm(output_text)

    print('\n'.join(output_text))
    return output_text
