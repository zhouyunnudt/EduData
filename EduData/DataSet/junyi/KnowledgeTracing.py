# coding: utf-8
# create by tongshiwei on 2019-7-5

"""
This script is used to convert the original junyi dataset into json sequence, which can be applied in kt task.
"""

__all__ = ["select_n_most_frequent_students"]

import csv
import json

from longling import wf_open
from longling.lib.candylib import as_list
from tqdm import tqdm


def _read(source: str, ku_dict: str) -> dict:
    """
    Read the learners' interaction records and classify them by user id and session id.
    In the same time, the exercise name will be converted to id.

    Notes
    -----
    Require big memory to run this function.
    """

    outcome = {
        "INCORRECT": 0,
        "CORRECT": 1,
        "HINT": 0,
    }

    students = {}

    with open(ku_dict) as f:
        ku_dict = json.load(f)

    with open(source) as f:
        f.readline()
        for line in tqdm(csv.reader(f, delimiter='\t'), "reading data"):
            student, session, exercise = line[0], line[1], ku_dict[line[-5]],
            correct, timestamp = outcome[line[10]], line[8]
            if student not in students:
                students[student] = {}
            if session not in students[student]:
                students[student][session] = []

            students[student][session].append([int(timestamp), exercise, correct])
    return students


def _write(students, target):
    with wf_open(target) as wf:
        for student_id, sessions in tqdm(students.items(), "writing -> %s" % target):
            for session_id, exercises in sessions.items():
                exercises.sort(key=lambda x: x[0])
                exercise_response = [(exercise[1], exercise[2]) for exercise in exercises]
                print(json.dumps(exercise_response), file=wf)


def extract_students_log(source, target, ku_dict):
    students = _read(source, ku_dict)
    _write(students, target)


def _frequency(students):
    frequency = {}
    for student_id, sessions in tqdm(students.items(), "calculating frequency"):
        frequency[student_id] = sum([len(session) for session in sessions])
    return sorted(frequency.items(), key=lambda x: x[1], reverse=True)


def get_n_most_frequent_students(students, n=None, frequency: list = None):
    frequency = _frequency(students) if frequency is None else frequency
    __frequency = frequency if n is None else frequency[:n]
    _students = {}
    for _id, _ in __frequency:
        _students[_id] = students[_id]
    return _students


def select_n_most_frequent_students(source, target_prefix, ku_dict, n: (int, list)):
    """None in n means select all students"""
    n_list = as_list(n)
    students = _read(source, ku_dict)
    frequency = _frequency(students)
    for _n in n_list:
        _write(get_n_most_frequent_students(students, _n, frequency), target_prefix + "%s" % _n)


if __name__ == '__main__':
    root = "../../../"
    student_log_raw_file = root + "data/junyi/junyi_ProblemLog_for_PSLC.txt"
    # student_log_file = root + "data/junyi/student_log_kt.json"
    ku_dict_file = root + "data/junyi/graph_vertex.json"

    select_n_most_frequent_students(
        student_log_raw_file,
        root + "data/junyi/student_log_kt_",
        ku_dict_file,
        [None]
    )

    # select_n_most_frequent_students(
    #     student_log_raw_file,
    #     root + "data/junyi/student_log_kt_",
    #     ku_dict_file,
    #     [100, 200, 300]
    # )
    # [500, 1000, 2000]

    # extract_students_log(student_log_raw_file, student_log_file, ku_dict_file)

    # student_log_file_small = student_log_file + ".small"
    #
    # with open(student_log_file) as f, wf_open(student_log_file_small) as wf:
    #     for i, line in tqdm(enumerate(f)):
    #         if i > 50000:
    #             break
    #         print(line, end="", file=wf)
    #
    # print(train_valid_test(
    #     student_log_file_small,
    #     valid_ratio=0.,
    #     test_ratio=0.2,
    #     root_dir=root + "data/junyi/",
    #     silent=False,
    # ))
