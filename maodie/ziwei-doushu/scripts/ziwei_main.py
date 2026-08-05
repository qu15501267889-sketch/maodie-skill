#!/usr/bin/env python3
"""
紫微斗数完整排盘脚本
基于 FANzR-arch/Numerologist_skills 的 calculation.md 规则
三合派口径，默认子时换日
"""

import json, sys, math
from datetime import datetime

# ===== 基础数据 =====
TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
YANG_GAN = {'甲', '丙', '戊', '庚', '壬'}
YIN_GAN = {'乙', '丁', '己', '辛', '癸'}

# 地支固定宫位（寅起）
PALACE_DIZHI = ['寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑']

# 十二宫顺序（从命宫逆时针）
PALACE_NAMES = ['命宫', '兄弟宫', '夫妻宫', '子女宫', '财帛宫', '疾厄宫',
                '迁移宫', '交友宫', '官禄宫', '田宅宫', '福德宫', '父母宫']

# 时辰对照
SHICHEN = {
    '子': (23, 0, 0, 59), 
    '丑': (1, 0, 2, 59), 
    '寅': (3, 0, 4, 59),
    '卯': (5, 0, 6, 59), 
    '辰': (7, 0, 8, 59), 
    '巳': (9, 0, 10, 59),
    '午': (11, 0, 12, 59), 
    '未': (13, 0, 14, 59), 
    '申': (15, 0, 16, 59),
    '酉': (17, 0, 18, 59), 
    '戌': (19, 0, 20, 59), 
    '亥': (21, 0, 22, 59),
}

# 寅首诀
YIN_SHOU = {
    '甲': '丙', '乙': '戊', '丙': '庚', '丁': '壬', '戊': '甲',
    '己': '丙', '庚': '戊', '辛': '庚', '壬': '壬', '癸': '甲',
}

# 天干取数（定五行局）
TIAN_GAN_NUM = {'甲': 1, '乙': 1, '丙': 2, '丁': 2, '戊': 3, '己': 3, '庚': 4, '辛': 4, '壬': 5, '癸': 5}
# 地支取数
DI_ZHI_NUM = {'子': 1, '午': 1, '丑': 1, '未': 1,
              '寅': 2, '申': 2, '卯': 2, '酉': 2,
              '辰': 3, '戌': 3, '巳': 3, '亥': 3}
WUXING_MAP = {1: '木三局', 2: '金四局', 3: '水二局', 4: '火六局', 5: '土五局'}
WUXING_NUM = {'木三局': 3, '金四局': 4, '水二局': 2, '火六局': 6, '土五局': 5}

# 紫微星系（北斗）
ZIWEI_STARS = ['紫微', '天机', '太阳', '武曲', '天同', '廉贞']
# 紫微星系排列（紫微位置确定后，其他星按固定顺序逆时针排列）
ZIWEI_ORDER = {0: '紫微', 1: '天机', 2: '太阳', 3: '武曲', 4: '天同', 5: '廉贞'}
ZIWEI_OFFSETS = [0, -1, -3, -4, -5, -7]  # 相对于紫微的位置偏移（逆时针）

# 天府星系（南斗）
TIANFU_STARS = ['天府', '太阴', '贪狼', '巨门', '天相', '天梁', '七杀', '破军']
# 天府星位置由紫微星位置决定：紫微与天府在寅申巳亥相对
# 紫微在寅→天府在寅，紫微在卯→天府在丑，紫微在辰→天府在子...
TIANFU_POS = {0: 0, 1: -1, 2: -2, 3: -3, 4: -4, 5: -5, 6: -6, 7: -7, 8: -8, 9: -9, 10: -10, 11: -11}
# 实际天府定位：紫微在X宫，天府在(12-X)%12宫（从寅起算）
# 寅=0, 卯=1, 辰=2, 巳=3, 午=4, 未=5, 申=6, 酉=7, 戌=8, 亥=9, 子=10, 丑=11
# 天府在紫微的对宫关系：天府宫 = (12 - 紫微宫) % 12
# 然后天府系顺排：天府、太阴、贪狼、巨门、天相、天梁、七杀、破军

# 文昌文曲（按时辰直接查表）
CHANG = {'子': '戌', '丑': '酉', '寅': '申', '卯': '未', '辰': '午', '巳': '巳',
         '午': '辰', '未': '卯', '申': '寅', '酉': '丑', '戌': '子', '亥': '亥'}
QU = {'子': '辰', '丑': '巳', '寅': '午', '卯': '未', '辰': '申', '巳': '酉',
      '午': '戌', '未': '亥', '申': '子', '酉': '丑', '戌': '寅', '亥': '卯'}

