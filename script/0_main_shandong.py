# -*- coding: utf-8 -*-
from urllib import request
from urllib import error
from bs4 import BeautifulSoup
import csv
import re
import time

# region global parameters
debug_mode = True
root_link = "http://zwfw.sd.gov.cn"
decode_type = "utf-8"
file_txt = open("../data/rlt_gov.txt", 'w', encoding='utf-8')
file_csv_name = "../data/rlt_gov.csv"
head_line = ['省政府分部门', '主要职责', '具体工作事项', '具体处室',
             '备注', '管理事项', '相关部门', '职责分工', '相关依据',
             '事中事后管理制度', '服务事项', '主要内容', '承办机构']
file_txt.write(",".join(head_line))
# endregion


# region main classes
class Duty(object):
    def __init__(self):
        self.main_duty = []
        self.work_options = []
        self.dependence = []
        pass
    pass


class Bounder(object):
    def __init__(self):
        self.manage_options = []
        self.about_apartments = []
        self.duties = []
        self.about_depends = []
        pass
    pass


class Service(object):
    def __init__(self):
        self.service_options = []
        self.main_contents = []
        self.organizations = []
        pass
    pass


class Apartment(object):
    def __init__(self):
        self.gov_apartment = []
        self.duties = []
        self.bounders = []
        self.manage_rules = []
        self.services = []
        pass
    pass

apartments = []
# endregion


# region general functions
# --------------------------------------------------------------------
# Get the link's content and return its content as a multi-line string
def getLinkContent(link, try_max_times=5):
    for ii in range(try_max_times):
        try:
            try:
                response = request.urlopen(link, timeout=3)
                page = response.read()
                page = page.decode(decode_type)
                page = str(page)
            except TimeoutError as reason:
                page = ''
                print(reason)
        except error.HTTPError as reason:
            page = ''
            print(reason, "\n\tand try ", ii, ' time...')
        if page != '':
            break
        pass
    return page
# --------------------------------------------------------------------


# --------------------------------------------------------------------
# Sub-function to help reduce the lines of code
def writeElementToList(a_list=[], l_rlt=[], flag=False):
    if a_list:
        l_rlt.append(a_list.pop(0))
        flag = False
    else:
        l_rlt.append('')
        pass
    return l_rlt, flag


# Write new_line's elements to file_out
def writeNewLineToFile(lines=apartments, filename=file_csv_name):
    # translate the line to text
    l_department = []
    l_main_duty = []
    l_work_option = []
    l_office = []
    l_remark = []
    l_manage_option = []
    l_about_apartment = []
    l_duty = []
    l_about_depend = []
    l_manage_rule = []
    l_service_option = []
    l_main_content = []
    l_organization = []
    for line in lines:
        duty = Duty()
        bounder = Bounder()
        service = Service()
        while True:
            end_flag = True
            if line.duties and not duty.remarks and not duty.dependence\
                    and not duty.work_options and not duty.main_duty:
                duty = line.duties.pop(0)
                pass
            if line.bounders and not bounder.about_depends and not bounder.duties\
                    and not bounder.about_apartments and not bounder.manage_options:
                bounder = line.bounders.pop(0)
            if line.services and not service.organizations and not service.main_contents\
                    and not service.service_options:
                service = line.services.pop(0)

            l_department, end_flag = writeElementToList(line.gov_apartment, l_department, end_flag)

            l_main_duty, end_flag = writeElementToList(duty.main_duty, l_main_duty, end_flag)
            l_work_option, end_flag = writeElementToList(duty.work_options, l_work_option, end_flag)
            l_office, end_flag = writeElementToList(duty.dependence, l_office, end_flag)
            l_remark, end_flag = writeElementToList(duty.remarks, l_remark, end_flag)

            l_manage_option, end_flag = writeElementToList(bounder.manage_options, l_manage_option, end_flag)
            l_about_apartment, end_flag = writeElementToList(bounder.about_apartments, l_about_apartment, end_flag)
            l_duty, end_flag = writeElementToList(bounder.duties, l_duty, end_flag)
            l_about_depend, end_flag = writeElementToList(bounder.about_depends, l_about_depend, end_flag)

            l_manage_rule, end_flag = writeElementToList(line.manage_rules, l_manage_rule, end_flag)

            l_service_option, end_flag = writeElementToList(service.service_options, l_service_option, end_flag)
            l_main_content, end_flag = writeElementToList(service.main_contents, l_main_content, end_flag)
            l_organization, end_flag = writeElementToList(service.organizations, l_organization, end_flag)

            if end_flag:
                break
            pass
        pass
    text_list = [l_department, l_main_duty, l_work_option, l_office, l_remark,
                 l_manage_option, l_about_apartment, l_duty, l_about_depend,
                 l_manage_rule, l_service_option, l_main_content, l_organization]

    # Like matrix's transpose
    text_list = list(zip(*text_list))

    with open(file=filename, mode='w', encoding='utf-8', newline='') as file_csv:
        writer = csv.writer(file_csv)
        for elem in text_list:
            writer.writerow(elem)
            pass
        pass
    pass
    file_csv.close()
    pass
