from scipy import *
import glob, os, sys, cPickle, re

import txt_mixin

from IPython.Debugger import Pdb

def O_replace(match):
    return match.group(1)+'0'+match.group(2)


def S_replace(match):
    return match.group(1)+'5'+match.group(2)


def tricky_replacer(match):
    print('in tricky_replacer')
    body = match.group(1)
    body = body.replace('O','0')
    body = body.replace('S','5')
    return body


item_titles = ["The course content was well organized.", \
               "The objectives of the course were clear.", \
               "Please rate the textbooks/manuals/workbooks.", \
               "This course was interesting and motivated you to want to learn more.", \
               "The instructor explained the material clearly.", \
               "The class time was used efficiently.", \
               "The instructor efficiently cleared up student difficulties with the course material.", \
               "The instructor was accessible outside of class.", \
               "The instructor's style/format was effective.", \
               "The instructor was open and helpful.", \
               "The assignments enhanced your learning.", \
               "The tests were reliable measures of your knowledge of the material.", \
               "The grading was fair.", \
               "You were provided with timely and helpful feedback about your performance.", \
               "Please rate the instructor's overall performance.", \
               "The amount of work was appropriate.", \
               "What percentage of class meetings did you attend?", \
               "Approximately how many hours did you work outside of class for each hour in class"]


class Eval_Base(txt_mixin.txt_file_with_list):
    def __init__(self, pathin=None, list_map=None, \
                 semester='Spring 2007', course='ME 356'):
        txt_mixin.txt_file_with_list.__init__(self, pathin=pathin, \
                                              list_map=list_map)
        fno, ext = os.path.splitext(self.pathin)
        self.fno = fno
        self.ext = ext
        self.semester = semester
        self.course = course
        self.clean = False


    def Add_Header(self):
        if not hasattr(self, 'latex'):
            self.Build_Latex()
        header_path = '/home/ryan/siue/tenure/student_evaluations/header.tex'
        header = txt_mixin.txt_file_with_list(header_path)
        self.full_latex = header.list + self.latex + ['\\end{document}']

        

    def Save_Latex(self):
        if not hasattr(self, 'latex'):
            self.Build_Latex()
        self.latex_path = self.fno + '_clean_nh.tex'
        self.latex_full_path = self.fno + '_clean.tex'
        self.writefile(self.latex_path, self.latex)
        self.Add_Header()
        self.writefile(self.latex_full_path, self.full_latex)
        return self.latex_path


    def Fancy_Header(self):
        fancy_list = []
        out = fancy_list.append
        out('\\pagestyle{fancy}')
        ws = ' '*5
        out(ws + '\\lhead{%s}' % self.course)
        out(ws + '\\chead{}')
        out(ws + '\\rhead{%s}' % self.semester)
        out(ws + '\\lfoot{Summarized Student Evaluations}')
        out(ws + '\\rfoot{Ryan W. Krauss}')
        out(ws + '\\cfoot{\\thepage}')
        out(ws + '\\renewcommand{\\headrulewidth}{0pt}')
        out(ws + '\\renewcommand{\\footrulewidth}{0pt}')
        return fancy_list


class Course_Report(Eval_Base):
    def input_latex_file(self, latex_in):
        lne, ext = os.path.splitext(latex_in)
        if not hasattr(self,'latex'):
            self.latex = []
        self.latex.append('\\input{%s}' % lne)
        

    def latex_append(self, line):
        if not hasattr(self,'latex'):
            self.latex = []
        self.latex.append(line)


    def latex_extend(self, listin):
        if not hasattr(self,'latex'):
            self.latex = []
        self.latex.extend(listin)
        

