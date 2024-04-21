import json
from openai import OpenAI
client = OpenAI()

output = open( "puzzleQuality.txt", "w" )

# test 0
def find_answer( a, b, c, hint ):
    content = "" + a + " " + c
    completion = client.chat.completions.create(
      model="gpt-4-turbo",
      messages=[
        {"role": "system", "content": "We are going to play a word game. I am going to give you two words which represents two distinct two-word phrases you need to guess. You guess the phrases by inserting one word between the two provided words to create two, commonly known, two-word phrases. For example, if I give you 'talk wave' you would guess 'radio' because inserting radio between talk and wave makes the two-word phrase 'talk radio' and it makes the two word phrase 'radio wave'. In some cases the word you insert can make either, or both, of the given words into a single compound word (with or without a hyphen) instead of a two word phrase. For example, if I give you 'break lane' you could guess 'fast' because it makes the compound word 'breakfast' and the two-word phrase 'fast lane'. You may realize there are multiple solutions, but I want the best solution. If you think there might be more than 1 solution you must pick the one best solution that maximizes the 'American-Undertanding-Score'. The American-Understanding-Score is a number between 1-10 where 10 represents a result where both two word phrases (e.g. 'talk radio' and 'radio wave') are common, well-known phrases in American English and should be known to most people. Score 5 if one of the two-word phrases would not be commonly understood by Americans, or if both phrases would only be understood by a fraction of Americans such as those who are more well-educated or those who have specialized domain knowledge in a certain field. Score 1 if both two word phrases formed are not very common in American English and would not be understood by most Americans or both require specalized domain knowledge.  Your result must be a well-structured | delimited string consisting of the pair of 3 components: the given words|your guess|American-Understanding-Score. For example if I give 'talk wave' and you guess 'radio' and you score that guess as 8 your result would be 'talk wave|radio|8'"},
        {"role": "user", "content": content},
      ]
    )
    #print( content, " --- ", completion.choices[0].message.content, end='\n') 
    return str( completion.choices[0].message.content ) + '\n'

# test 1
def score_answer( a, b, c, hint ):
    content2 = "" + a + " " + c + " answer=" + b
    completion = client.chat.completions.create(
      model="gpt-4",
      messages=[
        {"role": "user", "content": "Now I am going to give you the answer I have thought of already for this puzzle. It might be answer that you already guessed. I want you to return this result in a similar well-structured format including providing an American-Understanding-Score. So if the puzzle were 'eaves kick answer=drop' and if you determined 'eavesdrop' and 'drop kick' combined had an American-Understanding-Score of 9 you would return 'eaves kick|drop|9'"},
        {"role": "user", "content": content2}
      ]
    )
    #print( content, " --- ", completion.choices[0].message.content, end='\n') 
    return str( completion.choices[0].message.content ) + '\n'

# test 2
def score_hint_ab( a, b, c, hint ):
    content3 = "" + a + " " + c + " hint=" + hint
    completion = client.chat.completions.create(
      model="gpt-4",
      messages=[
        {"role": "user", "content": "We are going to play a word game. I am going to give you two words which represents two distinct two-word phrases you need to guess. I will also give you a hint for the first two-word phrase. You guess the phrases by inserting one word between the two provided words to create two, commonly known, two-word phrases. For example, if I give you 'talk wave' and the hint 'broadcasted blabber' you would guess 'radio' because inserting radio between talk and wave makes the two-word phrase 'talk radio' which is a form of 'broadcasted blabber' and it makes the two word phrase 'radio wave'. In some cases the word you insert can make either, or both, of the given words into a single compound word (with or without a hyphen) instead of a two word phrase. For example, if I give you 'break lane' you could guess 'fast' because it makes the compound word 'breakfast' and the two-word phrase 'fast lane'. I want you to consider multiple solutions and find the best solutions. If there is more than one good solution, I want you to make up to 3 guesses. For each guess I want you to compute an American-Understanding-Score for the quality of the hint. The American-Understanding-Score will be between 1-10 where 10 represents a result where the hint for the first two word phrase was very helpful in finding the overall solution and the average American who does not have a specialized vocabulary in a particular field would be able to guess the answer from the given words and hint. If the hint is not helpful for the average American to find the answer score it a 1. The American--Understanding-Score thus is a measure of the hint quality. Your result should also state your reasoning why you scored the hint as you did. The format of results must be a well-structured | delimited string consisting of 5 things: the pair of given words|the hint|your guess|American-Understanding-Score|hint-reasoning of your guess. For example if I give 'peach stop hint=tropical fruit seed' and you guess 'pit' and you score the hint as being a 5 in terms of helpfulness because peaches are not a tropical fruit, your result would be 'peach stop|tropical fruit seed|pit|5|peaches are not a tropical fruit'"},
        {"role": "user", "content": content3}
      ]
    )
    #print( content, " --- ", completion.choices[0].message.content, end='\n') 
    return str( completion.choices[0].message.content ) + '\n'