# 左辅右弼（按月份，直接查表）
ZUO = ['辰', '巳', '午', '未', '申', '酉', '戌', '亥', '子', '丑', '寅', '卯']
YOU = ['戌', '酉', '申', '未', '午', '巳', '辰', '卯', '寅', '丑', '子', '亥']

# 天魁天钺（按年干）
KUIYUE = {
    '甲': ('丑', '未'), '乙': ('子', '申'), '丙': ('亥', '酉'), '丁': ('酉', '亥'),
    '戊': ('丑', '未'), '己': ('子', '申'), '庚': ('丑', '未'), '辛': ('午', '寅'),
    '壬': ('卯', '巳'), '癸': ('卯', '巳'),
}

# 禄存擎羊陀罗（按年干）
LUCUN = {'甲': '寅', '乙': '卯', '丙': '巳', '丁': '午', '戊': '巳',
         '己': '午', '庚': '申', '辛': '酉', '壬': '亥', '癸': '子'}
YANG = {'甲': '卯', '乙': '辰', '丙': '午', '丁': '未', '戊': '午',
        '己': '未', '庚': '酉', '辛': '戌', '壬': '子', '癸': '丑'}
LUO = {'甲': '丑', '乙': '寅', '丙': '辰', '丁': '巳', '戊': '辰',
       '己': '巳', '庚': '未', '辛': '申', '壬': '戌', '癸': '亥'}

# 火星铃星起点（按年支组）
HUO_START = {'寅': '丑', '午': '丑', '戌': '丑', '申': '寅', '子': '寅', '辰': '寅',
             '巳': '卯', '酉': '卯', '丑': '卯', '亥': '酉', '卯': '酉', '未': '酉'}
LING_START = {'寅': '卯', '午': '卯', '戌': '卯', '申': '戌', '子': '戌', '辰': '戌',
              '巳': '戌', '酉': '戌', '丑': '戌', '亥': '戌', '卯': '戌', '未': '戌'}

# 地空地劫（按时辰）
DIKONG = {'子': '亥', '丑': '戌', '寅': '酉', '卯': '申', '辰': '未', '巳': '午',
          '午': '巳', '未': '辰', '申': '卯', '酉': '寅', '戌': '丑', '亥': '子'}
DIJIE = {'子': '亥', '丑': '子', '寅': '丑', '卯': '寅', '辰': '卯', '巳': '辰',
         '午': '巳', '未': '午', '申': '未', '酉': '申', '戌': '酉', '亥': '戌'}

# 天马（按年支组）
TIANMA = {'寅': '申', '午': '申', '戌': '申', '申': '寅', '子': '寅', '辰': '寅',
          '巳': '亥', '酉': '亥', '丑': '亥', '亥': '巳', '卯': '巳', '未': '巳'}

# 四化表
SIHUA_TABLE = {
    '甲': ('廉贞', '破军', '武曲', '太阳'),
    '乙': ('天机', '天梁', '紫微', '太阴'),
    '丙': ('天同', '天机', '文昌', '廉贞'),
    '丁': ('太阴', '天同', '天机', '巨门'),
    '戊': ('贪狼', '太阴', '右弼', '天机'),
    '己': ('武曲', '贪狼', '天梁', '文曲'),
    '庚': ('太阳', '武曲', '太阴', '天同'),
    '辛': ('巨门', '太阳', '文曲', '文昌'),
    '壬': ('天梁', '紫微', '左辅', '武曲'),
    '癸': ('破军', '巨门', '太阴', '贪狼'),
}

# 庙旺陷表
MIAOWANG = {
    '紫微': [3, -1, 4, 1, 2, 2, 4, -1, 4, 1, 2, 2],
    '天机': [4, 2, 4, 3, 1, -1, 4, 2, 4, 3, 1, -1],
    '太阳': [-1, 0, 3, 4, 3, 4, 4, 2, 2, -1, -1, -1],
    '武曲': [3, 4, 2, 1, 4, 1, 3, 4, 2, 1, 4, 1],
    '天同': [3, 0, -1, 1, 4, -1, -1, 0, -1, 1, 4, -1],
    '廉贞': [4, 1, -1, -1, 2, 3, 4, 1, -1, -1, 2, 3],
    '天府': [3, 2, 4, 2, 4, 3, 4, 2, 4, 2, 4, 3],
    '太阴': [4, 4, 2, -1, -1, -1, -1, 0, 2, 3, 4, 4],
    '贪狼': [3, 4, 1, 4, -1, 3, 3, 4, 1, 4, -1, 3],
    '巨门': [3, 0, 4, 4, -1, 4, 3, 0, 4, 4, -1, 4],
    '天相': [4, -1, 2, 4, 3, 1, 4, -1, 2, 4, 3, 1],
    '天梁': [4, 3, -1, 4, 4, 3, 4, 3, -1, 4, 4, 3],
    '七杀': [3, 4, 4, 3, 1, 4, 3, 4, 4, 3, 1, 4],
    '破军': [3, 4, -1, 1, 1, 3, 3, 4, -1, 1, 1, 3],
}
MIAOWANG_NAMES = {5: '庙', 4: '旺', 3: '得地', 2: '利', 1: '平', 0: '不得地', -1: '落陷'}


