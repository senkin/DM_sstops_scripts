import numpy             as np
import matplotlib        as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import LogLocator, MultipleLocator
from matplotlib.colors import LogNorm
import scipy.interpolate
import ROOT
from optparse import OptionParser
from calculate_MG_xsection import make_folder_if_not_exists
from cross_sections_DM import *


processes = ['tt_excl','onshell','offshell', 'monotop','visible']
# processes = ['visible']
additional_text = 'DM model, combined SS tops'

# Nominal model parameters
mediator_masses = [1000, 1500, 2000, 2500, 3000]
mDM = 1.
lumi = 36.1

# Ignore warning related to undefined division
np.seterr(divide='ignore', invalid='ignore') 

# Plot settings
#mpl.rcParams['legend.frameon' ] = False
mpl.rcParams['legend.fontsize'] = 'xx-large'
mpl.rcParams['xtick.labelsize'] = 16
mpl.rcParams['ytick.labelsize'] = 16
mpl.rcParams['axes.titlesize' ] = 18
mpl.rcParams['axes.labelsize' ] = 18
mpl.rcParams['lines.linewidth'] = 2.5
plt.rc('text', usetex=True)
plt.rc('font', family='sans-serif')

def set_labels(plt, axes):
    # ATLAS text
    # note: fontweight/weight does not change anything as we use Latex text!!!
    logo_location = (0.05, 0.97)
    prelim_location = (0.2, 0.97)
    additional_location = (0.05, 0.90)
    lumi_location = (0.55, 0.97)
        
    plt.text(logo_location[0], logo_location[1], r"$\emph{\textbf{ATLAS}}$", 
             fontsize=20, transform=axes.transAxes, 
             verticalalignment='top',horizontalalignment='left')
    plt.text(prelim_location[0], prelim_location[1], "Internal", 
            fontsize=20, transform=axes.transAxes, 
            verticalalignment='top', horizontalalignment='left')

    plt.text(lumi_location[0], lumi_location[1], r"$\sqrt{s} =$ 13 TeV, %.1f fb$^{-1}$" % (lumi),
           fontsize=20, transform=axes.transAxes, 
           verticalalignment='top', horizontalalignment='left')

    # channel text
    axes.text(additional_location[0], additional_location[1], 
              r"%s" % additional_text, transform=axes.transAxes,
              fontsize=18, verticalalignment='top',
              horizontalalignment='left')


def get_limit_value(mV, a_r, g, type=1):
    global input_folder_with_limits, mode, bkg_type
    signal_name = 'sstops_mV{0:.0f}'.format(mV) + '_a_r{0:.2f}'.format(a_r) + '_g{0:.2f}'.format(g)

    input_root_file = ROOT.TFile(input_folder + '/' + signal_name + '/' + mode + '/' + bkg_type + 'bkg.root', "read")
    histogram = input_root_file.Get("limit")

    value = histogram.GetBinContent(type)
    input_root_file.Close()

    if value>1e3:
        print 'Warning: limit value for mV = %s, a_r = %s, g = %s: %s' % (mV, a_r, g, value)
        value = 500
        # raw_input("Press Enter to continue...")
    
    return value

def get_limit_border(masses, x, y, z):
    limit_values = {}

    for i,j,k in zip(x,y,z):
        if k<=1:
            try:
                limit_values[i].append(j)
            except:
                limit_values[i] = [j]

    limit_border = []
    for mass in sorted(limit_values.keys()):
        limit_border.append(np.asarray(limit_values[mass]).min())
    return limit_border

def make_all_plots(mV, my_data, process):
    make_limitless_plots(mV, my_data, process)
    if 'visible' in process:
        make_limit_plots(mV, my_data)
    elif not 'monotop' in process:
        make_2D_plots(mV, my_data, process, show_alpha_beta_gamma = True)


def make_limitless_plots(mV, my_data, process):
    make_1D_plots(mV, my_data, process)
    make_2D_plots(mV, my_data, process)