# --------------------------------------------------------------------


# --------------------------------------------------------------------
# Simplify the list and remove the repeat elements
def simplifyList(src=[]):
    dst = []
    if not src:
        return src
    elem = src[0]
    for tmp in src:
        if elem != tmp:
            dst.append(elem)
            elem = tmp
            pass
        pass
    if not len(dst):
        return dst
    if dst[len(dst) - 1] != elem:
        dst.append(elem)
    return dst
# --------------------------------------------------------------------


# --------------------------------------------------------------------
# Remove useless tds labels such as 'img', 'functions'
def removeUselessTds(tds=list()):
    rlt = []
    for elem in tds:
        if str(elem).find('img') == -1 and str(elem).find('function') == -1:
            rlt.append(str(elem))
    return rlt
# --------------------------------------------------------------------


# --------------------------------------------------------------------
def getPureText(src=str()):
    return BeautifulSoup(src, "html.parser").getText()
# --------------------------------------------------------------------


# --------------------------------------------------------------------
def simplifyStr(src=str()):
    return src.replace('\n', '').replace('\r', '')
# --------------------------------------------------------------------
# endregion


# TODO: The remote server is bad, debug this later, same as HeBei
# region some re block and key words finder
######################################################################
gov_apartment_line_finder = re.compile("<a class=\"bmys\"(.*?)/div>", re.M)
gov_apartment_link_finder = re.compile("href=\"(.*?)\"")
gov_apartment_name_finder = re.compile("title=\"(.*?)\"")

gov_apartment_duty_finder = re.compile("<a href='DtlBMZZ(.*?)'")
gov_apartment_bounder_finder = re.compile("review/reviewDeptNexusDetails(.*?)\"")
gov_apartment_manage_finder = re.compile("<td><a title=\"(.*?)\"")
gov_apartment_general_finder = re.compile("<td align=\"left\" style=\"border(.*?)</td>")
######################################################################
# endregion

# Step 1: Gather information from the root page
# Step 1.1: Get the content of root page
root_page = getLinkContent(root_link + '/sdzw/bscx/qlqd/zrqd_show.do?orgcode=SD370000FG')

