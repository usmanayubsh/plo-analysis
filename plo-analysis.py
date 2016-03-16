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
import pickle
import cStringIO
import matplotlib.pyplot as plt

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

with open('pickles/intake.pkl', 'rb') as handle:
    data_dic = pickle.load(handle)

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
        "programs": data_dic.keys()
    }

    def render_form(self, **kwargs):
        self.render("intake.html", **kwargs)

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

            semesters = data_dic[' '.join(program.split('+'))]

            self.intake_params["program_selected"] = program
            self.intake_params["semesters"] = semesters
            self.render_form(**self.intake_params)

        semester = self.request.get("semester")

        if semester:
            self.intake_params["semester_selected"] = semester
            p_s = self.intake_params["program_selected"]

            intakes = data_dic[p_s][semester]

            self.intake_params["intakes"] = intakes
            self.render_form(**self.intake_params)

        intake = self.request.get("intake")

        if intake:
            self.intake_params["intake_selected"] = intake
            p_s = self.intake_params["program_selected"]
            s_s = self.intake_params["semester_selected"]
            plo_av = data_dic[p_s][s_s][intake]

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
