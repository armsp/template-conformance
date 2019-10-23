import logging

from template_compliance.ears_template_conformance import EARSParser
from template_compliance.rupp_template_conformance import RuppParser
from template_compliance.agile_user_story_conformance import AgileUserStoryParser

logging.basicConfig(level=logging.DEBUG)

def requirement_formatter(requirement, conformance):
    formatted_req = f"<{conformance}>{requirement}</{conformance}>"
    return formatted_req

def check_rupp_template_compliance(requirements):
    requirement_list = []
    conformance_list = []
    doc = RuppParser.first_parse(requirements)
    for sent in doc.sents:
        rp = RuppParser(sent)
        rp.parse_head()
        rp.parse_modal_vp()
        rp.parse_system_name()
        rp.parse_anchor()
        rp.is_valid_sentence()
        rp.parse_condition()
        rp.parse_object()
        rp.parse_conformant_segment()
        rp.parse_details()
        rp.parse_conditional_details()
        rp.parse_conformance()
        requirement_list.append(rp.sent.text)
        conformance_list.append(rp.template_conformance)
        logging.debug(f"Requirement conformance is : {rp.template_conformance}")
        logging.debug('< < < < ~~~~~~~~ * * * * * * * * ~~~~~~~~ > > > >')
    tagged_requirements_list = [requirement_formatter(requirement, conformance) for requirement, conformance in zip(requirement_list, conformance_list)]
    return tagged_requirements_list


def check_ears_template_compliance(requirements):
    requirement_list = []
    conformance_list = []
    doc = EARSParser.first_parse(requirements)
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
        requirement_list.append(ep.sent.text)
        conformance_list.append(ep.template_conformance)
        logging.debug(f"Requirement conformance is : {ep.template_conformance}")
        logging.debug('< < < < ~~~~~~~~ * * * * * * * * ~~~~~~~~ > > > >')
    tagged_requirements_list = [requirement_formatter(requirement, conformance) for requirement, conformance in zip(requirement_list, conformance_list)]
    return tagged_requirements_list


def check_agile_story_template_conformance(requirements):
    requirement_list = []
    conformance_list = []
    doc = AgileUserStoryParser.first_parse(requirements)
    for sent in doc.sents:
        #print(sent)
        aus = AgileUserStoryParser(sent)
        aus.check_conformance()
        requirement_list.append(aus.sent.text)
        conformance_list.append(aus.template_conformance)
        #print(aus.template_conformance)
        logging.debug(f"Requirement conformance is : {aus.template_conformance}")
        logging.debug('< < < < ~~~~~~~~ * * * * * * * * ~~~~~~~~ > > > >')
    tagged_requirements_list = [requirement_formatter(requirement, conformance) for requirement, conformance in zip(requirement_list, conformance_list)]
    return tagged_requirements_list