def make_limit_plots(mV, my_data, process = 'visible'):
    make_1D_plots(mV, my_data, process = 'visible', with_limits = True)
    make_1D_plots(mV, my_data, process = 'visible', show_only_mu = True)
    make_2D_plots(mV, my_data, process = 'visible', with_limits = True)
    make_2D_plots(mV, my_data, process = 'visible', show_only_mu = True)


def make_fraction_plots(mV, my_data, mode='visible'):
    global output_folder, log_scale
    
    # sort by G_tot
    my_data = my_data[my_data[:,1].argsort()]

    if mode=='visible':
        # slice in columns
        BR = my_data[:,0]
        G_tot = my_data[:,1]
        a_r = my_data[:,2]

        # cross-sections
        xsection_tt_excl  = my_data[:,9]
        xsection_onshell  = my_data[:,8]
        xsection_offshell = my_data[:,7]
        xsection_monotop  = my_data[:,6]
        xsection_visible  = xsection_tt_excl + xsection_onshell + xsection_offshell
        xsection_total    = xsection_visible + xsection_monotop

        # fractions to visible
        fraction_tt_excl  = xsection_tt_excl/xsection_visible
        fraction_onshell  = xsection_onshell/xsection_visible
        fraction_offshell = xsection_offshell/xsection_visible

        plt.figure(figsize=(8,8))
        plotTitle='$m_V=$'+'{:.1f} TeV'.format(mV/1000.) + \
                  ' ; $m_{DM}=$' + '{:.0f} GeV'.format(mDM) #+ \
                  # ' ; $g_{DM}=$' + '{:.1f} '.format(g_DM)

        # x_slice = a_r
        # x_label = '$g_{SM}$'
        x_slice = G_tot
        x_label = '$\Gamma_{tot}$'

        x_values = sorted(np.unique(x_slice))
        len_x = len(x_values)

        lower_border = [0 for i in range(len_x)]
        upper_border = [1 for i in range(len_x)]

        plt.fill_between(x_values, lower_border, fraction_onshell, facecolor='red', label = 'on-shell V')
        plt.fill_between(x_values, fraction_onshell,fraction_onshell+fraction_offshell, facecolor='blue', label = 'off-shell V')
        plt.fill_between(x_values, fraction_onshell+fraction_offshell, fraction_tt_excl+fraction_onshell+fraction_offshell, facecolor='green', label = 'tt exclusive')

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
        plt.savefig(output_folder + '/fractions/' + 'fractions_mV%s.pdf' % (mV) )
        plt.close()

    elif mode=='total':
        # make visible vs invisible plots

        # only consider g_DM = 1
        g_DM = 1
        my_data = my_data[my_data[:,3]==g_DM]

        # slice in columns
        BR = my_data[:,0]
        G_tot = my_data[:,1]
        a_r = my_data[:,2]

        # cross-sections
        xsection_tt_excl  = my_data[:,9]
        xsection_onshell  = my_data[:,8]
        xsection_offshell = my_data[:,7]
        xsection_monotop  = my_data[:,6]
        xsection_visible  = xsection_tt_excl + xsection_onshell + xsection_offshell
        xsection_total    = xsection_visible + xsection_monotop

        # fractions to total
        fraction_visible   = xsection_visible/xsection_total
        fraction_invisible = xsection_monotop/xsection_total

        # x_slice = BR
        # x_label = 'BR_$_{DM}$'
        x_slice = G_tot
        x_label = '$\Gamma_{tot}$'

        x_values = sorted(np.unique(x_slice))
        len_x = len(x_values)

        lower_border = [0 for i in range(len_x)]
        upper_border = [1 for i in range(len_x)]

        plt.figure(figsize=(8,8))
        plotTitle='$m_V=$'+'{:.1f} TeV'.format(mV/1000.) + \
                  ' ; $m_{DM}=$' + '{:.0f} GeV'.format(mDM) + \
                  ' ; $g_{DM}=$' + '{:.1f} '.format(g_DM)

        plt.fill_between(x_values, lower_border, fraction_invisible, facecolor='blue', label = 'Invisible (monotop)')
        plt.fill_between(x_values, fraction_invisible,fraction_visible+fraction_invisible, facecolor='green', label = 'Visible (di-top)')

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
        plt.savefig(output_folder + '/fractions/' + 'fractions_total_gDM%s_mV%s.pdf' % (g_DM, mV) )
        # plt.savefig(output_folder + '/fractions/' + 'fractions_total_mV%s.pdf' % (mV) )

        plt.close()


