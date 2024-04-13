import re
import random
import json
from itertools import product

all_pairs = {}         # all the two-word pairs we have
all_hints = {}         # the hint for each pair of words
unique_trios = {}      # all unique three-word cores (cols 2,3,4) as keys mapped to their combined word frequency as the value
minTrioFreqSum = 99999
maxTrioFreqSum = -9999
word_freq = {}         # what is the frequency of the each word in the accepted list?
pair_freq = {}         # how often is each pair used in a puzzle?

JOIN        = "after" # used in game1, join style, if set to 'after', then requires the next word to follow the current word
MIN_SUBS    = 1       # used in game2, minimum # of substituable words for the first and last word
MIN_CHARS   = 3
PATH_LENGTH = 5

isFirstOutput = 1     # because retarted json parsing doesn't like a trailing comma in a list
random.seed(2304875)  # seed the random number generator 

#p = re.compile('^([^ ]+) {1}([^ ]+)$')
pair_data  = open("wordPairsWithHints.txt", "r") # all our word paris and their hints

# track some statistics
wordInTrioCount = {}   # how often a word appears in a trio (potential puzzle)
wordInPuzzleCount = {} # how often a word appears in a puzzle 
pairInPuzzleCount = {} # how often a pair appears in a puzzle

# write our outputs
word_stats = open( "wordStats.txt", "w")  # frequency of words used in trios 
puzz_out   = open( "puzzles.js",    "w")  # actual puzzle data
puzz_rej   = open( "rejected_puzzles.txt", "w" ) # puzzles we threw out at the end
pair_stats = open( "pairStats.txt", "w")  # frequency of pairs used in puzzles

def dumpDict( d,ftw ):
    for key in d:
        #ftw.write( m ) 
        l = d[key]
        for i in l:
            x = key + ' ' + i + "\n"
            ftw.write( x ) 

#
# game2
# use this to find multiple words connected to each other in a path
# e.g. baby talk, talk radio, radio wave, wave goodbye
# in game2 we only allow the "AFTER" join so a pair like 'baby talk' is 
# only baby talk, not talk baby as well.
#
# for each word, find all paths that are n deep 
# add each new word into workingList
# do not allow a repeat within workingList
#
# we are building the list of words along with a list of substitute words
# for the first and last words in the list. so in practice if we want a list
# of length 5, we do this depthSearchGame2 to build a list of 3, then we 
# create a list of substituable words that can precede the first and a list
# that can follow the last word in the list. 
#
#
def depthSearchGame2( dict, maxLevel, workingList ):
    global maxTrioFreqSum
    global minTrioFreqSum
    if len(workingList) == maxLevel:
        wlCopy = [ workingList[1].replace("_",""), workingList[2].replace("_",""), workingList[3].replace("_","") ]

        # we have a 5 word long path, but now we need to make sure the ends can have at
        # least one more valid clue

        # find the substitutions for the last word in the path
        penultimate = workingList[maxLevel-2] 
        subpen = dict[penultimate.replace("_","")]
        properLastSubs = []
        for w in subpen:
            if( w[0]=="_"):
                properLastSubs.append( w.replace("_","") ) 

        # find the substitutions for the first word in the path
        second = workingList[1] 
        subsec = dict[second.replace("_","")]
        properFirstSubs = []
        for w in subsec:  # we interpret the 'after' join type in opposite way vs above
            if( w[len(w)-1]=="_"):
                properFirstSubs.append( w.replace("_","") ) 
        
        # write it out to the file as long as the firstSubs and lastSubs both have at least 3 words each (original + 2 subs)
        if "eager" in wlCopy:
            xx = "got a path with eager " + str( workingList ) + "\n" 
            puzz_rej.write( xx ) 
        if( len( properLastSubs ) >= MIN_SUBS and len( properFirstSubs ) >= MIN_SUBS ):
            if "eager" in wlCopy:
                xx = "\t it survived " + str(workingList) + "\n" 
                puzz_rej.write( xx )
            uniqTri = workingList[1].replace("_","") + "/" + workingList[2].replace("_","") + "/" + workingList[3].replace("_","")  # not ideal assumes length 5, fix later
            if uniqTri not in unique_trios:
                # compute the total word frequency value of this trio THIS RIGHT HERE
                freq = word_freq[workingList[1].replace("_","")] + word_freq[workingList[2].replace("_","")] + word_freq[workingList[3].replace("_","")]
                unique_trios[uniqTri] = freq
                if freq>maxTrioFreqSum:
                    maxTrioFreqSum = freq
                if freq<minTrioFreqSum:
                    minTrioFreqSum = freq

        return  # move on to the next 
    
    lastWord = workingList[len(workingList)-1]
    l = dict[lastWord.replace("_","")]
    for i in l:
        newWord = i
        if len(newWord.replace("_","")) >= MIN_CHARS:
            # if we have restricted join type to "after" the new word has to have _ as first char
            if( JOIN == "after" and newWord[0]=="_") or ( JOIN != "after" and len(newWord) != len(newWord.replace("_",""))):
                # ensure we don't already have this word in either join type
                # e.g. can't have _system and system_
                reject = 0
                for x in workingList:
                   if newWord.replace("_","") == x.replace("_",""):
                       reject = 1
                if( reject == 0 ):
                    workingList.append( newWord ) 
                    depthSearchGame2( dict, maxLevel, workingList ) 
                    workingList.pop()