# test 3
def score_hint_bc( a, b, c, hint ):
    content4 = "" + a + " " + c + " hint=" + hint
    completion = client.chat.completions.create(
      model="gpt-4",
      messages=[
        {"role": "user", "content": "We are going to play a word game. I am going to give you two words which represents two distinct two-word phrases you need to guess. I will also give you a hint for the second two-word phrase. You guess the phrases by inserting one word between the two provided words to create two, commonly known, two-word phrases. For example, if I give you 'baby radio' and the hint 'broadcasted blabber' you would guess 'talk' because inserting talk between baby and radio makes the two-word phrase 'baby talk' and 'talk radio' the latter of which is a form of 'broadcasted blabber'. In some cases the word you insert can make either, or both, of the given words into a single compound word (with or without a hyphen) instead of a two word phrase. For example, if I give you 'break lane' you could guess 'fast' because it makes the compound word 'breakfast' and the two-word phrase 'fast lane'. I want you to consider multiple solutions and find the best solutions. If there is more than one good solution, I want you to make up to 3 guesses. For each guess I want you to compute an American-Understanding-Score for the quality of the hint. The American-Understanding-Score will be between 1-10 where 10 represents a result where the hint for the second two word phrase was very helpful in finding the overall solution and the average American who does not have a specialized vocabulary in a particular field would be able to guess the answer from the given words and hint. If the hint is not helpful for the average American to find the answer score it a 1. The American--Understanding-Score thus is a measure of the hint quality. Your result should also state your reasoning why you scored the hint as you did. The format of results must be a well-structured | delimited string consisting of the pair of 5 things: the given words|the hint|your guess|American-Understanding-Score|hint-reasoning of your guess. For example if I give 'georgia pit hint=tropical fruit seed' and you guess 'pit' and you score the hint as being a 5 in terms of American-Understanding-Score because peaches are not tropical fruit, your result would be 'georgia pit|tropical fruit seed|pit|5|peaches are not a tropical fruit'"},
        {"role": "user", "content": content4}
      ]
    )
    #print( content, " --- ", completion.choices[0].message.content, end='\n') 
    return str( completion.choices[0].message.content ) + '\n'


# Path to the JSONP file
file_path = 'puzzles.js'

# Read the content of the JSONP file
with open(file_path, 'r') as file:
    jsonp_content = file.read()

# Strip the JavaScript variable assignment part (jsonData =) and the surrounding backticks
jsonp_cleaned = jsonp_content.strip().split('=', 1)[1].strip(' `;')

# Parse the JSON part
data = json.loads(jsonp_cleaned)