class Eval_CSV(Eval_Base):
    def clean_O_and_S(self):
        self.replaceall('"S"','5')
        self.replaceall('"O"','0')
        pat1 = '"([0-9S\.]*)O([0-9S\.]*)"'
        pat2 = pat1.replace('S','')
        pat2 = pat2.replace('O','S')        
        self.replaceallre(pat1, O_replace)
        self.replaceallre(pat2, S_replace)


    def clean_numbers_as_text(self):
        pat = '"([0-9\.]*)"'
        self.replaceallre(pat, '\\1')


    def clean_tricky_O_and_S_cases(self):
        pat = '"([0-9SO\.]+)"'
        print('calling tricky_replacer')
        self.replaceallre(pat, tricky_replacer)
        

    def clean_leading_blanks(self, pat='^[;, ]*'):
        self.replaceallre(pat, '')


    def clean_multiple_delims(self, pat='[;,]+', delim=','):
        self.replaceallre(pat, delim)


    def Save(self):
        self.pathout = self.fno+'_clean'+self.ext
        self.writefile(self.pathout)
        return self.pathout


##     def Save_Data(self):
##         fno, ext = os.path.splitext(self.pathin)
##         self.fno = fno
##         self.pretty_path = fno+'_pretty'+ext
##         self.Build_Pretty_Data()
##         self.writefile(self.pretty_path, self.pretty_data)
##         return self.pretty_path




    def Run(self):
        self.clean_O_and_S()
        self.clean_numbers_as_text()
        self.clean_tricky_O_and_S_cases()
        self.clean_leading_blanks()
        self.clean_multiple_delims()
        pathout = self.Save()
        self.clean = True
        return pathout



## "Sample Size",38,38,38,38,37
## "Number Missing",1,1,1,1,2
## "Mean",4.58,4.39,3.92,3.84,4.51
## "Variance",0.3,0.62,0.51,1,0.53
## "Standard Deviation",0.55,0.79,0.71,1,0.73

stats_map = {'size':'Sample Size','missing':'Number Missing', \
             'mean':'Mean', 'variance':'Variance', \
             'std_dev':'Standard Deviation'}

func_map = {'size':int,'missing':int, \
             'mean':float, 'variance':float, \
             'std_dev':float}


class stats_data(object):
    def __init__(self, rawdata=None, map=stats_map, func_map=func_map):
        self.rawdata = rawdata
        self.map = stats_map
        self.keys = map.keys()
        self.labels = map.values()
        self.func_map = func_map
        self.lookup = dict(zip(self.labels, self.keys))
        self.pickle_keys = self.keys+['inds']
        for key in map.keys():
            setattr(self, key, [])
        if rawdata is not None:
            self.process_raw()


    def _process_one_chunk(self, chunk):
        for row in chunk:
            curlist = row.split(',')
            curlabel = curlist.pop(0)
            curlabel = curlabel.replace('"','')
            curkey = self.lookup[curlabel]
            curattr = getattr(self, curkey)
            curattr.extend(curlist)


    def check_lengths(self, N=18):
        for key in self.keys:
            cur_list = getattr(self, key)
            cur_n = len(cur_list)
            if cur_n != N:
                print('Problem with length of '+key+':')
                print('   len('+key+')='+str(cur_n))
                

    def process_raw(self, datain=None):
        if datain is not None:
            self.rawdata = datain
        for chunk in self.rawdata:
            self._process_one_chunk(chunk)
        N = len(self.size)
        self.inds = range(1,N+1)
        self.check_lengths()
        

    def call_funcs(self):
        for key in self.keys:
            cur_list = getattr(self, key)
            cur_func = self.func_map[key]
            clean_list = [cur_func(item) for item in cur_list]
            setattr(self, key, clean_list)


    def pickle(self, filename):
        mydict = {}
        for key in self.pickle_keys:
            cur_list = getattr(self, key)
            mydict[key] = cur_list
        mypkl = open(filename,'wb')
        cPickle.dump(mydict,mypkl)
        mypkl.close()


    def load_pickle(self, filename):
        mypkl = open(filename,'rb')
        mydict = cPickle.load(mypkl)
        mypkl.close()
        for key, val in mydict.iteritems():
            setattr(self, key, val)
        
        
            
##  ['"Sample Size",38,38,38',
##   '"Number Missing",1,1,1',
##   '"Mean",4.05,4.82,3.11',
##   '"Variance",0.54,0.15,1.02',
##   '"Standard Deviation",0.73,0.39,1.01']

class Stats_CSV(Eval_CSV):
    def find_inds_for_data(self):
        start_inds = self.findall('"Sample Size"')
        end_inds = self.findall('"Standard Deviation"')
        test = array(end_inds)-array(start_inds)
        msg1 = 'Did not find 18 inds for'