def make_limit_plot_vs_mV(my_data, g_DM, mode = "BlindExp"):
    global output_folder, log_scale
    
    # plt.figure(figsize=(8,8))
    fig, axes = plt.subplots(figsize=(8,8))
    plotTitle= 'Expected and observed limit, $m_{DM}=$' + '{:.0f} GeV'.format(mDM) + ', $g_{DM}=$' + '{:.1f}'.format(g_DM)
    if "BlindExp" in mode:
        plotTitle = plotTitle.replace("and observed ", "")

    # this is not working for some reason, need to investigate
    set_labels(plt, axes)

    print 'Making a limit plot with g_DM = ', g_DM

    my_data = my_data[my_data[:,3]==g_DM]

    # slice in columns
    a_r_slice = my_data[:,2]
    mV_slice = my_data[:,5]

    limits_exp = np.asarray([get_limit_value(mV, a_r_value, g_DM, 2) for mV, a_r_value in zip(mV_slice, a_r_slice)])
    limits_upper_2sigma = np.asarray([get_limit_value(mV, a_r_value, g_DM, 3) for mV, a_r_value in zip(mV_slice, a_r_slice)])
    limits_upper_1sigma = np.asarray([get_limit_value(mV, a_r_value, g_DM, 4) for mV, a_r_value in zip(mV_slice, a_r_slice)])
    limits_lower_1sigma = np.asarray([get_limit_value(mV, a_r_value, g_DM, 5) for mV, a_r_value in zip(mV_slice, a_r_slice)])
    limits_lower_2sigma = np.asarray([get_limit_value(mV, a_r_value, g_DM, 6) for mV, a_r_value in zip(mV_slice, a_r_slice)])
    if not "BlindExp" in mode:
        limits_obs = np.asarray([get_limit_value(mV, a_r_value, g_DM, 1) for mV, a_r_value in zip(mV_slice, a_r_slice)])
    else:
        limits_obs = limits_exp

    # x = mV_slice
    # y = a_r_slice
    # z = limits

    # if log_scale:
    #     plt.scatter(x, y, c=z, norm=LogNorm())
    # else:
    #     plt.scatter(x, y, c=z)

    masses = sorted(np.unique(mV_slice))
    len_x = len(masses)

    limit_border_exp = get_limit_border(masses, mV_slice, a_r_slice, limits_exp)
    limit_border_upper_1sigma = get_limit_border(masses, mV_slice, a_r_slice, limits_upper_1sigma)
    limit_border_lower_1sigma = get_limit_border(masses, mV_slice, a_r_slice, limits_lower_1sigma)
    limit_border_upper_2sigma = get_limit_border(masses, mV_slice, a_r_slice, limits_upper_2sigma)
    limit_border_lower_2sigma = get_limit_border(masses, mV_slice, a_r_slice, limits_lower_2sigma)
    limit_border_obs = get_limit_border(masses, mV_slice, a_r_slice, limits_obs)
    
    lower_border = [a_r_slice.min() for i in range(len_x)]
    upper_border = [a_r_slice.max() for i in range(len_x)]

    plt.fill_between(masses, limit_border_lower_2sigma, limit_border_upper_2sigma, facecolor='yellow', label = '$\pm2\sigma$')
    plt.fill_between(masses, limit_border_lower_1sigma, limit_border_upper_1sigma, facecolor='lime', label = '$\pm1\sigma$')
    plt.plot(masses, limit_border_exp, '--', color="black", label = 'Expected limit')
    if not "BlindExp" in mode:
        plt.fill_between(masses, limit_border_obs, upper_border, facecolor='none', hatch = '//', edgecolor="red", label = 'Excluded area')
        plt.plot(masses, limit_border_obs, color="black", label = 'Observed limit')



    plt.xlim(min(masses), max(masses))
    plt.ylim(min(a_r_slice), max(a_r_slice))

    ml = MultipleLocator(0.01)
    axes.yaxis.set_minor_locator(ml)

    plt.title(plotTitle)
    plt.xlabel('$m_{V}$ [GeV]')
    plt.ylabel('$g_{SM}$') 

    plt.legend(loc='lower right')

    
    # if log_scale:
    #     plt.colorbar( ticks = LogLocator(subs=range(10)) )
    # else:
    #     plt.colorbar()

    plt.tight_layout()
    make_folder_if_not_exists(output_folder + '/mu_values/')
    
    if mode!="":
        mode = "_" + mode
    plt.savefig(output_folder + '/mu_values/' + '/mu_visible_vs_mV_%.2f_gDM%s.pdf' % (g_DM, mode) )    
    plt.close()