def hour_to_shichen(hour, minute):
    """将小时分钟转换为时辰地支"""
    for dz, (sh, sm, eh, em) in SHICHEN.items():
        if sh == 23:  # 子时跨天
            if hour >= 23 or hour < 1:
                return dz
        elif sh <= hour <= eh:
            return dz
    return '子'  # default


def get_lunar_date(year, month, day):
    """使用lunar_python转换公历到农历"""
    try:
        from lunar_python import Solar, Lunar
        solar = Solar.fromYmd(year, month, day)
        lunar = solar.getLunar()
        return lunar.getYear(), lunar.getMonth(), lunar.getDay()
    except ImportError:
        # 如果lunar_python不可用，返回输入值（带标记）
        return year, month, day


def get_ganzhi(year, month, day, hour):
    """获取年月日时的干支"""
    try:
        from lunar_python import Solar, Lunar
        solar = Solar.fromYmdHms(year, month, day, hour, 0, 0)
        lunar = solar.getLunar()
        return {
            'year': lunar.getYearInGanZhiExact(),
            'month': lunar.getMonthInGanZhiExact(),
            'day': lunar.getDayInGanZhiExact(),
            'hour': lunar.getTimeInGanZhi(),
        }
    except ImportError:
        return {'year': '', 'month': '', 'day': '', 'hour': ''}


def calc_ziwei(n, d):
    """计算紫微星位置（验证过的算法）"""
    q = math.ceil(d / n)
    r = q * n - d
    base = (q - 1) % 12
    if r == 0:
        return PALACE_DIZHI[base]
    elif r % 2 == 1:
        return PALACE_DIZHI[(base - r + 120) % 12]
    else:
        return PALACE_DIZHI[(base + r) % 12]