# if the key w doesn't exist in dictionary d
# then create it and set it to 1. if it already
# exists in the dictionary, increment its count
def incrementWordCount( d, w ):
    if( w not in d):
        d[w] = 1
    else:
        n = d[w]
        d[w] = (n+1)

# ensure it exists as a key and set to zero
# otherwise no change
def noopWordCount( d, w ):
    if( w not in d):
        d[w] = 0

def getPairs( dict, word, join, maxWords, avoidWords ):
    mylist = dict[word.replace("_","")]
    options = []
    for w in mylist:
        if( w[0]=="_" and join == 'post'):
            options.append( w.replace("_",""))
        if( w[len(w)-1]=="_" and join == 'pre'):
            options.append( w.replace("_",""))

    #print("initial options for ", word, " join=", join, " are ", options )
    # get the frequency of each word
    wordMap = {}
    for w in options:
        f = word_freq[w]
        wordMap[w] = f

    # now sort the wordMap by the frequency and return up to maxWords
    sortedWords = sorted( wordMap.items(), key=lambda x:x[1])

    #if( w.replace("_","") == "over" and join == 'pre' ):
    #print( "for ", word, " join=", join, " sorted word options are: ", sortedWords )

    topOptions = []
    for i in range( 0, min( 10, len(sortedWords)) ):
        topOptions.append( sortedWords[i][0] )

    if( len(topOptions) <= maxWords ):
        #print("returning early, topOptions ", topOptions )
        return topOptions

    # if we have enough other words, remove words that are super high frequency
    prunedOptions = [] 
    overage = len(topOptions) - maxWords
    for c in topOptions:
        if avoidWords and contains_specific_values( [c], avoidWords ) and overage > 1:
           overage = overage - 1
        elif contains_specific_values( [c] ) and overage > 1:
           overage = overage - 1
        else:
           prunedOptions.append(c)

    finalOptions = {}
    safety_counter = 0
    while( len( finalOptions ) < maxWords and safety_counter<50 ):
        r = int( random.random() * len( prunedOptions ) -1 ) 
        choice = prunedOptions[r]
        finalOptions[ choice ] = r
        safety_counter = safety_counter + 1

    if safety_counter > 48:
        print( "exited via safety_counter=", safety_counter )

    #print("final options for ", word, " are ", finalOptions )
 
    fk = list( finalOptions.keys() )
    if contains_specific_values( [ fk[0] ], avoidWords):
        return rotate_list( fk )
    else:
        return fk

def rotate_list( lst ):
    if not lst:  # Check if the list is empty
        return []
    return [lst[-1]] + lst[:-1]

def randomly_sort_list(input_list):
    shuffled_list = input_list[:]  # Make a copy to avoid modifying the original list
    random.shuffle(shuffled_list)
    return shuffled_list

def contains_specific_values( input_str_array, specific_values= { "back", "over", "down", "fall", "water", "line", "hand", "out" } ):
    return any(part in specific_values for part in input_str_array )

def differs_by_one_part(str1, str2):
    # Split both strings into parts
    parts1 = str1.split('/')
    parts2 = str2.split('/')
    # Ensure both strings are of the correct form
    if len(parts1) != 3 or len(parts2) != 3:
        return False
    # Count the differences
    differences = sum(1 for p1, p2 in zip(parts1, parts2) if p1 != p2)
    # Check if they differ by exactly one part
    return differences == 1

