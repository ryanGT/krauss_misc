class bb_107_final_grade_calculator(bb_grade_checker):
    def project_report_data(self, short=False):
        # The card game is the only project score for 107 in W17,
        # everything else is a group grade
        data = []
        labels = []


        for col in self.project:
            shortname = get_short_col_name(col.attr_name)
            labels.append(shortname)
            data.append(col.floatvect)

        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def find_group_average(self):
        self.get_graded_cols_one_classification("group_assign")

        group_total = copy.copy(self.group_assign[0].floatvect)
        group_poss_total = self.group_assign[0].p_poss

        for col in self.group_assign[1:]:
            group_total += col.floatvect
            group_poss_total += col.p_poss

        self.group_total = group_total
        self.group_ave = (group_total/group_poss_total)*100
        self.group_poss_total = group_poss_total
        return self.group_ave


    def group_report_data(self, short=False):
        data = []
        labels = []


        if not short:
            for col in self.group_assign:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

        data.append(self.group_total)
        labels.append('Group Total (%i points possible)' % \
                               self.group_poss_total)

        data.append(self.group_ave)
        labels.append('Group Ave (%i points possible)' % \
                               self.group_poss_total)

        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def attr_to_mat(self, attr, label):
        col = getattr(self, attr)
        vect = col.floatvect
        mylist = vect.astype(str).tolist()
        list_w_label = [label] + mylist
        mymat = atleast_2d(list_w_label).T
        return mymat


    def big_report(self, short=False):
        mat1 = self.hw_report_data(short=short)
        mat2 = self.project_report_data(short=short)
        matq = self.quiz_report_data(short=short)
        matg = self.group_report_data(short=short)
        name_data = self.data[:,0:4]
        name_labels = self.labels[0:4]
        start_data = row_stack([name_labels,name_data])

        # --> Get midterm and exam 2 into big_report

        if not hasattr(self,"midterm_exam"):
            self.find_midterm()

        midpoint_mat = self.attr_to_mat("midterm_exam", "Midterm Exam")

        if not hasattr(self, "exam_2"):
            self.find_exam_2()

        e2_mat = self.attr_to_mat("exam_2","Exam 2")

        ## self.estimate_grade_midpoint()
        ## midpoint_data = self.midpoint.tolist()
        ## midpoint2 = ["Midpoint Grade Estimate"] + midpoint_data
        ## midpoint_mat = atleast_2d(midpoint2).T
        ## data = column_stack([start_data,mat1,mat2,matq,midterm_mat, \
        ##                      midpoint_mat])
        data = column_stack([start_data,mat1,mat2,matq,matg, \
                             midpoint_mat, e2_mat])
        return data

    # To do:
    # - check how I calculate the quiz average


