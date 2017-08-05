# -*- coding: gb2312 -*-
from urllib import request
from urllib import error
from bs4 import BeautifulSoup
import csv
import re
import time

# region global parameters
debug_mode = True
root_link = "http://www.henan.gov.cn/zwgk/"
decode_type = "gb2312"
file_txt = open("../data/rlt_gov.txt", 'w', encoding='utf-8')
file_csv_name = "../data/rlt_gov.csv"
head_line = ['省政府分部门', '主要职责', '具体工作事项', '具体处室',
             '备注', '管理事项', '相关部门', '职责分工', '相关依据',
             '事中事后管理制度', '服务事项', '主要内容', '承办机构']
file_txt.write(",".join(head_line))
# endregion


# region main classes
class Apartment(object):
    def __init__(self):
        self.apartment_names = []
        self.seq_numbers = []
        self.duty_names = []
        self.sub_items = []
        self.dependence = []
        self.stage_names = []
        self.matters = []
        self.offices = []
        self.promise_spans = []
        self.law_spans = []
        self.payments = []
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
        try:
            page = page.decode(decode_type)
        except UnicodeDecodeError as reason:
            page = ''
            print(reason)
            pass
        page = str(page)
    except error.HTTPError as reason:
        page = ''
        print(reason)
        pass
    return page
# --------------------------------------------------------------------


# --------------------------------------------------------------------
# Sub-function to help reduce the lines of code
def addNullStringToList(a_list=[], num=0):
    for i in range(num):
        a_list.append('')
        pass
    return a_list


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
    l_apartment_name = []
    l_seq_number = []
    l_duty_name = []
    l_sub_item = []
    l_dependence = []
    l_stage_name = []
    l_matter = []
    l_office = []
    l_promise_span = []
    l_law_span = []
    l_payment = []
    for line in lines:
        while True:
            end_flag = True

            l_apartment_name, end_flag = writeElementToList(line.apartment_names, l_apartment_name, end_flag)
            l_seq_number, end_flag = writeElementToList(line.seq_numbers, l_seq_number, end_flag)
            l_duty_name, end_flag = writeElementToList(line.duty_names, l_duty_name, end_flag)
            l_sub_item, end_flag = writeElementToList(line.sub_items, l_sub_item, end_flag)
            l_dependence, end_flag = writeElementToList(line.dependence, l_dependence, end_flag)
            l_stage_name, end_flag = writeElementToList(line.stage_names, l_stage_name, end_flag)
            l_matter, end_flag = writeElementToList(line.matters, l_matter, end_flag)
            l_office, end_flag = writeElementToList(line.offices, l_office, end_flag)
            l_promise_span, end_flag = writeElementToList(line.promise_spans, l_promise_span, end_flag)
            l_law_span, end_flag = writeElementToList(line.law_spans, l_law_span, end_flag)
            l_payment, end_flag = writeElementToList(line.payments, l_payment, end_flag)

            if end_flag:
                break
            pass
        pass

    text_list = [l_apartment_name, l_seq_number, l_duty_name, l_sub_item,
                 l_dependence, l_stage_name, l_matter, l_office,
                 l_promise_span, l_law_span, l_payment]

    # Like matrix's transpose
    text_list = list(zip(*text_list))
    if sum([len(ii) for ii in text_list[-1]]) == 0:
        text_list.pop(-1)

    with open(file=filename, mode='a', encoding=decode_type, newline='') as file_csv:
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
gov_apartment_line_finder = re.compile("href=\"/zwgk/z(.*?)</li>")
gov_apartment_link_finder = re.compile("rqd(.*?)\"")
gov_apartment_name_finder = re.compile(">(.*?)</a")

gov_apartment_detail_finder = re.compile("</div><a href=\"(.*?)\"")
######################################################################
# endregion

# Step 1: Gather information from the root page
# Step 1.1: Get the content of root page
root_page = getLinkContent(root_link + 'qlqd/')

# Step 1.2: From the root page get all gov apartments' name and its link
gov_apartment_lines = gov_apartment_line_finder.findall(root_page)
info_sum = len(gov_apartment_lines)
info_index = 0
print("The Total list is %d, begin processing..." % info_sum)
print("============================================")
time_begin = time.time()
threshold_min = 5
threshold_max = 10
# Step 1.3: Get all apartments's name and links then dig them
for gov_apartment_line in gov_apartment_lines:
    if info_index < threshold_min:
        info_index = info_index + 1
        continue
        pass
    elif info_index > threshold_max:
        break
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
    apartment.apartment_names.append(gov_apartment_name)

    info_index = info_index + 1
    print("The ", info_index, "('st) item: ", gov_apartment_name, "| and completed: ",
          info_index/info_sum*100, "%.")
    # endregion

    # region Step 2: Gather information from the detail link
    # Step 2.1: Get the content from child page
    child_link = root_link + 'zrqd' + gov_apartment_link
    child_link = 'http://www.henan.gov.cn/zwgk/zrqd/gat/'
    child_page = getLinkContent(child_link)
    print("          Step 2 completed.")
    # endregion

