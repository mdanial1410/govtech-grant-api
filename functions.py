from datetime import datetime, date


def dup_name_check(family_arr, new_name):
    '''
    checks for duplicate name in the family array
    :return: boolean
    '''
    for member in family_arr:
        if member.get('name') == new_name:
            return True
    return False


def rm_spouse(fam_list):
    '''
    removes the 'spouse' key from the list of family members
    '''
    for member in fam_list:
        member.pop('spouse', None)


def seb(house, threshold):
    '''
    Student Encouragement Bonus
    :return: a dict
    '''
    res = dict()
    family_list = list()
    age_arr = get_age(house['family'])
    total_income = cal_income(house['family'])
    if total_income < threshold:
        for member in age_arr:
            if member['age'] < 16:
                family_list.append({'id': member['id'], 'name': member['name']})
    if family_list:
        res['house_id'] = house['house_id']
        res['family'] = family_list
    return res


def fts(house):
    '''
    Family Togetherness Scheme
    :return: a dict
    '''
    res = dict()
    family_list = list()
    age_arr = get_age(house['family'])
    if check_spouse_exist(house['family']):
        for member in age_arr:
            if member['age'] < 18:
                family_list.append({'id': member['id'], 'name': member['name']})
    if family_list:
        res['house_id'] = house['house_id']
        res['family'] = family_list
    return res


def elder_bonus(house):
    '''
    Elder Bonus
    :return: a dict
    '''
    res = dict()
    family_list = list()
    age_arr = get_age(house['family'])
    for member in age_arr:
        if member['age'] > 50:
            family_list.append({'id': member['id'], 'name': member['name']})
    if family_list:
        res['house_id'] = house['house_id']
        res['family'] = family_list
    return res


def baby_sunshine_grant(house):
    '''
    Baby Sunshine Grant
    :return: a dict
    '''
    res = dict()
    family_list = list()
    age_arr = get_age(house['family'])
    for member in age_arr:
        if member['age'] < 5:
            family_list.append({'id': member['id'], 'name': member['name']})
    if family_list:
        res['house_id'] = house['house_id']
        res['family'] = family_list
    return res


def yolo_grant(house, threshold):
    '''
    retrieve households that qualify for the YOLO GST Grant
    returns the house_id
    '''
    total_income = cal_income(house['family'])
    if total_income < threshold:
        return house['house_id']
    return None


def check_spouse_exist(fam_arr):
    '''
    Check if spouse field is filled and if spouse is in the family array
    :return: Boolean
    '''
    for member in fam_arr:
        if 'spouse' in member.keys():
            spouse = member.get('spouse')
            for mem in fam_arr:
                if spouse == mem['name']:
                    return True
    return False


def get_age(fam_arr):
    '''
    for every family member. get their age
    return a dict {'name' : ... , 'age': ...}
    '''
    new_arr = list()
    for member in fam_arr:
        date_obj = datetime.strptime(member['dob'], "%d-%m-%Y")
        new_arr.append({
                'id': member['id'],
                'name': member['name'],
                'age': calculate_age(date_obj),
            })
    return new_arr


def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def cal_income(fam_arr):
    '''
    calculate total annual income of the family
    return int
    '''
    total_income = 0
    for member in fam_arr:
        total_income += member['annualIncome']
    return total_income