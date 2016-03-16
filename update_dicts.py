import xlrd
import os
import re
from glob import glob
import pickle

intake_re = re.compile(r"[A-Z]+-[0-9]+")

def intake_list(sheet_list):
    intakes = []
    for sheet in sheet_list:
        if intake_re.match(sheet):
            intakes.append(sheet)
    return intakes

def update_intake_dic():
    dic = {}
    print 'Updating pickles:',
    for program in glob('data/*'):
        program_dic = {}
        print '*',
        for semester in glob(os.path.join(program, '*')):
            semester_dic = {}
            print '.',
            semester_wb = xlrd.open_workbook(filename = semester)
            for intake in intake_list(semester_wb.sheet_names()):
                print '!',
                intake_sheet = xlrd.open_workbook(filename = semester).sheet_by_name(intake)

                no_of_rows, no_of_cols = intake_sheet.nrows, intake_sheet.ncols

                all_data = []
                for row in range(no_of_rows):
                    row_data = []
                    for column in range(no_of_cols):
                        row_data.append(intake_sheet.cell(row, column))
                    all_data.append(row_data)
                for i in range(no_of_rows):
                    for j in range(no_of_cols):
                        if all_data[i][j].value == 'PLO Average':
                            inds = [i, j]

                plo_av = []
                for cell in all_data[inds[0] + 2][inds[1]:inds[1] + 12]:
                    if cell.ctype != xlrd.XL_CELL_EMPTY:
                        plo_av.append(float(cell.value))
                    else:
                        plo_av.append(0)

                semester_dic[intake] = plo_av
            program_dic[os.path.basename(semester)[:-5]] = semester_dic
        dic[os.path.basename(program)] = program_dic
    print 'Done!\n'
    return dic

def update_course_dic():
    pass

def update_student_dic():
    pass

if __name__ == '__main__':
    by_intake = update_intake_dic()
    with open('pickles/intake.pkl', 'wb') as handle:
        pickle.dump(by_intake, handle)