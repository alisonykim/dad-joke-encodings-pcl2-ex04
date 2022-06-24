#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# joke.py

# University of Zurich
# Department of Computational Linguistics

# Author 1: Alison Y. Kim
# Author 2: Naomi Bleiker

import time
from typing import List, Tuple, Dict
import re
import random
import csv
import lxml.etree as ET
import json
import sys


class Joke:
    """The Joke object contains the joke, and some metadata on that joke. One can compare the jokes by upvotes."""
    def __init__(self, raw_joke):
        self.raw_joke = raw_joke
        self.author = self.raw_joke[0]
        self.link = self.raw_joke[1]
        self.joke = self.raw_joke[2]
        self.rating = int(self.raw_joke[3])
        self.time = self.raw_joke[4]

        self.sentences_joke = self.split_into_sentences()
        self.tokenized_joke = self._tokenize()
        self.filtered_joke = self.filter_profanity()[0]
        self.num_profanities = self.filter_profanity()[1]

        self.xml_repr = self._get_xml_repr() # XML representation as attribute
        self.json_repr = self._get_json_repr() # JSON representation as attribute

    def split_into_sentences(self) -> List[str]:
        """Split text into sentences."""
        output = re.findall(r' ?([^.!?\n]+[.?!]*|\n)', self.joke)
        return output

    def _tokenize(self) -> List[List[str]]:
        """Tokenize all the words in the sentences."""
        output = []
        for sentence in self.sentences_joke:
            tokenized_sentence = re.findall(r'([\w\']+|\?|\.|\n|,|!)', sentence)
            output.append(tokenized_sentence)
        return output

    def filter_profanity(self, filename="profanities.txt") -> Tuple[List[List[str]], int]:
        """Filter out all the profanity."""
        output = []

        # Count number of profanities
        num_profanities = 0

        # Read in profanity file
        with open(filename, "r")as file:
            profanities = file.read().split("\n")

        for sentence in self.tokenized_joke:
            no_profanity = True
            text_sentence = " ".join(sentence)
            for profanity in profanities:

                # Check if there is profanity in the sentence
                if profanity in text_sentence:
                    profanity_in_text = True
                else:
                    profanity_in_text = False

                while profanity_in_text:
                    num_profanities += 1
                    no_profanity = False

                    # Find the index of the profanity
                    index = text_sentence.index(profanity)
                    front = text_sentence[:index - 1]

                    # Find the words that need to be replaced
                    num_words_before_profanity = len(front.split(" "))
                    num_profanity_words = len(profanity.split(" "))
                    profanity_in_sentence = sentence[num_words_before_profanity: num_words_before_profanity + num_profanity_words]

                    # Replace the profanity with '#'
                    replacement = ["#" * len(word) for word in profanity_in_sentence]

                    # Construct new sentence composed of the parts with and without profanity
                    new_sent = []
                    new_sent.extend(sentence[:num_words_before_profanity])
                    new_sent.extend(replacement)
                    new_sent.extend(sentence[num_words_before_profanity + len(replacement):])
                    text_sentence = " ".join(new_sent)
                    sentence = new_sent

                    # Check if there is still profanity in the sentence
                    if profanity in text_sentence:
                        profanity_in_text = True

                    else:
                        profanity_in_text = False
                        output.append(new_sent)

            # Add sentence immediately if there are no profanities in the sentence
            if no_profanity:
                output.append(sentence)
        return output, num_profanities

    def tell_joke(self):
        """Suspensefully deliver the joke."""
        if len(self.filtered_joke) > 1:
            build_up = self.filtered_joke[:-1]
            punch_line = self.filtered_joke[-1:]

            print(self.pretty_print(build_up))
            time.sleep(1)
            print(self.pretty_print(punch_line))
        else:
            print(self.pretty_print(self.filtered_joke))

    @staticmethod
    def pretty_print(joke) -> str:
        """Print joke in a humanly readable way."""
        output = ""
        for sentence in joke:
            output += " ".join(sentence) + " "
        return output

    def _get_xml_repr(self) -> ET.Element:
        """Create XML representation of a joke and its metadata."""
        # Initialize tree
        joke_xml = ET.Element('joke')
        text = ET.SubElement(joke_xml, 'text')
        author = ET.SubElement(joke_xml, 'author')
        link = ET.SubElement(joke_xml, 'url')
        rating = ET.SubElement(joke_xml, 'rating')
        time = ET.SubElement(joke_xml, 'time')
        profanity_score = ET.SubElement(joke_xml, 'profanity_score')

        # Define elements
        text.text = self.joke
        author.text = self.author
        link.text = self.link
        rating.text = str(self.rating)
        time.text = self.time
        profanity_score.text = str(self.num_profanities)
        
        return joke_xml

    def _get_json_repr(self) -> Dict:
        """Create JSON representation of a joke and its metadata."""
        # Initialize Python dictionary to be used for JSON representation
        joke_json = {'author': self.author,
                     'link': self.link,
                     'text': self.joke,
                     'rating': self.rating,
                     'time': self.time,
                     'profanity_score': self.num_profanities}
        return joke_json

    def __repr__(self):
        """Allows for printing."""
        return self.pretty_print(self.filtered_joke)

    def __eq__(self, other):
        """Equal rating"""
        return self.rating == other.rating

    def __lt__(self, other):
        """Less than rating"""
        return self.rating > other.rating

    def __gt__(self, other):
        """Greater than rating"""
        return self.rating < other.rating

    def __le__(self, other):
        """Less than or equal rating"""
        return self.rating >= other.rating

    def __ge__(self, other):
        """Greater than or equal rating"""
        return self.rating <= other.rating


