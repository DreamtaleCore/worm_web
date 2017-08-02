# -*- coding: utf-8 -*-
from urllib import request
from urllib import error
from bs4 import BeautifulSoup
import csv
import re
import time
import gc

# region global parameters
debug_mode = True
root_link = "http://old.jl.gov.cn/rdzt/zwzt/qlzrqd/zrqd/anbumen/anbumen_54919/"
decode_type = "utf-8"
file_txt = open("../data/rlt_gov.txt", 'w', encoding='utf-8')
file_csv_name = "../data/rlt_gov.csv"
head_line = ['省政府分部门', '主要职责', '具体工作事项', '具体处室',
             '备注', '管理事项', '相关部门', '职责分工', '相关依据',
             '事中事后管理制度', '服务事项', '主要内容', '承办机构']
file_txt.write(",".join(head_line))
# endregion


# region main classes
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
        self.responsibilities = []
        self.dependencies = []
        self.manage_rules = []
        self.services = []
        pass
    pass

apartments = []
# endregion


# region general functions
# --------------------------------------------------------------------
# Get the link's content and return its content as a multi-line string
def getLinkContent(link):
    try:
        response = request.urlopen(link)
        page = response.read()
        page = page.decode(decode_type)
        page = str(page)
    except error.HTTPError as reason:
        page = ''
        print(reason)
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
    l_responsibility = []
    l_dependency = []
    l_manage_option = []
    l_about_apartment = []
    l_duty = []
    l_about_depend = []
    l_manage_rule = []
    l_service_option = []
    l_main_content = []
    l_organization = []
    for line in lines:
        bounder = Bounder()
        service = Service()
        while True:
            end_flag = True
            if line.bounders and not bounder.about_depends and not bounder.duties\
                    and not bounder.about_apartments and not bounder.manage_options:
                bounder = line.bounders.pop(0)
            if line.services and not service.organizations and not service.main_contents\
                    and not service.service_options:
                service = line.services.pop(0)

            l_department, end_flag = writeElementToList(line.gov_apartment, l_department, end_flag)

            l_main_duty, end_flag = writeElementToList(line.duties, l_main_duty, end_flag)

            l_responsibility, end_flag = writeElementToList(line.responsibilities, l_responsibility, end_flag)
            l_dependency, end_flag = writeElementToList(line.dependencies, l_dependency, end_flag)

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
    text_list = [l_department, l_main_duty, l_manage_option, l_about_apartment,
                 l_duty, l_about_depend, l_responsibility, l_dependency,
                 l_manage_rule, l_service_option, l_main_content, l_organization]

    # Like matrix's transpose
    text_list = list(zip(*text_list))

    with open(file=filename, mode='a', encoding='utf-8', newline='') as file_csv:
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
# In order to get the Chinese letters from 1.汉字。 \n  =>  1AA汉字BB BB
def replaceStr(s=str()):
    s = s.replace('.', 'AA')
    s = s.replace('。', 'BB')
    s = s.replace('\n', 'BB')
    s = s.replace('\r', 'BB')
    s = s.replace('<br/>', 'BB')
    return s
    pass
# --------------------------------------------------------------------
# endregion


# region some re block and key words finder
######################################################################
gov_apartment_link_finder = re.compile("href=\"(.*?)\"")

gov_apartment_classes_finder = re.compile("scrolling=\"no\" src=\'(.*?)\'")
gov_apartment_duties_finder = re.compile("AA(.*?)BB")
gov_apartment_rd_item_finder = re.compile("AA(.*?)BB")
gov_apartment_bounder_finder = re.compile("a href=\"(.*?)\"")
gov_apartment_manage_finder = re.compile("<td><a title=\"(.*?)\"")
gov_apartment_general_finder = re.compile("<td align=\"left\" style=\"border(.*?)</td>")
gov_apartment_page_sum_finder = re.compile("countPage = (.*?)//")
######################################################################
# endregion

# Step 1: Gather information from the root page
# Step 1.1: Get the content of root page
root_page = getLinkContent(root_link)