class bb_445_final_grade_helper(bb_107_final_grade_calculator):
    def __init__(self, *args, **kwargs):
        if 'pat_order' not in kwargs:
            kwargs['pat_order'] = pat_order_445
        bb_107_final_grade_calculator.__init__(self, *args, **kwargs)


    def find_project_average(self):

        for attr in self.attr_names:
            if attr.find(pat) == 0:
                myvect = getattr(self, attr)
                col = bb_column(attr, myvect, pat_order=self.pat_order)
                setattr(self, attr_set, col)


    def find_exam_2(self):
        #Pdb().set_trace()
        self.find_column_with_start_match("Exam_2", "exam_2")


    ## def find_midterm(self):
    ##     for attr in self.attr_names:
    ##         if attr.find("Midterm_Exam") == 0:
    ##             myvect = getattr(self, attr)
    ##             self.midterm_exam = bb_column(attr, myvect)


    def find_midterm(self):
        self.find_column_with_start_match("Midterm_Exam", "midterm_exam")


    def estimate_grade_midpoint(self):
        # Assignments and Learning Activities 20 %
        # Quizzes 10 %
        # Exams 40 %
        # Project 30%
        self.midpoint = 0.2*self.hw_ave + \
                        0.1*self.quiz_average + \
                        0.4*self.midterm_exam.floatvect + \
                        0.3*self.project_ave
        return self.midpoint


    def big_report(self, short=False):
        mat1 = self.hw_report_data(short=short)
        mat2 = self.project_report_data(short=short)
        matq = self.quiz_report_data(short=short)
        name_data = self.data[:,0:4]
        name_labels = self.labels[0:4]
        start_data = row_stack([name_labels,name_data])
        if not hasattr(self,"midterm_exam"):
            self.find_midterm()
        midterm_data = self.midterm_exam.floatvect.astype(str).tolist()
        midterm2 = ["Midterm Exam"] + midterm_data
        midterm_mat = atleast_2d(midterm2).T
        self.estimate_grade_midpoint()
        midpoint_data = self.midpoint.tolist()
        midpoint2 = ["Midpoint Grade Estimate"] + midpoint_data
        midpoint_mat = atleast_2d(midpoint2).T
        data = column_stack([start_data,mat1,mat2,matq,midterm_mat, \
                             midpoint_mat])
        return data


    def check_column_classification(self):
        self.get_graded_cols_one_classification("quiz")
        N_quizzes = len(self.quiz)

        q_total = copy.copy(self.quiz[0].percentages)

        for q in self.quiz[1:]:
            q_total += q.percentages

        q_ave = q_total/N_quizzes

        self.quiz_average = q_ave
        return q_ave


    def find_hw_average(self):
        self.get_graded_cols_one_classification("assignment")
        self.get_graded_cols_one_classification("learning_activity")
        hw_cols = self.assignment + self.learning_activity
        self.hw_cols = hw_cols

        hw_total = copy.copy(hw_cols[0].floatvect)
        hw_poss_total = hw_cols[0].p_poss

        for col in hw_cols[1:]:
            hw_total += col.floatvect
            hw_poss_total += col.p_poss

        self.hw_total = hw_total
        self.hw_ave = (hw_total/hw_poss_total)*100
        self.hw_poss_total = hw_poss_total
        return self.hw_ave


    def hw_report_data(self, short=False):
        data = []
        labels = []

        if not short:
            for col in self.hw_cols:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

        if not short:
            data.append(self.hw_total)
            labels.append('HW Total')

        data.append(self.hw_ave)
        labels.append('HW Ave (%i points possible)' % self.hw_poss_total)

        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def quiz_report_data(self, short=False):
        data = []
        labels = []

        if not short:
            for col in self.quiz:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

            for col in self.quiz:
                shortname = get_short_col_name(col.attr_name) + " %"
                labels.append(shortname)
                data.append(col.percentages)

        data.append(self.quiz_average)
        labels.append('Quiz Ave')

        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def find_project_average(self):
        self.get_graded_cols_one_classification("project")

        project_total = copy.copy(self.project[0].floatvect)
        project_poss_total = self.project[0].p_poss

        for col in self.project[1:]:
            project_total += col.floatvect
            project_poss_total += col.p_poss

        self.project_total = project_total
        self.project_ave = (project_total/project_poss_total)*100
        self.project_poss_total = project_poss_total
        return self.project_ave


    def project_report_data(self, short=False):
        data = []
        labels = []


        if not short:
            for col in self.project:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

        if not short:
            data.append(self.project_total)
            labels.append('Project Total')

        data.append(self.project_ave)
        labels.append('Project Ave (%i points possible)' % \
                               self.project_poss_total)

        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def find_midterm(self):
        for attr in self.attr_names:
            if attr.find("Midterm_Exam") == 0:
                myvect = getattr(self, attr)
                self.midterm_exam = bb_column(attr, myvect, \
                                              pat_order=self.pat_order)


    def estimate_grade_midpoint(self):
        # Assignments and Learning Activities 20 %
        # Quizzes 10 %
        # Exams 40 %
        # Project 30%
        self.midpoint = 0.2*self.hw_ave + \
                        0.1*self.quiz_average + \
                        0.4*self.midterm_exam.floatvect + \
                        0.3*self.project_ave
        return self.midpoint


    def big_report(self, short=False):
        mat1 = self.hw_report_data(short=short)
        mat2 = self.project_report_data(short=short)
        matq = self.quiz_report_data(short=short)
        name_data = self.data[:,0:4]
        name_labels = self.labels[0:4]
        start_data = row_stack([name_labels,name_data])
        if not hasattr(self,"midterm_exam"):
            self.find_midterm()
        midterm_data = self.midterm_exam.floatvect.astype(str).tolist()
        midterm2 = ["Midterm Exam"] + midterm_data
        midterm_mat = atleast_2d(midterm2).T
        self.estimate_grade_midpoint()
        midpoint_data = self.midpoint.tolist()
        midpoint2 = ["Midpoint Grade Estimate"] + midpoint_data
        midpoint_mat = atleast_2d(midpoint2).T
        data = column_stack([start_data,mat1,mat2,matq,midterm_mat, \
                             midpoint_mat])
        return data


    def check_column_classification(self):
        self.get_graded_cols_one_classification("quiz")
        N_quizzes = len(self.quiz)

        q_total = copy.copy(self.quiz[0].percentages)

        for q in self.quiz[1:]:
            q_total += q.percentages

        q_ave = q_total/N_quizzes

        self.quiz_average = q_ave
        return q_ave


    def find_hw_average(self):
        self.get_graded_cols_one_classification("assignment")
        self.get_graded_cols_one_classification("learning_activity")
        hw_cols = self.assignment + self.learning_activity
        self.hw_cols = hw_cols

        hw_total = copy.copy(hw_cols[0].floatvect)
        hw_poss_total = hw_cols[0].p_poss

        for col in hw_cols[1:]:
            hw_total += col.floatvect
            hw_poss_total += col.p_poss

        self.hw_total = hw_total
        self.hw_ave = (hw_total/hw_poss_total)*100
        self.hw_poss_total = hw_poss_total
        return self.hw_ave


    def hw_report_data(self, short=False):
        data = []
        labels = []

        if not short:
            for col in self.hw_cols:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

        if not short:
            data.append(self.hw_total)
            labels.append('HW Total')

        data.append(self.hw_ave)
        labels.append('HW Ave (%i points possible)' % self.hw_poss_total)

        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def quiz_report_data(self, short=False):
        data = []
        labels = []

        if not short:
            for col in self.quiz:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

            for col in self.quiz:
                shortname = get_short_col_name(col.attr_name) + " %"
                labels.append(shortname)
                data.append(col.percentages)

        data.append(self.quiz_average)
        labels.append('Quiz Ave')

        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def find_project_average(self):
        self.get_graded_cols_one_classification("project")

        project_total = copy.copy(self.project[0].floatvect)
        project_poss_total = self.project[0].p_poss

        for col in self.project[1:]:
            project_total += col.floatvect
            project_poss_total += col.p_poss

        self.project_total = project_total
        self.project_ave = (project_total/project_poss_total)*100
        self.project_poss_total = project_poss_total
        return self.project_ave


    def project_report_data(self, short=False):
        data = []
        labels = []


        if not short:
            for col in self.project:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

        if not short:
            data.append(self.project_total)
            labels.append('Project Total')

        data.append(self.project_ave)
        labels.append('Project Ave (%i points possible)' % \
                               self.project_poss_total)

        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def find_midterm(self):
        for attr in self.attr_names:
            if attr.find("Midterm_Exam") == 0:
                myvect = getattr(self, attr)
                self.midterm_exam = bb_column(attr, myvect, \
                                              pat_order=self.pat_order)


    def estimate_grade_midpoint(self):
        # Assignments and Learning Activities 20 %
        # Quizzes 10 %
        # Exams 40 %
        # Project 30%
        self.midpoint = 0.2*self.hw_ave + \
                        0.1*self.quiz_average + \
                        0.4*self.midterm_exam.floatvect + \
                        0.3*self.project_ave
        return self.midpoint


    def big_report(self, short=False):
        mat1 = self.hw_report_data(short=short)
        mat2 = self.project_report_data(short=short)
        matq = self.quiz_report_data(short=short)
        name_data = self.data[:,0:4]
        name_labels = self.labels[0:4]
        start_data = row_stack([name_labels,name_data])
        if not hasattr(self,"midterm_exam"):
            self.find_midterm()
        midterm_data = self.midterm_exam.floatvect.astype(str).tolist()
        midterm2 = ["Midterm Exam"] + midterm_data
        midterm_mat = atleast_2d(midterm2).T
        self.estimate_grade_midpoint()
        midpoint_data = self.midpoint.tolist()
        midpoint2 = ["Midpoint Grade Estimate"] + midpoint_data
        midpoint_mat = atleast_2d(midpoint2).T
        data = column_stack([start_data,mat1,mat2,matq,midterm_mat, \
                             midpoint_mat])
        return data


    def check_column_classification(self, skip_list=[]):

        all_attrs = copy.copy(self.attr_names)

        for key in self.pat_order:
            cols = self.get_graded_cols_one_classification(key)

            if cols:
                print(key)
                print("-"*20)

            for col in cols:
                print(col.attr_name)
                all_attrs.remove(col.attr_name)

            print('')


        for item in skip_list:
            if item in all_attrs:
                all_attrs.remove(item)


        print('')
        print('Not used:')
        print('-'*20)

        for item in all_attrs:
            print(item)


        return all_attrs


