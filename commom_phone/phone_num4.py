import re

def phone_num(n):
    # n = input("请输入一个手机号：")
    if re.match(r'1[34578]\d{9}', n):
        # print("您输入的的手机号码是：\n", n)
        # 中国联通：
        # 130，131，132，155，156，185，186，145，176
        if re.match(r'13[012]\d{8}', n) or \
                re.match(r"15[56]\d{8}", n) or \
                re.match(r"18[56]", n) or \
                re.match(r"145\d{8}", n) or \
                re.match(r"176\d{8}", n):
            print("该号码属于：中国联通")
            return "该号码属于：中国联通"
        # 中国移动
        # 134, 135 , 136, 137, 138, 139, 147, 150, 151,
        # 152, 157, 158, 159, 178, 182, 183, 184, 187, 188；
        elif re.match(r"13[4,56789]\d{8}", n) or \
                re.match(r"147\d{8}|178\d{8}", n) or \
                re.match(r"15[012789]\d{8}", n) or \
                re.match(r"18[23478]\d{8}", n):
            print("该号码属于：中国移动")
            return "该号码属于：中国移动"
        else:
            # 中国电信
            # 133,153,189
            print("该号码属于：中国电信")
            return "该号码属于：中国电信"
    else:
        return "请输入正确的手机号"


if __name__ == '__main__':
    phone_num('')
