import txt_database
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import txt_database
import pylab_util as PU


class vector_summary(object):
    def calc_stats(self):
        self.mean = self.vector.mean()
        self.max = self.vector.max()
        self.min = self.vector.min()
        self.std = self.vector.std()
        self.maxdabove = (self.max-self.mean)
        self.mindbelow = (self.mean-self.min)
        self.maxpabove = (self.max-self.mean)/self.mean*100
        self.minpbelow = (self.mean-self.min)/self.mean*100
        

    def __repr__(self):
        outstr = ""

        attr_list = ['mean','max','min','std', \
                     'maxdabove','mindbelow', \
                     'maxpabove','minpbelow']

        for attr in attr_list:
            val = getattr(self, attr)
            curline = "%s = %0.4g\n" % (attr, val)
            outstr += curline

        return outstr
    
        
    def __init__(self, vectin):
        self.vector = vectin
        self.calc_stats()
        
    

class column(object):
    """Class for representing one column of a Saleae csv file.  The
    class will be used to find rising and fall edges and various
    periods."""
    def __init__(self, t, data):
        """I don't know how to do this without duplicating t.  Saleae
        files are just lists of 0's and 1's without the time vector.
        Do I make a copy of t each time or am I sure I am not going to
        modify it?"""
        self.t = t
        self.data = data
        self.find_rising_edges()
        self.find_falling_edges()
        self.find_high_periods()
        self.find_rising_edge_periods()
        self.find_falling_edge_periods()
        

    def find_rising_edges(self):
        """A rising edge is any point where the current value is
        greater than the previous value.  The time of the rising edge
        is after the value has switched high."""
        d1 = self.data[1:]
        t1 = self.t[1:]
        d2 = self.data[0:-1]
        inds = np.where(d1>d2)[0]
        self.rising_edges = t1[inds]
        self.rising_points = d1[inds]


    def find_falling_edges(self):
        d1 = self.data[1:]
        t1 = self.t[1:]
        d2 = self.data[0:-1]
        inds = np.where(d1<d2)[0]
        self.falling_edges = t1[inds]
        self.falling_points = d1[inds]


    def find_high_periods(self):
        try:
            self.high_periods = self.falling_edges - self.rising_edges
        except:
            pass


    def find_rising_edge_periods(self):
        self.rising_edge_periods = self.rising_edges[1:] - \
                                   self.rising_edges[0:-1]
        

    def find_falling_edge_periods(self):
        self.falling_edge_periods = self.falling_edges[1:] - \
                                    self.falling_edges[0:-1]



    def plot_edges_check(self, ax, linefmt='-', ptfmt=None, \
                         case='rising', ylim=[-0.1,1.1]):
        ax.step(self.t, self.data, linefmt, where='post')

        if case == 'rising':
            if ptfmt is None:
                ptfmt = 'o'
            ax.plot(self.rising_edges, self.rising_points, ptfmt)
        else:
            if ptfmt is None:
                ptfmt = '^'
            ax.plot(self.falling_edges, self.falling_points, ptfmt)
            
        ax.set_ylim(ylim)


    def plot_rising_edges_check(self, *args, **kwargs):
        self.plot_edges_check(*args, case='rising', **kwargs)
        

    def plot_falling_edges_check(self, *args, **kwargs):
        self.plot_edges_check(*args, case='falling', **kwargs)


class saleae_csv(txt_database.txt_database_from_file):
    """Class for plotting and analyzing Saleae csv files from my
    Saleae logic"""
    def __init__(self, filepath, skipcols=None):
        data, labels = txt_database._open_txt_file(filepath, delim=',')
        self.data = data.astype(float)
        self.raw_labels = labels
        self.N_cols = len(labels)
        ch_nums = range(self.N_cols-1)
        ch_labels = ['ch_%i' % i for i in ch_nums]
        clean_labels = ['t'] + ch_labels
        self.labels = clean_labels
        inds = range(self.N_cols)
        self.col_inds = dict(zip(self.labels, inds))
        self.next_ind = -1
        self.map_cols_to_attr()
        self.ch_nums = ch_nums
        self.ch_labels = ch_labels
        self._process_data()


    def _process_data(self):
        self.create_columns()
        

    def map_cols_to_attr(self):
        """make each column of self.data an attribute of the db
        instance."""
        ## this is from the base class:
        ## for attr, label in zip(self.attr_names, self.labels):
        ##     col_ind = self.col_inds[label]
        ##     if len(self.data) > 0:
        ##         setattr(self, attr, self.data[:,col_ind])
        #
        # hard coding based on what I know about saleae files:
        self.t = self.data[:,0]#.astype(float)
        nr, nc = self.data.shape
        self.num_cols = nc-1
        
        for i in range(0,self.num_cols):
            attr = 'ch_%i' % i
            j = i+1
            setattr(self, attr, self.data[:,j])#.astype(float))
            
    

    def create_columns(self):
        if not hasattr(self, 'ch_0'):
            self.map_cols_to_attr()
            
        cols = []
        for i in range(self.num_cols):
            attr = 'ch_%i' % i
            vect = getattr(self, attr)
            cur_col = column(self.t, vect)
            cols.append(cur_col)

        self.columns = cols
        