class bb_107_final_grade_calculator(bb_grade_checker):
    def project_report_data(self, short=False):
        # The card game is the only project score for 107 in W17,
        # everything else is a group grade
        data = []
        labels = []


        for col in self.project:
            shortname = get_short_col_name(col.attr_name)
            labels.append(shortname)
            data.append(col.floatvect)

        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def find_group_average(self):
        self.get_graded_cols_one_classification("group_assign")

        group_total = copy.copy(self.group_assign[0].floatvect)
        group_poss_total = self.group_assign[0].p_poss

        for col in self.group_assign[1:]:
            group_total += col.floatvect
            group_poss_total += col.p_poss

        self.group_total = group_total
        self.group_ave = (group_total/group_poss_total)*100
        self.group_poss_total = group_poss_total
        return self.group_ave


    def group_report_data(self, short=False):
        data = []
        labels = []


        if not short:
            for col in self.group_assign:
                shortname = get_short_col_name(col.attr_name)
                labels.append(shortname)
                data.append(col.floatvect)

        data.append(self.group_total)
        labels.append('Group Total (%i points possible)' % \
                               self.group_poss_total)

        data.append(self.group_ave)
        labels.append('Group Ave (%i points possible)' % \
                               self.group_poss_total)

        data_float = column_stack(data)
        data_str = data_float.astype('S30')

        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def attr_to_mat(self, attr, label):
        col = getattr(self, attr)
        vect = col.floatvect
        mylist = vect.astype(str).tolist()
        list_w_label = [label] + mylist
        mymat = atleast_2d(list_w_label).T
        return mymat


    def big_report(self, short=False):
        mat1 = self.hw_report_data(short=short)
        mat2 = self.project_report_data(short=short)
        matq = self.quiz_report_data(short=short)
        matg = self.group_report_data(short=short)
        name_data = self.data[:,0:4]
        name_labels = self.labels[0:4]
        start_data = row_stack([name_labels,name_data])

        # --> Get midterm and exam 2 into big_report

        if not hasattr(self,"midterm_exam"):
            self.find_midterm()

        midpoint_mat = self.attr_to_mat("midterm_exam", "Midterm Exam")

        if not hasattr(self, "exam_2"):
            self.find_exam_2()

        e2_mat = self.attr_to_mat("exam_2","Exam 2")

        ## self.estimate_grade_midpoint()
        ## midpoint_data = self.midpoint.tolist()
        ## midpoint2 = ["Midpoint Grade Estimate"] + midpoint_data
        ## midpoint_mat = atleast_2d(midpoint2).T
        ## data = column_stack([start_data,mat1,mat2,matq,midterm_mat, \
        ##                      midpoint_mat])
        data = column_stack([start_data,mat1,mat2,matq,matg, \
                             midpoint_mat, e2_mat])
        return data

    # To do:
    # - check how I calculate the quiz average


