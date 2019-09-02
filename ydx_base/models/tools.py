# -*- coding: utf-8 -*-
import random
import string


def single_get_first(unicode):
    str1 = unicode.encode('gbk')
    try:
        ord(str1)
        return unicode
    except:
        asc = str1[0] * 256 + str1[1] - 65536
        if asc >= -20319 and asc <= -20284:
            return 'a'
        if asc >= -20283 and asc <= -19776:
            return 'b'
        if asc >= -19775 and asc <= -19219:
            return 'c'
        if asc >= -19218 and asc <= -18711:
            return 'd'
        if asc >= -18710 and asc <= -18527:
            return 'e'
        if asc >= -18526 and asc <= -18240:
            return 'f'
        if asc >= -18239 and asc <= -17923:
            return 'g'
        if asc >= -17922 and asc <= -17418:
            return 'h'
        if asc >= -17417 and asc <= -16475:
            return 'j'
        if asc >= -16474 and asc <= -16213:
            return 'k'
        if asc >= -16212 and asc <= -15641:
            return 'l'
        if asc >= -15640 and asc <= -15166:
            return 'm'
        if asc >= -15165 and asc <= -14923:
            return 'n'
        if asc >= -14922 and asc <= -14915:
            return 'o'
        if asc >= -14914 and asc <= -14631:
            return 'p'
        if asc >= -14630 and asc <= -14150:
            return 'q'
        if asc >= -14149 and asc <= -14091:
            return 'r'
        if asc >= -14090 and asc <= -13119:
            return 's'
        if asc >= -13118 and asc <= -12839:
            return 't'
        if asc >= -12838 and asc <= -12557:
            return 'w'
        if asc >= -12556 and asc <= -11848:
            return 'x'
        if asc >= -11847 and asc <= -11056:
            return 'y'
        if asc >= -11055 and asc <= -10247:
            return 'z'
        return ''


def getPinyin(string):
    if string == "":
        return ""
    shortname = ""
    lst = list(string)
    charLst = []
    for l in lst:
        charLst.append(single_get_first(l))

    for i in charLst:
        shortname = shortname + i

    return shortname


def Num2MoneyFormat(self, change_number):
    """
    .转换数字为大写货币格式( format_word.__len__() - 3 + 2位小数 )
    change_number 支持 float, int, long, string
    :return string
    """
    format_word = ["分", "角", "元",
                   "拾", "佰", "仟", "万",
                   "拾", "佰", "仟", "亿",
                   "拾", "佰", "仟", "万",
                   "拾", "佰", "仟", "兆"]

    format_num = ["零", "壹", "贰", "叁", "肆", "伍", "陆", "柒", "捌", "玖"]

    if type(change_number) == str:
        # - 如果是字符串,先尝试转换成float或int.
        if '.' in change_number:
            try:
                change_number = float(change_number)
            except:
                raise ValueError
        else:
            try:
                change_number = int(change_number)
            except:
                raise ValueError

    zf = ''
    if change_number < 0:
        change_number = abs(change_number)
        zf = '负'
    if type(change_number) == float:
        real_numbers = []
        for i in range(len(format_word) - 3, -3, -1):
            if change_number >= 10 ** i or i < 1:
                real_numbers.append(int(round(change_number / (10 ** i), 2) % 10))

    elif isinstance(change_number, (int)):
        real_numbers = [int(i) for i in str(change_number) + '00']

    else:
        raise ValueError

    zflag = 0  # 标记连续0次数，以删除万字，或适时插入零字
    start = len(real_numbers) - 3
    change_words = []
    for i in range(start, -3, -1):  # 使i对应实际位数，负数为角分
        if 0 != real_numbers[start - i] or len(change_words) == 0:
            if zflag:
                change_words.append(format_num[0])
                zflag = 0
            change_words.append(format_num[real_numbers[start - i]])
            change_words.append(format_word[i + 2])

        elif 0 == i or (0 == i % 4 and zflag < 3):  # 控制 万/元
            change_words.append(format_word[i + 2])
            zflag = 0
        else:
            zflag += 1

    if change_words[-1] not in (format_word[0], format_word[1]):
        # - 最后两位非"角,分"则补"整"
        change_words.append("整")

    return zf + ''.join(change_words)


def get_random_string():
    """
    生成随机的四位小写字母字符串
    :return:
    """
    return ''.join(random.sample(string.ascii_lowercase, 4))
