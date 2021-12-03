import pandas as pd
import random
import logging
import sys

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

class MatchFinder:
    def __init__(self):
        # {student: course}
        self.matching = dict()
        # {student: [course1, course2 ...]}
        self.student_pref = dict()
        # {course: capacity}
        self.courses = dict()
        self.num_students = 0

    def load(self, student_pref = 'student_pref.csv', courses = 'courses.csv'):
        self.student_pref = pd.read_csv(student_pref, dtype = 'Int64').fillna(-1).set_index('Student').T.to_dict('list')
        df = pd.read_csv(courses, dtype = 'Int64')
        self.courses = dict(zip(df.Course, df.Capacity))
        self.num_students = len(self.student_pref)

    def match(self):
        logging.error("Abstract MatchFinder match(). Override this!")

    def write_output(self, csv_path = 'output.csv'):
        with open(csv_path, 'w') as w:
            w.write('student,course\n')
            for student,course in self.matching.items():
                w.write(f'{student},{course}\n')


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
        print(self.matching)


r = RSD()
r.load()
r.match()
r.write_output()
