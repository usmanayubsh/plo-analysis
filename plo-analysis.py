#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
import re

import xlrd
import cStringIO

import matplotlib.pyplot as plt

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

def dir_struct(directory):
    dir_dict = {}
    for path, dirs, files in os.walk(directory):
        if dirs:
            dir_dict[path] = dirs
        else:
            dir_dict[path] = files
    return dir_dict

data_dir = os.path.join(os.path.dirname('__file__'), 'data')
this_dir = dir_struct(data_dir)

intake_re = re.compile(r"[A-Z]+-[0-9]+")

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainHandler(Handler):
    def get(self):
        self.render("intro.html")

class IntakeHandler(Handler):
    intake_params = {
        "programs": this_dir[data_dir]
    }

    def render_form(self, **kwargs):
        self.render("intake.html", **kwargs)

    def intake_list(self, sheet_list):
        intakes = []
        for sheet in sheet_list:
            if intake_re.match(sheet):
                intakes.append(sheet)
        return intakes

    def remove_dict_entries(self, entries, dictionary):
        for key in entries:
            if key in dictionary:
                del dictionary[key]

    def get(self):
        self.render_form(**self.intake_params)

    def post(self):
        program = self.request.get("program")

        if program:
            self.remove_dict_entries(["semester_selected", "intake_selected", "intakes"], self.intake_params)

            program_dir = data_dir + '/' + ' '.join(program.split('+'))
            semesters = [s[:-5] for s in this_dir[program_dir]]

            self.intake_params["program_selected"] = program
            self.intake_params["semesters"] = semesters
            self.render_form(**self.intake_params)

        semester = self.request.get("semester")

        if semester:
            self.intake_params["semester_selected"] = semester
            p_s = self.intake_params["program_selected"]
            semester_wb = xlrd.open_workbook(filename = data_dir + '/' + p_s + '/' + semester + '.xlsx')
            intakes = self.intake_list(semester_wb.sheet_names())

            self.intake_params["intakes"] = intakes
            self.render_form(**self.intake_params)

        intake = self.request.get("intake")

        if intake:
            self.intake_params["intake_selected"] = intake
            p_s = self.intake_params["program_selected"]
            s_s = self.intake_params["semester_selected"]
            intake_sheet = xlrd.open_workbook(filename = data_dir + '/' + p_s + '/' + s_s + '.xlsx').sheet_by_name(intake)

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

            plt.bar(range(len(plo_av)), plo_av, align = 'center')
            plt.yticks(range(0, 101, 10))
            plt.xticks(range(len(plo_av)), range(1, 13))

            plt.ylabel('Percentage (%)')
            plt.xlabel('PLO #')

            plt.suptitle(p_s + ', ' + s_s + ', ' + intake)

            sio = cStringIO.StringIO()
            plt.savefig(sio, format="png")
            img_b64 = sio.getvalue().encode("base64").strip()
            plt.clf()
            sio.close()

            self.intake_params["figure"] = img_b64
            self.render_form(**self.intake_params)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/intake', IntakeHandler)
], debug=True)
