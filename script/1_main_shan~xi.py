# -*- coding: utf-8 -*-
from urllib import request
from bs4 import BeautifulSoup
import csv
import re
import time

# region global parameters
debug_mode = True
root_link = "http://qzqd.shaanxi.gov.cn/smp/jsp/portals/index.jsp"
decode_type = "utf-8"
file_txt = open("../data/rlt_gov.txt", 'w', encoding='utf-8')
file_csv_name = "../data/rlt_gov.csv"
head_line = ['省政府分部门', '主要职责', '具体工作事项', '具体处室',
             '备注', '管理事项', '相关部门', '职责分工', '相关依据',
             '事中事后管理制度', '服务事项', '主要内容', '承办机构']
file_txt.write(",".join(head_line))
# endregion


# TODO: The remote server is made by jsp, need the js.lib to
# TODO: deal with and run the js code to get the result, out of my
# TODO: computer configuration
# region general functions
# --------------------------------------------------------------------
# Get the link's content and return its content as a multi-line string
def getLinkContent(link):
    response = request.urlopen(link)
    page = response.read()
    page = page.decode(decode_type)
    page = str(page)
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
            if line.duties and not duty.remarks and not duty.offices\
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
            l_office, end_flag = writeElementToList(duty.offices, l_office, end_flag)
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
# endregion

# region some re block and key words finder
######################################################################
gov_apartment_line_finder = re.compile("/review/dutyIndex(.*?)\n")
gov_apartment_link_finder = re.compile("do(.*?)\">")
gov_apartment_name_finder = re.compile("省(.*?)\r")

gov_apartment_duty_finder = re.compile("review/deptDutyDetails(.*?)\"")
gov_apartment_bounder_finder = re.compile("review/reviewDeptNexusDetails(.*?)\"")
gov_apartment_manage_finder = re.compile("<td><a title=\"(.*?)\"")
gov_apartment_general_finder = re.compile("<td align=\"left\" style=\"border(.*?)</td>")
######################################################################
# endregion

# Step 1: Gather information from the root page
# Step 1.1: Get the content of root page
root_page = getLinkContent(root_link)

# Step 1.2: From the root page get all gov apartments' name and its link
gov_apartment_lines = gov_apartment_line_finder.findall(root_page)
info_sum = len(gov_apartment_lines)
info_index = 0
print("The Total list is %d, begin processing..." % info_sum)
print("============================================")
time_begin = time.time()
# Step 1.3: Get all apartments's name and links then dig them
for gov_apartment_line in gov_apartment_lines:
    pass
