import sys
import math
import numpy as np

class ParameterSpace :
    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other): 
        first = np.array(self.__dict__.values())
        second = np.array(other.__dict__.values())
        return np.allclose(first, second)
    
    def __ne__(self, other):
        first = np.array(self.__dict__.values())
        second = np.array(other.__dict__.values())
        return not np.allclose(first, second)

    def __init__(self) :
        self.mV = 0
        self.mDM = 0
        self.a_r = 0
        self.g = np.nan
        self.G_tot = np.nan
        self.BR = np.nan
        self.m_top = 172
    
    # Setting parameters
    def set_mV(self, mV):
        self.mV = float(mV)
    def set_mDM(self, mDM):
        self.mDM = float(mDM)
    def set_a_r(self, a_r):
        self.a_r = float(a_r)
    def set_g(self, g):
        self.g = float(g)
    def set_G_tot(self, G_tot):
        self.G_tot = float(G_tot)
    def set_BR(self, BR):
        self.BR = float(BR)
    def set_m_top(self, m_top):
        self.m_top = float(m_top)

    def print_initial_parameters(self):
        print 'mV = ', self.mV
        print 'mDM = ', self.mDM
        print 'a_r = ', self.a_r
        if not np.isnan(self.g):
            print 'g_{DM} = ', self.g
        if not np.isnan(self.BR):
            print 'BR_{DM} = ', self.BR
        if not np.isnan(self.G_tot):
            print 'G_tot = ', self.G_tot

    def print_calculated_parameters(self):
        print 'g_{DM} = ', self.g
        print 'BR_{DM} = ', self.BR
        print 'G_tot = ', self.G_tot

    def parameter_space_name(self):
        name = 'mV%.0f_mDM%.0f_a_r%.1f' % (self.mV, self.mDM, self.a_r)
        if not np.isnan(self.BR):
            name += '_BR%.2f' % self.BR
        elif not np.isnan(self.g):
            name += '_g%.2f' % self.g
        elif not np.isnan(self.G_tot):
            name += '_G_tot%.2f' % self.G_tot

        return str(name)

    def mV(self):
        return self.mV

    def mDM(self):
        return self.mDM

    def a_r(self):
        return self.a_r

    def G_tot(self):
        return self.G_tot

    def g(self):
        return self.g

    def BR(self):
        return self.BR

    def m_top(self):
        return self.m_top

    # ratio of top mass to mediator mass
    def r_t(self):
        return float(self.m_top/self.mV)

    # ratio of DM mass to mediator mass
    def r_chi(self):
        return float(self.mDM/self.mV)

    # phase space function for visible decay
    def phi_vis(self):
        return (1-self.r_t()**2) * (1-0.5*self.r_t()**2-0.5*self.r_t()**4)
    
    # phase space function for invisible decay
    def phi_invis(self):
        return math.sqrt(1-4*self.r_chi()**2) * (1+2*self.r_chi()**2)

    # visible partial width
    def G_vis(self):
        return self.a_r**2 * (self.mV/math.pi) * self.phi_vis()

    # invisible partial width
    def G_invis(self):
        if not np.isnan(self.G_tot):
            return self.G_tot-self.G_vis()
        elif not np.isnan(self.g):
            return self.g**2 * (self.mV/(12*math.pi)) * self.phi_invis()
        elif not np.isnan(self.BR):
            calculate_g()
            return self.g**2 * (self.mV/(12*math.pi)) * self.phi_invis()
        else:
            print 'Error: can not calculate the invisible decay width, please set the total width, g coupling or the BR to invisible.'
            sys.exit(1)

    def calculate_G_tot(self):
        if not np.isnan(self.G_tot):
            print 'Warning: total width already set to ', self.G_tot

        calculated_G_tot = self.G_vis()+self.G_invis()

        if not np.isnan(self.G_tot) and not np.isclose(self.G_tot, calculated_G_tot, equal_nan=False):
            print 'Error: calculated total width of %s incompatible with already set one of %s' % (calculated_G_tot, self.G_tot)
            sys.exit(1)

        # set total width
        self.G_tot = calculated_G_tot

    def calculate_g(self):
        if not np.isnan(self.g):
            print 'Warning: g coupling (to invisible) already set to ', self.g

        # coupling constant squared
        if not np.isnan(self.G_tot):
            g_squared = self.G_invis()/((self.mV/(12*math.pi)) * self.phi_invis())
        elif not np.isnan(self.BR):
            g_squared = 12 * self.a_r**2 * (self.BR/(1-self.BR)) * self.phi_vis() / self.phi_invis()
        else:
            print 'Error: can not calculate g coupling, please set either total width or the BR to invisible.'
            sys.exit(1)

        if g_squared<0:
            print 'Unphysical parameters: negative g_squared.'
            sys.exit(1)

        calculated_g = math.sqrt(g_squared)

        if not np.isnan(self.g) and not np.isclose(self.g, calculated_g, equal_nan=False):
            print 'Error: calculated g coupling of %s incompatible with already set one of %s' % (calculated_g, self.g)
            sys.exit(1)

        self.g = calculated_g

    def calculate_BR(self):
        if not np.isnan(self.BR):
            print 'Warning: BR (to invisible) already set to ', self.BR

        calculated_BR = float(self.G_invis()/(self.G_vis()+self.G_invis()))

        if not np.isnan(self.BR) and not np.isclose(self.BR, calculated_BR, equal_nan=False):
            print 'Error: calculated BR to invisible of %s incompatible with already set one of %s' % (calculated_BR, self.BR)
            sys.exit(1)

        self.BR = calculated_BR

    def calculate_all(self):
        if not np.isnan(self.g):
            self.calculate_G_tot()
            self.calculate_BR()
        elif not np.isnan(self.BR):
            self.calculate_g()
            self.calculate_G_tot()
        elif not np.isnan(self.G_tot):
            self.calculate_g()
            self.calculate_BR()