def optimize(choices):
    # This function aims to find the optimal set of words for each row that minimizes repetition
    
    def all_row_combinations(head, core, tail):
        # Generate all combinations for a single row given head, core, and tail arrays
        return [([h] + core + [t]) for h in head for t in tail]
    
    # Generate all possible row combinations for each of the choice sets
    all_choices_combinations = [all_row_combinations(choice[0], choice[1], choice[2]) for choice in choices]

    # Generate all possible combinations of rows
    all_possible_combinations = list(product(*all_choices_combinations))

    # Initialize the best combination (minimize repetition) and its score (number of unique words)
    best_combination = None
    best_score = 0

    # Evaluate each combination to find the one with the most unique words (minimizing repetition)
    for combination in all_possible_combinations:
        # Flatten the combination into a single list and count unique words
        combined_words = sum(combination, [])
        unique_word_count = len(set(combined_words))

        # Update best combination if this one has more unique words
        if unique_word_count > best_score:
            best_combination = combination
            best_score = unique_word_count

    # Return the best combination found
    if best_score == 15:
        return best_combination
    return []

def puzzle_to_json(puzzle):
    x = ""
    count = 0 
    for r in puzzle:
        h12 = all_hints[ r[0] + " " + r[1] ] # hint between words 1 and 2
        h23 = all_hints[ r[1] + " " + r[2] ] 
        h34 = all_hints[ r[2] + " " + r[3] ] 
        h45 = all_hints[ r[3] + " " + r[4] ] 
        hints = [ h12, h23, h34, h45]
        hintsJSON = json.dumps( hints )
        rowJSON   = json.dumps( r )
        for rr in r:
            incrementWordCount( wordInPuzzleCount, rr )
        # Increment word pair count
        for i in range(len(r) - 1):
            word_pair = r[i] + " " + r[i+1]
            incrementWordCount( pairInPuzzleCount, word_pair )

        comma = ","
        if count == 0:
            comma = " "
        count = count + 1
        x = x + "    " + comma + "{ \"c\": " + rowJSON + ", \"h\":" + hintsJSON + " }\n"
    return x

# read in the word pair dictionary
for a in pair_data:
    parts = a.split("|")
    if( len( parts ) == 3 ):
        hintlength = parts[0]
        words = parts[1].split(" ");
        w1 = words[0].strip().lower()
        w2 = words[1].strip().lower()
        hint = parts[2].strip()
        bigram = w1 + " " + w2  # create a fully normalized key
        pairInPuzzleCount[bigram] = 0
        all_hints[bigram] = hint # store the hint for retrieval by the word pair
        #print( "w1=", w1, " w2=", w2, " all_hints[", bigram, "]=", all_hints[bigram] )
        if w1 not in all_pairs:
            all_pairs[w1] = []
        all_pairs[w1].append("_"+w2)
        incrementWordCount( word_freq, w1 )

        if w2 not in all_pairs:
            all_pairs[w2] = []
        all_pairs[w2].append(w1+"_")
        incrementWordCount( word_freq, w2 )

s = len(all_pairs)
c = 0

for k in all_pairs:
    wl = []
    startWord = k.replace("_","")
    if len(startWord)>=MIN_CHARS:
        wl.append(startWord)
        depthSearchGame2( all_pairs, PATH_LENGTH, wl)


print("size of unique_trios: ", str(len(unique_trios )))
#
# create the actual puzzles
# 
puzzles = []
skipped_puzzles = []


tcount = 0
pcount = 0 
withBad = {}
notWithBad = {}

puzz_rej.write("========================\n\nstart building puzzles\n\n==============================\n")