# Process each puzzle's rows of data
counter = 0
LIMIT = 2000
UPDATE_COUNT = 10
P1_START=0
for puzzle in data:
    #print(f"Puzzle {puzzle['puzzle']} outputs:")
    if counter>LIMIT:
        break
    if counter % UPDATE_COUNT == 0:
        print( "1 of 3 puzzle " + str(counter ) )
    counter = counter + 1
    if counter >= P1_START:
        for row in puzzle['rows']:
            words = row['c']
            hints = row['h']
        
            # Generate trios of adjacent words and their corresponding hints
            for i in range(len(words) - 2):  # Stop before the last two words
                trio = words[i:i+3]  # Select three consecutive words
                hint = hints[i] if i < len(hints) else None  # Get corresponding hint or None
                setup = "setup-" + str(counter) + "|" + trio[0] + " " + trio[1] + " " + trio[2] + " (" + hint + ")\n"
                output.write( setup ) 
                fa = find_answer(trio[0], trio[1], trio[2], hint)
                lines = fa.replace("\r","\n")
                lines = fa.replace("\n\n","\n")
                lines = fa.split("\n")
                for l in lines:
                    if len(l)>1:
                        # test# | input1 | goal | output 
                        s = 't0|' + trio[0] + " " + trio[2] + "|" + trio[1] + "|" + l + "\n" 
                        output.write( s ) 
                sa = score_answer( trio[0], trio[1], trio[2], hint )
                # test# | input1 | output 
                s = 't1|' + trio[0] + " " + trio[2] + "|" + trio[1] + "|" + sa 
                output.write( s )
        

# now lets go through and see how good the A B hints are (Given A _ C and a hint for A B)
counter = 0 
for puzzle in data:
    #print(f"Puzzle {puzzle['puzzle']} outputs:")
    counter = counter + 1
    if counter>LIMIT:
        break
    if counter % UPDATE_COUNT == 0:
        print( "2 of 3 puzzle " + str(counter) )
    for row in puzzle['rows']:
        words = row['c']
        hints = row['h']
        
        # Generate trios of adjacent words and their corresponding hints
        for i in range(len(words) - 2):  # Stop before the last two words
            trio = words[i:i+3]  # Select three consecutive words
            hint = hints[i] if i < len(hints) else None  # Get corresponding hint or None
            setup = "setup-" + str(counter) + "|" + trio[0] + " " + trio[1] + " " + trio[2] + " (" + hint + ")\n"
            output.write( setup ) 
            fa = score_hint_ab(trio[0], trio[1], trio[2], hint)
            lines = fa.replace("\r","\n")
            lines = fa.replace("\n\n","\n")
            lines = fa.split("\n")
            for l in lines:
                if len(l)>1:
                    # test# | input1 | input2 | goal | output 
                    s = 't2|' + trio[0] + " " + trio[2] + "|" + hint + "|" + trio[1] + "|" + l + "\n"
                    output.write(s ) 

# now lets go through and see how good the B C hints are (Given A _ C and a hint for B C)
counter = 0 
for puzzle in data:
    #print(f"Puzzle {puzzle['puzzle']} outputs:")
    counter = counter + 1
    if counter>LIMIT:
        break
    if counter % UPDATE_COUNT == 0:
        print( "3 of 3 puzzle " + str(counter) )
    for row in puzzle['rows']:
        words = row['c']
        hints = row['h']
        
        # Generate trios of adjacent words and their corresponding hints
        for i in range(len(words) - 2):  # Stop before the last two words
            trio = words[i:i+3]  # Select three consecutive words
            hint = hints[i+1] if i < len(hints) else None  # Get corresponding hint or None
            setup = "setup-" + str(counter) + "|" + trio[0] + " " + trio[1] + " " + trio[2] + " (" + hint + ")\n"
            output.write( setup ) 
            fa = score_hint_bc(trio[0], trio[1], trio[2], hint)
            lines = fa.replace("\r","\n")
            lines = fa.replace("\n\n","\n")
            lines = fa.split("\n")
            for l in lines:
                if len(l)>1:
                    # test# | input1 | input2 | goal | output 
                    s = 't3|' + trio[0] + " " + trio[2] + "|" + hint + "|" + trio[1] + "|" + l + "\n"
                    output.write(s ) 

output.close()
