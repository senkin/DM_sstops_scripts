import sys
import numpy as np
import array
import matplotlib as mpl
from rootpy.tree import Tree
from rootpy.io import File, root_open
from rootpy.plotting import Hist, Hist2D, Hist3D
import rootpy.plotting.root2matplotlib as rplt
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, MultipleLocator
from matplotlib.colors import LogNorm
import scipy.interpolate
import scipy.optimize
import ROOT
from optparse import OptionParser
from calculate_MG_xsection import make_folder_if_not_exists
from cross_sections_DM import *

import matplotlib.cm as cm

# use full spectrum, yet use white for less than vmin=1 events
my_cmap = cm.get_cmap('jet')
my_cmap.set_under('w')
mpl.use('Agg')

processes = ['tt_excl', 'onshell', 'offshell', 'monotop', 'visible']

# Nominal model parameters
mediator_masses = [1000, 1500, 2000, 2500, 3000]
mDM = 1.
lumi = 36.1

m_ex = 0.03
monotop_excluded_xsections = {
    #mV : [observed, expected, upper_2sigma, upper_1sigma, lower_1sigma, lower_2sigma]
    1000: [m_ex, m_ex, m_ex, m_ex, m_ex, m_ex],
    1500: [m_ex, m_ex, m_ex, m_ex, m_ex, m_ex],
    2000: [m_ex, m_ex, m_ex, m_ex, m_ex, m_ex],
    2500: [m_ex, m_ex, m_ex, m_ex, m_ex, m_ex],
    3000: [m_ex, m_ex, m_ex, m_ex, m_ex, m_ex],
}

latex_labels = {
    'mV' : '$m_\mathrm{V}$ [GeV]',
    'mDM' : '$m_\mathrm{DM}$ [GeV]',
    'a_r' : '$g_\mathrm{SM}$',
    'g' : '$g_\mathrm{DM}$',
    'G_tot' : '$\Gamma_\mathrm{tot}$',
    'BR' : '$\mathrm{BR}_{\chi\chi}$',
}

additional_text_visible = 'DM model, combined SS tops'
additional_text_invisible = 'DM model, monotop, excl. %.0f fb' % (m_ex * 1000)
additional_text_overlay = 'DM model overlay, monotop excl. %.0f fb' % (m_ex * 1000)

# Ignore warning related to undefined division
np.seterr(divide='ignore', invalid='ignore')

# Plot settings
# mpl.rcParams['legend.frameon' ] = False
mpl.rcParams['legend.fontsize'] = 22
mpl.rcParams['xtick.labelsize'] = 22
mpl.rcParams['ytick.labelsize'] = 22
mpl.rcParams['axes.titlesize'] = 24
mpl.rcParams['axes.labelsize'] = 24
mpl.rcParams['lines.linewidth'] = 2.5
plt.rc('text', usetex=True)
plt.rc('font', family='sans-serif')


def set_labels(plt, axes, additional_text):
    # ATLAS text
    # note: fontweight/weight does not change anything as we use Latex text!!!
    logo_location = (0.05, 0.97)
    prelim_location = (0.2, 0.97)
    additional_location = (0.05, 0.90)
    lumi_location = (0.55, 0.97)

    plt.text(logo_location[0], logo_location[1], r"$\emph{\textbf{ATLAS}}$",
             fontsize=20, transform=axes.transAxes,
             verticalalignment='top', horizontalalignment='left')
    plt.text(prelim_location[0], prelim_location[1], "Internal",
             fontsize=20, transform=axes.transAxes,
             verticalalignment='top', horizontalalignment='left')

    plt.text(lumi_location[0], lumi_location[1], r"$\sqrt{s} =$ 13 TeV, %.1f fb$^{-1}$" % (lumi),
             fontsize=20, transform=axes.transAxes,
             verticalalignment='top', horizontalalignment='left')

    # channel text
    axes.text(additional_location[0], additional_location[1],
              r"%s" % additional_text, transform=axes.transAxes,
              fontsize=20, verticalalignment='top',
              horizontalalignment='left')


def get_limit_value(mV, a_r, g = '', BR='', type=1, process='visible', xsection_monotop=''):
    global parameterisation
    if process == 'visible':
        global input_folder_with_limits, mode, bkg_type
        if BR:
            signal_name = 'sstops_mV{0:.0f}'.format(mV) + '_a_r{0:.2f}'.format(a_r) + '_BR{0:.2f}'.format(BR)
        else:
            signal_name = 'sstops_mV{0:.0f}'.format(mV) + '_a_r{0:.2f}'.format(a_r) + '_g{0:.2f}'.format(g)
            if 'nominal_fine' in parameterisation:
                signal_name = 'sstops_mV{0:.0f}'.format(mV) + '_a_r{0:.3f}'.format(a_r) + '_g{0:.2f}'.format(g)

        try:
            input_root_file = ROOT.TFile(input_folder + '/' + signal_name + '/' + mode + '/' + bkg_type + 'bkg.root', "read")
            histogram = input_root_file.Get("limit")
            value = histogram.GetBinContent(type)
            input_root_file.Close()
        except:
            # print 'Warning: problem with reading file %s' % input_folder + '/' + signal_name + '/' + mode + '/' + bkg_type + 'bkg.root'
            # assuming exclusion
            value = 0.1

        if value > 1e3:
            # print 'Warning: limit value for (mV = %s, a_r = %s, g = %s) is %s. Setting it to 1000.' % (mV, a_r, g, value)
            value = 1000
            # raw_input("Press Enter to continue...")
        if np.isnan(value):
            # print 'Warning: limit value for (mV = %s, a_r = %s, g = %s) is %s. Setting it to 1000.' % (mV, a_r, g, value)
            value = 1000
            # raw_input("Press Enter to continue...")

    elif process == 'invisible' or process == 'monotop':
        if type == 1:
            # observed limit
            value = monotop_excluded_xsections[mV][0] / xsection_monotop
        elif type == 2:
            # expected limit
            value = monotop_excluded_xsections[mV][1] / xsection_monotop
        elif type == 3:
            # exp limit +2sigma
            value = monotop_excluded_xsections[mV][2] / xsection_monotop
        elif type == 4:
            # exp limit +1sigma
            value = monotop_excluded_xsections[mV][3] / xsection_monotop
        elif type == 5:
            # exp limit -1sigma
            value = monotop_excluded_xsections[mV][4] / xsection_monotop
        elif type == 6:
            # exp limit -2sigma
            value = monotop_excluded_xsections[mV][5] / xsection_monotop

    return value


