"""
This script runs a simple glm on one subject for the MCSE condition 
and returns the contrasts obtained
TODO: group analysis
TODO: remove anatomical images from data package
TODO: make it a notebook
TODO: trial-wise model
"""
import os
import glob
import numpy as np

from nilearn.glm.first_level import make_first_level_design_matrix
from nilearn.image import high_variance_confounds
from nilearn.plotting import plot_design_matrix, show
from nilearn.image import load_img
import pandas as pd
from nilearn.glm.first_level import FirstLevelModel

gm_mask = '../data/gm_mask_3mm.nii.gz'

TR = 2.0 # TODO: read from meta-data

write_dir = 'results'
if not os.path.exists(write_dir):
    os.mkdir(write_dir)

data_dir = '/home/bertrandthirion/Téléchargements/3mm' # TODO: update me
subjects = [os.path.basename(x) for x in
            glob.glob(os.path.join(data_dir, 'sub-*'))]

##########################################################################
# utility function to fetch individual data

def fetch_data(data_dir, subject):
    # prepare the data for the subject
    bold = []
    confounds = []
    events = []
    # infer the session name for the data
    session = [os.path.basename(x) for x in glob.glob(os.path.join(data_dir, subject, 'ses-*'))
               if 'ses-00' not in x][0]
    func_dir = os.path.join(data_dir, subject, session, 'func')
    for direction in ['pa', 'ap']: # ap and pa correspond to 2 runs
        wc = os.path.join(
            func_dir,
            '{}_{}_task-MCSE_dir-{}_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz'.format(
                subject, session, direction))
        bold.append(wc)
        wc = os.path.join(
            func_dir,
            '{}_{}_task-MCSE_dir-{}_desc-confounds_timeseries.tsv'.format(
                subject, session, direction))
        confounds.append(wc)
        wc = os.path.join(func_dir,
            '{}_{}_task-MCSE_dir-{}_events.tsv'.format(subject, session, direction))
        events.append(wc)
    return bold, confounds, events

##########################################################################
# Explore the design
# Get the data
subject = subjects[0]
bold, confounds, events = fetch_data(data_dir, subject)

from nilearn.plotting import plot_event, show
event_dfs = [pd.read_csv(event, sep='\t') for event in events]
plot_event(event_dfs, figsize=(9, 4))

#############################################################################
# GLM fitting
model = FirstLevelModel(
    t_r=TR, 
    mask_img=gm_mask,
    smoothing_fwhm=5,
    high_pass = 0.008,
    hrf_model='spm + derivative',
    slice_time_ref=.5)

##########################################################################
# utility function to specify contrasts

def mcse_contrasts():
    """Specification of relevant MCSE contrasts"""
    contrasts = {
        'low-high salience': 'low_salience_left + low_salience_right' +\
            '- hi_salience_left - hi_salience_right',
        'salience_left-right': 'low_salience_left - low_salience_right' +\
            '+ hi_salience_left - hi_salience_right'
    }
    return contrasts
contrasts = mcse_contrasts()

#############################################################################
# run the analysis in one subject

# Prepare write dir
subject_dir = os.path.join(write_dir, subject)
if not os.path.exists(subject_dir):
    os.mkdir(subject_dir)
    
event_dfs = []
for i, (event, confound, img) in enumerate(zip(events, confounds, bold)):
    # Don't model implicit baseline
    event_df = pd.read_csv(event, index_col=None, sep='\t')
    event_df = event_df[event_df. trial_type != 'Bfix']
    event_dfs.append(event_df) 

    """
    # fit the model
    model.fit(img, events=event_df, confounds=confound)
    report = model.generate_report(contrasts)
    report.save_as_html(
        os.path.join(subject_dir, 'report_{}.html'.format(i)))
    """

#############################################################################
# Directly compute a fixed effects
model.fit(bold, events=event_dfs, confounds=confounds)
report = model.generate_report(contrasts)
report.save_as_html(os.path.join(subject_dir, 'report_ffx.html'))


#############################################################################
# Save contrast images for future use
for  key in contrasts.keys():
    stat_img = model.compute_contrast(contrasts[key], output_type='z_score')
    output_file = os.path.join(subject_dir, f'{key}_z_score.nii.gz')
    stat_img.to_filename(output_file)

#############################################################################
# run that on all subjects
for subject in subjects:
    subject_dir = os.path.join(write_dir, subject)
    if not os.path.exists(subject_dir):
        os.mkdir(subject_dir)
    bold, confounds, events = fetch_data(data_dir, subject)
    event_dfs = []
    for event in events:
        event_df = pd.read_csv(event, index_col=None, sep='\t')
        event_df = event_df[event_df. trial_type != 'Bfix']
        event_dfs.append(event_df) 
    
    model.fit(bold, events=event_dfs, confounds=confounds)
    for  key in contrasts.keys():
        stat_img = model.compute_contrast(
                contrasts[key], output_type='z_score')
        output_file = os.path.join(subject_dir, f'{key}_z_score.nii.gz')
        stat_img.to_filename(output_file)

###########################################################################
# Do a one-sample test across subjects
from nilearn.glm.second_level import SecondLevelModel
from nilearn.plotting import plot_stat_map
from nilearn.glm import threshold_stats_img
design_matrix = pd.DataFrame([1] * len(subjects), columns=['intercept'])
second_level_model = SecondLevelModel()
alpha = .05 # desired significance level

for key in contrasts.keys():
    # Get the images
    imgs = [os.path.join(write_dir, subject, f'{key}_z_score.nii.gz')
            for subject in subjects]    
    second_level_model.fit(imgs, design_matrix=design_matrix)
    z_map = second_level_model.compute_contrast(output_type='stat')
    
    # Take a statistical threshold
    _, threshold = threshold_stats_img(
        z_map, alpha=alpha, height_control='fdr')

    # look at the result
    plot_stat_map(
        z_map, threshold=threshold, title=f'{key}, fdr <{alpha}')
