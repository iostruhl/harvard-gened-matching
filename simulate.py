from matching import *
import numpy as np
import random
import matplotlib.pyplot as plt

# Assume 3000 out of 5000 students apply to Geneds
num_students = 3000
# num_students = 5

# How much more likely students are to want the most popular course compared to least popular course
course_correlation_factor = 10

# How much more likely courses are to want the most popular student compared to least popular student
student_correlation_factor = 5

# Taken from Fall 2021 stats
num_courses = 40
courses_without_caps = 26
courses_with_caps = 14

# Fall 2021 course caps
# [100,50,80,50,200,60,60,240,60,50,60,50,105,200]
course_size_avg = 97.5
course_size_std = 65.8
min_course_size = 10

def generate_course_caps():
    courses = {i:int(max(c,min_course_size)) for i,c in enumerate(np.random.normal(course_size_avg,course_size_std,courses_with_caps)) }
    return courses

def generate_correlated_student_prefs():
    student_prefs = dict()
    course_list = list(range(courses_with_caps))+[-1]
    course_probs = np.linspace(1, course_correlation_factor ,num=len(course_list))
    course_probs = course_probs/sum(course_probs)
    # print(course_probs)
    np.random.shuffle(course_probs)
    # print(course_probs)
    for i in range(num_students):
        student_prefs[i] = np.random.choice(course_list, len(course_list), replace=False, p=course_probs)
    # print(student_prefs)
    return student_prefs

def generate_uncorrelated_student_prefs():
    course_list = list(range(courses_with_caps))+[-1]
    student_prefs = dict()
    for i in range(num_students):
        student_prefs[i] = random.sample(course_list,len(course_list))
    return student_prefs

def generate_uncorrelated_course_prefs():
    course_pref = dict()
    student_order = list(range(num_students))
    for course in range(num_courses):
        random.shuffle(student_order)
        course_pref[course] = copy.deepcopy(student_order)
    return course_pref

def generate_correlated_course_prefs():
    course_pref = dict()
    student_list = list(range(num_students))
    student_probs = np.linspace(1, course_correlation_factor ,num=num_students)
    student_probs = student_probs/sum(student_probs)
    np.random.shuffle(student_probs)
    for i in range(num_courses):
        course_pref[i] = list(np.random.choice(student_list, len(student_list), replace=False, p=student_probs))
    return course_pref


def calculate_matching_stats(matching, student_pref, course_prefs=None):
    student_happiness = []
    unmatched_students = 0
    for student,course in matching.items():
        if course == -1:
            unmatched_students += 1
        else:
            # print(course)
            # print(student_pref[student])
            # print(np.where(student_pref[student] == course))
            # print(student_pref[student].index(course))
            student_happiness.append(np.where(student_pref[student] == course)[0][0] + 1)
            # student_happiness.append(student_pref[student].index(course) + 1)
    
    if course_prefs:
        # todo
        pass

    mean = np.mean(student_happiness)
    median = np.median(student_happiness)
    quart = np.quantile(student_happiness, 0.25)
    three_quart = np.quantile(student_happiness, 0.75)
    min_happiness = np.max(student_happiness)
    return mean, median, quart, three_quart, min_happiness, unmatched_students, student_happiness

def run_simulation(alg, num_iters = 1, correlated_student_prefs=False, course_group_prefs=False, graph_output=True):
    mean_list = []
    median_list = []
    quart_list = []
    three_quart_list = []
    min_happiness_list = []
    unmatched_students_list = []
    if graph_output:
        fig, ax = plt.subplots()

    for _ in range(num_iters):
        if correlated_student_prefs:
            student_pref = generate_correlated_student_prefs()
        else:
            student_pref = generate_uncorrelated_student_prefs()
        if course_group_prefs:
            course_pref = generate_correlated_course_prefs()
        else:
            course_pref = generate_uncorrelated_course_prefs()

        courses = generate_course_caps()
        # print(student_pref)
        # print(courses)

        if alg == "rsd":
            a = RSD()
            a.load(student_pref, courses)
            a.match()
        if alg == "da":
            a = StudentProposingDA()
            a.load(student_pref, courses)
            a.course_pref = course_pref
            a.match()

    
        mean, median, quart, three_quart, min_happiness, unmatched_students, student_happiness = calculate_matching_stats(a.matching, student_pref)
        mean_list.append(mean)
        median_list.append(median)
        quart_list.append(quart)
        three_quart_list.append(three_quart)
        min_happiness_list.append(min_happiness)
        unmatched_students_list.append(unmatched_students)
        if graph_output:
            counts, bins = np.histogram(student_happiness)
            ax.plot(bins[:-1],counts)

    plt.show()
    print("Happiness statistics:")
    print("Mean: " + str(np.mean(mean_list)))
    print("Median: " + str(np.mean(median_list)))
    print("0.25: " + str(np.mean(quart_list)))
    print("0.75: " + str(np.mean(three_quart_list)))
    print("Min: " + str(np.mean(min_happiness_list)))
    print("Average unmatched students: " + str(np.mean(unmatched_students_list)))
    return

run_simulation("da", 5, correlated_student_prefs=True, course_group_prefs=True, graph_output=True)