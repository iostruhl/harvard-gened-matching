import pandas as pd
import random
import logging
import sys
import copy

logging.basicConfig(stream=sys.stderr, level=logging.ERROR)

class MatchFinder:
    def __init__(self):
        # {student: course}
        self.matching = dict()
        # {student: [course1, course2 ...]}
        self.student_pref = dict()
        # {course: capacity}
        self.courses = dict()
        self.num_students = 0
        self.num_courses = 0

    def load_from_csv(self, student_pref = 'student_pref.csv', courses = 'courses.csv'):
        self.student_pref = pd.read_csv(student_pref, dtype = 'Int64').fillna(-1).set_index('Student').T.to_dict('list')
        # Append -1, nonallocation to each student.
        for student in self.student_pref:
            self.student_pref[student].append(-1)

        df = pd.read_csv(courses, dtype = 'Int64')
        self.courses = dict(zip(df.Course, df.Capacity))
        self.num_students = len(self.student_pref)
        self.num_courses = len(self.courses)

    def load(self, student_pref, courses):
        self.student_pref = student_pref
        self.courses = courses
        self.num_students = len(self.student_pref)

    def match(self):
        logging.error("Abstract MatchFinder match(). Override this!")

    def write_output(self, csv_path = 'output.csv'):
        with open(csv_path, 'w') as w:
            w.write('Student,Course\n')
            for student,course in self.matching.items():
                w.write(f'{student},{course}\n')

# Random Serial Dictatorship Mechanism
class RSD(MatchFinder):
    def __init__(self):
        super().__init__()

    def match(self):
        student_order = list(range(self.num_students))
        random.shuffle(student_order)

        for student in student_order:
            debug_string = ''
            debug_string += f'Student {student} choosing...'
            for pref in self.student_pref[student]:
                debug_string += f'{pref}.'
                # If the student now prefers not to be allocated, don't allocate them.
                if pref == -1:
                    debug_string += 'not allocated.'
                    self.matching[student] = -1
                    break
                # If there is space for the student in their current preference, allocate.
                if self.courses[pref] > 0:
                    debug_string += f'allocated {pref}'
                    self.courses[pref] -= 1
                    self.matching[student] = pref
                    break
            logging.debug(debug_string)
        logging.info(sorted(self.matching.items()))


# Student-proposing DA Mechanism
class StudentProposingDA(MatchFinder):
    def __init__(self):
        super().__init__()
        self.course_pref = dict()
        self.max_round = 10**6 # Avoid infinite loops due to bugs.

    def randomize_course_prefs(self):
        student_order = list(range(self.num_students))
        for course in range(self.num_courses):
            random.shuffle(student_order)
            self.course_pref[course] = copy.deepcopy(student_order)

    def match(self):
        accepted = {course: [] for course in self.courses}
        need_to_propose = set(i for i in self.student_pref.keys() if self.student_pref[i][0] != -1)
        for i in self.student_pref.keys():
            if self.student_pref[i][0] == -1:
                self.matching[i] = -1
        for i in range(self.max_round):
            logging.debug(f'Round {i}')
            at_least_one_reject = False

            # Take proposals from each student.
            received_proposals = {course: [] for course in self.courses}
            for student in self.student_pref:
                # Ignore students who prefer not to be matched.
                if student not in need_to_propose:
                    continue
                logging.debug(f'Student {student} proposes {self.student_pref[student][0]}')
                received_proposals[self.student_pref[student][0]] += [student]
            need_to_propose = set()

            # Calculate accepted and rejected students.
            for course in received_proposals:
                accepted[course].extend(received_proposals[course])
                accepted[course].sort(key = lambda student: self.course_pref[course].index(student))
                capacity = self.courses[course]
                if len(accepted[course]) > capacity:
                    at_least_one_reject = True
                    for reject_student in accepted[course][capacity:]:
                        logging.debug(f'Student {reject_student} rejected.')
                        self.student_pref[reject_student] = self.student_pref[reject_student][1:]
                        # If the rejected student now prefers to be unallocated, unallocate them.
                        if self.student_pref[reject_student][0] == -1:
                            logging.debug(f'Student {reject_student} prefers deallocation.')
                            self.matching[reject_student] = -1
                        else:
                            need_to_propose.add(reject_student)

                        accepted[course] = accepted[course][0:capacity]
            # If nobody was rejected, we're done; accept everyone.
            if not at_least_one_reject:
                break

        for course in accepted:
            for student in accepted[course]:
                self.matching[student] = course
        logging.info(sorted(self.matching.items()))


if __name__ == '__main__':
    a = RSD()
    a.load_from_csv()
    a.match()

    a = StudentProposingDA()
    a.load_from_csv()
    a.randomize_course_prefs()
    a.match()