def make_1D_plots(mV, my_data, process, with_limits = False, show_only_mu = False):
    global output_folder, log_scale
    if not 'visible' in process and with_limits:
        print 'Can not show limit plots for ', process
        sys.exit(1)

    plt.figure(figsize=(8,8))
    plotTitle='$m_V=$'+'{:.1f} TeV'.format(mV/1000.) + \
              ' ; $m_{DM}=$' + '{:.0f} GeV'.format(mDM)
    
    first_a_r_data = my_data[my_data[:,2]==my_data[:,2][0]]
    g_DMs = first_a_r_data[:,3]

    # select first, middle and last g_DMs
    g_DMs = [g_DMs[0], g_DMs[(len(g_DMs) - 1)/2], g_DMs[-1]]
    # g_DMs = [0.5]

    for g_DM in g_DMs:
        # pick a given g_DM slice
        my_data_g_DM = my_data[my_data[:,3]==g_DM]

        # slice in columns
        BR = my_data_g_DM[:,0]
        G_tot = my_data_g_DM[:,1]
        a_r = my_data_g_DM[:,2]
        # print 'Process: ', process, 'with_limits: ', with_limits, 'mV = ', mV, 'show_only_mu: ', show_only_mu
        # print 'a_r =', a_r

        if 'tt_excl' in process:
            xsection = my_data_g_DM[:,9]
        elif 'onshell' in process:
            xsection = my_data_g_DM[:,8]
        elif 'offshell' in process:
            xsection = my_data_g_DM[:,7]
        elif 'Monotop' in process or 'monotop' in process:
            xsection = my_data_g_DM[:,6]
        elif 'visible' in process:
            xsection = my_data_g_DM[:,9] + my_data_g_DM[:,8] + my_data_g_DM[:,7]
            if with_limits:
                limits = np.asarray([get_limit_value(mV, a_r_value, g_DM) for a_r_value in a_r])
                xsection = xsection*limits

        x = a_r
        if show_only_mu:
            limits = np.asarray([get_limit_value(mV, a_r_value, g_DM) for a_r_value in a_r])
            limits_upper = np.asarray([get_limit_value(mV, a_r_value, g_DM, 4) for a_r_value in a_r])
            limits_lower = np.asarray([get_limit_value(mV, a_r_value, g_DM, 5) for a_r_value in a_r])
            y = limits
        else:
            y = xsection

        xi = np.linspace(x.min(), x.max(), 100)

        # Interpolate
        # if not show_only_mu:
        f = scipy.interpolate.interp1d(x, y, kind='linear')
        plt.plot( xi, f(xi), '-', label='$g_{DM}=%.1f$' % g_DM )

        plt.scatter(x, y)
        if show_only_mu:
            plt.fill_between(x, limits_lower, limits_upper, facecolor='yellow', alpha=0.5, label = '$\pm1\sigma$')

        plt.axis([x.min(), x.max(), y.min(), y.max()])

    plt.legend(loc='best')
    plt.title(plotTitle)

    plt.xlabel('$g_{SM}$')
    plt.ylabel('$\sigma_\mathrm{%s}$ [pb]' % process.replace('_','-'))

    if log_scale:
        plt.yscale('log')

    if not show_only_mu:
        plt.ylabel('$\sigma_\mathrm{%s}$ [pb]' % process.replace('_','-'))
    else:
        plt.ylabel('$\mu$')

    plt.tight_layout()
    if show_only_mu:
        make_folder_if_not_exists(output_folder + '/mu_values/')
        plt.savefig(output_folder + '/mu_values/' + '/mu_1D_%s_mV%s.pdf' % (process, mV) )    
    elif with_limits: 
        make_folder_if_not_exists(output_folder + '/with_limits/')
        plt.savefig(output_folder + '/with_limits/' + '/sigma_excl_1D_%s_mV%s.pdf' % (process, mV) )    
    else:
        plt.savefig(output_folder + '/sigma_1D_%s_mV%s.pdf' % (process, mV) )
    plt.close()