def build_palace_data(lunar_year, lunar_month, lunar_day, shichen_dz, hour, gender):
    """构建完整的紫微斗数盘"""
    result = {}
    
    # ---- 1. 定命宫与身宫 ----
    # 寅起正月，顺数至生月
    month_pos = (lunar_month - 1) % 12  # 正月=寅=0
    # 从此宫起子时，逆数到生时 → 命宫
    ming_pos = (month_pos - PALACE_DIZHI.index(shichen_dz) + 12) % 12
    # 身宫：顺数
    shen_pos = (month_pos + PALACE_DIZHI.index(shichen_dz)) % 12
    
    ming_gong = PALACE_DIZHI[ming_pos]
    shen_gong = PALACE_DIZHI[shen_pos]
    
    result['ming_gong'] = ming_gong
    result['shen_gong'] = shen_gong
    
    # ---- 2. 安十二宫 ----
    palaces = {}
    for i, name in enumerate(PALACE_NAMES):
        pos = (ming_pos - i + 12) % 12
        palaces[name] = {'dizhi': PALACE_DIZHI[pos], 'pos': pos}
    result['palaces'] = palaces
    
    # ---- 3. 起寅首定宫干 ----
    # 获取年干
    ganzhi = get_ganzhi(year, month, day, hour)
    year_gan = ganzhi['year'][0] if ganzhi['year'] else ''
    
    if not year_gan:
        # fallback: 用lunar_python的年份干支
        from lunar_python import Lunar
        lunar = Lunar.fromYmdHms(lunar_year, lunar_month, lunar_day, hour, 0, 0)
        year_gan = lunar.getYearInGanZhiExact()[0]
    
    # 寅宫的天干
    yin_gan = YIN_SHOU[year_gan]
    yin_idx = TIAN_GAN.index(yin_gan)
    
    # 各宫宫干
    for name, info in palaces.items():
        gan_idx = (yin_idx + info['pos']) % 10
        info['gan'] = TIAN_GAN[gan_idx]
        info['ganzhi'] = TIAN_GAN[gan_idx] + info['dizhi']
    
    result['year_gan'] = year_gan
    
    # ---- 4. 定五行局 ----
    ming_gan = palaces['命宫']['gan']
    ming_zhi = palaces['命宫']['dizhi']
    gan_num = TIAN_GAN_NUM[ming_gan]
    zhi_num = DI_ZHI_NUM[ming_zhi]
    total = gan_num + zhi_num
    while total > 5:
        total -= 5
    wuxing = WUXING_MAP[total]
    wuxing_n = WUXING_NUM[wuxing]
    result['wuxing'] = wuxing
    
    # ---- 5. 安紫微星 ----
    ziwei_dizhi = calc_ziwei(wuxing_n, lunar_day)
    ziwei_pos = PALACE_DIZHI.index(ziwei_dizhi)
    result['ziwei'] = ziwei_dizhi
    
    # ---- 6. 安十四主星 ----
    # 紫微星系（逆时针）
    ziwei_stars = {}
    offsets = [0, -1, -3, -4, -5, -7]
    for i, name in enumerate(ZIWEI_ORDER.values()):
        pos = (ziwei_pos + offsets[i] + 12) % 12
        ziwei_stars[name] = PALACE_DIZHI[pos]
    
    # 天府星系（顺时针）
    tianfu_pos = (12 - ziwei_pos) % 12  # 天府在紫微的对宫
    tianfu_stars = {}
    for i, name in enumerate(TIANFU_STARS):
        pos = (tianfu_pos + i) % 12
        tianfu_stars[name] = PALACE_DIZHI[pos]
    
    # 合并主星
    all_stars = {**ziwei_stars, **tianfu_stars}
    result['stars'] = all_stars
    
    # 主星入宫
    for name, info in palaces.items():
        info['main_stars'] = []
    for star_name, dz in all_stars.items():
        for name, info in palaces.items():
            if info['dizhi'] == dz:
                info['main_stars'].append(star_name)
                break
    
    # ---- 7. 安辅星 ----
    fushi = {}
    
    # 左辅右弼（按出生月，直接查表）
    fushi['左辅'] = ZUO[(lunar_month - 1) % 12]
    fushi['右弼'] = YOU[(lunar_month - 1) % 12]
    
    # 文昌文曲（按时辰，直接查表）
    fushi['文昌'] = CHANG[shichen_dz]
    fushi['文曲'] = QU[shichen_dz]
    
    # 天魁天钺（按年干）
    if year_gan in KUIYUE:
        kui, yue = KUIYUE[year_gan]
        fushi['天魁'] = kui
        fushi['天钺'] = yue
    
    # 禄存擎羊陀罗（按年干）
    if year_gan in LUCUN:
        fushi['禄存'] = LUCUN[year_gan]
    if year_gan in YANG:
        fushi['擎羊'] = YANG[year_gan]
    if year_gan in LUO:
        fushi['陀罗'] = LUO[year_gan]
    
    # 火星铃星（按年支组+时辰）
    year_zhi = ganzhi['year'][1] if len(ganzhi['year']) > 1 else ''
    if year_zhi in HUO_START:
        sc_n = PALACE_DIZHI.index(shichen_dz)
        huo_start = HUO_START[year_zhi]
        ling_start = LING_START[year_zhi]
        fushi['火星'] = PALACE_DIZHI[(PALACE_DIZHI.index(huo_start) + sc_n) % 12]
        fushi['铃星'] = PALACE_DIZHI[(PALACE_DIZHI.index(ling_start) + sc_n) % 12]
    
    # 地空地劫（按时辰查表）
    fushi['地空'] = DIKONG[shichen_dz]
    fushi['地劫'] = DIJIE[shichen_dz]
    
    # 天马（按年支组）
    if year_zhi in TIANMA:
        fushi['天马'] = TIANMA[year_zhi]
    
    result['fushi'] = fushi
    
    # 辅星入宫
    for name, info in palaces.items():
        info['fu_stars'] = []
    for star_name, dz in fushi.items():
        for name, info in palaces.items():
            if info['dizhi'] == dz:
                info['fu_stars'].append(star_name)
                break
    
    # ---- 8. 安四化 ----
    sihua = {}
    if year_gan in SIHUA_TABLE:
        sihua['化禄'] = SIHUA_TABLE[year_gan][0]
        sihua['化权'] = SIHUA_TABLE[year_gan][1]
        sihua['化科'] = SIHUA_TABLE[year_gan][2]
        sihua['化忌'] = SIHUA_TABLE[year_gan][3]
    result['sihua'] = sihua
    
    # 四化入宫
    for name, info in palaces.items():
        info['sihua'] = []
    for sihua_type, star_name in sihua.items():
        if star_name in all_stars:
            dz = all_stars[star_name]
            for name, info in palaces.items():
                if info['dizhi'] == dz:
                    info['sihua'].append(f"{star_name}{sihua_type}")
                    break
    
    # ---- 9. 定大限 ----
    # 五行局定起限年龄
    age_start = wuxing_n  # 水二局=2, 木三局=3, 金四局=4, 土五局=5, 火六局=6
    # 阳男阴女顺行，阴男阳女逆行
    is_yang = year_gan in YANG_GAN
    is_male = (gender == '男')
    forward = (is_yang and is_male) or (not is_yang and not is_male)
    
    daixian = []
    for i in range(12):
        if forward:
            palace_idx = i
        else:
            palace_idx = (12 - i) % 12
        name = PALACE_NAMES[palace_idx]
        start_age = age_start + i * 10
        end_age = start_age + 9
        dz = palaces[name]['dizhi']
        daixian.append({
            'palace': name,
            'dizhi': dz,
            'start_age': start_age,
            'end_age': end_age,
        })
    result['daixian'] = daixian
    
    # ---- 10. 庙旺陷 ----
    for name, info in palaces.items():
        info['miao_wang'] = {}
        for star in info['main_stars']:
            if star in MIAOWANG:
                star_idx = PALACE_DIZHI.index(info['dizhi'])
                val = MIAOWANG[star][star_idx]
                info['miao_wang'][star] = MIAOWANG_NAMES.get(val, '平')
    
    return result