class JokeGenerator:
    def __init__(self, filename="reddit_dadjokes.csv"):
        self.filename = filename
        self.jokes = self.make_jokes_objects()

    def make_jokes_objects(self):
        """
        Create Joke-objects from a joke file (.csv or .json).

        :return: List of lists whose elements are jokes and their metadata.
        """
        try:
            if self.filename.endswith('.csv'):
                with open(self.filename, "r") as lines:
                    lines = csv.reader(lines, delimiter=',')
                    jokes = [Joke(row) for row in lines]
            elif self.filename.endswith('.json'):
                with open(self.filename, 'r') as lines:
                    lines_json = json.load(lines) # Dictionary of raw joke dictionaries
                    lines_list = [list(raw_joke.values()) for raw_joke in lines_json.values()] # List of raw joke (i.e. joke and its metadata)
                    jokes = [Joke(line) for line in lines_list] # Create Joke-object
            return jokes
        except OSError:
            print(f'Could not open/read file: {self.filename}. Joke file must be in .csv or .json format. Please try again with an appropriate file type.')
            sys.exit()

    def generate_jokes(self):
        """Print jokes that are longer than 1 sentence."""
        for joke in self.jokes:
            if len(joke.filtered_joke) > 1:
                joke.tell_joke()
            time.sleep(10)

    def random_joke(self):
        """Randomly select a joke regardless of sentence length and print it."""
        joke = random.sample(self.jokes, 1)[0]
        joke.tell_joke()

    def save_jokes_xml(self, outfile: str) -> None:
        """Create and save XML representations of all jokes."""
        # Create XML representation
        root = ET.Element('jokes') # Create superelement <jokes>
        for joke in self.jokes: # Iterate over Joke-objects
            root.append(joke.xml_repr) # Add XML representation of individual Joke-object
        jokes_tree = ET.ElementTree(root)

        # Write to file
        jokes_tree.write(outfile, encoding='utf-8', pretty_print=True, xml_declaration=True)

    def save_jokes_json(self, outfile: str) -> None:
        """Save all the jokes of the Generator in their JSON representation to the outfile"""
        # Fill Python dictionary with JSON representations of each Joke-object as VALUE with /Python index + 1/ as KEY
        json_dict = {n+1: joke.json_repr for n, joke in enumerate(self.jokes)}

        # Convert Python dictionary to JSON-formatted string to be saved in file
        json_string = json.dumps(json_dict, indent='\t')

        # Write to file
        with open(outfile, 'w', encoding='utf-8') as json_file:
            json_file.write(json_string)


if __name__ == "__main__":
    # You can use the following commands for testing your implementation
    gen = JokeGenerator('reddit_dadjokes.csv') # Create Joke-objects
    for object in gen.jokes:
        print(object)
    gen.random_joke()

    # # Test save_jokes_xml(self, outfile)
    # gen.save_jokes_xml('reddit_dadjokes.xml')

    # # Test save_jokes_json(self, outfile)
    # gen.save_jokes_json('reddit_dadjokes.json')

    # # Test make_jokes_objects(self): does it correctly process jokes from JSON files?
    # gen_json = gen = JokeGenerator('reddit_dadjokes.json')
    # gen_json.random_joke()