# TODO: Some error here and not for all pass
    # region Step 3: Get the detail pages from the child page
    if debug_mode:
        detail_links = gov_apartment_detail_finder.findall(child_page)
        detail_index = 0
        for detail_link in detail_links:
            success_flag = False
            detail_index = detail_index + 1
            print('             Begin dealing with ', detail_index, ' ...')
            print('             Link is ', detail_link)
            # detail_link = 'http://www.henan.gov.cn/zwgk/system/2015/10/31/010597737.shtml'
            detail_page = getLinkContent(detail_link)
            detail_trs = BeautifulSoup(detail_page, 'html.parser').find_all('tr')
            if len(detail_trs) > 3:
                tds = BeautifulSoup(str(detail_trs[3]), 'html.parser').find_all('td')
                if tds:
                    td_text = BeautifulSoup(str(tds[0]), 'html.parser').getText()
                    item_list = []
                    items_raw = td_text.split('\n\n')
                    if len(items_raw) > 5:
                        for items in items_raw:
                            item_tmp = items.split('\n')
                            item_tmp1 = []
                            for tmp in item_tmp:
                                if tmp != '':
                                    tmp = tmp.replace('\xa0', ' ').replace('\r', '')
                                    if tmp[0:5] == '     ':
                                        item_tmp1[-1] = item_tmp1[-1] + tmp.replace(' ', '')
                                    else:
                                        item_tmp1.append(tmp)
                            if item_tmp1:
                                item_list.append(item_tmp1)
                                pass
                            pass
                        pass
                    for ii in item_list:
                        print(ii)
                        pass
                    while item_list and '序号' not in item_list[0]:
                        item_list.pop(0)
                    tmp_list = []
                    while item_list and '收费情况及依据' not in item_list[0]:
                        tmp_list = tmp_list + item_list.pop(0)
                    if item_list:
                        item_list[0] = tmp_list + item_list[0]
                    else:
                        item_list.append(tmp_list)
                    if not item_list:   # error item
                        continue
                    header = item_list.pop(0)
                    sub_item_flag = '子项' in header
                    first_row_flag = True
                    while item_list:
                        item_row = item_list.pop(0)

                        if '服务电话' in item_row[0]:
                            break
                        if '受理地点' in item_row[0]:
                            break
                        if first_row_flag is True:
                            if len(item_row) < 2:
                                while (item_row and ('不收费' not in item_row[-1]) and item_list) \
                                        or (not item_row and item_list):
                                    item_row = item_row + item_list.pop(0)
                            apartment.seq_numbers.append(item_row.pop(0))
                            apartment.duty_names.append(item_row.pop(0))
                            if sub_item_flag is True:
                                apartment.sub_items.append(item_row.pop(0))
                            while (item_row and ('不收费' not in item_row[-1] and len(item_row[-1]) > 4) and item_list)\
                                    or (not item_row and item_list):
                                item_row = item_row + item_list.pop(0)
                            apartment.payments.append(item_row.pop(-1))
                            while item_row and len(item_row[0]) != len('受理'):
                                apartment.dependence.append(item_row.pop(0))
                            first_row_flag = False
                            if not item_row:
                                break
                            pass
                        while len(item_row) < 5 and item_list:
                            item_row = item_row + item_list.pop(0)
                            if item_list and ('日' not in item_list[0]) and len(item_row) == 4:
                                break
                        apartment.stage_names.append(item_row.pop(0))
                        apartment.matters.append(item_row.pop(0))
                        apartment.offices.append(item_row.pop(0))
                        if item_row:
                            apartment.promise_spans.append(item_row.pop(0))
                        if item_row:
                            apartment.law_spans.append(item_row.pop(0))
                        pass

            # apartments.append(apartment)
            writeNewLineToFile([apartment])
        pass
    pass

# region Step7: Write all apartments' information into csv file
# writeNewLineToFile(apartments, file_csv_name)
time_end = time.time()
print("All completed, used time: ", time_end - time_begin, " s.")
# endregion
