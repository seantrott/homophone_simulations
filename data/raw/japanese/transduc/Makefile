PATH = bin/

all: Japanese.glfst Japanese.words_glfst 

Japanese.glfst:Japanese.lmfst
	/bin/egrep -v "^#" Japanese.lmfst | /bin/sort -u | $(PATH)Lfst_info  -o Japanese.glfst

Japanese.words_glfst: Japanese.words
	$(PATH)Lfst_trans -l 2 -d Japanese.glfst -i 2 -m < Japanese.words|/bin/sort -u > Japanese.words_glfst

testing:
	/bin/sort -u Japanese.words_ana | /bin/diff - Japanese.words_glfst