def make_2D_plots(mV, my_data, process, with_limits = False, show_only_mu = False, show_alpha_beta_gamma = False):
    global output_folder
    
    if not 'visible' in process and with_limits:
        print 'Can not show limit plots for ', process
        sys.exit(1)

    # slice in columns
    BR = my_data[:,0]
    G_tot = my_data[:,1]
    a_r = my_data[:,2]
    g = my_data[:,3]
    if 'tt_excl' in process:
        xsection = my_data[:,9]
        MC_cross_section = cross_sections_tt_excl[str(mV)]
    elif 'onshell' in process:
        xsection = my_data[:,8]
        MC_cross_section = cross_sections_onshellV[str(mV)]
    elif 'offshell' in process:
        xsection = my_data[:,7]
        MC_cross_section = cross_sections_offshellV[str(mV)]
    elif 'Monotop' in process or 'monotop' in process:
        xsection = my_data[:,6]
    elif 'visible' in process:
        xsection = my_data[:,9] + my_data[:,8] + my_data[:,7]
        if with_limits:
            limits = np.asarray([get_limit_value(mV, a_r_value, g_value) for a_r_value, g_value in zip(a_r, g)])
            xsection = xsection*limits

    # alpha beta gamma weights
    if show_alpha_beta_gamma:
        weights = xsection/MC_cross_section

    if show_alpha_beta_gamma and (show_only_mu or with_limits):
        print 'Incompatible options with and show_alpha_beta_gamma'
        sys.exit(1)

    plt.figure(figsize=(14,6))
    plotTitle='$m_V=$'+'{:.1f} TeV'.format(mV/1000.) + \
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
        #xi, yi = np.linspace(x.min(), x.max(), 10), np.linspace(y.min(), y.max(), 10)
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
           extent=[x.min(), x.max(), y.min(), y.max()], norm=LogNorm(), interpolation = interpolation)
    else:
        plt.imshow(zi, vmin=z.min(), vmax=z.max(), origin='lower', aspect='auto',
           extent=[x.min(), x.max(), y.min(), y.max()], interpolation = interpolation)

    if not show_only_mu:
        plt.title('$\sigma_\mathrm{%s}$ [pb] ; %s' % (process.replace('_','-'), plotTitle))
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
        plt.colorbar( ticks = LogLocator(subs=range(10)) )
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
        plt.title('$\sigma_\mathrm{%s}$ [pb] ; %s' % (process.replace('_','-'), plotTitle))
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
        plt.colorbar( ticks = LogLocator(subs=range(10)) )
    else:
        plt.colorbar()
    
    plt.tight_layout()
    if show_only_mu:
        make_folder_if_not_exists(output_folder + '/mu_values/')
        plt.savefig(output_folder + '/mu_values/' + '/mu_%s_mV%s.pdf' % (process, mV) )    
    elif with_limits: 
        make_folder_if_not_exists(output_folder + '/with_limits/')
        plt.savefig(output_folder + '/with_limits/' + '/sigma_excl_%s_mV%s.pdf' % (process, mV) )    
    elif show_alpha_beta_gamma:
        if 'tt_excl' in process:
            plt.savefig(output_folder + '/alpha_mV%s.pdf' % mV)
        elif 'onshell' in process:
            plt.savefig(output_folder + '/beta_mV%s.pdf' % mV)
        elif 'offshell' in process:
            plt.savefig(output_folder + '/gamma_mV%s.pdf' % mV)
    else:
        plt.savefig(output_folder + '/sigma_%s_mV%s.pdf' % (process, mV) )
    plt.close()

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option( "-o", "--output_folder", dest = "output_folder", default = 'plots/',
                  help = "set path to save plots" )
    parser.add_option( "-i", "--input_folder", dest= "input_folder", default = '/afs/cern.ch/work/s/ssenkin/public/LimitsOutput/',
                  help = "set path to limits" )
    parser.add_option( "-l", "--log_scale", action = "store_true", dest = "log_scale",
                      help = "Plot histograms in log scale" )
    parser.add_option( "-f", "--fraction_plots", action = "store_true", dest = "fraction_plots",
                      help = "Make fraction plots (ratios to total/visible cross section)" )
    parser.add_option( "-a", "--additional_plots", action = "store_true", dest = "more_plots",
                      help = "Make additional plots" )
    parser.add_option( "-m", "--mode", dest= "mode", default = '',
                  help = "set mode (e.g. BlindExp)" )
    parser.add_option( "-d", "--data_driven", action = "store_true", dest = "data_driven",
                      help = "Use data-driven background instead of full MC background" )


    ( options, args ) = parser.parse_args()

    output_folder = options.output_folder
    
    make_folder_if_not_exists(output_folder)

    input_folder = options.input_folder
    data_driven = options.data_driven
    mode = options.mode

    if data_driven:
        bkg_type = 'DD'
    else:
        bkg_type = 'FullMC'
    
    input_folder += '/' + bkg_type
    output_folder += '/' + bkg_type

    if options.mode != '':
        input_folder += '_' + options.mode
        output_folder += '_' + options.mode

    log_scale = options.log_scale
    if log_scale:
        output_folder += '/log/'

    whole_data = np.genfromtxt('big_table.csv', delimiter=',')
    #delete first row (variable names)
    whole_data = np.delete(whole_data, (0), axis=0)

    # work with a single mV:
    if options.more_plots:
        for mV in mediator_masses:
            single_mV_data = whole_data[whole_data[:,5]==mV]
            for process in processes:
                make_all_plots(mV, single_mV_data, process)

    # make a g_SM vs mV limit plot
    first_a_r_data = whole_data[whole_data[:,2]==whole_data[:,2][0]]
    g_DMs = first_a_r_data[:,3]
    # select first, middle and last g_DMs
    g_DMs = [g_DMs[0], g_DMs[(len(g_DMs) - 1)/2], g_DMs[-1]]
    # g_DMs = [0.5]

    for g_DM in g_DMs:
        make_limit_plot_vs_mV(whole_data, g_DM, mode)

    if options.fraction_plots:
        for mV in mediator_masses:
            single_mV_data = whole_data[whole_data[:,5]==mV]
            make_fraction_plots(mV, single_mV_data, mode='visible')
            make_fraction_plots(mV, single_mV_data, mode='total')

