This is the GitHub for the project: "Do human languages select for homophones?" [(Trott & Bergen, 2020)](https://www.sciencedirect.com/science/article/pii/S0010027720302687?via%3Dihub).

# Data

All data can be found in the `data` directory. Original lexica are located under `data/raw/{language}`, while the processed lexica (see below for details) are found under `data/processed/{language}/reals`. Artificial lexica with minimal pair data are found under `data/processed/{language}/minimal_pairs`.

# Generating artificial lexicons

To generate an artificial lexicon, first modify the appropriate values in `src/config.py`:

```
LANGUAGE = {german, english, dutch, french, japanese}
ITERATIONS = {N} # number of lexicons to generate
```

Then run:

```
python src/generate_artificial_lexicon.py 
```

## Output

This command will generate three files:

1. The original .csv file for that lexicon, but with all words annotated for surprisal (`data/processed/{language}/{language}_all_reals.csv`).  
2. A .csv file with only unique wordforms, annotated for surprisal and number of homophones (`data/processed/{language}/{language}_lemmas_processed.csv`).  
3. A .csv file with `N` artificial lexicons, matched for the distribution of lengths in the real lexicon (`data/processed/{language}/{language}_artificial_{N}_matched_on_{sylls/phones}.csv`).  


# Extracting number of minimal pairs for a lexicon

Once you've generated the artificial lexicons using the commands above, you can also analyze the number of minimal pairs. 

As before, make sure your `config` file is set properly:

```
LANGUAGE = {german, english, dutch, french, japanese}
ITERATIONS = {N} # number of lexicons to generate
```

Then run:

```
python src/minimal_pairs.py
```

# Analyze real artificial lexica.

Replication of Piantadosi et al (2012) can be found in the [Replication and extension notebook](https://github.com/seantrott/homophone_simulations/blob/master/Replication%20and%20extension.ipynb).

Analyses of the artificial lexica and comparisons to the real lexica can be found in this [comparison notebook](https://github.com/seantrott/homophone_simulations/blob/master/Homophony%20in%20real%20and%20artificial%20lexica.ipynb). This will also generate the main figures from the manuscript.


# Note on future work and refactoring

Note that we are currently exploring several directions for future work (mentioned in the manuscript), including the relationship between homophony and neighborhood sizes, as well as extending this work to Mandarin Chinese. As part of this extension, we have been refactoring the code; this refactored code is in the `mandarin` branch of the repository. We have not yet updated the main branch of the repository, as we want to "freeze" the original analysis pipeline used for the 2020 paper. Feel free to contact me (sttrott@ucsd.edu or trott.sean@gmail.com) if you have any questions about the code!
