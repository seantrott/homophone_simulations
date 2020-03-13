"""Class for doing analysis."""


import matplotlib.pyplot as plt
import numpy as np
import os.path as op
import pandas as pd 
import seaborn as sns
import statsmodels.formula.api as sm

from scipy.optimize import curve_fit
from sklearn.metrics import r2_score

import src.config as config
import src.utils as utils


def get_analysis_parameters(config, language):

    return {'language': language,
            'phon_column': config.PHON_COLUMN[language],
            'word_column': config.WORD_COLUMN[language],
            'match_on': config.MODEL_INFO['match_on'],
            'n': config.MODEL_INFO['n'],
            'target': config.TARGET,
            'regressors': config.REGRESSORS}


### TODO: Also write code to selectively read in artificial lexica on the basis 
###       of which "mode" was used to generate lexicon.

### TODO: Determine `rank_N`. Use all words, some, or what?

class Analyzer(object):

    def __init__(self, language, n, phon_column, word_column, match_on, target, regressors):
        self.modes = ['neutral', 'anti_homophones', 'pro_neighborhoods']
        self.language = language
        self.n = n
        self.phon_column = phon_column
        self.word_column = word_column
        self.match_on = match_on
        self.target = target
        self.regressors = regressors
        self.formula = self.target + " ~ " + ' + '.join(regressors)
        self.artificial_lexica = []

    def load_real_lexica(self):
        """Load and process real preprocessed language."""
        # TODO: Change to "data/processed/{language}/reals/..."
        PATH = "data/processed/{lan1}/minimal_pairs/{lan2}_all_mps_{n}phone.csv".format(
            lan1=self.language, lan2=self.language, n =self.n)
        self.df_og = pd.read_csv(PATH)
        self.df_og['mode'] = 'real'
        self.df_processed = utils.preprocess_for_analysis(self.df_og, word_column=self.word_column, phon_column=self.phon_column)

    def load_artificial_lexica(self):
        """Load and process artificial lexica."""
        self.artificial_lexica = []
        for mode in self.modes:
            for lex in range(config.ITERATIONS):
                PATH = "data/processed/{language}/artificials/lex{lex}_matched_on_{match}_mode_{mode}_{n}phone.csv".format(
                        language=self.language, lex=lex, match=self.match_on, mode=mode, n=self.n)
                if op.exists(PATH):
                    df_tmp = pd.read_csv(PATH)
                    self.artificial_lexica.append(df_tmp)
        return self.artificial_lexica


    def get_stats_for_lexicon(self, df_lex):
        """Return basic stats about lexicon. Number of homophones, etc."""
        return {'homophone_percentage': round((len(df_lex[df_lex['num_homophones']>0]) / len(df_lex)), 4),
                'mean_homophones': round(df_lex['num_homophones'].mean(), 4),
                'max_homophones': round(df_lex['num_homophones'].max(), 2),
                'mean_mp': round(df_lex['neighborhood_size'].mean(), 4),
                'max_mp': round(df_lex['neighborhood_size'].max(), 2),
                'total_mp': round(df_lex['neighborhood_size'].sum(), 2),
                # 'mean_mp_w_hp': round(df_lex['neighborhood_size_with_homophones'].mean(), 4),
                # 'max_mp_w_hp': round(df_lex['neighborhood_size_with_homophones'].max(), 2),
                # 'total_mp_w_hp': round(df_lex['neighborhood_size_with_homophones'].sum(), 2)}
                }

    def run_model_on_lexicon(self, lexicon, formula):
        """Fit model to lexicon."""
        fit = sm.poisson(data = lexicon, formula=formula).fit(disp=0)
        params = fit.params 
        coefs = []
        coefs.append(params)
        return coefs

    def extract_cumulative_distribution(self, lexicon, y='num_senses'):
        """Extract cumulative distribution for target variable."""

        ## Approach 1: use cumulative density function

        ## Approach 2: hackier, but just calculate proportions directly
        proportions = []
        upper_bound = max(lexicon[y])
        values = list(range(1, upper_bound + 1))
        for value in values:
            df_tmp = lexicon[lexicon[y] >= value]
            proportions.append(len(df_tmp)/len(lexicon))

        d = self.characterize_power_law(values, proportions)
        return d[0]['a'], d[0]['b']   



    def extract_params(self, lexicon, formula=None):
        """Extract params from real lexicon for decay rate, growth rate, etc."""
        if formula is None:
            formula = self.formula

        # Get descriptive stats
        descriptive_stats = pd.DataFrame(self.get_stats_for_lexicon(lexicon), index=[0])

        # Get results of running model
        modeling_results = pd.DataFrame(self.run_model_on_lexicon(lexicon=lexicon, formula=formula), index=[0])

        # Concatenate
        df_concat = pd.concat([descriptive_stats, modeling_results], axis=1)

        # Get homophone rank distribution
        lexicon['num_senses'] = lexicon['num_homophones'] + 1
        homophone_params = self.characterize_rank_distribution(lexicon, 'num_senses', rank_N=1000)

        # Get neighborhood rank distribution
        neighborhood_params = self.characterize_rank_distribution(lexicon, 'neighborhood_size')

        # Put into conatenated dataframe
        df_concat['a (homophone rank)'] = homophone_params[0]['a']
        df_concat['b (homophone rank)'] = homophone_params[0]['b']
        df_concat['a (neighborhood rank)'] = neighborhood_params[0]['a']
        df_concat['b (neighborhood rank)'] = neighborhood_params[0]['b']

        # Get cumulative distribution parameters
        a, b = self.extract_cumulative_distribution(lexicon, y='num_senses')   
        df_concat['a (homophone decay intercept)'], df_concat['b (homophone decay rate)'] = a, b

        # Add 1 to give lonely words a boost (so we don't divide by 0)
        lexicon['neighborhood_boosted'] = lexicon['neighborhood_size'] + 1
        a, b = self.extract_cumulative_distribution(lexicon, y='neighborhood_boosted')   
        df_concat['a (neighborhood decay intercept)'], df_concat['b (neighborhood decay rate)'] = a, b

        # Other relevant info
        df_concat['num_wordforms'] = len(lexicon)
        df_concat['language'] = self.language

        return df_concat

    def get_real_params(self):
        """Extract and save params for real lexicon."""
        params = self.extract_params(self.df_processed)
        params.to_csv("data/params/real/{language}_params.csv".format(language=self.language))

    def characterize_rank_distribution(self, df, y_column, rank_N=1000):
        """Assign rank to Y and fit power law."""
        new_col = "rank_{x}".format(x=y_column)
        df[new_col] = df[y_column].rank(ascending=False, method="first")

        df_tmp = df[df[new_col]<=rank_N]

        params = self.characterize_power_law(df_tmp[new_col].values, df_tmp[y_column].values)

        return params

    def _power_func(self, x, a, b):
        """Zipf's law."""
        return a / (x**b)

    def fit_law(self, x, y, func):
        """Fit specified function."""
        # Fit function
        z_popt, z_pcov = curve_fit(func, x, y)
        # Generate predictions
        z_pred = func(x, *z_popt)
        # Characterize fit with R^2
        r2 = r2_score(y, z_pred)
        return z_popt, z_pcov, z_pred, r2

    def characterize_power_law(self, x, y):
        """Use func to characterize powerlaw."""
        z_popt, z_pcov, z_pred, r2 = self.fit_law(x, y, self._power_func)
        a, b = z_popt
        # Return fit, along with parameters
        return [{'r2': r2,
                'a': a,
                'b': b}, 
                z_pred]


    def rank_column(self, df, y_column):
        """Return dataframe with ranked version of Y."""
        new_col = "rank_{x}".format(x=y_column)
        df[new_col] = df[y_column].rank(ascending=False, method="first")
        return df   


    def aggregate_rank_distributions(self, y_column, rank_N=1000):
        """Create rank distributions of some Y for real lexicon and each mode."""
        print(y_column)
        new_col = "rank_{x}".format(x=y_column)
        print(new_col)
        self.df_processed[new_col] = self.df_processed[y_column].rank(ascending=False, method="first")

        for index, lexicon in enumerate(self.artificial_lexica):
            lexicon[new_col] = lexicon[y_column].rank(ascending=False, method="first")

        df_critical = self.df_processed[[new_col, y_column, 'mode']]
        df_critical = df_critical[df_critical[new_col]<=rank_N]

        all_df = [df_critical]

        for mode in self.modes:
            # For each lexicon of that mode, subset just the top N rows and sort them.
            subset = np.array([sorted(l[l[new_col]<=rank_N][y_column].values, reverse=True) for l in self.artificial_lexica if l['mode'].values[0] == mode])
            if len(subset) > 0:
                # Get the median value for each i-th rank.
                medians = np.median(subset, axis=0)
                # Put into dataframe
                df_tmp = pd.DataFrame({'mode': mode, y_column: medians, new_col: list(range(rank_N))})
                all_df.append(df_tmp)

        return pd.concat(all_df)


    def visualize_rank_distribution(self, y_column, rank_N=1000):
        """Visualize rank distributions."""
        new_col = "rank_{x}".format(x=y_column)
        df_ranks = self.aggregate_rank_distributions(y_column=y_column, rank_N=rank_N)

        sns.scatterplot(data = df_ranks,
            x = new_col,
            y = y_column,
            hue = 'mode',
            alpha =.5)

        plt.xlabel(new_col.replace("_", " "))
        plt.ylabel(y_column.replace("_", " "))