def diff_vects(vect1, vect2, shift2=0):
    N1 = len(vect1)
    N2 = len(vect2)
    N = min([N1,N2])
    if (N+shift2) > N2:
        N = N2-shift2
    diff_vect = vect1[0:N] - vect2[shift2:N+shift2]

    return diff_vect


class arduino_saleae_comp(object):
    def find_csv_files(self):
        name_pat = "*%s*%0.3d*.csv"
        #Allowing for capital or small A in arduino 
        arduino_name_pat = name_pat % ("rduino",self.test_num)
        saleae_name_pat = name_pat % ("aleae",self.test_num)
        arduino_pat = os.path.join(self.root, arduino_name_pat)
        saleae_pat = os.path.join(self.root, saleae_name_pat)
        arduino_matches = glob.glob(arduino_pat)
        saleae_matches = glob.glob(saleae_pat)
        len_ard = len(arduino_matches)
        len_sal = len(saleae_matches)
        assert len_ard==1, "Found %d arduino matches for %s" % (len_ard, arduino_pat)
        assert len_sal==1, "Found %d arduino matches for %s" % (len_sal, saleae_pat)
        self.arduino_filepath = arduino_matches[0]
        self.saleae_filepath = saleae_matches[0]


    def load_arduino(self):
        self.arduino_db = txt_database.txt_database_from_file(self.arduino_filepath)
        ard_map = {'dtA':'dt_ms', \
                   'dt2A':'_dt2_ms', \
                   #'dt2A':'dt2_ms', \
                   'dt1A':'dt1_ms', \
                   'timeA':'t_ms', \
                   'theta_d':'theta_d', \
                   'encoder':'encoder', \
                   'pwm':'pwm'}
        
        for key, val in ard_map.items():
            if hasattr(self.arduino_db, val):
                str_vect = getattr(self.arduino_db, val)
                float_vect = str_vect.astype(float)
                setattr(self, key, float_vect)
            else:
                print('attr not found: %s' % val)
        


    def load_saleae(self):
        self.saleae_file = saleae_csv(self.saleae_filepath)
        self.ncS = len(self.saleae_file.columns)

        for i in range(self.ncS):
            curcol = self.saleae_file.columns[i]
            attr = 'ch%iS' % i
            setattr(self, attr, curcol)
        
        self.dtS = self.ch1S.rising_edge_periods*1000
        self.dtSf = self.ch1S.falling_edge_periods*1000
        self.dt1S = self.ch1S.high_periods*1000
        self.dt2S = self.ch2S.high_periods*1000


    def _calc_one_diff(self, case, percent=True):
        if case == 0:
            sattr = 'dtS'
            aattr = 'dtA'
            pattr = 'diff_dt'
            shift = 1#Arduino lags
            

        elif case == 1:
            sattr = 'dt1S'
            aattr = 'dt1A'
            pattr = 'diff_dt1'
            shift = 0#no lag
            
        elif case == 2:
            sattr = 'dt2S'
            aattr = 'dt2A'
            pattr = 'diff_dt2'
            shift = 1#Arduino lags

            
        svect = getattr(self, sattr)
        avect = getattr(self, aattr)

        dvect = diff_vects(svect, avect, shift2=shift)
        

        if percent:
            pattr = 'p' + pattr
            D = (svect.mean()+avect.mean())/2.0
            pvect = (dvect/D)*100
            setattr(self, pattr, pvect)
        else:
            setattr(self, pattr, dvect)
            

    def calc_pdiffs(self):
        for i in range(3):
            self._calc_one_diff(case=i, percent=True)


    def calc_diffs(self):
        for i in range(3):
            self._calc_one_diff(case=i, percent=False)

            
    def __init__(self, test_num, root):
        """It is assumed that one and only one test will match the
        glob pattern root/*arduino*test_num*.csv and that 'arduino' or
        'saleae' proceeds test_num."""
        self.test_num = test_num
        self.root = root


    def plot_one_hist(self, attr, label_case=1, nbins=20, xticks=None, \
                      save=False, suffix=None):
        if label_case == 1:
            xlabel = 'Time (ms)'
        elif label_case == 2:
            xlabel = 'Percent Difference'

        data = getattr(self, attr)

        shift_list = ['dtA','dt2A']

        if attr in shift_list:
            data = data[1:]
        
        plt.figure()
        n, bins, patches = plt.hist(data, nbins)

        plt.ylabel('Frequency of Occurence')
        plt.xlabel(xlabel)

        if xticks is not None:
            plt.xticks(xticks)

        if save:
            assert suffix is not None, \
                   "you must pass in a filename suffix when saving"
            self.save_fig(suffix)



    def plot_side_by_side_hist(self, attr1, attr2, label_case=1, \
                               nbins=20, xticks=None, \
                               save=False, suffix=None,
                               labels=None):
        if label_case == 1:
            xlabel = 'Time (ms)'
        elif label_case == 2:
            xlabel = 'Percent Difference'

        data1 = getattr(self, attr1)
        data2 = getattr(self, attr2)
        
        shift_list = ['dtA','dt2A']

        if attr1 in shift_list:
            data1 = data1[1:]
        if attr2 in shift_list:
            data2 = data2[1:]


        data = np.column_stack([data1,data2])

        plt.figure()
        
        n, bins, patches = plt.hist(data, nbins)#, alpha=0.5)
        #plt.hist(data2, bins, alpha=0.5)

        plt.ylabel('Frequency of Occurence')
        plt.xlabel(xlabel)

        if labels is not None:
            plt.legend(labels)
            
        if xticks is not None:
            plt.xticks(xticks)

        if save:
            assert suffix is not None, \
                   "you must pass in a filename suffix when saving"
            self.save_fig(suffix)

        
    def get_fig_path(self, suffix):
        fn = 'test_%0.3d_%s.eps' % (self.test_num, suffix)
        figpath = os.path.join('figs', fn)
        return figpath


    def save_fig(self, suffix):
        figpath = self.get_fig_path(suffix)
        PU.mysave(figpath)


    def plot_hist_list(self, attr_list, label_cases=None, nbins=None,
                       xticks=None, save=False):

        N = len(attr_list)

        if label_cases is None:
            label_cases = [None]*N

        if xticks is None:
            xticks = [None]*N
            

        for attr, label_case, xts in zip(attr_list, label_cases, xticks):
            kwargs = {}
            if label_case is not None:
                kwargs['label_case'] = label_case
            if nbins is not None:
                kwargs['nbins'] = nbins
            if xts is not None:
                kwargs['xticks'] = xts

            self.plot_one_hist(attr, **kwargs)

            if save:
                suffix = '%s_hist' % attr
                self.save_fig(suffix)
                

    def main(self):
        self.find_csv_files()
        self.load_arduino()
        self.load_saleae()
        self.calc_pdiffs()
        self.calc_diffs()


    def report_one_attr(self, attr):
        vect = getattr(self, attr)
        cur_sum = vector_summary(vect)
        print('='*20)
        print('%s:\n' % attr)
        print(cur_sum)
        print('')

        
    def report(self, case='all'):
        if case == 'all':
            vectlist = ['pdiff_dt',
                        'diff_dt',
                        'dtS',
                        'dt1S',
                        'dt2A',
                        'dtA',
                        'diff_dt1',
                        'pdiff_dt1',
                        'dtSf',
                        'diff_dt2',
                        'dt2S',
                        'dt1A',
                        'pdiff_dt2']
            
        elif case == 'dt1':
            vectlist = ['dt1A', \
                        'dt1S', \
                        'diff_dt1', \
                        'pdiff_dt1', \
                        ]

        elif case == 'dt2':
            vectlist = ['dt2A', \
                        'dt2S', \
                        'diff_dt2', \
                        'pdiff_dt2', \
                        ]

        elif case == 1:
            # diff dts
            vectlist = ['diff_dt', \
                        'diff_dt1', \
                        'diff_dt2', \
                        ]

        elif case == 2:
            # pdiff dts
            vectlist = ['pdiff_dt', \
                        'pdiff_dt1', \
                        'pdiff_dt2', \
                        ]


        for attr in vectlist:
            self.report_one_attr(attr)



    def plot_dt_vs_time(self, case=0, xmax=1000, save=False):
        skip = 0
        if case == 0:
            skip = 1
            yvect = self.dtA[skip:]
            ylabel = 'dt (ms) \nArduino'
            suffix = 'dt_vs_time'
        elif case == 1:
            skip = 0
            yvect = self.dt1A[skip:]
            ylabel = 'calc time $dt_1$ (ms) \nArduino'
            suffix = 'dt1_vs_time'            
        elif case == 2:
            skip = 1
            yvect = self.dt2A[skip:]
            ylabel = 'print time $dt_2$ (ms) \nArduino'
            suffix = 'dt2_vs_time'
            

        enc = self.encoder[skip:]
        t = self.timeA[skip:]

        yemin = enc.min()-25
        yemax = enc.max()+25

        kwargs={'linewidth':2}
        
        plt.figure()
        plt.subplot(211)
        plt.plot(t,enc, **kwargs)
        plt.ylim([yemin,yemax])
        plt.xlim([0,xmax])
        plt.ylabel('$\\theta$ from \nEncoder')
        
        plt.subplot(212)
        plt.plot(t, yvect, **kwargs)
        plt.xlim([0,xmax])
        plt.xlabel('Time (ms)')
        plt.ylabel(ylabel)
        
        
        if save:
            self.save_fig(suffix)
