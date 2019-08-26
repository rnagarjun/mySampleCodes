import re
import pandas as pd

import nltk
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter

import urllib3
#import beautifulsoup4



def rejoin_text(list_of_text, delimeter=" "):
	"""
	Util function to put together text that's been fragmeted into lists	
	based on the given delimeter, default delimeter: Empty space
	
	Example:
	>>> text = ['this', 'is', 'an', 'example']
	>>> rejoin_text(text, '-')
	>>> this-is-an-example
	"""

	try:
		return delimeter.join(word for word in list_of_text)
	except TypeError:
		pass


class Content:
	"""
	A class to represent the contents on a news article
	"""
	
	def __init__(self, content, url=None):
		"""
		intializing of content class
		Connects the Comment class to the pands object
		Note:
		countStatus will be reprsented in binary
		Example: 0101 -> sentence: False, words: True, Sylabble: False, character: True
		"""
		# hold raw text value
		self.content = content
		# url link, if exist
		self.source = url
		
		# preprocessed value, aka; tokenized/cleaned/stemmed and stopwords removed text, o/w specified
		# the content is tokenized automatically when pre_procesed; hence will be of type List
		self.pre_processed = []
		# status of pre_processed content
		self.pre_process_status = {'cleaned_content': None, 'stemmed': None, 'stopwords_removed': None}
		
		# initialing counts
		self.counts = {'sentences': 0, 'words': 0, 'sylabble': 0, 'characters': 0}

	
	def pre_process(self, clean=True, remove_stopwords = True, stem=True, custom_regex=None) -> None:
		"""
		(self: Content, clean: bool, remove_stopwords: bool, stem: bool, custom_regex: str)
		The order in which pre processing typically occur is as follows,
			tokenize -> clean_content -> remove_stopwords -> stem
		"""
		self.tokenize()
		self.clean_content()
		#self.remove_stopwords()
		#self.stem()


	
	def tokenize(self, text=None):
		"""
		(self: Content, text: str) -> List[str]
		Given a text, this function will split the text into appropriate sentences.
		"""
		tokenized_content = nltk.sent_tokenize(text) if text else nltk.sent_tokenize(self.content)
			
		#tokenized_content = nltk.sent_tokenize(self.content)
		# get the number of sentences
		
		if not text:
			self.pre_process_status['tokenized'] = True
			self.pre_processed = tokenized_content

		return tokenized_content

	def POS_tagging(self, text=None):
		"""
		(self: Content, text: str) -> List[Tuples(str)]
		Given a text of words, this function will assign part of speech tagging for each individual word
		"""
		#cfg_list = Counter(tag for word,tag in cleaned_text)
		return nltk.pos_tag(text.split()) if text else nltk.pos_tag(self.pre_processed)
		
	
	def stem(self, text=None, stopwords=True):
		"""
		(self: Content, text: str) -> list[list[str]]
		helps to classify words such as jump, jumpping, jumped etc into 
		one word jump.
		"""
		sentences =  self.tokenize(text) if text else self.pre_processed

		ss = nltk.stem.SnowballStemmer('english')
	
		stemmed_content = []

		for sentence in sentences:
			
			temp_sentence = ""
			for word in sentence.split():
				temp_sentence+= ss.stem(word)+' '
			stemmed_content.append(temp_sentence)

		#stemmed = [(ss.stem(w[0]), w[1]) for w in self.pre_processed]
		if text:
			self.pre_processed = stemmed_content
			self.pre_process_status['stemmed'] = True
		
		return rejoin_text(stemmed_content)

	def remove_stopwords(self, text=None) -> str:
		"""
		(self: Content, text: str)
		Removes unneccesary words such as in, the, at etc. The words that 
		are not very useful when trying to create a word cloud.
		"""
		stop_words = set(nltk.corpus.stopwords.words("english"))
		all_words =  self.clean_content(text) if text else self.pre_processed
		all_words = rejoin_text(all_words)
		all_words = all_words.split()
		stopwords_removed = [w for w in all_words if not str(w).lower() in stop_words]
		
		if text:
			self.counts['words'] = len(stopwords_removed)

			self.pre_processed = rejoin_text(stopwords_removed) 
			self.pre_process_status['stopwords_removed'] = True

		return rejoin_text(stopwords_removed)
	
	def calculate_ari(self) -> float:
		"""
		Calculate the artifical readability index for a given text
		This value approximates the level of reading difficulty of the text
		"""
		ARI = 4.71*(character_count/word_count) + 0.5*(word_count/sentence_count)-21.43
		return ARI

	def sentiment_analysis(self, text=None):	
		"""
		(self: Content, sentences: str)
		For a given group of sentences, it will indicate the polarity of the sentence.
		This method makes use of the SentimentIntensityAnalyzer from the NLTK library
		
		EXAMPLE:
		>>> The dog climbed up the bench today.
		>>> compound: 0.0, neg: 0.0, neu: 1.0, pos: 0.0
		
		>>> I just broke my leg.
		>>> compound: -0.4215, neg: 0.483, neu: 0.517, pos: 0.0
		
		>>> Flowers are beautiful.
		>>> compound: 0.5994, neg: 0.0, neu: 0.339, pos: 0.661
		
		>>> She was sick but atleast she got a day off from work.
		>>> compound: -0.2846, neg: 0.177, neu: 0.823, pos: 0.0
		"""
		polarity_calculated = dict()
		sid = SentimentIntensityAnalyzer()
		sentences = self.tokenize(text) if text else self.pre_processed
		for sentence in sentences:
			polarity_calculated[sentence] = list()
			ss = sid.polarity_scores(sentence)
			for k in sorted(ss):
				temp = '{0}: {1} '.format(k, ss[k])
				
				pol_stat = temp
				#(k+': '+ ss[k])
				polarity_calculated[sentence].append(pol_stat)
				#print('{0}: {1}, '.format(k, ss[k]), end='')
			#print()
		print(polarity_calculated)
		return polarity_calculated
	
	def count_syllable(word) -> None:
		"""
		count the number of syllable in a given word
		
		EXAMPLE
		>>> word
		>>> sylabble
		"""
		word = word.lower()
		count = 0
		vowels = "aeiouy"
		if word[0] in vowels:
			count += 1
		for index in range(1, len(word)):
			if word[index] in vowels and word[index - 1] not in vowels:
				count += 1
		if word.endswith("e"):
			count -= 1
		if count == 0:
			count += 1
		return count
	
	def clean_content(self, text=None, punctuations=True, digits=True, custom_regex=None) -> None:
		"""
		Clean the text based on the given conditions, if puntuation
		and digits are specificed as false, then the clean will not eliminate those
		contents from the text.
		"""
		sentences = self.tokenize(text) if text else self.pre_processed
		
		cleaned = []
		for sentence in sentences:
			clean = sentence
			if punctuations:
				clean = re.sub("[^\w\s]", "", clean)

			if digits:
				clean = re.sub("\d+", "", clean)

		
			if custom_regex:
				clean = re.sub(custom_regex, "", clean)
			
			clean = clean.strip()
		
			cleaned.append(clean)

		if text:
			#self.pre_processed = rejoin_text(tokenized_words)
			self.pre_process_status['cleaned_content'] = True
		return rejoin_text(cleaned, ". ")

	def plot_word_cloud(self, title="wordCloud", text=None, width=600, height=400):
		"""
		Creates word cloud using the text from pre_processed
		A new file with the title.png will be created in the directory
		"""
		word_bank = text if text else rejoin_text(self.pre_procesed)
		wordcloud = WordCloud(width=width, height=height, background_color="white").generate(text)        
		fig, ax = plt.subplots()        
		ax.imshow(wordcloud, interpolation="bilinear")        
		plt.axis("off")        
		plt.tight_layout()        
		plt.title(title)        
		plt.savefig(title+ ".png")

	def raw_source(self, url=None):
		"""
		Returns the raw webpage content
		"""
		http = urllib3.PoolManager()
		if url:
			response = http.request('GET', url)
			return response.data
		else:
			response = http.request('GET', self.source)
			return response.data

		
