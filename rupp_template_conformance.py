# -*- coding: utf-8 -*-
import re
import logging
import spacy
from spacy.matcher import Matcher

logging.basicConfig(level=logging.DEBUG)
nlp = spacy.load('en_core_web_sm')
matcher = Matcher(nlp.vocab)

CONDITIONS = ['whenever', 'whereas', 'once', 'within', 'after']
CONDITION_PHRASES = ['as soon as']# as soon as needs phrase checking

class RuppParser:
    def __init__(self, requirement_sent):
        self.sent = requirement_sent
        self.head = None

        self.modal_vp = None
        self.is_multiple_modals = None
        self.modals = []

        self.system_name = None
        self.anchor = None
        self.process = None
        #self.is_anchor = False

        self.valid_sentence = None

        self.condition = None
        #self.is_condition = False

        self.object = None

        self.conformant_segment = None
        self.details = None
        self.conditional_details = None
        self.conditions = []
        self.conditional_type = None
        self.template_conformance = None

    @staticmethod
    def first_parse(requirements):
        doc = nlp(requirements)
        return doc


    def parse_head(self):
        self.head = self.sent[0]


    def parse_modal_vp(self):
        for token in self.sent:
            if token.tag_ == 'MD':
                self.modals.append(token)

        if len(self.modals) > 1:
            self.is_multiple_modals = True
            logging.warning(f'Multiple modals found : {self.modals}')

        if self.modals:
            self.modal_vp = self.modals[0]
            logging.debug(f'Modal is : {self.modal_vp}')


    def parse_system_name(self):
        if self.modal_vp:
            modal_location = self.modal_vp.i
            #print(modal_location)
            for noun_chunk in self.sent.noun_chunks:
                #print(f"NC = {noun_chunk}")
                #print(noun_chunk.start, noun_chunk.end, modal_location)
                if noun_chunk.end <= modal_location:#What if there are multiple NPs before modal
                    self.system_name = noun_chunk
                    #print(f"SysName = {self.system_name} STARTS AT {self.system_name.start}")
                else:
                    break
            logging.debug(f'System Name is : {self.system_name}')


    def parse_anchor(self):
        #user_interaction = [{'LOWER': 'provide'},{'IS_ALPHA': True, 'OP': '+'},{'LOWER': 'with'}, {'LOWER': 'the'}, {'LOWER': 'ability'}, {'LOWER' : 'to'}]
        #interface = [{'LOWER': 'be'},{'LOWER': 'able'}, {'LOWER': 'to'}]
        user_interaction = re.compile(r"provide [\w\s]+ with the ability to", re.IGNORECASE)
        interface = re.compile(r"be able to", re.IGNORECASE)

        if self.modal_vp:
            modal_location = self.modal_vp.i
            if self.sent[modal_location+1-self.sent.start].pos_ is not 'VERB':
                #print('No verb immediately after modal')
                logging.warning('No verb immediately after modal. Anchor not present.')
                return
            #for token in self.sent[modal_location-self.sent.start : ]:
            #    if token.pos_ == 'VERB':#adverbs?
            text = self.sent[modal_location-self.sent.start : ].text
            if re.search(interface, text):
                logging.debug('Interface requirement found')
                interface_match = re.search(interface, text)
                #interface_match.start
                #interface_match.end
                #self.requirement = self.sent[modal_location+interface_match.start():modal_location+interface_match.end()]
                to_location = None
                for token in self.sent[modal_location-self.sent.start :]:
                    if token.pos_ == 'PART' and token.tag_ == 'TO':
                        to_location = token.i
                if to_location:
                    for token in self.sent[to_location-self.sent.start+1 :]:
                        if token.pos_ == 'VERB':#add adverbs too
                            verb_phrase_end = token
                            #print(f"VERB = {verb_phrase_end.text}, LOCATION = {verb_phrase_end.i}")
                        elif token.i > modal_location:
                            break
                    self.process = self.sent[to_location-self.sent.start+1:verb_phrase_end.i+1-self.sent.start]
                self.requirement = interface_match.group(0)+self.process.text
                logging.debug(f"Process = {self.process}")
                logging.debug(f"Requirement = {self.requirement}")
                #self.whom =

            elif re.search(user_interaction, text):
                logging.debug('User-Interaction requirement found')
                user_interaction_match = re.search(user_interaction, text)
                #user_interaction_match.end
                #print(self.sent.start, user_interaction_match.start(), user_interaction_match.end(), user_interaction_match.group(0))
                #self.requirement = self.sent[modal_location+user_interaction_match.start():modal_location+user_interaction_match.end()]
                to_location = None
                for token in self.sent[modal_location-self.sent.start :]:
                    if token.pos_ == 'PART' and token.tag_ == 'TO':
                        to_location = token.i
                if to_location:
                    for token in self.sent[to_location-self.sent.start+1 :]:
                        if token.pos_ == 'VERB':#add adverbs too
                            verb_phrase_end = token
                            #print(f"VERB = {verb_phrase_end.text}, LOCATION = {verb_phrase_end.i}")
                        elif token.i > modal_location:
                            break
                    self.process = self.sent[to_location-self.sent.start+1:verb_phrase_end.i+1-self.sent.start]
                self.requirement = user_interaction_match.group(0)+' '+self.process.text
                logging.debug(f"Process = {self.process}")
                logging.debug(f"Requirement = {self.requirement}")

            else:
                logging.debug('Autonomous requirement found')
                #self.process =
                for token in self.sent[modal_location-self.sent.start : ]:#Modify it, after shall we must have VERb otherwise not conformant ? #Already handled in the first 5-10 lines of this method
                    if token.pos_ == 'VERB':#add adverbs too
                        verb_phrase_end = token
                        #print(f"VERB = {verb_phrase_end.text}, LOCATION = {verb_phrase_end.i}")
                    elif token.i > modal_location:
                        break
                self.process = self.sent[modal_location-self.sent.start:verb_phrase_end.i+1-self.sent.start]
                self.requirement = self.process

            for token in self.sent[modal_location-self.sent.start :]:
                if token.pos_ == 'VERB':
                    anchor_end = token.i
                else:
                    break

            if self.system_name:
                #print("Making anchor")
                self.anchor = self.sent[self.system_name.start-self.sent.start : anchor_end+1-self.sent.start]#There is an overlap between methods you have already used and this part. Nothing wring in implementing it again. Fix it.

                logging.debug(f"ANCHOR = {self.anchor}")
            else:
                logging.debug("No anchor (no modal either)")


    def is_valid_sentence(self):
        if self.anchor:
            self.valid_sentence = True
            logging.debug('Valid sentence')
        else:
            self.valid_sentence = False
            logging.warning('Invalid sentence')


    def parse_condition(self):#This is the optional condition at the beginning
        # Everything before anchor is condition. It may or may not be present.
        # There are certain ways conditions start. Find the list of phrases that indicate the start of conditions.
        if self.valid_sentence:
            self.condition = self.sent[:self.anchor.start-self.sent.start]
        #TODO
        # if conditional exists then it must start with IF, AFTER, AS SOON AS, AS LONG AS
        # we can have those(IF, AFTER, AS SOON AS, AS LONG AS) pre determined phrases as a constant or editable from a config file


    def parse_object(self):# having an object slot is a must otherwise requirement is non conformant. #Automatically managed in the following method. No need to check again in the parse_conformance method
        if self.process:
            process_location = self.process.end
            for noun_chunk in self.sent[process_location-self.sent.start : ].noun_chunks:
                #print(f"Noun chunk: {noun_chunk.text}, NC start : {noun_chunk.start}, Process_End : {process_location}")
                if noun_chunk.start == process_location:
                    self.object = noun_chunk
                    break
                else:# should we be flexible with for_ADP_IN or to_ADP_IN. For now NO.
                    logging.debug("Noun Phrase doesn't start immediately after <process>")
                    self.object = None #unnecessary line of code
                    break

    def parse_conformant_segment(self):
        if self.modal_vp and self.valid_sentence and self.object:#Actually only self.object needs to be tested as if the others arnt there that automatically gurantees that self.object would be None
            self.conformant_segment = self.sent[ : self.object.end-self.sent.start]


    def parse_details(self):# AKA optional
        if self.conformant_segment:
            self.details = self.sent[self.object.end-self.sent.start : ]


    def parse_conditional_details(self):#this is the optional thing at the end
        #must not contain subordinate conjunction (after, before, unless)
        #the research paper implemented this by taking a pre determined list of conditional keywords like once, whenever, whereas
        if self.details:
            for con_phrase in CONDITION_PHRASES:
                pattern = re.compile(r"as soon as", re.IGNORECASE)
                if re.search(pattern, self.details.text):
                    logging.warning('''Found 'as soon as' in optional details''')
                    self.conditions.append("as soon as")
                    self.conditional_details = self.details

            for token in self.details:
                if ((token.pos_ == 'ADP' and token.tag_ == 'IN')  or (token.pos_ == 'ADV' and token.tag_ == 'WRB')) and token.text.lower() in CONDITIONS:
                    self.conditions.append(token.text)
                    self.conditional_details = self.details

            if self.conditions:
                logging.warning(f'Sub ordinate conjunctions found in conditional : {self.condition}')


    def parse_conformance(self):
        if self.is_multiple_modals:
            logging.error('Multiple modals present')
            self.template_conformance = False

        elif self.conditional_details:
            logging.error('Conditionals present in optional details')
            self.template_conformance = False

        elif self.anchor is None:
            logging.error('No anchor in sentence')
            self.template_conformance = False

        elif self.conformant_segment is None:
            logging.error('Conformant segment not present')
            self.template_conformance = False

        else:
            self.template_conformance = True

    # def is_autonomous_requirement(self):
    #     pass
    # def is_user_interaction_requirement(self):
    #     pass
    # def is_interface_requirement(self):
    #     pass

