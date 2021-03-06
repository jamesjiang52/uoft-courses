import pymysql


def __get_params(path):
    f = open(path, 'r')
    params = f.readlines()
    f.close()
    params = [item.strip('\n') for item in params]
    params[3] = int(params[3])
    return params


def init_db(path, DB_NAME): # Should be called when this project is executed first time
    params = __get_params(path)
    connection = pymysql.connect(host = params[0], user = params[1], password = params[2], port = params[3])
    cursor = connection.cursor()
    create_db_sql = "CREATE DATABASE {} DEFAULT CHARACTER SET utf8".format(DB_NAME)
    cursor.execute(create_db_sql)

    connection.select_db(DB_NAME)

    create_course_table_sql = "CREATE TABLE IF NOT EXISTS Course (cID VARCHAR(30) NOT NULL, cName\
    VARCHAR(300) NOT NULL, credits FLOAT NOT NULL, campus VARCHAR(150) NOT NULL,\
    department VARCHAR(160) NOT NULL, term VARCHAR(150) NOT NULL, division\
    VARCHAR(200) NOT NULL, prerequisites VARCHAR(1000), exclusion VARCHAR(1000), br\
    VARCHAR(200), lecNum VARCHAR(30) NOT NULL, lecTime VARCHAR(125) NOT\
    NULL, instructor VARCHAR(500), location VARCHAR(250), size INT(5),\
    currentEnrollment INT(5), PRIMARY KEY (cID, term, lecNum)) CHARACTER SET=utf8"
    cursor.execute(create_course_table_sql)

    create_eval_table_sql = "CREATE TABLE IF NOT EXISTS Eval (department\
    VARCHAR(160) NOT NULL, cID VARCHAR(30) NOT NULL, cName VARCHAR(300) NOT\
    NULL, lecNum VARCHAR(30) NOT NULL, campus VARCHAR(150) NOT NULL, term\
    VARCHAR(150) NOT NULL, instructor VARCHAR(150), instructorFullName\
    VARCHAR(200), intellectuallySimulating FLOAT(10), deeperUnderstanding\
    FLOAT(10), courseAtmosphere FLOAT(10), homeworkQuality FLOAT(10),\
    homeworkFairness FLOAT(10), overallQuality FLOAT(10), enthusiasm FLOAT(10),\
    workload FLOAT(10), recommend FLOAT(10), numInvited INT(10), numResponded\
    INT(10), PRIMARY KEY (cID, term, lecNum, instructorFullName)) CHARACTER SET=utf8"
    cursor.execute(create_eval_table_sql)

    print("database intialized")

    connection.close()


def get_connection(path, DB_NAME):
    params = __get_params(path)
    connection = pymysql.connect(host = params[0], user = params[1], password = params[2], port = params[3], db = DB_NAME)
    return connection

def get_connection_with_dict_cursor(path, DB_NAME):
    params = __get_params(path)
    connection = pymysql.connect(host = params[0], user = params[1], password =\
            params[2], port = params[3], db = DB_NAME,\
            cursorclass=pymysql.cursors.DictCursor)
    return connection

def insert_course_data(cursor, info_dict):
    sql = "INSERT INTO Course(cID, cName, credits, campus, department, term,\
    division, prerequisites, exclusion, br, lecNum, lecTime, instructor,\
    location, size, currentEnrollment) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    cID = info_dict['cID']
    cName = info_dict['cName']
    credits = info_dict['credits']
    campus = info_dict['campus']
    department = info_dict['department']
    term = info_dict['term']
    division = info_dict['division']
    prerequisites = info_dict['prerequisites']
    exclusion = info_dict['exclusion']
    br = info_dict['br']
    lecNum_list = info_dict['lecNum']
    lecTime_list = info_dict['lecTime']
    instructor_list = info_dict['instructor']
    location_list = info_dict['location']
    size_list = info_dict['size']
    currentEnrollment_list = info_dict['currentEnrollment']

    num_of_courses = len(lecNum_list) # this must be equal to len(info_dict['lecTime'], etc.

    for i in range(num_of_courses):
        print(cID)
        cursor.execute(sql, (cID, cName, credits, campus, department, term,\
            division, prerequisites, exclusion, br, lecNum_list[i], lecTime_list[i],\
            instructor_list[i], location_list[i], size_list[i], currentEnrollment_list[i]))