if __name__ == "__main__":
#	text2Analyze = "Seoul, South Korea (CNN)South Korea is scrapping its military intelligence-sharing agreement with Japan, the latest escalation in a trade dispute that threatens global supply chains for smartphones and other gadgets. Kim You-geun, first deputy director of the Blue House National Security Office, said the move was in retaliation to Japans decision to exclude South Korea from its list of trusted trading partners.Under these circumstances, the government judged that it would not be in our national interest to keep the agreement in place, which was signed for the purpose of exchanging sensitive military information for security (purposes), Kim said.The rising tensions between the two countries have sparked worries around the world. We encourage Japan and Korea to work together to resolve their differences. I hope they can do this quickly, said Lt. Col. Dave Eastburn, a Pentagon spokesman. We are all stronger -- and northeast Asia is safer -- when the United States, Japan, and Korea work together in solidarity and friendship, he said, adding that intelligence sharing was key to developing common defense policy and strategy.The standoff between Tokyo and Seoul started last month when Japan placed new restrictions on the export of three chemical materials to South Korea. Those chemicals are used in computer chips manufacturing -- a key part of the South Korean economy. The new rules delay exports as Japanese companies must apply for licenses for each of the materials, a process that can take up to 90 days. But tension between the two countries has been rising for months, stemming in part from Japans colonial rule over the Korean peninsula in the early 20th century. South Koreas top court recently ruled that its citizens can sue Japanese companies for using forced Korean labor during World War II. Japan has denied that the two issues are linked."

	text2Analyze = "I just broke my leg! Flowers are beautiful! Today was my 2nd day at work. Once upon a time there was a cat, but the cat had no fur. The dog climbed up the bench today. I bought a new bag today. She was sick but atleast she got a day off from work. Finally, the quick brown fox jumped over the lazy dog."
	paragraph = Content(text2Analyze)
#	paragraph.pre_process()


	print('tokenized')
	print(paragraph.tokenize())
	
	print('sentiment_analysis')
	print(paragraph.sentiment_analysis())
	
	print('clean_content')
	print(paragraph.clean_content())
	
	print('remove_stopwords')
	print(paragraph.remove_stopwords())

	print('POS tag')
	print(paragraph.POS_tagging())

	print('Stem')
	print(paragraph.stem())


	#paragraph.pre_process()
	#paragraph.plot_word_cloud()