if __name__ == '__main__':
    r = "The Surveillance and Tracking module shall provide the system administrator with the ability to monitor system configuration changes posted to the database. \
    As soon as a power outage is detected, the Surveillance and Tracking module shall record a warning in the system alert log file. \
    The information technology tools used in the design of systems performing safety functions shall be assessed for safety implications on the end-product. \
    When a GSI component constraint changes STS shall deliver a warning message to the system operator. \
    As soon as an unplanned outage is detected the S&T shall inform the SMP interface. \
    When an unplanned outage is detected the S&T shall inform the SMP interface. \
    \
    \
    For each communication channel type the syatem needs to maintain a configurable timeout parameter. \
    As soon as a power outage is detected, the Surveillance and Tracking module shall record a warning in the system alert log file whenever logging is enabled. \
    The S&T shall present to the SOT operator the EDTM anomalies. \
    The approval of the final safety analysis report is a precondition for the endorsement of the applicaiton for an operating license. \
    The S&T module shall load a new configuration from the database as soon as the module receives a reloading request. \
    After underwriting1 is complete, if necessary the Insurance Officer shall perform underwriting2. \
    The OPENCOSS platform shall provide users with the ability to use in an assurance project evidence types that have been defined in another project. \
    The state of the S&T module can be standby, active or degraded. \
    The S&T component shall provide the user with a function to view the network status."
    parsed_doc = first_parse(r)
    for sent in parsed_doc.sents:
        rupp = RuppParser(sent)
        rupp.parse_head()
        rupp.parse_modal_vp()
        rupp.parse_system_name()
        rupp.parse_anchor_()
        rupp.parse_condition()
        rupp.parse_object()
        rupp.parse_conformant_segment()
        rupp.parse_details()
        rupp.parse_conditional_details()
        rupp.parse_conformance()
        print(f"SENT = {rupp.sent}, HEAD = {rupp.head}, MODAL = {rupp.modal_vp}, MULTI_MODAL = {rupp.is_multiple_modals}, MODAL_LIST = {rupp.modals}, ANCHOR = {rupp.anchor}, CONDITION = {rupp.condition}, OBJECT = {rupp.object}, DETAILS = {rupp.details}, CONDITIONAL_DETAILS = {rupp.conditional_details}, CONDITIONS = {rupp.conditions}, TEMPLATE_CONFORMANCE = {rupp.template_conformance}")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
'''
The S&T shall present to the SOT operator the EDTM anomalies. #Not Rupp compliant, EARS compliant however
The S&T shall periodically check the of the network elements by using the ping command. #grammatically incorrect
'''