class bb_445_final_grade_helper(bb_107_final_grade_calculator):
    def __init__(self, *args, **kwargs):
        if 'pat_order' not in kwargs:
            kwargs['pat_order'] = pat_order_445
        bb_107_final_grade_calculator.__init__(self, *args, **kwargs)


    def find_exams(self):
        exam_list = ["Exam_%i" % i for i in range(1,3)]

        for exam_attr in exam_list:
            self.find_column_with_start_match(exam_attr)
            curcol = getattr(self,exam_attr)
            curcol.clean_grades()


    def find_final_exam(self):
        if not hasattr(self, "Final_Exam"):
            self.find_column_with_start_match("Final_Exam")
            self.Final_Exam.clean_grades()


    def find_project_average(self):
        project_list = ["Project_%i" % i for i in range(1,4)]

        for proj_attr in project_list:
            self.find_column_with_start_match(proj_attr)
            curcol = getattr(self,proj_attr)
            curcol.clean_grades()

        project_ave = 0.25*self.Project_1.floatvect + \
                      0.5*self.Project_2.floatvect + \
                      0.25*self.Project_3.floatvect

        self.project_ave = project_ave
        return project_ave


    def project_report_data(self, short=False):
        # The card game is the only project score for 107 in W17,
        # everything else is a group grade
        data = []
        labels = []


        for col in self.project:
            shortname = get_short_col_name(col.attr_name)
            labels.append(shortname)
            data.append(col.floatvect)


        labels.append('Project Average')
        data.append(self.project_ave)

        data_float = column_stack(data)
        data_str = data_float.astype('S30')


        out_mat = row_stack([labels, data_str])
        #return data_float, labels
        return out_mat


    def calc_exam_average(self):
        e1scores = self.Exam_1.floatvect
        e2scores = self.Exam_2.floatvect
        self.find_final_exam()
        finalscores = self.Final_Exam.floatvect
        exam_average = 0.25*e1scores + 0.25*e2scores + 0.5*finalscores
        self.exam_average = exam_average
        return exam_average


    def exam_report(self):
        if not hasattr(self,"Exam_2"):
            self.find_exams()

        exam_report_data = []

        for i in range(1,3):
            e_attr = "Exam_%i" % i
            exam_col = getattr(self, e_attr)
            exam_data = exam_col.floatvect.astype(str).tolist()
            exam_w_label = [e_attr] + exam_data
            exam_report_data.append(exam_w_label)

        self.find_final_exam()
        final_data = self.Final_Exam.floatvect.astype(str).tolist()
        final_w_label = ['Final Exam'] + final_data
        exam_report_data.append(final_w_label)
        self.calc_exam_average()

        ave_w_label = ['Exam Average'] + self.exam_average.astype(str).tolist()
        exam_report_data.append(ave_w_label)
        exam_mat = numpy.column_stack(exam_report_data)
        return exam_mat


    def calc_course_grade(self):
        cg = 0.15*self.hw_ave + 0.15*self.quiz_average + \
             0.3*self.project_ave + 0.4*self.exam_average
        self.course_grade = cg 

    def big_report(self, short=False):
        mat1 = self.hw_report_data(short=short)
        mat2 = self.project_report_data(short=short)
        matq = self.quiz_report_data(short=short)
        name_data = self.data[:,0:4]
        name_labels = self.labels[0:4]
        start_data = row_stack([name_labels,name_data])

        exam_mat = self.exam_report()
        #Pdb().set_trace()
        self.calc_course_grade()
        cg_col = ['Course Grade'] + self.course_grade.astype(float).tolist()
        data = column_stack([start_data,mat1,mat2,matq,exam_mat,cg_col])
        return data