# Step 1.2: From the root page get all gov apartments' name and its link
# gov_apartment_lines = gov_apartment_line_finder.findall(root_page)
gov_apartment_lines = BeautifulSoup(root_page, 'html.parser').find_all('a', {'class': 'bmys'})
info_sum = len(gov_apartment_lines)
info_index = 0
print("The Total list is %d, begin processing..." % info_sum)
print("============================================")
time_begin = time.time()
# Step 1.3: Get all apartments's name and links then dig them
is_first_flag = True
for gov_apartment_line in gov_apartment_lines:
    apartment = Apartment()
    # region Step 1.4: Prepare the apartment's header
    gov_apartment_line = str(gov_apartment_line)
    gov_apartment_name = gov_apartment_name_finder.findall(gov_apartment_line)
    if gov_apartment_name:
        gov_apartment_name = gov_apartment_name[0]  # The first one is the right name
        pass
    gov_apartment_link = gov_apartment_link_finder.findall(gov_apartment_line)
    if gov_apartment_link:
        gov_apartment_link = gov_apartment_link[0]  # Same as the name
        pass
    apartment.gov_apartment.append(gov_apartment_name)

    info_index = info_index + 1
    print("The ", info_index, "('st) item: ", gov_apartment_name, "| and completed: ",
          info_index/info_sum*100, "%.")
    # endregion

    # region Step 2: Gather information from the detail link
    # Step 2.1: Get the content from child page
    if is_first_flag:
        gov_apartment_link = '/sdzw/bscx/qlqd/zrqd_show.do?orgcode=SD370000FG'

    gov_apartment_code = gov_apartment_link.split('?')[1]
    child_link = root_link + gov_apartment_link

    if not is_first_flag:
        child_page = getLinkContent(child_link)
    # endregion

    # region Step 3: Get the duty information from the child page
    if not debug_mode:
        duty_item_index = 1
        while True:
            duty_detail_link = root_link + '/sdzw/zrqd/orgduty/detail.do?' \
                               + gov_apartment_code + '&sn=' + str(duty_item_index)
            duty_item_index = duty_item_index + 1

            # Step 3.1 Get duty detail page's content and deal with the table
            duty_detail_page = getLinkContent(duty_detail_link)
            duty_item_tds = BeautifulSoup(duty_detail_page, 'html.parser').find_all('td')
            duty_detail_items = []
            for td in duty_item_tds:
                duty_detail_items.append(simplifyStr(BeautifulSoup(str(td), 'html.parser').getText()))
            duty = Duty()
            if len(duty_detail_items) > 10:
                print(duty_detail_items)
                while duty_detail_items and duty_detail_items.pop(0) != '追责依据及追责情形':
                    pass
                if duty_detail_items:
                    duty.main_duty.append(simplifyStr(duty_detail_items.pop(0)))
                if duty_detail_items:
                    duty.work_options.append(simplifyStr(duty_detail_items.pop(0)))
                if duty_detail_items:
                    duty.dependence.append(simplifyStr(duty_detail_items.pop(0)))
                while duty_detail_items:
                    duty.work_options.append(simplifyStr(duty_detail_items.pop(0)))

                apartment.duties.append(duty)
                pass
            else:
                break
            pass
        pass
    # endregion

    # region Step 4：Get the bounder information from the child page
    if debug_mode:
        bounder_item_index = 1
        while True:
            bounder_detail_link = root_link + '/sdzw/zrqd/boundaryduty/detail.do?' \
                               + gov_apartment_code + '&subsn=' + str(bounder_item_index)
            bounder_item_index = bounder_item_index + 1

            # Step 3.1 Get duty detail page's content and deal with the table
            bounder_detail_page = getLinkContent(bounder_detail_link)
            bounder_item_tds = BeautifulSoup(bounder_detail_page, 'html.parser').find_all('td')
            bounder_detail_items = []
            for td in bounder_item_tds:
                bounder_detail_items.append(simplifyStr(BeautifulSoup(str(td), 'html.parser').getText()))
            bounder = Bounder()
            if len(bounder_detail_items) > 6:
                print(bounder_detail_items)
                while bounder_detail_items and bounder_detail_items.pop(0) != '职责分工及协调配合机制':
                    pass
                while len(bounder_detail_items) % 2 == 0 and bounder_detail_items:
                    bounder.about_apartments.append(simplifyStr(bounder_detail_items.pop(0)))
                    bounder.duties.append(simplifyStr(bounder_detail_items.pop(0)))
                pass
            else:
                break
            pass

            bounder_item_divs = BeautifulSoup(bounder_detail_page, 'html.parser').find_all('div')
            bounder_detail_items = []
            for div in bounder_item_divs:
                bounder_detail_items.append(simplifyStr(BeautifulSoup(str(div), 'html.parser').getText()))

            bounder_detail_items = simplifyList(bounder_detail_items)
            while bounder_detail_items and bounder_detail_items.pop(0) != '管理事项':
                pass
            while bounder_detail_items and bounder_detail_items[0] != '职责分工':
                bounder.manage_options.append(simplifyStr(bounder_detail_items.pop(0)))

            while bounder_detail_items and bounder_detail_items.pop(0) != '相关依据':
                pass
            while bounder_detail_items and bounder_detail_items[0] != '事　　例':
                bounder.about_depends.append(simplifyStr(bounder_detail_items.pop(0)))
                pass

            apartment.bounders.append(bounder)
        pass
    # endregion

    # region Step 5: Get management rules information from the child page
    # todo: bug occurred
    # todo: Cannot get the Chinese letters because need the environment of Ajax
    if debug_mode:
        manage_rules = gov_apartment_manage_finder.findall(child_page)
        for manage_rule in manage_rules:
            apartment.manage_rules.append(manage_rule)
            pass
        pass
    # endregion

    apartments.append(apartment)

    pass

# region Step7: Write all apartments' information into csv file
writeNewLineToFile(apartments, file_csv_name)
time_end = time.time()
print("All completed, used time: ", time_end - time_begin, " s.")
# endregion