def load_limits_to_tree(tree, mode="BlindExp", BR_run=False):
    events = tree.GetEntries()

    leaves  = "limit_vis_exp/D:limit_vis_exp_upper_2sigma/D:limit_vis_exp_upper_1sigma/D:limit_vis_exp_lower_1sigma/D:limit_vis_exp_lower_2sigma/D:"
    leaves += "limit_vis_obs/D:limit_invis_exp/D:limit_invis_obs/D"
    leafValues = array.array("d", [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    new_tree = tree.CloneTree(0)
    newBranch = new_tree.Branch("limits", leafValues, leaves)

    for i in range(events):
        tree.GetEntry(i)
        mV = tree.GetLeaf("mV").GetValue()
        a_r = tree.GetLeaf("a_r").GetValue()
        g = tree.GetLeaf("g").GetValue()
        if BR_run:
            BR = tree.GetLeaf("BR").GetValue()
        else:
            BR = ''
        xsection_monotop = tree.GetLeaf("xsection_monotop").GetValue()

        # print 'mV, a_r, g, BR, monotop_xsec, monotop limit:', mV, a_r, g, BR, xsection_monotop, monotop_excluded_xsections[int(mV)][0] / xsection_monotop
        # raw_input("Press Enter to continue...")

        # expected limit
        leafValues[0] = get_limit_value(mV, a_r, g, BR, 2)
        # exp limit +2sigma
        leafValues[1] = get_limit_value(mV, a_r, g, BR, 3)
        # exp limit +1sigma
        leafValues[2] = get_limit_value(mV, a_r, g, BR, 4)
        # exp limit -1sigma
        leafValues[3] = get_limit_value(mV, a_r, g, BR, 5)
        # exp limit -2sigma
        leafValues[4] = get_limit_value(mV, a_r, g, BR, 6)

        # exp monotop limit
        leafValues[6] = get_limit_value(mV, a_r, type=2, process='invisible', xsection_monotop=xsection_monotop)
        if not "BlindExp" in mode:
            # visible observed limit
            leafValues[5] = get_limit_value(mV, a_r, g, BR, 1)
            # invisible observed limit
            leafValues[7] = get_limit_value(mV, a_r, type=1, process='invisible', xsection_monotop=xsection_monotop)
        else:
            # observed limits = expected ones
            leafValues[5] = leafValues[0]
            # same for monotop
            leafValues[7] = leafValues[6]

        new_tree.Fill()

    return new_tree

def get_narrow_width_approx_area(tree, variables='mV:a_r', nwa_limit=0.1, interpolate=True):
    x_variable_name, y_variable_name = variables.split(":")

    x_array = []
    y_array = []

    for event in tree:
        x_array.append(getattr(event, x_variable_name))
        y_array.append(getattr(event, y_variable_name))

    x_array = np.asarray(x_array)
    y_array = np.asarray(y_array)

    x_array = sorted(np.unique(x_array))
    y_array = sorted(np.unique(y_array))

    roots = []

    for x_value in x_array:
        x_selection = "%s == %s" % (x_variable_name, x_value)
        x_selected_tree = tree.CopyTree(x_selection)

        # print 'Working with x value of ', x_value, ' applying selection ', x_selection
        # print 'Tree size: ', x_selected_tree.GetEntries()

        y_values = []
        relative_width_values = []

        # nwa (narrow width approx.) values
        y_nwa_values = []
        relative_width_nwa_values = []

        for event in x_selected_tree:
            y_value = getattr(event, y_variable_name)
            relative_width_value = float(getattr(event, 'G_tot'))/float(getattr(event, 'mV'))
            y_values.append(y_value)
            relative_width_values.append(relative_width_value)
            if relative_width_value<=nwa_limit:
                y_nwa_values.append(y_value)
                relative_width_nwa_values.append(relative_width_value)

        y_values = np.asarray(y_values)
        relative_width_values = np.asarray(relative_width_values)

        y_nwa_values = np.asarray(y_nwa_values)
        relative_width_nwa_values = np.asarray(relative_width_nwa_values)

        # print 'Couplings: ', y_values
        # print 'G_tot/mV: ', relative_width_values
        # print 'nwa couplings: ', y_nwa_values
        # print 'nwa G_tot/mV: ', relative_width_nwa_values

        if interpolate:
            f_inv = scipy.interpolate.interp1d(relative_width_values, y_values)

            # finding a nwa border when relative_width_values==nwa_limit
            # Assuming the continuous G_tot/mV function

            if relative_width_values[-1]<nwa_limit:
                # can't interpolate if the last coupling is already in nwa, try extrapolating:
                f_extr = scipy.interpolate.interp1d(relative_width_values, y_values, fill_value='extrapolate')
                roots.append(f_extr(nwa_limit))
                # roots.append(1e10)
            elif relative_width_values[0]>nwa_limit:
                # none of the values are in nwa
                roots.append(y_values[0])
            else:
                roots.append(f_inv(nwa_limit))
        else:
            # assuming monotonic, rising function
            try:
                roots.append(max(y_nwa_values))
            except:
                # if nothing's excluded, append a very big number
                roots.append(1e10)

        # print 'Saving nwa limit: ', roots[-1]

    # print 'Resulting nwa limits: ', roots
    return roots


def get_limits_from_tree(tree, variables='mV:a_r', process = 'visible', limit_type='expected', interpolate=True):
    if process == 'visible':
        if limit_type == 'observed':
            if interpolate:
                print 'Warning: interpolating observed limit. Are you sure?'
            limit_string = 'limit_vis_obs'
        elif limit_type == 'expected':
            limit_string = 'limit_vis_exp'
        else:
            # +/- sigma variations
            limit_string = 'limit_vis_exp_' + limit_type
    elif process == 'invisible' or process == 'monotop':
        if limit_type == 'observed':
            limit_string = 'limit_invis_obs'
        else:
            # only have expected limit so far, no variations
            limit_string = 'limit_invis_exp'
    else:
        print 'Unknown process %s for limit extraction, choose from visible/invisible.' % process
        sys.exit(1)

    x_variable_name, y_variable_name = variables.split(":")

    x_array = []
    y_array = []

    for event in tree:
        x_array.append(getattr(event, x_variable_name))
        y_array.append(getattr(event, y_variable_name))

    x_array = np.asarray(x_array)
    y_array = np.asarray(y_array)

    x_array = sorted(np.unique(x_array))
    y_array = sorted(np.unique(y_array))

    roots = []

    for x_value in x_array:
        x_selection = "%s == %s" % (x_variable_name, x_value)
        x_selected_tree = tree.CopyTree(x_selection)

        # print 'Working with x value of ', x_value, ' applying selection ', x_selection
        # print 'Tree size: ', x_selected_tree.GetEntries()

        y_values = []
        mu_values = []

        y_excl_values = []
        mu_excl_values = []

        for event in x_selected_tree:
            y_value = getattr(event, y_variable_name)
            mu_value = getattr(event, limit_string)
            y_values.append(y_value)
            mu_values.append(mu_value)
            if mu_value<=1:
                y_excl_values.append(y_value)
                mu_excl_values.append(mu_value)

        y_values = np.asarray(y_values)
        mu_values = np.asarray(mu_values)

        y_excl_values = np.asarray(y_excl_values)
        mu_excl_values = np.asarray(mu_excl_values)

        # print 'Couplings: ', y_values
        # print 'Limits: ', mu_values
        # print 'Excluded couplings: ', y_excl_values
        # print 'Exclusion limits: ', mu_excl_values

        if interpolate:
            f_inv = scipy.interpolate.interp1d(mu_values, y_values)

            # finding a limit value when mu_values==1
            # Assuming the continuous limit function

            if mu_values[0]<1 or mu_values[-1]>1:
                # none of the values are excluded, try extrapolating:
                f_extr = scipy.interpolate.interp1d(mu_values, y_values, fill_value='extrapolate')
                if f_extr(1)>0:
                    roots.append(f_extr(1))
                else:
                    # can't have a negative limit
                    roots.append(1e10)
            else:
                roots.append(f_inv(1))
        else:
            # assuming monotonic, rising function
            try:
                roots.append(min(y_excl_values))
            except:
                #if nothing's excluded, append a very big number
                roots.append(1e10)

        # print 'Saving limit: ', roots[-1]
        # check if the mu array is decreasing:
        # if not all(x>=y for x, y in zip(mu_values, mu_values[1:])):
        #     print '!!! Warning: the mu array is not decreasing monotonically.'
        #     raw_input("Press Enter to continue...")

        # print 'Limit type %s, mass %i, found root: %f' % (limit_type, mass, roots[-1])

    # print 'Resulting limits: ', roots
    return roots


def make_all_plots(mV, my_data, process):
    if 'visible' in process:
        make_limit_plots(mV, my_data, process)
    elif not 'monotop' in process:
        make_2D_plots(mV, my_data, process, show_alpha_beta_gamma=True)

def make_limit_plots(mV, my_data, process='visible'):
    make_2D_plots(mV, my_data, process, with_limits=True)
    make_2D_plots(mV, my_data, process, show_only_mu=True)


def make_fraction_plots(mV, my_data, mode='visible'):
    global output_folder, log_scale

    # sort by G_tot
    my_data = my_data[my_data[:, 1].argsort()]

    if mode == 'visible':
        # slice in columns
        BR = my_data[:, 0]
        G_tot = my_data[:, 1]
        a_r = my_data[:, 2]

        # cross-sections
        xsection_tt_excl = my_data[:, 9]
        xsection_onshell = my_data[:, 8]
        xsection_offshell = my_data[:, 7]
        xsection_monotop = my_data[:, 6]
        xsection_visible = xsection_tt_excl + xsection_onshell + xsection_offshell
        xsection_total = xsection_visible + xsection_monotop

        # fractions to visible
        fraction_tt_excl = xsection_tt_excl / xsection_visible
        fraction_onshell = xsection_onshell / xsection_visible
        fraction_offshell = xsection_offshell / xsection_visible

        plt.figure(figsize=(6, 6))
        plotTitle = '$m_V=$' + '{:.1f} TeV'.format(mV / 1000.) + \
                    ' ; $m_{DM}=$' + '{:.0f} GeV'.format(mDM)  # + \
        # ' ; $g_{DM}=$' + '{:.1f} '.format(g_DM)

        # x_slice = a_r
        # x_label = '$g_{SM}$'
        x_slice = G_tot
        x_label = '$\Gamma_{tot}$'

        x_values = sorted(np.unique(x_slice))
        len_x = len(x_values)

        lower_border = [0 for i in range(len_x)]
        upper_border = [1 for i in range(len_x)]

        plt.fill_between(x_values, lower_border, fraction_onshell, facecolor='red', label='on-shell V')
        plt.fill_between(x_values, fraction_onshell, fraction_onshell + fraction_offshell, facecolor='blue',
                         label='off-shell V')
        plt.fill_between(x_values, fraction_onshell + fraction_offshell,
                         fraction_tt_excl + fraction_onshell + fraction_offshell, facecolor='green',
                         label='tt exclusive')

        plt.legend(loc='best')
        plt.title(plotTitle)

        plt.xlabel(x_label)
        plt.ylabel('Fraction to visible $\sigma$')

        if log_scale:
            plt.axis([x_slice.min(), x_slice.max(), 0.01, 1])
            plt.yscale('log')
        else:
            plt.axis([x_slice.min(), x_slice.max(), 0, 1])

        plt.tight_layout()

        make_folder_if_not_exists(output_folder + '/fractions/')
        # plt.savefig(output_folder + '/fractions/' + 'fractions_gDM%s_mV%s.pdf' % (g_DM, mV) )
        plt.savefig(output_folder + '/fractions/' + 'fractions_mV%s.pdf' % (mV))
        plt.close()

    elif mode == 'total':
        # make visible vs invisible plots

        # only consider g_DM = 1
        g_DM = 1
        my_data = my_data[my_data[:, 3] == g_DM]

        # slice in columns
        BR = my_data[:, 0]
        G_tot = my_data[:, 1]
        a_r = my_data[:, 2]

        # cross-sections
        xsection_tt_excl = my_data[:, 9]
        xsection_onshell = my_data[:, 8]
        xsection_offshell = my_data[:, 7]
        xsection_monotop = my_data[:, 6]
        xsection_visible = xsection_tt_excl + xsection_onshell + xsection_offshell
        xsection_total = xsection_visible + xsection_monotop

        # fractions to total
        fraction_visible = xsection_visible / xsection_total
        fraction_invisible = xsection_monotop / xsection_total

        # x_slice = BR
        # x_label = 'BR_$_{DM}$'
        x_slice = G_tot
        x_label = '$\Gamma_{tot}$'

        x_values = sorted(np.unique(x_slice))
        len_x = len(x_values)

        lower_border = [0 for i in range(len_x)]
        upper_border = [1 for i in range(len_x)]

        plt.figure(figsize=(6, 6))
        plotTitle = '$m_V=$' + '{:.1f} TeV'.format(mV / 1000.) + \
                    ' ; $m_{DM}=$' + '{:.0f} GeV'.format(mDM) + \
                    ' ; $g_{DM}=$' + '{:.1f} '.format(g_DM)

        plt.fill_between(x_values, lower_border, fraction_invisible, facecolor='blue', label='Invisible (monotop)')
        plt.fill_between(x_values, fraction_invisible, fraction_visible + fraction_invisible, facecolor='green',
                         label='Visible (di-top)')

        if log_scale:
            plt.axis([x_slice.min(), x_slice.max(), 0.01, 1])
            plt.yscale('log')
        else:
            plt.axis([x_slice.min(), x_slice.max(), 0, 1])

        plt.legend(loc='best')
        plt.title(plotTitle)

        plt.xlabel(x_label)
        plt.ylabel('Fraction to total $\sigma$')

        plt.tight_layout()

        make_folder_if_not_exists(output_folder + '/fractions/')
        plt.savefig(output_folder + '/fractions/' + 'fractions_total_gDM%s_mV%s.pdf' % (g_DM, mV))
        # plt.savefig(output_folder + '/fractions/' + 'fractions_total_mV%s.pdf' % (mV) )

        plt.close()


def make_2D_limit_plot_from_tree(tree, variables='mV:a_r', select_gDM="", select_mV="", mode="BlindExp", process='visible', interpolate=True, show_nwa_area=True):
    global output_folder, log_scale

    my_tree = tree.Clone()

    # plt.figure(figsize=(8,8))
    fig, axes = plt.subplots(figsize=(8, 8))

    selection = "1"
    filename_suffix = ""

    plotTitle = 'Expected and observed limit, $m_{DM}=$' + '{:.0f} GeV'.format(mDM)
    if select_gDM:
        plotTitle += ', $g_{DM}=$' + '{:.1f}'.format(select_gDM)
        selection += " && (g == %.2f)" % (select_gDM)
        filename_suffix += "_%.2fgDM" % (select_gDM)
    if select_mV:
        plotTitle += ', $m_{V}=$' + '{:.0f}'.format(select_mV) + ' GeV'
        selection += " && (mV == %.0f)" % (select_mV)
        filename_suffix += "_%.0fmV" % (select_mV)

    if "BlindExp" in mode:
        plotTitle = plotTitle.replace("and observed ", "")

    if process == 'visible':
        set_labels(plt, axes, additional_text_visible)
    elif process == 'invisible' or process == 'monotop':
        set_labels(plt, axes, additional_text_invisible)
    elif process == 'overlay':
        set_labels(plt, axes, additional_text_overlay)
    else:
        print 'Unknown process %s, choose from visible/invisible/overlay.' % process
        sys.exit(1)

    print 'Making a 2D limit plot for %s process, %s variables, selection %s' % (process, variables, selection)

    x_variable_name, y_variable_name = variables.split(":")

    x_axis_data = []
    y_axis_data = []

    selected_tree = my_tree.CopyTree(selection)
    for event in selected_tree:
        x_axis_data.append(getattr(event, x_variable_name))
        y_axis_data.append(getattr(event, y_variable_name))

    x_axis_data = np.asarray(x_axis_data)
    y_axis_data = np.asarray(y_axis_data)

    x_values = sorted(np.unique(x_axis_data))
    len_x = len(x_values)

    if process == 'overlay':
        if not "BlindExp" in mode:
            # calculate observed limit (normally not interpolated)
            limit_border_vis = get_limits_from_tree(selected_tree, variables, 'visible', limit_type='observed', interpolate=False)
            limit_border_invis = get_limits_from_tree(selected_tree, variables, 'invisible', limit_type='observed', interpolate=interpolate)
        else:
            limit_border_vis = get_limits_from_tree(selected_tree, variables, 'visible', limit_type='expected', interpolate=interpolate)
            limit_border_invis = get_limits_from_tree(selected_tree, variables, 'invisible', limit_type='expected', interpolate=interpolate)
    else:
        limit_border_exp = get_limits_from_tree(selected_tree, variables, process, limit_type='expected', interpolate=interpolate)

        if not "BlindExp" in mode:
            # calculate observed limit (never interpolated)
            limit_border_obs = get_limits_from_tree(selected_tree, variables, process, limit_type='observed', interpolate=False)

        if process == 'visible':
            limit_border_upper_1sigma = get_limits_from_tree(selected_tree, variables, process, limit_type='upper_1sigma', interpolate=interpolate)
            limit_border_lower_1sigma = get_limits_from_tree(selected_tree, variables, process, limit_type='lower_1sigma', interpolate=interpolate)
            limit_border_upper_2sigma = get_limits_from_tree(selected_tree, variables, process, limit_type='upper_2sigma', interpolate=interpolate)
            limit_border_lower_2sigma = get_limits_from_tree(selected_tree, variables, process, limit_type='lower_2sigma', interpolate=interpolate)

    # establish lower and upper borders for plotting
    lower_border = [y_axis_data.min() for i in range(len_x)]
    upper_border = [y_axis_data.max() for i in range(len_x)]

    # plot actual limits
    if process == 'overlay':
        if not "BlindExp" in mode:
            plt.plot(x_values, limit_border_vis, '-', color="red", label='Observed limit (vis.)')
            # correct once observed invisible limit is available!
            plt.plot(x_values, limit_border_invis, '--', color="blue", label='Expected limit (invis.)')
            
            plt.fill_between(x_values, limit_border_vis, upper_border, facecolor='red', alpha = 0.5, edgecolor="red",
                                 label='Excluded area (vis.)')
            plt.fill_between(x_values, limit_border_invis, upper_border, facecolor='blue', alpha = 0.5, edgecolor="blue",
                                 label='Excluded area (invis.)')
        else:
            plt.plot(x_values, limit_border_vis, '-', color="red", label='Expected limit (vis.)')
            plt.plot(x_values, limit_border_invis, '--', color="blue", label='Expected limit (invis.)')
            
            plt.fill_between(x_values, limit_border_vis, upper_border, facecolor='red', alpha = 0.5, edgecolor="red",
                                 label='Excluded area (vis.)')
            plt.fill_between(x_values, limit_border_invis, upper_border, facecolor='blue', alpha = 0.5, edgecolor="blue",
                                 label='Excluded area (invis.)')
    else:
        plt.plot(x_values, limit_border_exp, '--', color="black", label='Expected limit')
        # plot +/- sigma variations for visible process
        if process == 'visible':
            plt.fill_between(x_values, limit_border_lower_2sigma, limit_border_upper_2sigma, facecolor='yellow',
                         label='$\pm2\sigma$')
            plt.fill_between(x_values, limit_border_lower_1sigma, limit_border_upper_1sigma, facecolor='lime',
                         label='$\pm1\sigma$')

        if not "BlindExp" in mode:
            plt.fill_between(x_values, limit_border_obs, upper_border, facecolor='none', hatch = '//', edgecolor="red",
                             label='Excluded area')
            plt.plot(x_values, limit_border_obs, color="black", label='Observed limit', marker='.', ms=15)

    if show_nwa_area:
        nwa_area_border = get_narrow_width_approx_area(selected_tree, variables, nwa_limit=0.1, interpolate=interpolate)
        # check is the area is visible in the plot
        if min(nwa_area_border) < max(upper_border):
            # plt.plot(x_values, nwa_area_border, '-', color="black", label = 'Narrow width approx.')
            plt.fill_between(x_values, nwa_area_border, upper_border, facecolor='darkgray', zorder = 3,
                        label='$\\Gamma_\\textrm{tot}/m_V>0.1$')

    plt.xlim(min(x_values), max(x_values))
    plt.ylim(min(y_axis_data), max(y_axis_data))

    if ':G_tot' in variables and select_mV:
        plt.ylim(min(y_axis_data), 0.11*float(select_mV))

    if 'BR:a_r' in variables:
        plt.ylim(0, max(y_axis_data))

    if ':a_r' in variables:
        ml = MultipleLocator(0.01)
        axes.yaxis.set_minor_locator(ml)

    if 'g:' in variables or 'BR:' in variables:
        ml = MultipleLocator(0.1)
        axes.xaxis.set_minor_locator(ml)        


    plt.title(plotTitle)
    plt.xlabel(latex_labels[x_variable_name])
    plt.ylabel(latex_labels[y_variable_name])

    plt.legend(loc='lower right')

    if 'BR:' in variables or 'g:a_r' in variables:
        plt.legend(loc=[0.43, 0.45])

    # if log_scale:
    #     plt.colorbar( ticks = LogLocator(subs=range(10)) )
    # else:
    #     plt.colorbar()

    plt.tight_layout()
    make_folder_if_not_exists(output_folder + '/mu_values/')

    if mode != "":
        mode = "_" + mode
    plt.savefig(output_folder + '/mu_values/' + '/mu_%s_%s%s%s.pdf' % (process, variables.replace(":","_"), filename_suffix, mode))
    plt.close()


def make_limit_plot_with_tree_draw_BR_a_r(tree, mV=1000, mode="BlindExp", process='visible'):
    global output_folder, log_scale

    my_tree = tree.Clone()

    # plt.figure(figsize=(8,8))
    fig, axes = plt.subplots(figsize=(8, 8))
    plotTitle = 'Expected and observed limit, $m_{DM}=$' + '{:.0f} GeV'.format(
        mDM) + ', $m_{V}=$' + '{:.0f} GeV'.format(mV)
    if "BlindExp" in mode:
        plotTitle = plotTitle.replace("and observed ", "")

    if process == 'visible':
        set_labels(plt, axes, additional_text_visible)
        selection = "(limit_vis_exp < 1) && (mV==%s)" % mV
    else:
        set_labels(plt, axes, additional_text_invisible)
        selection = "(limit_invis_exp < 1) && (mV==%s)" % mV

    print 'Making a BR/g_SM 2D limit plot for %s process, mV = %.0f GeV' % (process, mV)

    histogram = Hist2D(10, 0.01, 0.99, 15, 0, 0.15)
    my_tree.Draw("BR:a_r", selection, hist=histogram)

    im = rplt.imshow(histogram, axes=axes, cmap=my_cmap, vmin=0.1)

    plt.title(plotTitle)
    plt.xlabel('BR$_{DM}$')
    plt.ylabel('$g_{SM}$')

    plt.legend(loc='lower right')

    plt.xlim(min(list(histogram.x())), max(list(histogram.x())))
    plt.ylim(min(list(histogram.y())), max(list(histogram.y())))

    plt.tight_layout()
    make_folder_if_not_exists(output_folder + '/mu_values/')

    if mode != "":
        mode = "_" + mode
    plt.savefig(output_folder + '/mu_values/' + '/tree_draw_%s_BR_vs_a_r_%.0f_mV%s.pdf' % (process, mV, mode))
    plt.close()


def make_2D_plots(mV, my_data, process, with_limits=False, show_only_mu=False, show_alpha_beta_gamma=False):
    global output_folder

    if not ('visible' in process or 'monotop' in process) and with_limits:
        print 'Can not show limit plots for ', process
        sys.exit(1)

    # slice in columns
    BR = my_data[:, 0]
    G_tot = my_data[:, 1]
    a_r = my_data[:, 2]
    g = my_data[:, 3]
    if 'tt_excl' in process:
        xsection = my_data[:, 9]
        MC_cross_section = cross_sections_tt_excl[str(mV)]
    elif 'onshell' in process:
        xsection = my_data[:, 8]
        MC_cross_section = cross_sections_onshellV[str(mV)]
    elif 'offshell' in process:
        xsection = my_data[:, 7]
        MC_cross_section = cross_sections_offshellV[str(mV)]
    elif 'monotop' in process:
        xsection = my_data[:, 6]
    elif 'visible' in process:
        xsection = my_data[:, 9] + my_data[:, 8] + my_data[:, 7]
        if with_limits:
            limits = np.asarray([get_limit_value(mV, a_r_value, g_value) for a_r_value, g_value in zip(a_r, g)])
            xsection = xsection * limits

    # alpha beta gamma weights
    if show_alpha_beta_gamma:
        weights = xsection / MC_cross_section

    if show_alpha_beta_gamma and (show_only_mu or with_limits):
        print 'Incompatible options with and show_alpha_beta_gamma'
        sys.exit(1)

    plt.figure(figsize=(14, 6))
    plotTitle = '$m_V=$' + '{:.1f} TeV'.format(mV / 1000.) + \
                ' ; $m_{DM}=$' + '{:.0f} GeV'.format(mDM)

    plt.subplot(121)

    x = a_r
    y = g
    if show_only_mu:
        limits = np.asarray([get_limit_value(mV, a_r_value, g_value) for a_r_value, g_value in zip(a_r, g)])
        z = limits
    elif show_alpha_beta_gamma:
        z = weights
    else:
        z = xsection

    if log_scale:
        # if show_only_mu or with_limits:
        #     plt.scatter(x, y, c=z, marker = 's', s=100, edgecolors='none', norm=LogNorm())
        # else:
        plt.scatter(x, y, c=z, norm=LogNorm())
    else:
        # if show_only_mu:
        #     plt.scatter(x, y, c=z, marker = 's', s=100, edgecolors='none')
        # else:
        plt.scatter(x, y, c=z)

    if show_only_mu:
        # xi, yi = np.linspace(x.min(), x.max(), 10), np.linspace(y.min(), y.max(), 10)
        zi = np.asarray([[get_limit_value(mV, a_r_value, g_value) for a_r_value in a_r] for g_value in g])
        zi = np.ma.masked_where(zi > 1, zi)
        interpolation = 'nearest'
    else:
        # Interpolate
        # Set up a regular grid of interpolation points
        xi, yi = np.linspace(x.min(), x.max(), 100), np.linspace(y.min(), y.max(), 100)
        xi, yi = np.meshgrid(xi, yi)
        rbf = scipy.interpolate.Rbf(x, y, z, function='linear')
        zi = rbf(xi, yi)
        interpolation = 'none'

    if log_scale:
        plt.imshow(zi, vmin=z.min(), vmax=z.max(), origin='lower', aspect='auto',
                   extent=[x.min(), x.max(), y.min(), y.max()], norm=LogNorm(), interpolation=interpolation)
    else:
        plt.imshow(zi, vmin=z.min(), vmax=z.max(), origin='lower', aspect='auto',
                   extent=[x.min(), x.max(), y.min(), y.max()], interpolation=interpolation)

    if not show_only_mu:
        plt.title('$\sigma_\mathrm{%s}$ [pb] ; %s' % (process.replace('_', '-'), plotTitle))
    elif show_alpha_beta_gamma:
        if 'tt_excl' in process:
            plt.title('$\alpha$ ; %s' % (plotTitle))
        elif 'onshell' in process:
            plt.title('$\beta$ ; %s' % (plotTitle))
        elif 'offshell' in process:
            plt.title('$\gamma$ ; %s' % (plotTitle))
        else:
            print 'Unsupported process for alpha beta gamma:', process
            sys.exit(1)
    else:
        plt.title('$\mu$ ; %s' % (plotTitle))

    plt.xlabel('$g_{SM}$')
    plt.ylabel('$g_{DM}$')
    if log_scale:
        plt.colorbar(ticks=LogLocator(subs=range(10)))
    else:
        plt.colorbar()

    # if show_only_mu:
    #     # Interpolate
    #     xi, yi = np.linspace(x.min(), x.max(), 100), np.linspace(y.min(), y.max(), 100)
    #     rbf = scipy.interpolate.Rbf(x, y, z, function='gaussian')
    #     xi, yi = np.meshgrid(xi, yi)
    #     zi = rbf(xi, yi)
    #     unity_line = plt.contour(x, y, zi, (1,), colors='r', linewidths=2)

    plt.subplot(122)

    x = G_tot
    y = BR

    # Set up a regular grid of interpolation points
    xi, yi = np.linspace(x.min(), x.max(), 100), np.linspace(y.min(), y.max(), 100)
    xi, yi = np.meshgrid(xi, yi)

    # # Interpolate
    # if not show_only_mu:
    #     rbf = scipy.interpolate.Rbf(x, y, z, function='cubic')
    #     zi = rbf(xi, yi)
    #     if log_scale:
    #         plt.imshow(zi, vmin=z.min(), vmax=z.max(), origin='lower', aspect='auto',
    #            extent=[x.min(), x.max(), y.min(), y.max()], norm=LogNorm())
    #     else:
    #         plt.imshow(zi, vmin=z.min(), vmax=z.max(), origin='lower', aspect='auto',
    #            extent=[x.min(), x.max(), y.min(), y.max()])

    if log_scale:
        # if show_only_mu or with_limits:
        #     plt.scatter(x, y, c=z, marker = 'o', s=50, edgecolors='none', norm=LogNorm())
        # else:
        plt.scatter(x, y, c=z, norm=LogNorm())
    else:
        # if show_only_mu:
        #     plt.scatter(x, y, c=z, marker = 'o', s=50, edgecolors='none')
        # else:
        plt.scatter(x, y, c=z)

    plt.xlim(x.min(), x.max())
    plt.ylim(y.min(), y.max())

    if not show_only_mu:
        plt.title('$\sigma_\mathrm{%s}$ [pb] ; %s' % (process.replace('_', '-'), plotTitle))
    elif show_alpha_beta_gamma:
        if 'tt_excl' in process:
            plt.title('$\alpha$ ; %s' % (plotTitle))
        elif 'onshell' in process:
            plt.title('$\beta$ ; %s' % (plotTitle))
        elif 'offshell' in process:
            plt.title('$\gamma$ ; %s' % (plotTitle))
        else:
            print 'Unsupported process for alpha beta gamma:', process
            sys.exit(1)
    else:
        plt.title('$\mu$ ; %s' % (plotTitle))

    plt.xlabel('$\Gamma_\mathrm{tot}$')
    plt.ylabel('BR$_{DM}$')
    if log_scale:
        plt.colorbar(ticks=LogLocator(subs=range(10)))
    else:
        plt.colorbar()

    plt.tight_layout()
    if show_only_mu:
        make_folder_if_not_exists(output_folder + '/mu_values/')
        plt.savefig(output_folder + '/mu_values/' + '/mu_%s_mV%s.pdf' % (process, mV))
    elif with_limits:
        make_folder_if_not_exists(output_folder + '/with_limits/')
        plt.savefig(output_folder + '/with_limits/' + '/sigma_excl_%s_mV%s.pdf' % (process, mV))
    elif show_alpha_beta_gamma:
        if 'tt_excl' in process:
            plt.savefig(output_folder + '/alpha_mV%s.pdf' % mV)
        elif 'onshell' in process:
            plt.savefig(output_folder + '/beta_mV%s.pdf' % mV)
        elif 'offshell' in process:
            plt.savefig(output_folder + '/gamma_mV%s.pdf' % mV)
    else:
        plt.savefig(output_folder + '/sigma_%s_mV%s.pdf' % (process, mV))
    plt.close()


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-o", "--output_folder", dest="output_folder", default='plots/',
                      help="set path to save plots")
    parser.add_option("-i", "--input_folder", dest="input_folder",
                      default='/eos/atlas/atlascerngroupdisk/phys-exotics/hqt/SSbjets/Limit/sstops_limits_outputs/',
                      help="set path to limits")
    parser.add_option("-l", "--log_scale", action="store_true", dest="log_scale",
                      help="Plot histograms in log scale")
    parser.add_option("-f", "--fraction_plots", action="store_true", dest="fraction_plots",
                      help="Make fraction plots (ratios to total/visible cross section)")
    parser.add_option("-a", "--additional_plots", action="store_true", dest="more_plots",
                      help="Make additional plots")
    parser.add_option("-m", "--mode", dest="mode", default='',
                      help="set mode (e.g. BlindExp), empty by default (i.e. unblinded)")
    parser.add_option("-p", "--parameterisation", dest="parameterisation", default = 'nominal',
                      help="Choose paramaterisation of interest (nominal, nominal_fine, BR_scan_a_r_0.15, zoomed_in_scan_a_r_0.15_g_3.0)")

    (options, args) = parser.parse_args()

    output_folder = options.output_folder

    make_folder_if_not_exists(output_folder)

    input_folder = options.input_folder
    mode = options.mode
    parameterisation = options.parameterisation

    # possible parameterisations:
    # nominal: a_r from 0.01 to 0.34, g = [0.1, 0.5, 1.0, 1.5]
    # nominal_fine: a_r from 0.05 to 0.345 with a step of 0.005, g = [0.1, 0.5, 1.0]
    # large_scan_a_r_g_3.0: inital scan for both a_r and g from 0 up to 3.0 with a step of 0.2
    # zoomed_in_scan_a_r_0.15_g_3.0: similar scan but zoomed range of a_r from 0.01 to 0.15
    # BR_scan_a_r_0.15: a_r varies from 0.01 ro 0.15, BR from 0 to 1

    if 'BR_scan' in parameterisation:
        BR_run = True
    else:
        BR_run = False

    # temporary fix for the lack of observed limits in non-nominal scans:
    if not 'nominal' in parameterisation:
        mode = 'BlindExp'

    input_folder += '/' + parameterisation
    output_folder += '/' + parameterisation

    # file path to the parameters table, based on the parameterisation name
    parameter_table = 'parameter_tables/table_' + parameterisation + '.csv'

    # temporary fix for the lack of visible limit files for a_r>0.15 (automatically excluded)
    parameter_table = parameter_table.replace('a_r_0.15', 'a_r_0.3')

    # data-driven by default, switch to 'FullMC' if needed
    bkg_type = 'DD'

    input_folder += '/' + bkg_type
    output_folder += '/' + bkg_type

    if mode != '':
        input_folder += '_' + mode
        output_folder += '_' + mode

    log_scale = options.log_scale
    if log_scale:
        output_folder += '/log/'

    whole_data = np.genfromtxt(parameter_table, delimiter=',')
    # delete first row (variable names)
    whole_data = np.delete(whole_data, (0), axis=0)

    temp_root_file = ROOT.TFile("tree.root", "recreate")
    tree = ROOT.TTree("ntuple", "data from csv table")
    nlines = tree.ReadFile(parameter_table,'BR/D:G_tot/D:a_r/D:g/D:mDM/D:mV/D:xsection_monotop/D:xsection_offshellV/D:xsection_onshellV/D:xsection_tt_exclusive/D',',')
    print "found %s points" % (nlines)
    tree = load_limits_to_tree(tree, mode, BR_run=BR_run)
    temp_root_file.Write()
    temp_root_file.Close()

    rootpy_file = root_open("tree.root")
    rootpy_tree = rootpy_file.ntuple

    if 'nominal' in parameterisation:
        # make a g_SM vs mV limit plot
        g_DMs = [0.1, 0.5, 1.0, 1.5]
        if 'fine' in parameterisation:
            # don't have 1.5 in 'fine' parameterisation yet
            g_DMs = [0.1, 0.5, 1.0]

        for g_DM in g_DMs:
            make_2D_limit_plot_from_tree(rootpy_tree, variables='mV:a_r', select_gDM=g_DM, mode=mode, process='visible')
            make_2D_limit_plot_from_tree(rootpy_tree, variables='mV:a_r', select_gDM=g_DM, mode=mode, process='overlay')
    elif BR_run:
        make_2D_limit_plot_from_tree(rootpy_tree, variables='BR:a_r', select_mV=1000, mode="BlindExp", process='overlay', interpolate=True, show_nwa_area=True)
        make_2D_limit_plot_from_tree(rootpy_tree, variables='BR:G_tot', select_mV=1000, mode="BlindExp", process='overlay', interpolate=True, show_nwa_area=True)
    else:
        make_2D_limit_plot_from_tree(rootpy_tree, variables='g:a_r', select_mV=1000, mode="BlindExp", process='overlay', interpolate=True, show_nwa_area=True)        
        make_2D_limit_plot_from_tree(rootpy_tree, variables='g:G_tot', select_mV=1000, mode="BlindExp", process='overlay', interpolate=True, show_nwa_area=True)

    # work with a single mV:
    if options.more_plots:
        for mV in mediator_masses:
            single_mV_data = whole_data[whole_data[:, 5] == mV]
            for process in processes:
                make_all_plots(mV, single_mV_data, process)

    if options.fraction_plots:
        for mV in mediator_masses:
            single_mV_data = whole_data[whole_data[:, 5] == mV]
            make_fraction_plots(mV, single_mV_data, mode='visible')
            make_fraction_plots(mV, single_mV_data, mode='total')

    rootpy_file.close()