def insert_eval_data(cursor, info_dict):
    sql = "INSERT INTO Eval (department, cID, cName, lecNum, campus, term,\
        instructor, instructorFullName, intellectuallySimulating,\
        deeperUnderstanding, courseAtmosphere, homeworkQuality,\
        homeworkFairness, overallQuality, enthusiasm, workload, recommend,\
        numInvited, numResponded) values (%s, %s, %s, %s, %s, %s, %s, %s, %s,\
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"

    info_dict = {k: (lambda x: None if x == 'N/A' or x == 'NRP' else x)(v) for k, v in info_dict.items()}
    # clean data in info_dict (since N/A may appear, which can't be recognized by sql.)

    department = info_dict['department']
    cID = info_dict['cID']
    cName = info_dict['cName']
    lecNum = info_dict['lecNum']
    campus = info_dict['campus']
    term = info_dict['term']
    instructor = info_dict['instructor']
    instructorFullName = info_dict['instructorFullName']
    intellectuallySimulating = info_dict['intellectuallySimulating']
    deeperUnderstanding = info_dict['deeperUnderstanding']
    courseAtmosphere = info_dict['courseAtmosphere']
    homeworkQuality = info_dict['homeworkQuality']
    homeworkFairness = info_dict['homeworkFairness']
    overallQuality = info_dict['overallQuality']
    enthusiasm = info_dict['enthusiasm']
    workload = info_dict['workload']
    recommend = info_dict['recommend']
    numInvited = info_dict['numInvited']
    numResponded = info_dict['numResponded']

    print(cID)

    try:
        cursor.execute(sql, (department, cID, cName, lecNum, campus, term,\
            instructor, instructorFullName, intellectuallySimulating,\
            deeperUnderstanding, courseAtmosphere, homeworkQuality,\
            homeworkFairness, overallQuality, enthusiasm, workload, recommend,\
            numInvited, numResponded))
    except pymysql.err.IntegrityError as e:
        print("error due to the crappy data source:", e.args)

def commit_data(connection):
    try:
        connection.commit()
    except:
        connection.rollback()


def get_course_data_by_cID_and_campus(cursor, cID, campus):
    """
    cursor: the cursor of our connection.
    cID: a string, e.g., "CSC148"
    campus: a string - either "St. George", "Scarborough", or "Mississauga"
    -------------------------------------------------------
    Returns a list of tuples, with each tuple containing the data of a single
    section of the specified course
    -------------------------------------------------------
    We use cursor here to avoid unnecessary connections with database.
    """
    sql = "SELECT * FROM Course Where cID like %s And campus = %s"
    cursor.execute(sql, ("%{}%".format(cID), campus))

    return list(cursor.fetchall())

def get_instructor_by_cID_and_lecNum(cursor, cID, lecNum):
    """
    cursor: the cursor of our connection.
    cID: a string, e.g., "CSC148"
    lecNum: a string, representing the course section e.g. Lec 5101, Tut 0106
    -------------------------------------------------------
    Returns the instructor of the course given by cID and lecNum
    -------------------------------------------------------
    We use cursor here to avoid unnecessary connections with database.
    """
    sql = "SELECT instructor FROM Course Where cID like %s And lecNum = %s"
    cursor.execute(sql, ("%{}%".format(cID), lecNum))

    return cursor.fetchone()[0]


def get_eval_data_by_cID_and_instructor(cursor, cID, instructor):
    """
    cursor: the cursor of our connection.
    cID: a string, e.g., "CSC148"
    instructor: a string e.g. "S Huynh", "T Fairgrieve"
    -------------------------------------------------------
    Returns a list of tuples, with each tuple containing the evaluation data of a single
    section of the specified course
    -------------------------------------------------------
    We use cursor here to avoid unnecessary connections with database.
    """
    sql = "SELECT * FROM Eval Where cID like %s And instructor = %s"
    cursor.execute(sql, ("%{}%".format(cID), instructor))

    return list(cursor.fetchall())