##         if len(start_inds)  != 18:
##             print msg1 +' "Sample Size"' + '\n Found:' + \
##                   str(len(start_inds))
##         if len(end_inds) != 18:
##             print msg1 +' "Standard Deviation"' + '\n Found:' + \
##                   str(len(end_inds))
        mytest = test < 10
        if not mytest.all():
            print('Some of the differences between start and end inds ' + \
                        'where greater than 10:' + '\n' + str(test))
        self.start_inds = start_inds
        self.end_inds = end_inds


    def clean_last_page_data(self):
        """For some reason, the second page of stats gets transposed
        with just a few entries."""
        last_ind = self.end_inds[-1]
        last_std_dev = self.list[last_ind]
        if last_std_dev == '"Standard Deviation"':
            print('found bad data')
            last_lines = self.list[last_ind+1:]
            last_lines = filter(None, last_lines)
            pat = '"([0-9\\.]*)[,; \t]*([0-9\\.]*)"'
            p = re.compile(pat)
            row1 = []
            row2 = []
            for line in last_lines:
                q = p.search(line)
                if q:
                    row1.append(q.group(1))
                    row2.append(q.group(2))
            self.list[last_ind+1:] = []
            row1 = self.list[-2]+','+','.join(row1)
            self.list[-2] = row1
            row2 = self.list[-1]+','+','.join(row2)
            self.list[-1] = row2


    def Get_Data(self):
        if not self.clean:
            self.Run()
        self.data_lines = []

        if not hasattr(self, 'end_inds'):
            self.find_inds_for_data()
            
        self.data = []
        
        for start, end in zip(self.start_inds, self.end_inds):
            curdata = self.list[start:end+1]
            #"Total Valid" needs a blank cell next to it
            temp = txt_mixin.txt_list(curdata)
            self.data.append(temp)
        return self.data
        

    def Process_Data(self):
        if not hasattr(self, 'data'):
            self.Get_Data()
        self.stats_data = stats_data(self.data)
        self.stats_data.call_funcs()
        pne, ext = os.path.splitext(self.filename)
        pklname = pne+'.pkl'
        self.stats_data.pickle(pklname)
        self.variance = len(self.stats_data.variance) > 0


    def _list_to_row(self, row_list):
        return ' & '.join(row_list)+' \\\\'


    def _latex_one_row(self, ind, float_fmt='%0.2f'):
        data = self.stats_data
        keys = ['mean', 'size', 'missing', 'variance', 'std_dev']
        fmts = [float_fmt, '%i', '%i', float_fmt, float_fmt]
        cur_list = [str(ind+1)+': '+item_titles[ind]]
        for key, fmt in zip(keys, fmts):
            cur_attr = getattr(data, key)
            if cur_attr:
                cur_value = cur_attr[ind]
                cur_str = fmt % cur_value
                cur_list.append(cur_str)
        return self._list_to_row(cur_list)


    def latex_table_start(self):
        if self.variance:
            return '\\begin{tabular}{p{2.75in}*{5}{r}}'
        else:
            return '\\begin{tabular}{p{2.75in}*{4}{r}}'
    

    def _latex_label_format(self, labels, fstr='\\textbf'):
        flist = [fstr+'{'+item+'}' for item in labels]
        label_str_out = ' & '.join(flist)+ ' \\\\'
        return label_str_out


    def Build_Latex(self, N=18):
        tex_list = []
        out = tex_list.append
        ext = tex_list.extend

        #ext(self.Fancy_Header())
        
        out('')
        out('\\flushleft')
        out('')
        for i in range(N):
            if i == 0:
                out(self.latex_table_start())
                labels0 = ['','','Sample','Number','','Standard']
                labels1 = ['Question', 'Mean', 'Size', \
                           'Missing', 'Variance', \
                           'Deviation']
                if not self.variance:
                    labels0.pop(4)
                    labels1.pop(4)
                
                #labels = ['Question', 'Mean', 'Sample Size', \
                #          'Number Missing', 'Variance', \
                #          'Standard Deviation']
                flabels0 = self._latex_label_format(labels0)
                flabels1 = self._latex_label_format(labels1)
                out(flabels0)
                out(flabels1)
                out('\\hline')
            if i % 2 :
                out('\\rowcolor[gray]{0.9}')

            out(self._latex_one_row(i))

