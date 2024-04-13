from openai import OpenAI
client = OpenAI()

newpairs = open( "inputs/consider28.txt",  "r" )
existing = open( "wordPairsWithHints.txt", "r" )
output   = open( "newPairsWithHints.txt",  "w" )

def generate_hints( phrase ):
    content = phrase
    completion = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": "You are generating hints for a puzzle. The player of the puzzle must provide a two word phrase. Your job is to give the user a hint.  The hint is a short clue, like a synonym or brief description or meaning of the phrase. The hint cannot include either of the words in the two word pair, nor any variations of those words. For example if the two word phrase is 'time card' you might generate a hint like 'Tracking hours worked with a punchable sheet.' Your hint cannot include either of the word words in the phrase, nor a variation of them like 'timing' cannot be part of a hint for the word 'time'. If there is a phrase that you don't really know or don't think you can give a good hint for, then issue the hint 'NOT SURE' in all caps like that."}, 
        {"role": "user", "content": content}
      ]
    )
    print( phrase, " --- ", completion.choices[0].message.content, end='\n') 
    return str( completion.choices[0].message.content ) + '\n'

pairHash = {}
for p in existing:
    n = p.split('|')
    if len(n) == 3:
        wordPair = n[1]
        hint     = n[2]
        if wordPair not in pairHash:
            pairHash[wordPair] = hint
    else:
        print( "ERROR: ", p )
existing.close

for p in newpairs:
    n = p.split(' ')
    if len(n) == 3:
        if n[2].strip()=="":
            del n[2]
    if len(n) == 2:
        word1 = n[0].lower().strip()
        word2 = n[1].lower().strip()
        wordPair = word1 + " " + word2
        if wordPair not in pairHash:
            hint = str(generate_hints( wordPair ))
            dataout = str(len(hint)) + "|" + wordPair + "|" + hint
            output.write( dataout ) 
        else:
            print( "already had", wordPair )
    else:
        print( "ERROR length = ", str(len(n)), " on ", p, end=''  )

output.close()
newpairs.close()
