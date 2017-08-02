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
class Stage(object):
    def __init__(self):
        stage_name = ''
        matter = ''
        office = ''
        promise_span = ''
        law_span = ''
        pass
    pass


class ItemTable(object):
    def __init__(self):
        self.seq_num = ''
        self.name = ''
        self.child = ''
        self.dependence = ''
        self.stages = []
        self.payment = ''
        pass
    pass


class Apartment(object):
    def __init__(self):
        self.gov_apartment = ''
        self.item_tables = []
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
    l_department_name = []
    l_seq_num = []
    l_name = []
    l_child = []
    l_dependence = []
    l_stage_name = []
    l_matter = []
    l_office = []
    l_promise_span = []
    l_law_span = []
    l_payment = []
    for line in lines:
        l_department_name.append(line.gov_apartment)
        l_department_name = addNullStringToList(l_department_name, 6 * (len(line.item_tables)) - 1)
        for item in line.item_tables:
            l_seq_num.append(item.seq_num.replace('\xa0', ''))
            l_seq_num = addNullStringToList(l_seq_num, 5)
            l_name.append(item.name.replace('\xa0', ''))
            l_name = addNullStringToList(l_name, 5)
            l_child.append(item.child.replace('\xa0', ''))
            l_child = addNullStringToList(l_child, 5)
            l_payment.append(item.payment.replace('\xa0', ''))
            l_payment = addNullStringToList(l_payment, 5)
            l_dependence.append(item.dependence.replace('\xa0', ''))
            l_dependence = addNullStringToList(l_dependence, 5)
            for stage in item.stages:
                l_stage_name.append(stage.stage_name.replace('\xa0', ''))
                l_matter.append(stage.matter.replace('\xa0', ''))
                l_office.append(stage.office.replace('\xa0', ''))
                l_promise_span.append(stage.promise_span.replace('\xa0', ''))
                l_law_span.append(stage.law_span.replace('\xa0', ''))
                pass
            if not item.stages:
                for ii in range(6):
                    l_stage_name.append('')
                    l_matter.append('')
                    l_office.append('')
                    l_promise_span.append('')
                    l_law_span.append('')
                    pass
                pass
            pass
        pass
    text_list = [l_department_name, l_seq_num, l_name, l_child,
                 l_dependence, l_stage_name, l_matter, l_office,
                 l_promise_span, l_law_span, l_payment]

    # Like matrix's transpose
    text_list = list(zip(*text_list))

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
threshold_min = 42
threshold_max = 60
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
    apartment.gov_apartment = gov_apartment_name

    info_index = info_index + 1
    print("The ", info_index, "('st) item: ", gov_apartment_name, "| and completed: ",
          info_index/info_sum*100, "%.")
    # endregion

    # region Step 2: Gather information from the detail link
    # Step 2.1: Get the content from child page
    child_link = root_link + 'zrqd' + gov_apartment_link
    child_page = getLinkContent(child_link)
    print("          Step 2 completed.")
    # endregion

    # region Step 3: Get the detail pages from the child page
    if debug_mode:
        detail_links = gov_apartment_detail_finder.findall(child_page)
        detail_index = 0
        for detail_link in detail_links:
            success_flag = False
            detail_index = detail_index + 1
            print('             Begin dealing with ', detail_index, ' ...')
            print('             Link is ', detail_link)
            # detail_link = 'http://www.henan.gov.cn/zwgk/system/2015/10/23/010593851.shtml'
            detail_page = getLinkContent(detail_link)
            detail_tds = BeautifulSoup(detail_page, 'html.parser').find_all('td')
            detail_items = []
            for detail_td in detail_tds:
                detail_items.append(BeautifulSoup(str(detail_td), 'html.parser').getText())
                pass
            item_table = ItemTable()
            while detail_items and detail_items.pop(0) != '收费情况\r\n            及依据':
                pass
            if len(detail_items) > 33:
                success_flag = True
                item_table.seq_num = detail_items[0].replace('\"', '').replace('\n', '').replace('\r', '')
                item_table.name = detail_items[1].replace('\"', '').replace('\n', '').replace('\r', '')
                item_table.child = detail_items[2].replace('\"', '').replace('\n', '').replace('\r', '')
                item_table.dependence = detail_items[3].replace('\"', '').replace('\n', '').replace('\r', '')
                item_table.payment = detail_items[9].replace('\"', '').replace('\n', '').replace('\r', '')
                stage1 = Stage()
                stage1.stage_name = detail_items[4].replace('\"', '').replace('\n', '').replace('\r', '')
                stage1.matter = detail_items[5].replace('\"', '').replace('\n', '').replace('\r', '')
                stage1.office = detail_items[6].replace('\"', '').replace('\n', '').replace('\r', '')
                stage1.promise_span = detail_items[7].replace('\"', '').replace('\n', '').replace('\r', '')
                stage1.law_span = detail_items[8].replace('\"', '').replace('\n', '').replace('\r', '')
                item_table.stages.append(stage1)
                stage2 = Stage()
                stage2.stage_name = detail_items[10].replace('\"', '').replace('\n', '').replace('\r', '')
                stage2.matter = detail_items[11].replace('\"', '').replace('\n', '').replace('\r', '')
                stage2.office = detail_items[12].replace('\"', '').replace('\n', '').replace('\r', '')
                stage2.promise_span = detail_items[13].replace('\"', '').replace('\n', '').replace('\r', '')
                stage2.law_span = detail_items[14].replace('\"', '').replace('\n', '').replace('\r', '')
                item_table.stages.append(stage2)
                stage3 = Stage()
                stage3.stage_name = detail_items[15].replace('\"', '').replace('\n', '').replace('\r', '')
                stage3.matter = detail_items[16].replace('\"', '').replace('\n', '').replace('\r', '')
                stage3.office = detail_items[17].replace('\"', '').replace('\n', '').replace('\r', '')
                stage3.promise_span = detail_items[18].replace('\"', '').replace('\n', '').replace('\r', '')
                stage3.law_span = '与审查共用'
                item_table.stages.append(stage3)
                stage4 = Stage()
                stage4.stage_name = detail_items[19].replace('\n', '').replace('\r', '')
                stage4.matter = detail_items[20].replace('\n', '').replace('\r', '')
                stage4.office = detail_items[21].replace('\n', '').replace('\r', '')
                stage4.promise_span = detail_items[22].replace('\n', '').replace('\r', '')
                stage4.law_span = detail_items[23].replace('\n', '').replace('\r', '')
                item_table.stages.append(stage4)
                stage5 = Stage()
                stage5.stage_name = detail_items[24].replace('\n', '').replace('\r', '')
                stage5.matter = detail_items[25].replace('\n', '').replace('\r', '')
                stage5.office = detail_items[26].replace('\n', '').replace('\r', '')
                stage5.promise_span = detail_items[27].replace('\n', '').replace('\r', '')
                stage5.law_span = detail_items[28].replace('\n', '').replace('\r', '')
                item_table.stages.append(stage5)
                stage6 = Stage()
                stage6.stage_name = detail_items[29].replace('\n', '').replace('\r', '')
                stage6.matter = detail_items[30].replace('\n', '').replace('\r', '')
                stage6.office = detail_items[31].replace('\n', '').replace('\r', '')
                stage6.promise_span = detail_items[32].replace('\n', '').replace('\r', '')
                stage6.law_span = detail_items[33].replace('\n', '').replace('\r', '')
                item_table.stages.append(stage6)
                pass
            if success_flag:
                apartment.item_tables.append(item_table)
                pass
            pass
        print('             writing to file ...')
        writeNewLineToFile([apartment], file_csv_name)
        pass
    pass

# region Step7: Write all apartments' information into csv file
# writeNewLineToFile(apartments, file_csv_name)
time_end = time.time()
print("All completed, used time: ", time_end - time_begin, " s.")
# endregion