# Step 1.2: From the root page get all gov apartments' name and its link
gov_apartment_soup = BeautifulSoup(root_page, 'html.parser')
gov_apartment_lines = gov_apartment_soup.find_all('li')
info_sum = len(gov_apartment_lines)
info_index = 0
print("The Total list is %d, begin processing..." % info_sum)
print("============================================")
time_begin = time.time()
# Step 1.3: Get all apartments's name and links then dig them
threshold_min = 39
threshold_max = 50
for gov_apartment_line in gov_apartment_lines:
    if info_index < threshold_min:
        info_index = info_index + 1
        continue
        pass
    elif info_index > threshold_max:
        break
        pass
    apartment = Apartment()
    # region Step 1.4: Prepare the apartment's header
    gov_apartment_line = str(gov_apartment_line)
    gov_apartment_name = BeautifulSoup(gov_apartment_line, 'html.parser').getText()
    gov_apartment_link = gov_apartment_link_finder.findall(gov_apartment_line)
    if gov_apartment_link:
        gov_apartment_link = gov_apartment_link[0]  # The first one is the right link
        pass
    apartment.gov_apartment.append(gov_apartment_name.replace('\n', ''))

    info_index = info_index + 1
    print("The ", info_index, "('st) item: ", gov_apartment_name, "| and completed: ",
          info_index/info_sum*100, "%.")
    # endregion

    # region Step 2: Gather information from the detail link
    # Step 2.1: Get the content from child page
    child_link = root_link + gov_apartment_link
    child_page = getLinkContent(child_link)
    classes_links = gov_apartment_classes_finder.findall(child_page)
    if len(classes_links) != 5:
        continue
        pass
    # endregion

    # region Step 3: Get the duty information from the child page
    if debug_mode:
        duty_link = child_link + classes_links[0]
        duty_page = getLinkContent(duty_link)

        page_sum = gov_apartment_page_sum_finder.findall(duty_page)
        if page_sum:
            page_sum = int(page_sum[0])
            pass
        else:
            page_sum = 1
            pass
        for index_num in range(page_sum):
            index = 'index'
            if index_num == 0:
                index = ''
            else:
                index = index + '_' + str(index_num) + '.html'
                pass
            duty_page = getLinkContent(duty_link + index)

            duty_page = duty_page.replace('</p>', '<br />')
            duty_temp = BeautifulSoup(duty_page, 'html.parser').find_all('td', {'class': 'dis2'})
            if duty_temp:
                duty_info = duty_temp[0]
                duty_info = replaceStr(str(duty_info))
                duties = gov_apartment_duties_finder.findall(duty_info)
                if len(duties) == 1:
                    temp_str = duties[0]
                    tmp_finder = re.compile("normal;\">(.*?)。")
                    tmp_rlt = tmp_finder.findall(duty_page)
                    for t in tmp_rlt:
                        if t.find("widow-orphan") != -1:
                            tmp1_finder = re.compile("EN-US>\)</span>(.*?)BB")
                            tmp1_rlt = tmp1_finder.findall(t)
                            if tmp1_rlt:
                                t = tmp1_rlt[0]
                            else:
                                t = ''
                            pass
                        if t != '':
                            apartment.duties.append(t)
                            pass
                    pass
                else:
                    for d in duties:
                        if d != 'BB':
                            t = d.replace('\"', '').replace('\n', '')
                            if t.find("widow-orphan") != -1:
                                tmp1_finder = re.compile("EN-US>\)</span>(.*?)BB")
                                tmp1_rlt = tmp1_finder.findall(t + 'BB')
                                if tmp1_rlt:
                                    t = tmp1_rlt[0]
                                else:
                                    t = ''
                                pass
                            if t != '':
                                apartment.duties.append(t)
                                pass
                            pass
                        pass
                    pass
                pass
            pass
        print("          Step 3 completed.")
        pass
    # endregion

    # region Step 4：Get the bounder information from the child page
    if debug_mode:
        # Step 4.1: Gather all sub links of bounder
        bounder_link = root_link + classes_links[1]
        bounder_page = getLinkContent(bounder_link)

        page_sum = gov_apartment_page_sum_finder.findall(bounder_page)
        if page_sum:
            page_sum = int(page_sum[0])
            pass
        else:
            page_sum = 1
            pass
        print("                 Total page: ", page_sum)
        index_tmp = 0

        for index_num in range(page_sum):
            index = 'index'
            if index_num == 0:
                index = ''
            else:
                index = index + '_' + str(index_num) + '.html'
                pass
            bounder_page = getLinkContent(bounder_link + index)

            bounder_soup = BeautifulSoup(bounder_page, 'html.parser')
            bounder_trs = bounder_soup.find_all(name='tr')
            # Step 4.2 Query all sub pages and continue gather information
            for bounder_tr in bounder_trs:
                index_tmp = index_tmp + 1
                print("                 Current index: ", index_tmp)
                bounder_sub_links = gov_apartment_bounder_finder.findall(str(bounder_tr))
                if not bounder_sub_links:
                    continue
                    pass
                bounder_sub_link = bounder_link + bounder_sub_links[0]
                bounder_sub_page = getLinkContent(bounder_sub_link)
                # Step 4.1 Get bounder detail page's content and deal with the table

                # Step 4.2 Gather and classify all tds into new_line object
                bounder = Bounder()
                bounder_sub_tds = BeautifulSoup(bounder_sub_page, 'html.parser').find_all('td')
                bounder_sub_items = []
                for bounder_sub_td in bounder_sub_tds:
                    bounder_sub_items.append(str(BeautifulSoup(str(bounder_sub_td), 'html.parser').getText()))
                    pass
                if len(bounder_sub_items) < 7:
                    continue
                    pass
                for i in range(6):
                    bounder_sub_items.pop(0)
                    pass
                manage_option = str(bounder_sub_items.pop(0))
                if manage_option.find('TRS_PreAppend') == -1:
                    bounder.manage_options.append(manage_option.replace('\"', '').replace('\n', ''))
                if len(bounder_sub_items) % 3 == 0:
                    while bounder_sub_items:
                        bounder.about_apartments.append(bounder_sub_items.pop(0).replace('\"', '').replace('\n', ''))
                        bounder.duties.append(bounder_sub_items.pop(0).replace('\"', '').replace('\n', ''))
                        bounder.about_depends.append(bounder_sub_items.pop(0).replace('\"', '').replace('\n', ''))
                        pass
                    pass

                apartment.bounders.append(bounder)
                pass
            pass
        print("          Step 4 completed.")
        pass
    # endregion

    # region Step 5: Get all responsibilities and dependencies from the child page
    if debug_mode:
        rd_link = child_link + classes_links[2]
        rd_page = getLinkContent(rd_link)

        page_sum = gov_apartment_page_sum_finder.findall(rd_page)
        if page_sum:
            page_sum = int(page_sum[0])
            pass
        else:
            page_sum = 1
            pass
        print("                 Total page: ", page_sum)
        index_tmp = 0
        for index_num in range(page_sum):
            index = 'index'
            if index_num == 0:
                index = ''
            else:
                index = index + '_' + str(index_num) + '.html'
                pass
            rd_page = getLinkContent(rd_link + index)

            rd_soup = BeautifulSoup(rd_page, 'html.parser')
            rd_trs = rd_soup.find_all(name='tr')
            # Step 4.2 Query all sub pages and continue gather information
            for rd_tr in rd_trs:
                index_tmp = index_tmp + 1
                print("                 Current index: ", index_tmp)
                rd_sub_links = gov_apartment_bounder_finder.findall(str(rd_tr))
                if not rd_sub_links:
                    continue
                    pass
                rd_sub_link = rd_sub_links[0]
                if rd_sub_link.find("../../../") != -1:  # avoid wrong link
                    continue
                    pass
                rd_sub_link = rd_link + rd_sub_link
                rd_sub_page = getLinkContent(rd_sub_link)
                # Step 4.3: Open sub page and gather information from the table
                rd_sub_tds = BeautifulSoup(rd_sub_page, 'html.parser').find_all('td')
                rd_sub_items = []
                for rd_sub_td in rd_sub_tds:
                    rd_sub_items.append(str(BeautifulSoup(str(rd_sub_td), 'html.parser').getText()))
                    pass
                if len(rd_sub_items) == 5:
                    responsibilities_str = replaceStr(str(rd_sub_items[2]))
                    responsibilities = gov_apartment_rd_item_finder.findall(responsibilities_str)
                    for r in responsibilities:
                        if r.find("TRS_PreAppend") == -1:   # avoid some errors
                            apartment.responsibilities.append(r.replace('\"', '').replace('\n', ''))
                        pass
                    dependencies_str = replaceStr(str(rd_sub_items[4]))
                    dependencies = gov_apartment_rd_item_finder.findall(dependencies_str)
                    for d in dependencies:
                        apartment.dependencies.append(d.replace('\"', '').replace('\n', ''))
                        pass
                    pass
                pass
            pass
        print("          Step 5 completed.")
        pass
    # endregion

    # region Step 6: Get management rules information from the child page
    if debug_mode:
        manage_rules_link = child_link + classes_links[3]
        manage_rules_page = getLinkContent(manage_rules_link)

        page_sum = gov_apartment_page_sum_finder.findall(manage_rules_page)
        if page_sum:
            page_sum = int(page_sum[0])
            pass
        else:
            page_sum = 1
            pass
        for index_num in range(page_sum):
            index = 'index'
            if index_num == 0:
                index = ''
            else:
                index = index + '_' + str(index_num) + '.html'
                pass
            manage_rules_page = getLinkContent(manage_rules_link + index)

            manage_rules = BeautifulSoup(manage_rules_page, 'html.parser').find_all('td')
            for manage_rule in manage_rules:
                tmp_str = BeautifulSoup(str(manage_rule), 'html.parser').getText()
                tmp_rlt = tmp_str.split(']')
                if len(tmp_rlt) == 2:
                    apartment.manage_rules.append(tmp_rlt[1].replace('\"', '').replace('\n', ''))
                    pass
                pass
            pass
        print("          Step 6 completed.")
        pass
    # endregion

    # region Step 7: Get general information from the child page
    if debug_mode:
        general_details_link = child_link + classes_links[4]
        general_details_page = getLinkContent(general_details_link)

        page_sum = gov_apartment_page_sum_finder.findall(general_details_page)
        if page_sum:
            page_sum = int(page_sum[0])
            pass
        else:
            page_sum = 1
            pass
        for index_num in range(page_sum):
            index = 'index'
            if index_num == 0:
                index = ''
            else:
                index = index + '_' + str(index_num) + '.html'
                pass
            general_details_page = getLinkContent(general_details_link + index)

            general_details_tds = BeautifulSoup(general_details_page, 'html.parser').find_all('td')
            general_details_items = []
            for general_details_td in general_details_tds:
                general_details_items.append(BeautifulSoup(str(general_details_td), 'html.parser').getText())
                pass

            if len(general_details_items) < 8:
                continue
                pass
            for i in range(8):
                general_details_items.pop(0)
                pass
            service = Service()
            if len(general_details_items) % 5 == 0:
                while general_details_items:
                    general_details_items.pop(0)
                    service.service_options.append(general_details_items.pop(0).replace('\"', '').replace('\n', ''))
                    service.main_contents.append(general_details_items.pop(0).replace('\"', '').replace('\n', ''))
                    service.organizations.append(general_details_items.pop(0).replace('\"', '').replace('\n', ''))
                    general_details_items.pop(0)
                    pass
                apartment.services.append(service)
                pass
            pass
        print("          Step 7 completed.")
        pass
    # endregion

    # apartments.append(apartment)
    writeNewLineToFile([apartment], file_csv_name)
    gc.collect()    # recycle the memory

    pass

# region Step7: Write all apartments' information into csv file
# writeNewLineToFile(apartments, file_csv_name)
time_end = time.time()
print("All completed, used time: ", time_end - time_begin, " s.")
# endregion