def get_prof_quality_by_instructorFullName(dict_cursor, instructorFullName):
    """
    demo:
    > get_prof_quality_by_fullname(cursor, "David Liu")
    returns a dictionary
    {'average_course_atmosphere': 4.41, 'average_enthusiasm': 4.47}
    """

    sql = "SELECT round(avg(courseAtmosphere), 2) as average_course_atmosphere,\
    round(avg(enthusiasm), 2) as average_enthusiasm from Eval where instructorFullName = %s"

    dict_cursor.execute(sql, (instructorFullName))

    return dict_cursor.fetchone()


def get_avg_prof_quality_by_department(dict_cursor, departmentID):
    """
    demo:
    > get_avg_prof_quality_by_department(cursor, "CSC")
    returns a dictionary
    {'average_course_atmosphere': 3.9, 'average_enthusiasm': 3.95}
    -------------------------------------------------------------
    Note: departmentID is the first three char at the beginning of cID.
    """

    sql = "SELECT round(avg(courseAtmosphere), 2) as average_course_atmosphere,\
    round(avg(enthusiasm), 2) as average_enthusiasm from Eval where cID like %s"

    dict_cursor.execute(sql, ("{}%".format(departmentID)))

    return dict_cursor.fetchone()


def get_past_eval_by_instructorFullName_and_cID(dict_cursor, instructorFullName, cID):
    sql = "SELECT round(avg(intellectuallySimulating), 2) as\
    avg_intellectually_simulating, round(avg(deeperUnderstanding), 2) as\
    avg_deeper_understanding, round(avg(homeworkQuality), 2) as\
    avg_home_quality, round(avg(homeworkFairness), 2) as avg_homework_fairness,\
    round(avg(overallQuality), 2) as avg_overall_quality, round(avg(recommend),\
    2) as avg_recommend_rating, round(avg(numResponded)/avg(numInvited), 2) as\
    avg_respondent_percentage from Eval where instructorFullName = %s and cID like %s"

    dict_cursor.execute(sql, (instructorFullName, "{}%".format(cID)))

    result = dict_cursor.fetchone()
    result['avg_respondent_percentage'] = float(result['avg_respondent_percentage'])
    return result


def get_past_eval_by_cID(dict_cursor, cID):
    sql = "SELECT round(avg(intellectuallySimulating), 2) as\
    avg_intellectually_simulating, round(avg(deeperUnderstanding), 2) as\
    avg_deeper_understanding, round(avg(homeworkQuality), 2) as\
    avg_home_quality, round(avg(homeworkFairness), 2) as avg_homework_fairness,\
    round(avg(overallQuality), 2) as avg_overall_quality, round(avg(recommend),\
    2) as avg_recommend_rating, round(avg(numResponded)/avg(numInvited), 2) as\
    avg_respondent_percentage from Eval where cID like %s"

    dict_cursor.execute(sql, ("{}%".format(cID)))

    result = dict_cursor.fetchone()
    result['avg_respondent_percentage'] = float(result['avg_respondent_percentage'])
    return result


def get_past_eval_by_cID_excluding_one_prof(dict_cursor, exclusiveInstructorFullName, cID):
    sql = "SELECT round(avg(intellectuallySimulating), 2) as\
    avg_intellectually_simulating, round(avg(deeperUnderstanding), 2) as\
    avg_deeper_understanding, round(avg(homeworkQuality), 2) as\
    avg_home_quality, round(avg(homeworkFairness), 2) as avg_homework_fairness,\
    round(avg(overallQuality), 2) as avg_overall_quality, round(avg(recommend),\
    2) as avg_recommend_rating, round(avg(numResponded)/avg(numInvited), 2) as\
    avg_respondent_percentage from Eval where instructorFullName <> %s and cID like %s"

    dict_cursor.execute(sql, (exclusiveInstructorFullName, "{}%".format(cID)))

    result = dict_cursor.fetchone()
    result['avg_respondent_percentage'] = float(result['avg_respondent_percentage'])
    return result