##             if (i % 6) == 5:
##                 out('\\end{tabular}')
        out('\\end{tabular}')
        self.latex = tex_list



class Item_Analysis_CSV(Stats_CSV):
    def find_inds_for_data(self):
        total_inds = self.findall('"Total Valid"')
        label_inds = self.findall('"Label"')
        for n, ind in enumerate(total_inds):
            nt = self.findnext('"Total"',ind)
            if nt == ind+2:
                total_inds[n] = nt
        test = array(total_inds)-array(label_inds)
        msg1 = 'Did not find 18 inds for'
        if len(total_inds)  != 18:
            print msg1 +' "Total"' + '\n Found:' + \
                  str(len(total_inds))
        if len(label_inds) != 18:
            print msg1 +' "Label"' + '\n Found:' + \
                  str(len(label_inds))
        mytest = test < 10
        if not mytest.all():
            print('Some of the differences between total and label inds ' + \
                        'where greater than 10:' + '\n' + str(test))
        self.total_inds = total_inds
        self.label_inds = label_inds


    def clean_a_s(self):
        self.replaceall('"a"','0')

    def Get_Data(self):
        if not hasattr(self, 'label_inds'):
            self.find_inds_for_data()
            
        self.data = []
        
        for start, end in zip(self.label_inds, self.total_inds):
            curdata = self.list[start:end+1]
            #"Total Valid" needs a blank cell next to it
            temp = txt_mixin.txt_list(curdata)
            ind = temp.findnext("Total Valid")
            if ind:
                temp[ind] = temp[ind].replace('"Total Valid"','"Total Valid",')
            self.data.append(temp)
        return self.data
        
        
    def Build_Pretty_Data(self):
        if not hasattr(self, 'data'):
            self.Get_Data()

        self.pretty_data = []
        i = 0
        for title, curdata in zip(item_titles, self.data):
            i += 1
            formatted_title = 'Item Analysis - Survey: %i: ' %i
            formatted_title += title
            self.pretty_data.append(formatted_title)
            self.pretty_data.extend(curdata)
            self.pretty_data.append('')
            

    def Save_Data(self):
        fno, ext = os.path.splitext(self.pathin)
        self.fno = fno
        self.pretty_path = fno+'_pretty'+ext
        self.Build_Pretty_Data()
        self.writefile(self.pretty_path, self.pretty_data)
        return self.pretty_path



    def _latex_title(self, ind, title):
        return '\\textbf{\\large Item Analysis - Survey: %s: %s}' % (ind, title)


    def _row_str_to_list(self, rowstr):
        rowstr = rowstr.strip()
        if rowstr[-1] == ',':
            rowstr = rowstr[0:-1]
        row_list = rowstr.split(',')
        return row_list


    def _clean_row(self, row_list):
        list_out = [item.replace('"','') for item in row_list]
        list_out = [item.replace('%','\\%') for item in list_out]
        list_out = [item.replace('>','$>$') for item in list_out]
        list_out = [item.replace('&','\&') for item in list_out]
        return list_out
    

    def _latex_label_format_list(self, labels, fstr='\\textbf'):
        flist = [fstr+'{'+item+'}' for item in labels]
        return flist

    def _latex_label_format(self, labels, fstr='\\textbf'):
        flist = self._latex_label_format_list(labels, fstr=fstr)
        label_str_out = ' & '.join(flist)+ ' \\\\'
        return label_str_out
    

    
    def _latex_one_chunk(self, data, title, ind):
        tex_list = []
        out = tex_list.append

        out('\\parbox{\\textwidth}{')
        out(self._latex_title(ind, title))
        out('')
        labels = self._row_str_to_list(data.pop(0))
        labels = [item.replace('"','') for item in labels]
        n = len(labels)-1
        
        out('\\begin{tabular}{l*{%i}{r}}'%n)
        out('\\hline')

        if data[0].find('"Percent","Percent","Valid Percent"') > -1:
            row2 = self._row_str_to_list(data.pop(0))
            row2 = self._clean_row(row2)
            n = len(labels) - len(row2)
            row1 = ['']*n +self._latex_label_format_list(labels[n:])
            out(self._list_to_row(row1))
            row2b = labels[0:n] + row2
            out(self._latex_label_format(row2b))
        else:
            out(self._latex_label_format(labels))
        out('\\hline')

        i = 0
        
        for row in data:
            row_list = self._row_str_to_list(row)
            clean_list = self._clean_row(row_list)
            out(self._list_to_row(clean_list))
            i += 1
            if (i < 5) and (i % 2):
                out('\\rowcolor[gray]{0.9}')
            if i == 5:
                out('\\hline')
            
        out('\\end{tabular}')
        out('}')#end parbox
        out('\\vspace{0.3in}')
        return tex_list
            


    def Build_Latex(self):
        tex_list = []
        out = tex_list.append
        ext = tex_list.extend
        
        i = 0
        
        out('')
        out('\\flushleft')
        out('')

        Pdb().set_trace()
        
        for title, curdata in zip(item_titles, self.data):
            i += 1
            cur_list = self._latex_one_chunk(curdata, title, i)
            ext(cur_list)
            out('')
            out('')
            #if (i % 4 == 0):
            #    out('\\pagebreak')
                
        self.latex = tex_list



    def Run(self):
        self.clean_O_and_S()
        self.clean_numbers_as_text()
        self.clean_tricky_O_and_S_cases()
        self.clean_a_s()
        self.clean_leading_blanks()
        self.clean_multiple_delims()
        self.find_inds_for_data()
        self.Get_Data()
        self.Save()
        self.Save_Latex()
        self.Save_Data()
        return self.latex_path

