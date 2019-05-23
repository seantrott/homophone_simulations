In order to run, download IPHOD data here: http://iphod.com/


# Generating artificial lexicons

To generate an artificial lexicon, first modify the appropriate values in `src/config.py`:

```
LANGUAGE = {german, english, dutch}
ITERATIONS = {N} # number of lexicons to generate
```

Then run:

```
python src/generate_artificial_lexicon.py 
```

## Output

This command will generate three files:

1. The original .csv file for that lexicon, but with all words annotated for surprisal.  
2. A .csv file with only unique wordforms, annotated for surprisal and number of homophones.  
3. A .csv file with `N` artificial lexicons, matched for the distribution of lengths in the real lexicon.

