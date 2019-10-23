#As a < type of user >, I want < some goal > so that < some reason >.
#As a power user, I can specify files or folders to backup based on file size, date created and date modified.
#As a user, I can indicate folders not to backup so that my backup drive isn't filled up with things I don't need saved.
#As a vice president of marketing, I want to select a holiday season to be used when reviewing the performance of past advertising campaigns so that I can identify profitable ones.
import spacy
from spacy.matcher import Matcher
import logging

nlp = spacy.load('en_core_web_sm')
matcher = Matcher(nlp.vocab)
logging.basicConfig(level=logging.DEBUG)

#user_story = [{'LOWER': 'as'},{'LOWER': {"IN": ['a', 'an']}},{'OP': '+'}, {'LOWER': 'i'}, {'LOWER': {'IN': ['want', 'can']}}, {'OP': '+'}, {'LOWER': 'so', 'OP': '?'}, {'LOWER': 'that', 'OP': '?'}]
#uu = [{'LOWER': 'i'}, {'LOWER': {'IN': ['want', 'can']}}]

user_story = [{'LOWER': 'as'},{'LOWER': {"IN": ['a', 'an']}}, {'OP': '+'}, {'LOWER': 'i'}, {'LOWER': 'want'}, {'OP': '+'}, {'LOWER': 'so'}, {'LOWER': 'that'}]

#uu = [{'LOWER': 'as'}, {'LOWER': {'IN': ['a', 'an']}}]
class AgileUserStoryParser:
    def __init__(self, requirement):
        self.sent = requirement
        self.user_type = None
        self.goal = None
        self.reason = None
        self.template_conformance = None

    @staticmethod
    def first_parse(requirements):
        doc = nlp(requirements)
        return doc

    def check_conformance(self):
        matcher.add("UserStory", None, user_story)
        matches = matcher(self.sent.as_doc())
        #logging.debug(len(matches), matches)
        if matches:
            #if len(matches) > 1:
            #    self.template_conformance = False
            #    logging.warning('Invalid sentence. Multiple matches in single sentence.')
            #else:
            #    match_id, start, end = matches[0]
            #    if start == 0:
            #        self.template_conformance = True
            #    else:
            #       logging.warning('Invalid sentence as it does not start with As a/an')
            #        self.template_conformance = False

            match_id, start, end = matches[0]
            #print(self.sent.end-self.sent.start, end)
            if (start == 0) and (self.sent.end-self.sent.start-end > 3):#arbitrarily imposing that atlest 4 tokens need to exist after `so that`
                self.template_conformance = True
            else:
                logging.warning('Invalid sentence as it does not start with As a/an or doesnt have enough tokens after `so that`')
                self.template_conformance = False
        else:
            self.template_conformance = False
            logging.warning('No match in the requirement')

if __name__=='__main__':
    requirements = 'As a power user, I can specify files or folders to backup based on file size, date created and date modified. As a vice president of marketing, I want to select a holiday season to be used when reviewing the performance of past advertising campaigns so that I can identify profitable ones. As a user I want to see the output so that I may decide what to choose.'
    doc = AgileUserStoryParser.first_parse(requirements)
    for sent in doc.sents:
        print(sent)
        aus = AgileUserStoryParser(sent)
        aus.check_conformance()
        print(aus.template_conformance)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

#doc = nlp('As a power user, I can specify files or folders to backup based on file size, date created and date modified. As a vice president of marketing, I want to select a holiday season to be used when reviewing the performance of past advertising campaigns so that I can identify profitable ones. As a user I want to see the output so that I may decide what to choose.')

#for sent in doc.sents:
#    #print(sent)
#    matches = matcher(sent.as_doc())
#    print(matches)
#    #for match_id, start, end in matches:
#    #    string_id = nlp.vocab.strings[match_id]  # Get string representation
#    #    span = sent[start:end]  # The matched span
#   #    print(start, end, span.text)
#    #    print('~~~~~~~~~~~~~~~~~~~~~~~~')
#    #print('******************************************')