com_q1 = 'Please comment on the strengths and/or weaknesses of the instructor and the course, if any.'

com_q2 = 'Do you have any suggestions on how the course might be improved?'


class Comments_TXT(Item_Analysis_CSV):
    def Get_Comments(self):
        pat1 = r'[1 \.]*Please\s*comment\s*on\s*the\s*strengths'
        ind1 = self.findallre(pat1)
        assert len(ind1) == 1, 'Found more than one pat1 in self.list.'
        ind1 = ind1[0]
        pat2 = r'[2 \.]*Do\s*you\s*have\s*any\s*suggestions'
        ind2 = self.findallre(pat2)
        assert len(ind2) == 1, 'Found more than one pat2 in self.list.'
        ind2 = ind2[0]
        self.ind1 = ind1
        self.ind2 = ind2
        self.q1_comments = self.list[self.ind1+1:self.ind2]
        self.q2_comments = self.list[self.ind2+1:]
        self.q1_comments = filter(None, self.q1_comments)
        self.q2_comments = filter(None, self.q2_comments)

    def clean_comments(self):
        self.q1_comments = self._clean_row(self.q1_comments)
        self.q2_comments = self._clean_row(self.q2_comments)


    def _item_out(self, item):
        self.latex.append('\\item '+item)
        

    def Build_Latex(self):
        self.clean_comments()
        self.latex = []
        out = self.latex.append

        #out('\\textbf{\\large Written Comments}')
        out('\\begin{enumerate}')
        self._item_out('\\textbf{'+com_q1+'}')
        out('')
        if self.q1_comments:
            out('\\begin{itemize}')
            for item in self.q1_comments:
                self._item_out(item)
            out('\\end{itemize}')
            out('')
        if len(self.q1_comments) > 13:
            out('\\pagebreak')
        self._item_out('\\textbf{'+com_q2+'}')
        if self.q2_comments:
            out('\\begin{itemize}')
            for item in self.q2_comments:
                self._item_out(item)
            out('\\end{itemize}')
        out('\\end{enumerate}')
        
        
if __name__ == '__main__':
    myCSV = Stats_CSV('/home/ryan/siue/tenure/student_evaluations/ME356_S07_stats.csv')
    pathout = myCSV.Run()
    print('pathout='+pathout)
    myCSV.Get_Data()
    
