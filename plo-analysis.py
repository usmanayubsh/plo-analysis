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

import xlrd
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
    form_params = {
        "programs": this_dir[data_dir]
    }

    def render_form(self, **kwargs):
        self.render("intake.html", **kwargs)

    def get(self):
        self.render_form(**self.form_params)

    def post(self):
        program = self.request.get("program")
        program_dir = data_dir + '/' + ' '.join(program.split('+'))

        if program:
            semesters = [s[:-5] for s in this_dir[program_dir]]

            self.form_params["program_selected"] = program
            self.form_params["semesters"] = semesters
            self.render_form(**self.form_params)

        semester = self.request.get("semester")

        if semester:
            intakes = [1, 2, 3, 4]

            self.form_params["semester_selected"] = semester
            self.form_params["intakes"] = intakes
            self.render_form(**self.form_params)

        intake = self.request.get("intake")
        if intake:
            self.form_params["intake_selected"] = intake
            self.response.out.write(self.form_params)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/intake', IntakeHandler)
], debug=True)
