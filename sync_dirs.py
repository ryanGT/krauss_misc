"""This module defines various groups of directories for backing up
with unison and rsync."""
# directories that should be included with pretty much every
# backup
quick_all = ['scripts', \
             '.profile', \
             '.inputrc', \
             '.gitconfig', \
             '.gitexcludes', \
             '.gitignore', \
             '.emacs', \
             'elisp', \
             #'teaching/fall_2016', \
             'teaching/summer_2017', \
             #'teaching/general_class_prep', \
             'Documents/Arduino', \
             'research/papers/ACC_2017_345_paper', \
             'research/papers/krauss_main_bib.bib', \
             'research/papers/ASEE_2017_345_346_paper', \
             #'siue/dan_h', \
             #'siue/raspi_quiz_solutions', \
             #'siue/grad_comp_forms', \
             #'siue/raspi_student_submissions', \
             #'siue/raspi_exam_feedback', \
             #'siue/travel_reimbursement', \
             #'siue/raspi_grades', \
             #'siue/Research/Proposals/internal', \
             #'siue/Research/presentations/ACC', \
             ]

quick_only = []#'siue/admin/grad_committee', \
              #'siue/admin/tau_beta_pi', \
              #'siue/admin/travel_forms', \
              #'siue/admin/letters_of_recommendation', \
              #'siue/admin/search_committees', \
              #'siue/admin/MRE_program', \
              #'siue/Research/papers/ACC/2016_zumo_RPi_Arduino', \
              #'siue/Research/papers/ASEE/krauss_fries_karacal_2016', \
              #]

personal = []#'personal/business', \
            #]

# add specific Research/work folders latter

weekly_all = ['git/research', \
              'git/krauss_misc', \
              #'git/olliei2c', \
              'git/teaching', \
              'git/report_generation', \
              'git/restutils', \
              #'git/rpi_arduino_communication', \
              'git/rst2beamer', \
              'teaching/general_class_prep', \
              'teaching/winter_2017', \
              #'git/wxpython_guis', \
              #'git/pygtk_guis', \
              #'git/pygtk_utils', \
              #'git/zumo_serial', \
              #'git/raspberry_pi_learn', \
              'Library/Services', \
              'Library/Scripts', \
              'Library/texmf', \
              #'siue/admin', \
              #'siue/Research/papers', \
              ]

#'siue/admin/MRE_program', \
#'siue/admin/search_committes', \
#'siue/admin/ug_catalog', \

ignore_list = ['siue/raspi_grades/final_project_files', \
               'teaching/fall_2016/345/prep_345/mac_video_recordings', \
               'teaching/fall_2016/345/prep_345/windows_install_tutorial_presentations', \
               'teaching/fall_2016/345/prep_345/windows_install_videos', \
               ]