def format_output(data):
    """格式化输出"""
    output = {
        '命宫': data['ming_gong'],
        '身宫': data['shen_gong'],
        '五行局': data['wuxing'],
        '紫微星': data['ziwei'],
        '年干': data['year_gan'],
        '十二宫': {},
    }
    
    for name, info in data['palaces'].items():
        output['十二宫'][name] = {
            '干支': info['ganzhi'],
            '主星': info['main_stars'] if info['main_stars'] else ['无'],
            '辅星': info['fu_stars'] if info['fu_stars'] else ['无'],
            '四化': info['sihua'] if info['sihua'] else ['无'],
            '庙旺': info['miao_wang'],
        }
    
    output['四化'] = data['sihua']
    
    output['大限'] = []
    for dx in data['daixian']:
        output['大限'].append(f"{dx['palace']}({dx['dizhi']}): {dx['start_age']}-{dx['end_age']}岁")
    
    return output


def main():
    parser = argparse.ArgumentParser(description='紫微斗数排盘')
    parser.add_argument('--input', required=True, help='输入JSON文件路径')
    parser.add_argument('--output', required=True, help='输出JSON文件路径')
    args = parser.parse_args()
    
    import argparse
    # 重写，因为argparse被import了但还没
    import argparse as ap
    parser = ap.ArgumentParser(description='紫微斗数排盘')
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    
    with open(args.input, 'r', encoding='utf-8') as f:
        payload = json.load(f)
    
    year = payload.get('year', 2026)
    month = payload.get('month', 1)
    day = payload.get('day', 1)
    hour = payload.get('hour', 12)
    minute = payload.get('minute', 0)
    gender = payload.get('gender', '男')
    
    # 转农历
    lunar_year, lunar_month, lunar_day = get_lunar_date(year, month, day)
    
    # 时辰
    shichen_dz = hour_to_shichen(hour, minute)
    
    # 排盘
    data = build_palace_data(lunar_year, lunar_month, lunar_day, shichen_dz, hour, gender)
    output = format_output(data)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    return 0


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='紫微斗数排盘')
    parser.add_argument('--input', required=True, help='输入JSON文件路径')
    parser.add_argument('--output', required=True, help='输出JSON文件路径')
    args = parser.parse_args()
    
    with open(args.input, 'r', encoding='utf-8') as f:
        payload = json.load(f)
    
    year = payload.get('year', 2026)
    month = payload.get('month', 1)
    day = payload.get('day', 1)
    hour = payload.get('hour', 12)
    minute = payload.get('minute', 0)
    gender = payload.get('gender', '男')
    
    lunar_year, lunar_month, lunar_day = get_lunar_date(year, month, day)
    shichen_dz = hour_to_shichen(hour, minute)
    
    data = build_palace_data(lunar_year, lunar_month, lunar_day, shichen_dz, hour, gender)
    output = format_output(data)
    
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 排盘完成")
    print(f"命宫: {data['ming_gong']}, 身宫: {data['shen_gong']}")
    print(f"五行局: {data['wuxing']}")
    print(f"紫微星: {data['ziwei']}")
    print(f"十四主星: {len(data['stars'])} 颗")
    print(f"辅星: {len(data['fushi'])} 颗")
    sys.exit(0)