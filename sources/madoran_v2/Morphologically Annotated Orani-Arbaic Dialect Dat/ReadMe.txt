======================================================================================

Dataset: MADOran Morphologically Annotated Dataset
Authors: Majdi Sawalha, Faisal Alshargi, Sane Yagi, Wafa Kacha, Abdallah Alshdaifat
Published: 8 January 2025
Version 1
DOI:10.17632/pgr766jbhp.1
Institution: The University of Jordan
Categories: Artificial Intelligence, Computational Linguistics, Annotation, Morphological Analysis, Corpus Linguistics, Corpus Analysis
Licence: CC BY NC 3.0
Funding: The Scientific Research Fund of the Ministry of Higher Education and Scientific Research, Jordan (Grant No. Soci/2/1/2016)
Cite this dataset:
Sawalha, Majdi; Alshargi, Faisal; Yagi, Sane; Kacha, Wafa; Alshdaifat, Abdallah (2025), “Morphologically Annotated Orani-Arbaic Dialect Dataset (MADOran)”, Mendeley Data, V1, doi: 10.17632/pgr766jbhp.1

=====================================================================================
Description
We introduce a new morphologically annotated dataset for the Orani Arabic dialect (ORN), comprising 33,000 words gathered from diverse genres, including written sources (11.83%) which cover topics such as college life, culture, history, humor, politics, and traditions, as well as spoken language (88.17%) spanning storytelling, music, and daily conversation. Each word is manually annotated with a fine-grained tagset that provides part-of-speech, root, pattern, and English and French translations of the glosses. The morphological annotation was performed using the Dialectal Word Annotation Tool for Arabic (DIWAN) and it followed guidelines established for The Dynamic Arabella Corpus (Arabella), with adaptations to fit the dialectal context.
-----------------------------------------------------------------------------------------------------------------
DATA DESCRIPTION
(1) [Folder] Raw Data - Sentences 
	File 1:MADOran_Sentences.tsv
	File 2:MADOran_Sentences.txt
	(text file in utf8 encoding)

The source data files contains the sentences of the corpus in 2 formats, tab separated column file, and text file. The data is structured in three columns, the sentence no in the first column, the sentence text, and the number of words, using space and punctuation tokenizer, in the second and third columns respectively.

Stats about Source Data
		Sentences	Tokens	Lemmas	Roots	Patterns
No. of Instances	1356	30919	21429	15605	15661
No. of word types	-	8638	4975	1262	682
Lexical Diversity	-	0.279	0.232	0.081	0.044
--------------------------------------------------------------------------------
(2) MADOran Morphologically Annotated Dataset [Folder]
	File 1: MADOran.csv
	File 2: MADOran.db
	File 3: MADOran.json
	File 4: MADOran.tsv

The same content is presented in the form of a text file in utf8 encoding, comma delimited CSV-Utf8, SQLite3 database and JavaScript Object Notation (JSON). 

The structure of these files  contains 18 fields (in case of the MADOran.db and MADOran.json files) or columns (in case of .csv and .tsv files). These fields/columns are:
	1) "ID": (INTEGER), is a sequence number. 
	2) "Sentno": (INTEGER), is a sequence number for distinguishing the sentences.
	3) "Wordno": (INTEGER), is a sequence number for distinguishing words within a certain sentence.
	4) "Word": (TEXT), stores the word as appeared in the original text. 
	5) "diac": (TEXT), is the word written in standard orthography for Orani which was used in this project.
	6) "msa": (TEXT), is the equivalent MSA word for the Orani word.
	7) "Proclitic": (TEXT), In this data set, the proclitics represent all morphemes prior to the stem including the prefixes along with their morphological tags.
	8) "Stem": (TEXT),the main part of the decomposed word and its morphological tag.
	9) "Enclitic": (TEXT), stores all morphemes after the stem including the suffixes and their morphological tags.
	10) "Root": (TEXT), stores three or four consonant letters that indicate the semantics of the words.
	11) "Pattern": (TEXT), stores the morphological template that is used to derive a word in MSA. These patterns are also used to derive diacritical words of Orani. New patterns are introduced to the Orani.
	12) "num": (TEXT), stores singular, dual or plural in terms of identifying their number morphological feature.
	13) "gen": (TEXT), stores masculine or feminine for the morphological feature of gender
	14) "Sentiment": (TEXT), stores positive, negative or neutral that indicates the (subjectivity/objectivity) or the emotions embedded with the word semantics. 
	15) "en_gloss": (TEXT), stores the English translation for the Orani words.
	16) "fr_gloss": (TEXT), stores the French translation for the Orani words.


------------------------------------------------------------------------------------
(3) [Folder] Frequency distribution data
	File: MADOranFreqDist.csv
The file contains the frequency distribution of all tokens in the MADOran Dataset. The structure of the file consists of two columns: 
	1) Token – a unique word or token from the dataset.
	2) Frequency – the number of occurrences of that token in the corpus. 
The file is stored in descending order by frequency. 


Top 10 most frequent tokens in MADOran Dataset
Token	Frequency
.	1999
و	1646
ما	435
في	346
لا	277
?	274
كي	230
تع	225
,	218
الله	202

---------------------------------------------------------------------------------------------------------
Supplementary files
	1) ReadMe.txt (this file)
	2) Morphology Annotation Guidelines.pdf
	This guide is designed to support both new and experienced annotators in producing consistent, high-quality annotations. 