for t in unique_trios: # iterate over all trios
    tcount=tcount+1
    words = t.split('/')
    # track some statistics
    for x in words:
        incrementWordCount( wordInTrioCount, x )

    if( tcount % 500 == 0):
        print( tcount, " trios processed ", pcount, " puzzles made" ) 

    pres  = {} # trios that can precede the selected trio t
    posts = {} # trios that can follow  the selected trio t

    for ap in unique_trios: # iterate over all trios (ap)
        iw = ap.split('/') # for each Trio, get the individual words (iw)

        firstLeaders = all_pairs[iw[0]]
        secondLeaders = all_pairs[iw[2]]
        a = "_" + words[0] 
        b = "_" + words[2] 
        if a in firstLeaders and b in secondLeaders and iw[2] != words[1] and iw[1] != words[0]:
            pres[ap] = unique_trios[ap] # add to the list of possible preceding trios, mapped to its freq score

        firstFollowers = all_pairs[iw[0]]
        secondFollowers = all_pairs[iw[2]]
        x = words[0] +"_"
        y = words[2] +"_"
        if x in firstFollowers and y in secondFollowers and iw[0] != words[1] and iw[1] != words[2]:
            posts[ap] = unique_trios[ap] # add to the list of possible following trios, mapped to its freq score
 
    if len(pres) > 0 and len(posts) > 0:  
        trioWords = t.split('/') # the core 3 words in the middle row
        visibleWords = []

        # the first row,
        sortedPres = sorted( pres.items(), key=lambda x:x[1]) # sort by ? 
        r = int( random.random() * min( 8, len(pres)) ) # pick random from first 8
        firstRow = (sortedPres[r][0]).split('/')
        firstB4  = getPairs( all_pairs, firstRow[0], 'pre', 3, trioWords )
        firstAft = getPairs( all_pairs, firstRow[2], 'post', 3, trioWords )

        # the middle row
        midB4  = getPairs( all_pairs, trioWords[0], 'pre', 3, [] )
        midAft = getPairs( all_pairs, trioWords[2], 'post', 3, [] )
        
        # the last row
        sortedPosts = sorted( posts.items(), key=lambda x:x[1]) # sort by ?
        r = int( random.random() * min( 8, len(sortedPosts)) ) # pick random from first 8
        #print( "picked random ", r, " and select within array of len ", len(sortedPres) )
        lastRow = (sortedPosts[r][0]).split('/')
        lastB4  = getPairs( all_pairs, lastRow[0], 'pre', 3, trioWords )
        lastAft = getPairs( all_pairs, lastRow[2], 'post', 3, trioWords )

        # pick an optimal puzzle (no repeated words)
        choices = [[firstB4, firstRow, firstAft],[midB4, trioWords, midAft], [lastB4, lastRow, lastAft]]
        puzzle = optimize( choices )
        if len(puzzle) != 0:
            #print( "from ", choices, " get puzzle ", puzzle )
            puzzles.append(  puzzle_to_json( puzzle ) )
            pcount = pcount + 1


print( tcount, " trios processed ", pcount, " puzzles made" ) 

puzz_out.write("jsonData = `[\n")
puzzleCount = 0
# "rows": [
#   { "c": "heart/burn/down", "p": ["broken", "lion", "sweet"], "f":["draft", "size", "shift"] },
#   { "c": "break/water/right", "p": ["heart", "coffee", "spring"], "f":["along", "turn", "angle"], "x":103 },
#   { "c": "down/hill/side", "p": ["choke", "narrow", "jot"], "f":["dish", "kick", "stroke"] }


#for k in withBad:
#    wb = withBad[k]
#    nwb = notWithBad[k]
#    prctWB = wb / ( nwb+wb )
#    formatted_prcnt = format( prctWB, '.2f')
#    print( formatted_prcnt, ",", k, ",", str(wb), ",", str(nwb)) 

shuffledPuzzles = randomly_sort_list( puzzles )
for p in shuffledPuzzles:
    if( puzzleCount != 0 ):
        puzz_out.write(",")
    puzz_out.write("{\n")
    l = "  \"puzzle\": " + str(puzzleCount) + ",\n" 
    puzz_out.write( l )
    puzz_out.write( "  \"rows\": [\n" )
    puzzleCount = puzzleCount + 1
    #rows = p.split("|")
    #for r in rows:
    #    puzz_out.write( r )
    puzz_out.write( p )
    puzz_out.write("  ]\n")
    puzz_out.write("}\n" )
puzz_out.write("]`\n")

for p in skipped_puzzles:
    rows = p.split("|")
    puzz_rej.write( "--------\n" )
    for r in rows:
        puzz_rej.write( r )
        puzz_rej.write( "\n" )

#
# output some word statistics
#
word_stats.write( "word\tword count\t# in 2-word phrases\t# as first word\t# as second word\t# in trios\t# in puzzles\n" )
for w in all_pairs:
    witc = 0 
    wipc = 0 
    wipphc = 0 
    leadins = 0
    leadouts = 0

    
    for w2 in l:
        if(w2[0]=='_'):
            leadins = leadins + 1
        else:
            leadouts = leadouts + 1

    if w in wordInTrioCount:
        witc = wordInTrioCount[w]
    if w in wordInPuzzleCount:
        wipc = wordInPuzzleCount[w]
    l = w + "\t1\t" + str(word_freq[w]) + "\t" + str(leadins) + "\t" + str(leadouts) + "\t" + str(witc) + "\t" + str(wipc) + "\t" + str(wipphc) + "\n"
    word_stats.write( l ) 

# output pair statistics

for p in pairInPuzzleCount:
    x = p + "\t1\t" + str(pairInPuzzleCount[p]) + "\t" + "\n"
    pair_stats.write( x )


#
# close all the files
#
puzz_out.close()
word_stats.close()
pair_stats.close()
