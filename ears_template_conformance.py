# -*- coding: utf-8 -*-
import re
import logging
import spacy
from spacy.matcher import Matcher

logging.basicConfig(level=logging.DEBUG)
nlp = spacy.load('en_core_web_sm')
matcher = Matcher(nlp.vocab)

TYPE_CONDITIONAL_KEYWORDS = ['when', 'if', 'while', 'where']

CONDITIONS = ['whenever', 'whereas', 'once', 'within', 'after']
CONDITION_PHRASES = ['as soon as']

class EARSParser:
    def __init__(self, requirement_sent):
        self.sent = requirement_sent

        self.head = None

        self.modal = None
        self.modals = []
        self.is_multiple_modals = False

        self.anchor = None
        self.system_name = None

        self.system_response = None

        self.valid_sentence = None

        self.condition = None
        #self.precondition = None
        self.requirement_type = None

        self.conformant_segment = None

        self.details = None
        self.conditional_details = []

        self.template_conformance = None

    @staticmethod
    def first_parse(requirements):
        doc = nlp(requirements)
        return doc


    def parse_head(self):
        self.head = self.sent[0]


    def parse_modal(self):
        for token in self.sent:
            if token.tag_ == 'MD':
                self.modals.append(token)
        if len(self.modals) > 1:
            self.is_multiple_modals = True
            logging.warning(f'Multiple modals found : {self.modals}')

        if self.modals:
            self.modal = self.modals[0]
            logging.debug(f'Modal is : {self.modal}')


    def parse_system_name(self):
        if self.modal:
            modal_position = self.modal.i
            for noun_chunk in self.sent.noun_chunks:
                if noun_chunk.end <= modal_position:
                    self.system_name = noun_chunk
                else:
                    break
            logging.debug(f'System Name is : {self.system_name}')


    def parse_anchor(self):
        if self.modal and self.system_name:
            sent_start = self.sent.start
            modal_position = self.modal.i-sent_start
            for token in self.sent[modal_position:]:
                if token.pos_ == 'VERB':
                    vp_end = token.i
                    #print(vp_end, token.text)
                else:
                    break
            self.anchor = self.sent[self.system_name.start-sent_start : vp_end+1-sent_start]
            logging.debug(f'Anchor is : {self.anchor}')


    def parse_system_response(self):
        if self.modal:
            sent_start = self.sent.start
            modal_position = self.modal.i-sent_start
            for token in self.sent[modal_position : ]:
                if token.pos_ == 'VERB':
                    vp_end = token.i
                else:
                    break
            self.system_response = self.sent[vp_end-sent_start:]
            logging.debug(f'System response is : {self.system_response}')


    def parse_valid_sentence(self):
        if self.anchor:
            self.valid_sentence = True
            logging.debug('Valid sentence')
        else:
            self.valid_sentence = False
            logging.warning('Invalid sentence')


    def parse_condition(self):
        if self.valid_sentence:
            self.condition = self.sent[ : self.anchor.start-self.sent.start]
            if not self.condition.text:
                self.condition = None
            logging.debug(f'Condition is : {self.condition}')
        #TODO
        #complete checking of initial condition words must be done here or in conformant segment


    # def parse_conformant_segment(self):
    #     modal_position = self.modal.i
    #     sent_start = self.sent.start
    #     #here we completely segregate all the types of EARS conformant sentences
    #     #if they comply then we have a conformant segment otherwise NOT
    #     # <optional-precondition> is <np><vp> or <np><vp><np>
    #     if self.condition:
    #         if self.condition[0].text in conditional_keywords:
    #             if self.condition[0].text.lower() == 'when':
    #                 self.requirement_type = 'event driven'
    #             elif self.condition[0].text.lower() == 'if':
    #                 if self.condition[-1].text.lower() == 'then':
    #                     self.requirement_type = 'unwanted behaviour'
    #                 else:
    #                     self.conformant_segment = None
    #             elif self.condition[0].text.lower() == 'while':
    #                 self.requirement_type = 'state driven'
    #             elif self.condition[0].text.lower() == 'where':
    #                 self.requirement_type = 'optional feature'
    #         else:
    #             self.conformant_segment = self.sent[:modal_position-sent_start]
    #             self.requirement_type = 'ubiquitous'
    #         logging.debug(f'Conformant segment is : {self.conformant_segment}')
    #         logging.debug(f'Requirement type is : {self.requirement_type}')
    #     #TODO
    #     # How do we identify "Complex" requirement type ?

    # It is not exactly clear what determines if a requirement has a conformant segment when we are talking about EARS template
    def parse_pseudo_conformant_segment(self):
        if self.modal:
            sent_start = self.sent.start
            modal_position = self.modal.i-sent_start
            if self.valid_sentence:
                self.conformant_segment = self.sent[:modal_position+1]
                #logging.debug(f'Conformant segment is : {self.conformant_segment}')


    def parse_details(self):
        if self.conformant_segment:
            self.details = self.system_response


    def parse_conditional_details(self):
        #check above self.details for subordinate conjunctions
        if self.details:
            for con_phrase in CONDITION_PHRASES:
                pattern = re.compile(r"as soon as", re.IGNORECASE)
                if re.search(pattern, self.details.text):
                    logging.debug('''Conditional 'as soon as' found''')
                    #self.condition.append("as soon as")
                    self.conditional_details.append("as soon as")

            for token in self.details:
                if ((token.pos_ == 'ADP' and token.tag_ == 'IN')  or (token.pos_ == 'ADV' and token.tag_ == 'WRB')) and token.text.lower() in CONDITIONS:
                    self.conditional_details.append(token.text)
                    #self.conditional_details = self.details
            logging.debug(f'Sub ordinate conjunctions found in conditional : {self.conditional_details}')
        #TODO
        # if true should be marked as non conformant

    def parse_conditional_type(self):
        if not self.modal:
            return
        sent_start = self.sent.start
        modal_position = self.modal.i-sent_start
        #here we completely segregate all the types of EARS conformant sentences
        #if they comply then we have a conformant segment otherwise NOT
        # <optional-precondition> is <np><vp> or <np><vp><np>
        # <trigger> ?
        # <specific states> ?
        if self.condition:
            if self.condition[0].text.lower() in TYPE_CONDITIONAL_KEYWORDS:
                if self.condition[0].text.lower() == 'when':
                    self.requirement_type = 'event driven'
                elif self.condition[0].text.lower() == 'if':
                    if self.condition[-1].text.lower() == 'then':
                        self.requirement_type = 'unwanted behaviour'
                    else:
                        self.conformant_segment = None
                elif self.condition[0].text.lower() == 'while':
                    self.requirement_type = 'state driven'
                elif self.condition[0].text.lower() == 'where':
                    self.requirement_type = 'optional feature'
        else:
            if self.valid_sentence:
                self.conformant_segment = self.sent[:modal_position+1]
                self.requirement_type = 'ubiquitous'
        logging.debug(f'Conformant segment is : {self.conformant_segment}')
        logging.debug(f'Requirement type is : {self.requirement_type}')
        #TODO
        # How do we identify "Complex" requirement type ?


    def parse_template_conformance(self):
        if self.is_multiple_modals:
            self.template_conformance = False
            logging.debug('Non conformance due to presence of multiple modals')
        # non existence of modals
        # invalid sentence
        elif not self.valid_sentence:
            self.template_conformance = False
            logging.debug('Non conformance due to invalid sentence')

        elif not self.conformant_segment:
            self.template_conformance = False
            logging.debug('Non conformance due to presence of non conformant segment')
        # non conformant segment

        elif self.conditional_details:
            self.template_conformance = False
            logging.debug('Non conformance due to conditions in system response')
        # conditionals in system response

        else:
            self.template_conformance = True






if __name__ == '__main__':
    r = 'The S&T shall present to the SOT operator the EDTM anomalies.'
    doc = EARSParser.first_parse(r)
    for sent in doc.sents:
        ep = EARSParser(sent)
        ep.parse_head()
        ep.parse_modal()
        ep.parse_system_name()
        ep.parse_anchor()
        ep.parse_system_response()
        ep.parse_valid_sentence()
        ep.parse_condition()
        ep.parse_pseudo_conformant_segment()
        ep.parse_details()
        ep.parse_conditional_details()
        ep.parse_conditional_type()
        ep.parse_template_conformance()
        print(f"Template conformance is : {ep.template_conformance}")
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
