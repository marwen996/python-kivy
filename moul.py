# -*- coding: utf-8 -*-
import kivy
import self
import pickle

kivy.require('1.11.1')
import pymssql
from kivy.uix.button import Button
from kivy.app import App
# from kivy.garden.navigationdrawer import NavigationDrawer as ND
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
from kivy.uix.slider import Slider
from kivy.uix.widget import Widget

from os.path import join, dirname
from kivy.logger import Logger
from kivy.uix.scatter import Scatter
from kivy.properties import StringProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout

from kivy.graphics import BorderImage

from kivy.clock import Clock

from functools import partial
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import datetime

from datetime import datetime
# from RPi import GPIO
# import automationhat
# On import les modules necessaires
import time
from time import sleep
import smtplib
import subprocess

import socket

from kivy.config import Config

Config.read("/home/pi/Downloads/config.ini")
Builder.load_file('screen.kv')


##############################################################
# Input Output Declaration
##############################################################

# if automationhat.is_automation_hat():
#     automationhat.light.power.write(1)
# else:
#     automationhat.light.power.write(0)


##################################################################
# Main Screen Manager
#####################################################################
# Create the screen manager
class Progress(Popup):

    def __init__(self, **kwargs):
        super(Progress, self).__init__(**kwargs)
        # call dismiss_popup in 2 seconds
        Clock.schedule_once(self.dismiss_popup, 2)

    def dismiss_popup(self, dt):
        self.dismiss()


class Manager(AnchorLayout):
    machine = 'Machine N11'

    empreint = 0
    signal = 0
    TRS = 0
    total_arret = 0
    t_c_th = 1
    t1 = 0
    t2 = 0
    t3 = 0
    t4 = 0
    hh = 0
    mm = 0
    ss = 0
    quantitePalanifie = 0
    qtRestante = 0
    qtProduite = 0
    qtBon_t = 0

    qtsurcharge = 0
    qtRejet = 0
    qtBon = 0
    duree = 3600
    qtRejet_ajout = 0
    qtBon_ajout = 0
    shopOrder = ''
    touls = ''
    matricule = ''
    progression = 0
    step = 1
    equippement = 0
    cycle = 0
    Etat = ''
    CodeArret = ''
    temp = 0
    cycle_t = 0
    toolId = 0
    ############### PASS WORD #######################
    declaration_arret = ''
    start_time = time.time()
    now = datetime.now()
    temps_qualite_fin = datetime.now()
    temps_qualite_debut = datetime.now()
    temps_regleur_debut = datetime.now()
    temps_regleur_fin = datetime.now()
    arret_identification_at = datetime.now()
    Etat = ''
    compte = ''
    type_arret = ''
    type_arret_d = ''
    temps_arret_totale = 0
    shift = datetime.now()
    ###############" equippement Liste##########################"

    equippement1 = ''
    equippement2 = ''
    equippement3 = ''
    equippement4 = ''
    equippement5 = ''

    arretCode1 = ''
    arretCode2 = ''
    arretCode3 = ''
    arretCode4 = ''
    arretCode5 = ''

    description1 = ''
    description2 = ''
    description3 = ''
    description4 = ''
    description5 = ''

    ###############################################
    # Database Connection 
    ###############################################
    host = "192.168.61.21"
    username = "admin"
    password = "root"
    database = "mouldingDB"

    ################################################

    #################### started at finished at shop order ###########################
    shop_order_started_at = datetime.now()
    shop_order_finished_at = datetime.now()
    debut_arret = datetime.now()
    fin_arret = datetime.now()

    def __init__(self, **kwargs):
        super(Manager, self).__init__(**kwargs)
        self.shop_order_started_at = time.time()
        self.Etat = '0'
        self.CodeArret = '11'
        Clock.schedule_interval(self.popup_2, 10)

        Clock.schedule_interval(self.time, 1)
        Clock.schedule_interval(self.daily_audit, 1)
        self.arret_identification_at = datetime.now()
        Clock.schedule_interval(self.calcul_TRS, 3600)

    def daily_audit(self, dt):
        now = datetime.now()
        daily = now.strftime("%M:%S")
        if daily == "30:00":
            self.insert_Audit(self.machine, self.Etat, self.CodeArret, self.TRS)

    def compteur(self, dt):
        try:
            self.ss = self.ss + 1
            if self.ss == 60:
                self.mm += 1
                self.ss = 0
            elif self.mm == 60:
                self.mm = 0
                self.hh += 1
            self.ids.horloge.text = 'temps Arret = ' + str(self.hh) + ':' + str(self.mm) + ':' + str(self.ss)
        except:
            print('problem python')
    def Btn(self):
        self.ids.managerScreen.current = 'Production'
    def time(self, dt):
        now = datetime.now()
        self.ids.qtProduite.text = str(self.qtProduite)
        self.ids.qtBon.text = str(self.qtBon) + '/' + '(+)' + str(self.qtBon_ajout)
        self.ids.qtRejet.text = str(self.qtRejet) + '/' + '(+)' + str(self.qtRejet_ajout)
        if self.Etat == '0':
            self.total_arret += 1
            # print(self.total_arret)

    def calcul_TRS(self, dt):

        nb_th = ((self.empreint * self.duree) / self.t_c_th)
        if nb_th != 0:
            self.TRS = round((self.qtBon / nb_th) * 100, 2)
            self.ids.TRS.text = 'TRS=' + str(self.TRS) + '%'

        else:
            self.TRS = 0
            self.ids.TRS.text = 'TRS=' + str(self.TRS) + '%'

        self.duree = self.duree + 3600
        self.update_production(self.machine, 'TRS', str(self.TRS))

    def controle(self, dt):

        self.ids.spin2.background_color = [1, 0, 0, 1]
        self.ids.cas.text = 'Arrêt'
        self.ids.cas.color = [1, 0, 0, 1]
        now = datetime.now()
        self.ids.start.text = 'début = ' + str(now.strftime("%G/%m/%e  %H:%M:%S"))
        Clock.schedule_interval(self.compteur, 1)
        self.Etat = '0'
        self.CodeArret = '-'
        self.debut_arret = datetime.now()

        self.update_production(self.machine, 'Etat', '0')
        self.update_production(self.machine, 'Arrets', '-')
        self.update_production(self.machine, 'temps', self.now.strftime("%H:%M:%S"))
        Clock.unschedule(self.controle)

    ##################################################################
    # fonction de lire des entrés de donnés
    ###################################################################
    def popup_1(self):
        box = BoxLayout(orientation='vertical', padding=(10))
        box.add_widget(Label(text=self.ids.spin1.text, font_size=30, color=[1, 0, 0, 1]))
        btn1 = Button(text="OK", size_hint=[1, 0.2])
        box.add_widget(btn1)

        popup = Popup(title='Arret', title_size=(30),
                      title_align='center', content=box,
                      size_hint=(None, None), background_color=[1, 0, 0, 1], size=(600, 300),
                      auto_dismiss=True)
        btn1.bind(on_press=popup.dismiss)

        popup.open()

    def popup_2(self, dt):
        Clock.unschedule(self.popup_2)
        box = BoxLayout(orientation='vertical', padding=(10))
        box.add_widget(Label(text='MODICS Attente votre choix', font_size=30))
        btn1 = Button(text="OK", size_hint=[1, 0.5])
        box.add_widget(btn1)

        popup = Popup(title='WARNING!', title_color=(1, 0, 0, 1), title_size=(20),
                      title_align='center', content=box,
                      size_hint=(None, None), size=(500, 200),
                      auto_dismiss=False)
        btn1.bind(on_press=popup.dismiss)

        popup.open()

    def popup_3(self):

        box = BoxLayout(orientation='vertical', padding=(10))
        box.add_widget(Label(text='vous etes sure ??', font_size=20))
        btn1 = Button(text="OUI", size_hint=[1, 1])
        btn2 = Button(text="NON", size_hint=[1, 1])
        box.add_widget(btn1)
        box.add_widget(btn2)

        popup = Popup(title='Alerte', title_size=(30),
                      title_align='center', content=box,
                      size_hint=(None, None), size=(400, 200),
                      auto_dismiss=False)
        btn1.bind(on_press=self.dismiss, on_release=popup.dismiss)
        btn2.bind(on_press=popup.dismiss)
        popup.open()

    def dismiss(self, event):
        self.shop_order_finished_at = time.time()

        self.duree = self.shop_order_finished_at - self.shop_order_started_at

        nb_th = ((self.empreint * self.duree) / self.t_c_th)
        if nb_th != 0:
            self.TRS = round((self.qtBon / nb_th) * 100, 2)


        else:
            self.TRS = 0
        self.insert_kpi(self.machine, self.shift.strftime("%H:%M:%S"), self.shopOrder, (self.qtBon + self.qtBon_ajout),
                        (self.qtRejet + self.qtRejet_ajout), self.cycle_t, self.cycle, self.total_arret, self.TRS)
        self.update_production(self.machine, 'TRS', str(self.TRS))

        self.ids.managerScreen.current = 'Acceuil'
        self.shop_order_started_at = time.time()

        self.update_production(self.machine, 'shopordre', self.shopOrder)
        self.update_production(self.machine, 'quantite_produite', str(self.qtProduite))
        self.update_production(self.machine, 'quantite_planifier', str(self.quantitePalanifie))
        self.update_production(self.machine, 'Etat', '0')
        self.update_production(self.machine, 'Arrets', '-')
        self.update_production(self.machine, 'temps', self.now.strftime("%H:%M:%S"))
        # self.insert_shop_Order_jour(self.machine,self.shopOrder , self.toolId,self.quantitePalanifie,
        #                      self.qtProduite,self.qtProduite,self.qtRejet,self.cycle,
        #                     self.tempsProduction,
        #                    self.shop_order_started_at,self.shop_order_finished_at )
        self.step = 0
        self.Etat = '0'
        self.CodeArret = '14'
        self.duree = 3600
        Clock.schedule_interval(self.popup_2, 10)

    def on_spinner_select(self, value):
        value = self.ids.spin1.text
        l = ['[C/M] Changement matière uniquement', '[T/C/M] Changement moule et matière', '[AM] Attente matière',
             '[ME] Manque équipement', '[TC] Changement moule', '[PM] Problème moule au démarrage',
             '[DM] Démontage moule', '[MM] Montage moule', '[MR] Manque régleur', '[MO] Manque opérateur',
             '[AD] Attente Démarrage', '[MD] Manque dossier', '[ATC] Attente changement moule',
             '[MT] Problème Maintenance', '[CC] Coupure du courant', '[IM] Intervention moule', '[NM] Nettoyage moule',
             '[CV] Changement version', '[VP] Validation Procès', '[EM] Essai moule', '[NW] Manque planification',
             '[VQ] Validation Qualité']

        for i in range(len(l)):
            if value in l[i]:
                self.ids.spin1.background_color = [1, 0, 0, 1]
                self.debut_arret = datetime.now()
                Clock.unschedule(self.popup_2)
                if value == '[C/M] Changement matière uniquement':
                    self.CodeArret = '2'
                elif value == '[T/C/M] Changement moule et matière':
                    self.CodeArret = '3'
                elif value == '[AM] Attente matière':
                    self.CodeArret = '4'
                elif value == '[ME] Manque équipement':
                    self.CodeArret = '5'
                elif value == '[TC] Changement moule':
                    self.CodeArret = '6'
                elif value == '[PM] Problème moule au démarrage':
                    self.CodeArret = '7'
                elif value == '[DM] Démontage moule':
                    self.CodeArret = '8'
                elif value == '[MM] Montage moule':
                    self.CodeArret = '9'
                elif value == '[MR] Manque régleur':
                    self.CodeArret = '10'
                elif value == '[MO] Manque opérateur':
                    self.CodeArret = '11'
                elif value == '[AD] Attente Démarrage':
                    self.CodeArret = '12'
                elif value == '[MD] Manque dossier':
                    self.CodeArret = '13'
                elif value == '[ATC] Attente changement moule':
                    self.CodeArret = '14'
                elif value == '[MT] Problème Maintenance':
                    self.CodeArret = '15'
                elif value == '[CC] Coupure du courant':
                    self.CodeArret = '16'
                elif value == '[IM] Intervention moule':
                    self.CodeArret = '17'
                elif value == '[NM] Nettoyage moule':
                    self.CodeArret = '18'
                elif value == '[CV] Changement version':
                    self.CodeArret = '19'
                elif value == '[VP] Validation Procès':
                    self.CodeArret = '20'
                elif value == '[EM] Essai moule':
                    self.CodeArret = '21'
                elif value == '[NW] Manque planification':
                    self.CodeArret = '22'
                elif value == '[VQ] Validation Qualité':
                    self.CodeArret = '23'

                self.Etat = '0'

                self.popup_1()
                self.ids.yahoo.text = 'Arrêt'

                self.update_production(self.machine, 'Etat', self.Etat)
                self.update_production(self.machine, 'Arrets', self.CodeArret)
                self.update_production(self.machine, 'temps', self.now.strftime("%H:%M:%S"))

    # def on_spinner_select1(self,value):
    #     ure des empreintes','[C/M] Changement matière uniquement','[T/C/M] Changement moule et matière','[AM] Attente matière','[ME] Manque équipement','[TC] Changement moule','[PM] Problème moule au démarrage','[DM] Démontage moule','[MM] Montage moule','[MR] Manque régleur','[MO] Manque opérateur','[AD] Attente Démarrage','[MD] Manque dossier','[ATC] Attente changement moule','[MT] Problème Maintenance','[CC] Coupure du courant','[IM] Intervention moule','[NM] Nettoyage moule','[CV] Changement version','[VP] Validation Procès','[EM] Essai moule','[NW] Manque planification','[VQ] Validation Qualité']
    #
    #      for i in range(len(l)):
    #          if value in l[i]:
    #              self.ids.spin2.background_color= [1,0,0,1]
    #              self.debut_arret=datetime.now()
    #              if value=='[C/M] Changement matière uniquement':
    #                  self.CodeArret='2'
    #              elif value=='[T/C/M] Changement moule et matière':
    #                  self.CodeArret='3'
    #              elif value=='[AM] Attente matière':
    #                  self.CodeArret='4'
    #              elif value=='[ME] Manque équipement':
    #                  self.CodeArret='5'
    #              elif value=='[TC] Changement moule':
    #                  self.CodeArret='6'
    #              elif value=='[PM] Problème moule au démarrage':
    #                  self.CodeArret='7'
    #              elif value=='[DM] Démontage moule':
    #                  self.CodeArret='8'
    #              elif value=='[MM] Montage moule':
    #                  self.CodeArret='9'
    #              elif value=='[MR] Manque régleur':
    #                  self.CodeArret='10'
    #              elif value=='[MO] Manque opérateur':
    #                  self.CodeArret='11'
    #              elif value=='[AD] Attente Démarrage':
    #                  self.CodeArret='12'
    #              elif value=='[MD] Manque dossier':
    #                  self.CodeArret='13'
    #              elif value=='[ATC] Attente changement moule':
    #                  self.CodeArret='14'
    #              elif value=='[MT] Problème Maintenance':
    #                  self.CodeArret='15'
    #              elif value=='[CC] Coupure du courant':
    #                  self.CodeArret='16'
    #              elif value=='[IM] Intervention moule':
    #                  self.CodeArret='17'
    #              elif value=='[NM] Nettoyage moule':
    #                  self.CodeArret='18'
    #              elif value=='[CV] Changement version':
    #                  self.CodeArret='19'
    #              elif value=='[VP] Validation Procès':
    #                  self.CodeArret='20'
    #              elif value=='[EM] Essai moule':
    #                  self.CodeArret='21'
    #              elif value=='[NW] Manque planification':
    #                  self.CodeArret='22'
    #              elif value=='[VQ] Validation Qualité':
    #                  self.CodeArret='23'
    #              elif value=='Fermeture des empreintes':
    #                  self.ids.managerScreen.current ='Arret'
    #              self.ids.start.text=''
    #              self.ids.horloge.text=''
    #              self.hh=self.mm=self.ss=0
    #              Clock.unschedule(self.compteur)
    #              self.ids.cas.color= [1,0,0,1]
    #              self.ids.cas.text='Arrêt'
    #
    #              now=datetime.now()
    #              self.ids.start.text='début = ' + str(now.strftime("%G/%m/%e  %H:%M:%S"))
    #              Clock.schedule_interval(self.compteur,1)
    #
    #              self.Etat='0'
    #              self.update_production(self.machine,'Etat',self.Etat)
    #              self.update_production(self.machine,'Arrets',self.CodeArret)
    #              self.update_production(self.machine,'temps',self.now.strftime("%H:%M:%S"))
    #              Clock.unschedule(self.controle)
    def Btn_fin_arret(self):
        self.empreint = self.empreint - int(self.ids.ferme_emprient.text)
        self.ids.Empreint1.text = str(self.empreint)
        self.ids.managerScreen.current = 'Production'
        self.ids.entry1.text = ''

    def Btn_Annule_ferme(self):
        self.ids.managerScreen.current = 'Production'
        self.ids.entry1.text = ''

    def Btn_fin_arret_p(self):
        # automationhat.output.two.write(0)
        self.fin_arret = datetime.now()
        Clock.unschedule(self.compteur)
        self.ids.start.text = ''
        self.ids.horloge.text = ''
        self.hh = self.mm = self.ss = 0

        self.ids.spin2.background_color = [0, 0, 1, 1]
        self.ids.cas.color = [0, 0, 1, 1]
        if self.ids.valid_reglage.text == 'Validation Reglage':

            self.ids.cas.text = 'Attente Validation Réglage'
        else:
            self.ids.cas.text = 'Production'

        self.update_production(self.machine, 'Etat', self.Etat)
        self.update_production(self.machine, 'Arrets', self.CodeArret)
        self.update_production(self.machine, 'temps', self.now.strftime("%H:%M:%S"))
        Clock.schedule_interval(self.fermeture, 1 / 60.)
        Clock.schedule_interval(self.affiche, 1 / 60.)
        Clock.schedule_once(self.controle, 600)
        # self.data_base_id = self.insert_arret(self.machine,self.shopOrder,'Arret Production','Auto',
        #                                cation_at,
        #                                  self.debut_arret,
        #                                  self.fin_arret,
        #                                  self.arretCode1,self.arretCode2,
        #                                  self.arretCode3,self.arretCode4,self.arretCode5)
        #

    def active(self):

        self.fin_arret = datetime.now()
        self.ids.start.text = ''
        self.ids.cas.text = 'Production'
        self.ids.cas.color = [0, 0, 1, 1]

        Clock.unschedule(self.compteur)
        self.ids.horloge.text = ''
        self.hh = 0
        self.mm = 0
        self.ss = 0

        self.ids.spin2.background_color = [0, 0, 1, 1]
        Clock.schedule_interval(self.fermeture, 1 / 60.)
        Clock.schedule_interval(self.affiche, 1 / 60.)

        self.ids.cas.color = [0, 0, 1, 1]

        self.Etat = '1'
        self.CodeArret = '-'
        # self.data_base_id = self.insert_arret(self.machine,self.shopOrder,'Arret Production','Auto',
        #                                cation_at,
        #                                self.debut_arret,
        #                               self.fin_arret,
        #                              self.arretCode1,self.arretCode2,
        #                             self.arretCode3,self.arretCode4,self.arretCode5)

        self.update_production(self.machine, 'Etat', self.Etat)
        self.update_production(self.machine, 'Arrets', self.CodeArret)
        self.update_production(self.machine, 'temps', self.now.strftime("%H:%M:%S"))

    @staticmethod
    def fermeture(dt):
        return 0
        # self.now=datetime.now()
        #
        # if automationhat.input.two.is_off()and automationhat.input.one.is_on() and self.step == 1 :
        #     Clock.schedule_once(self.controle,600)
        #
        #
        #     self.step = 0
        #
        # if automationhat.input.two.is_off() and automationhat.input.one.is_on():
        #     self.start_time=time.time()
        #
        # if automationhat.input.two.is_on() and automationhat.input.one.is_on() and self.step == 0 and (time.time()-self.start_time)>0.05:
        #     self.signal = self.signal + self.empreint
        #     if(self.signal == self.empreint):
        #         self.t1=time.time()
        #     if(self.signal == self.empreint*2):
        #         self.t2=time.time()
        #         self.cycle=str(round(self.t2-self.t1,2))
        #         self.signal = 0
        #
        #     self.Etat='1'
        #     self.CodeArret='-'
        #
        #
        #
        #     self.step = 1
        #
        #
        #     if self.qtProduite < self.quantitePalanifie :
        #         if self.ids.valid_reglage.background_color == [0,255,0,1.0]:
        #             self.qtProduite = self.qtProduite  + self.empreint
        #
        #             self.qtBon= self.qtBon + self.empreint
        #         else:
        #             self.qtProduite = self.qtProduite  + self.empreint
        #             self.qtRejet = self.qtRejet  + self.empreint
        #
        #
        #     else:
        #         self.qtsurcharge = self.qtsurcharge + self.empreint
        #         self.qtProduite = self.qtProduite  + self.empreint
        #
        #         self.qtBon= self.qtBon + self.empreint
        #
        #
        #     self.update_production(self.machine,'cycle_time',str(self.cycle))
        #     self.update_production(self.machine,'quantite_rejet',str(self.qtRejet+self.qtRejet_ajout))
        #
        #     self.update_production(self.machine,'quantite_produite',str(self.qtProduite))
        #     self.update_production(self.machine,'Etat','1')
        #     self.update_production(self.machine,'Arrets','-')
        #     self.update_production(self.machine,'temps',self.now.strftime("%H:%M:%S"))
        #     Clock.unschedule(self.controle)
        #     self.active()

    ########### ehp#######################################################
    def affiche(self, dt):
        return 0

        # if automationhat.input.two.is_off()and automationhat.input.one.is_on():
        #     self.ids.step.background_color = [0,1,0,1]
        #     self.ids.qtProduite.text= str(self.qtProduite)
        #     self.ids.qtBon.text= str(self.qtBon)+'/'+'(+)' +str(self.qtBon_ajout)
        #     self.ids.qtRejet.text = str(self.qtRejet)+'/'+'(+)' + str(self.qtRejet_ajout)
        #
        #     self.ids.cycle1.text=str(self.cycle)+'/'+str(self.cycle_t)
        #     if  self.qtProduite <= self.quantitePalanifie :
        #             self.qtRestante = self.quantitePalanifie - self.qtProduite
        #             self.ids.qtRestante.text = str(self.qtRestante)
        #             self.ids.progression.value = self.qtProduite
        #     else :
        #         self.step = 0
        #

    ######################################################################
    # initialisation
    ##################################################################
    def initialisation_var(self):

        self.cycle = 0
        self.cycle_t = 1
        self.signal = 0
        self.t1 = 0
        self.t2 = 0
        self.t3 = 0
        self.t4 = 0

        self.ids.annule1.background_color = [1, 0, 0, 0]
        self.ids.annule2.background_color = [1, 0, 0, 0]
        self.ids.annule3.background_color = [1, 0, 0, 0]
        self.ids.annule4.background_color = [1, 0, 0, 0]
        self.ids.annule5.background_color = [1, 0, 0, 0]

        self.ids.annule1.text = ''
        self.ids.annule2.text = ''
        self.ids.annule3.text = ''
        self.ids.annule4.text = ''
        self.ids.annule5.text = ''

        self.ids.n.background_color = [0, 0, 0, 1]
        self.ids.t.background_color = [0, 0, 0, 1]

        self.ids.equippement2.background_color = [1, 0, 0, 0]
        self.ids.equippement3.background_color = [1, 0, 0, 0]
        self.ids.equippement4.background_color = [1, 0, 0, 0]
        self.ids.equippement5.background_color = [1, 0, 0, 0]
        self.ids.valid_reglage.background_color = [1, 0, 0, 1]
        self.ids.valid_qualite.background_color = [0, 0, 1, 1]
        self.ids.valid_qualite.color = [1, 1, 1, 1]
        self.ids.valid_reglage.color = [1, 1, 1, 1]

        self.ids.equippement1.text = '+'
        self.ids.equippement2.text = ''
        self.ids.equippement3.text = ''
        self.ids.equippement4.text = ''
        self.ids.equippement5.text = ''
        self.ids.valid_reglage.text = 'Validation Reglage'
        self.ids.valid_qualite.text = 'Validation Finale'

        self.ids.ShopOrder.background_color = [0, 0, 1, 1]
        self.ids.touls.background_color = [0, 0, 1, 1]
        self.ids.Empreint.background_color = [0, 0, 1, 1]
        self.ids.quantite.background_color = [0, 0, 1, 1]

        self.qtRejet_ajout = 0
        self.qtBon_ajout = 0

        self.ids.qtProduite.text = '0'
        self.empreint = 0
        self.quantitePalanifie = 0

        self.qtRestante = 0
        self.qtProduite = 0
        self.qtsurcharge = 0
        self.qtRejet = 0
        self.qtBon = 0

        self.shopOrder = ''
        self.touls = ''
        self.progression = 0

        self.equippement = 0

        self.ids.entry1.text = ''
        self.ids.entry2.text = ''

    ###################################################################   
    # Acceuil Screen 
    ################################################################### 
    def resume(self):
        Clock.unschedule(self.popup_2)
        data = pickle.load(open("data.text", "rb"))
        self.ids.ShopOrder1.text = data[0]
        self.ids.touls1.text = data[1]
        self.ids.Empreint1.text = data[2]
        self.ids.quantite1.text = data[3]
        self.ids.progression.value = data[4]

        self.ids.managerScreen.current = 'Production'

    def Btn_start(self):

        # self.initialisation_var()
        self.qtBon_ajout = 0
        self.qtRejet_ajout = 0
        Clock.unschedule(self.compteur)
        self.ids.start.text = ''
        self.ids.horloge.text = ''
        self.hh = self.mm = self.ss = 0

        self.ids.valid_qualite.background_color = [1, 0, 0, 1]
        self.arret_identification_at = datetime.now()

        self.ids.valid_reglage.disabled = False
        self.ids.valid_qualite.disabled = False
        Clock.unschedule(self.fermeture)
        Clock.unschedule(self.affiche)
        Clock.unschedule(self.controle)

        self.fin_arret = datetime.now()
        Clock.unschedule(self.popup_2)
        # if self.ids.spin1.text == 'Signaler un Arrêt' :
        #     self.data_base_id = self.insert_arret(self.machine,'' ,'arret machine','Auto',
        #                                           'arret non declarée',self.debut_arret,
        #                                           self.debut_arret,
        #                                           self.fin_arret,
        #                                           self.arretCode1,self.arretCode2,
        #                                           self.arretCode3,self.arretCode4,self.arretCode5)
        # else:
        #     self.data_base_id = self.insert_arret(self.machine,'' ,'arret machine','Auto',
        #                                           self.ids.spin1.text,self.arret_identification_at,
        #                                           self.debut_arret,
        #                                           self.fin_arret,
        #                                           self.arretCode1,self.arretCode2,
        #                                           self.arretCode3,self.arretCode4,self.arretCode5)
        # self.update_production(self.machine,'Etat','0')
        # self.update_production(self.machine,'Arrets','11')
        # self.update_production(self.machine,'temps',self.now.strftime("%H:%M:%S"))
        self.Etat = '0'
        self.CodeArret = '11'
        self.ids.spin1.background_color = [0, 0, 1, 1]
        self.ids.spin1.text = 'Signaler un Arrêt'

        self.ids.yahoo.text = ''
        # self.ids.keyboardinputInt.text = 'Ordre de fabrication'
        self.ids.entry1.text = ''
        self.ids.managerScreen.current = 'Setting'
        self.arret_identification_at = datetime.now()

    def Btn_fin_shopOrder(self):
        self.popup_3()

    def Btn_Valid_qualite(self, value):
        self.ids.cas.text = 'Prêt...'
        value = self.ids.valid_qualite.text
        l1 = ['Validé', 'Non Validé']
        if self.ids.valid_reglage.text == 'Reglage Validé':
            for i in range(len(l1)):
                if value in l1[i]:
                    if self.ids.valid_qualite.text == 'Validé':
                        self.ids.valid_qualite.background_color = [0, 255, 0, 1.0]
                        self.ids.valid_qualite.text = 'Validé'
                        self.ids.valid_reglage.disabled = True
                        self.ids.valid_qualite.disabled = True
                    elif self.ids.valid_qualite.text == 'Non Validé':
                        self.qtRejet = self.qtRejet + self.qtProduite

                        self.qtRestante = self.quantitePalanifie
                        self.qtProduite = 0
                        self.ids.valid_qualite.background_color = [1, 0, 0, 1]
                        self.ids.valid_reglage.background_color = [1, 0, 0, 1]
                        self.ids.valid_reglage.text = 'Validation Reglage'
                        self.temps_regleur_debut = datetime.now()
            self.ids.valid_qualite.color = [1, 1, 1, 1]
            self.temps_qualite_fin = datetime.now()

            self.type_arret = 'qualite'
            self.declaration_arret = 'Arret qualite'
            self.data_base_id = self.insert_arret(self.machine, self.shopOrder, self.type_arret, 'User',
                                                  self.declaration_arret, self.arret_identification_at,
                                                  self.temps_qualite_debut,
                                                  self.temps_qualite_fin, self.arretCode1, self.arretCode2,
                                                  self.arretCode3, self.arretCode4, self.arretCode5)

    def Btn_Valid_Reglage(self):
        self.ids.cas.text = 'Attente Validation Final'
        self.ids.valid_reglage.background_color = [0, 255, 0, 1.0]
        self.ids.valid_reglage.text = 'Reglage Validé'
        self.ids.valid_reglage.color = [0, 0, 0, 1]
        self.ids.valid_qualite.text = 'Validation Finale'
        self.ids.valid_qualite.background_color = [0, 0, 1, 1]

        self.temps_regleur_fin = datetime.now()
        self.temps_qualite_debut = datetime.now()
        self.type_arret = 'Reglage'
        self.declaration_arret = 'Arret Reglage'
        self.data_base_id = self.insert_arret(self.machine, self.shopOrder, self.type_arret, 'User',
                                              self.declaration_arret, self.arret_identification_at,
                                              self.temps_qualite_debut,
                                              self.temps_qualite_fin, self.arretCode1, self.arretCode2, self.arretCode3,
                                              self.arretCode4, self.arretCode5)

    def Btn_retour_n(self):
        self.ids.managerScreen.current = 'Production'

    def Btn_retour(self):
        self.ids.managerScreen.current = 'Acceuil'

    def Btn_fail(self):
        clavier = self.ids.keyboardinputInt.text
        self.ids.n.background_color = [0, 0, 0, 1]
        self.ids.t.background_color = [0, 0, 0, 1]
        l1 = ['Numéro de touls', 'Nombre des empreintes', 'Quantité demandé', 'Temps de cycle']
        l2 = ['Ordre de fabrication']
        l3 = ['Matricule Régleur', 'Mot de Pass Régleur', 'Matricule Qualité', 'Mot de Pass Qualité']
        l4 = ['saisir quantite rejet', 'saisir quantite Bon']
        for i in range(50):
            if clavier in l1:
                self.ids.managerScreen.current = 'Setting'
            elif clavier in l2:
                self.ids.managerScreen.current = 'Acceuil'
                Clock.schedule_interval(self.popup_2, 10)

            elif clavier in l3:
                self.ids.managerScreen.current = 'identification'
            elif clavier in l4:
                self.ids.managerScreen.current = 'Production'

    def Btn_retour11(self):
        self.ids.managerScreen.current = 'Setting'

    ###################################################################   
    # Keybord Screen int insert
    ################################################################### 

    def Btn_keyboard_int(self):
        pw_word = ''
        input_value = self.ids.entry1.text
        if input_value != '0' and input_value != '':
            modifieInt = str(self.ids.keyboardinputInt.text)
            if modifieInt == 'Nombre des empreintes':
                self.ids.Empreint.text = str(input_value)
                self.ids.keyboardinputInt.text = 'Quantité demandé'
                self.ids.entry1.text = ''

                self.ids.managerScreen.current = 'keyboardInputNum'




            elif modifieInt == 'Quantité demandé':
                self.ids.quantite.text = str(input_value)
                self.ids.keyboardinputInt.text = 'temps de cycle'
                self.ids.managerScreen.current = 'keyboardInputNum'
                self.ids.entry1.text = ''
            elif modifieInt == 'saisir quantite rejet':

                self.qtRejet_ajout = int(input_value)

                self.ids.managerScreen.current = 'Production'
                self.ids.entry1.text = ''
            elif modifieInt == 'saisir quantite Bon':

                self.qtBon_ajout = int(input_value)

                self.ids.managerScreen.current = 'Production'
                self.ids.entry1.text = ''
            elif modifieInt == 'Ordre de fabrication':
                self.ids.ShopOrder.text = str(input_value)
                self.ids.keyboardinputInt.text = 'Numéro de touls'
                self.ids.n.background_color = [0, 1, 0, 1]
                self.ids.t.background_color = [0, 1, 0, 1]
                self.ids.entry1.text = ''
                self.ids.managerScreen.current = 'keyboardInputNum'

            elif modifieInt == 'Numéro de touls':
                self.ids.touls.text = str(input_value)
                self.ids.keyboardinputInt.text = 'Nombre des empreintes'
                self.ids.entry1.text = ''
                self.ids.n.background_color = [0, 0, 0, 1]
                self.ids.t.background_color = [0, 0, 0, 1]
                self.ids.managerScreen.current = 'keyboardInputNum'


            elif modifieInt == 'temps de cycle':
                self.ids.cycle_t.text = str(input_value)
                self.cycle_t = float(input_value)
                self.ids.n.background_color = [0, 1, 0, 1]
                self.ids.t.background_color = [0, 1, 0, 1]
                self.ids.entry1.text = ''
                self.ids.managerScreen.current = 'Setting'



            elif modifieInt == 'nombre des empreintes fermées':
                self.ids.ferme_emprient.text = str(input_value)
                self.ids.entry1.text = ''
                self.ids.managerScreen.current = 'Arret'

    ###################################################################
    # Setting Screen Function
    ###################################################################

    def Btn_fermer_emprient(self):
        self.ids.keyboardinputInt.text = 'nombre des empreintes fermées'
        self.ids.entry1.text = ''
        self.ids.managerScreen.current = 'keyboardInputNum'

    def Btn_shop_order(self):
        self.ids.keyboardinputInt.text = 'Ordre de fabrication'
        self.ids.entry1.text = ''
        self.ids.ShopOrder.background_color = [0, 0, 1, 1]
        self.ids.managerScreen.current = 'keyboardInputNum'

    def Btn_touls(self):
        self.ids.keyboardinputInt.text = 'Numéro de touls'
        self.ids.touls.background_color = [0, 0, 1, 1]
        self.ids.entry1.text = ''
        self.ids.n.background_color = [0, 1, 0, 1]
        self.ids.t.background_color = [0, 1, 0, 1]
        self.ids.managerScreen.current = 'keyboardInputNum'

    def Btn_empreint(self):
        self.ids.keyboardinputInt.text = 'Nombre des empreintes'
        self.ids.Empreint.background_color = [0, 0, 1, 1]
        self.ids.entry1.text = ''
        self.ids.managerScreen.current = 'keyboardInputNum'

    def Btn_select_arret(self):

        self.ids.managerScreen.current = 'keyboardInputArrets'

    def Btn_qantite_demande(self):
        self.ids.keyboardinputInt.text = 'Quantité demandé'
        self.ids.quantite.background_color = [0, 0, 1, 1]
        self.ids.entry1.text = ''
        self.ids.managerScreen.current = 'keyboardInputNum'

    def Btn_cycle_time(self):
        self.ids.keyboardinputInt.text = 'temps de cycle'
        self.ids.cycle_t.background_color = [0, 0, 1, 1]
        self.ids.entry1.text = ''
        self.ids.managerScreen.current = 'keyboardInputNum'

        self.ids.cycle_t.background_color = [0, 0, 1, 1]

    def Btn_ajout_rejet(self):
        self.ids.keyboardinputInt.text = 'saisir quantite rejet'

        self.ids.entry1.text = ''
        self.ids.managerScreen.current = 'keyboardInputNum'

    def Btn_ajout_bon(self):
        self.ids.keyboardinputInt.text = 'saisir quantite Bon'

        self.ids.entry1.text = ''
        self.ids.managerScreen.current = 'keyboardInputNum'

    def Btn_production(self):
        self.t_c_th = self.cycle_t
        self.ids.cycle1.text = str(self.cycle) + '/' + str(self.cycle_t)
        Clock.schedule_interval(self.fermeture, 1 / 600.)
        Clock.schedule_interval(self.affiche, 1 / 600.)
        Clock.schedule_once(self.controle, 600)
        self.shopOrder = self.ids.ShopOrder.text
        self.touls = self.ids.touls.text
        self.empreint = int(self.ids.Empreint.text)
        self.quantitePalanifie = int(self.ids.quantite.text)
        self.qtRestante = self.quantitePalanifie
        self.qtProduite = 0
        self.progression = 0

        if self.shopOrder == '':
            self.ids.ShopOrder.background_color = [1, 1, 0, 1]

        elif self.touls == '':
            self.ids.touls.background_color = [1, 1, 0, 1]

        elif self.empreint == 0:
            self.ids.Empreint.background_color = [1, 1, 0, 1]

        elif self.quantitePalanifie == 0:
            self.ids.quantite.background_color = [1, 1, 0, 1]
        elif self.cycle_t in ['', '0']:
            self.ids.cycle_t.background_color = [1, 1, 0, 1]


        else:
            self.ids.ShopOrder1.text = self.shopOrder
            self.ids.touls1.text = self.touls
            self.ids.Empreint1.text = str(self.empreint)
            self.ids.quantite1.text = str(self.quantitePalanifie)
            self.ids.qtRestante.text = str(self.quantitePalanifie)
            self.ids.progression.max = self.quantitePalanifie
            self.ids.progression.value = 0
            # self.ids.cycle1.text= str(self.cycle_t)
            data = [self.ids.ShopOrder1.text, self.ids.touls1.text, self.ids.Empreint1.text, self.ids.quantite1.text,
                    self.ids.progression.value]
            pickle.dump(data, open("data.text", "wb"))
            print(data)
            self.page = 1
            ########################################"
            self.ids.ShopOrder.text = ''
            self.ids.touls.text = ''
            self.ids.Empreint.text = '0'
            self.ids.quantite.text = '0'
            self.ids.cycle_t.text = ''

            #############################################
            self.ids.managerScreen.current = 'Production'
            self.Etat = '0'
            self.CodeArret = '9'

            now = datetime.now()

            ######################################
            # Debut arret montage Moul
            self.temps_technicien_fin = datetime.now()
            # self.update_production(self.machine,'shopordre',self.shopOrder)
            # self.update_production(self.machine,'quantite_planifier',str(self.quantitePalanifie) )
            # self.update_production(self.machine,'debut_shop',self.now.strftime("%H:%M:%S"))

    ##            self.toolId = self.insert_Toul_number(self.machine , self.touls,self.empreint )
    ##            self.update_mail_notification(self.machine,'shopOrder', self.shopOrder)
    ###################################################################
    # Read Inerruption of input
    ###################################################################
    @staticmethod
    def conteur_piece():
        self.cycle
        self.empreint
        self.qtsurcharge
        if self.quantitePalanifie > self.qtProduite:
            self.qtProduite = self.qtProduite + self.empreint
            self.qtRestante = self.quantitePalanifie - self.qtProduite
        else:
            self.qtsurcharge = self.qtsurcharge + self.empreint

    ##################################################################
    # Data base connection
    ##################################################################
    # insertion shop order
    def insert_shop_Order_jour(self, machine, ShopOrder, ToolID, QuantitePlanifier,
                               QuantiteProduite, QuantiteBonne, QuantiteSurcharge, tempsShopOrdre,
                               TempsProduction, Debut, Fin):
        try:
            conn = pymssql.connect(self.host, self.username, self.password, self.database)
            cursor = conn.cursor()
            cursor.execute("select count(id) from ShopOrderJours")
            result = cursor.fetchall()
            id_insert = result[0][0] + 1
            id_insert = 1
            print(id_insert)
            requette = "INSERT INTO shoporderjours VALUES ("
            requette += "\'" + str(id_insert) + "\'"
            requette += ", \'" + machine + "\'"
            requette += ", \'" + ShopOrder + "\'"
            requette += ", \'" + str(ToolID) + "\'"
            requette += ", \'" + str(QuantitePlanifier) + "\'"
            requette += ", \'" + str(QuantiteProduite) + "\'"
            requette += ", \'" + str(QuantiteBonne) + "\'"

            requette += ", \'" + time.strftime('%H:%M:%S', time.gmtime(int((Fin - Debut).total_seconds()))) + "\'"
            requette += ", \'" + str(TempsProduction) + "\'"

            requette += ", \'" + str(Debut)[0:23] + "\'"
            requette += ", \'" + str(Fin)[0:23] + "\'"
            requette += ")"
            cursor.execute(requette)
            conn.commit()
            return id_insert
        except:
            print('probleme connexion1')

    ########################################################""
    # insertion Dashboard
    def insert_Audit(self, machine, Etat, CodeArret, TRS):
        try:
            conn = pymssql.connect(self.host, self.username, self.password, self.database)
            cursor = conn.cursor()
            cursor.execute("select count(id) from ProductionMi")
            result = cursor.fetchall()
            id_insert = result[0][0] + 1
            id_insert = 1
            requette = "INSERT INTO ProductionMi VALUES ("
            requette += "\'" + str(id_insert) + "\'"
            requette += ", \'" + machine + "\'"
            requette += ", \'" + Etat + "\'"
            requette += ", \'" + CodeArret + "\'"
            requette += ", \'" + str(datetime.now())[0:19] + "\'"
            requette += ", \'" + str(TRS) + "\'"
            requette += ")"
            print (requette)

            cursor.execute(requette)
            conn.commit()
            return id_insert
        except:
            print('probleme connexion')

    ########################################################""
    # insertion Arret
    def insert_arret(self, machine, ShopOrder, type_arret, operateur, declaration, Debut_declaration, Debut_Arret,
                     Fin_Arret, codeArret1, codeArret2, codeArret3, codeArret4, codeArret5):
        try:
            conn = pymssql.connect(self.host, self.username, self.password, self.database)
            cursor = conn.cursor()
            cursor.execute("select count(id) from Arret")
            result = cursor.fetchall()
            id_insert = result[0][0] + 1
            id_insert = 1
            print(id_insert)
            requette = "INSERT INTO Arret VALUES ("
            requette += "\'" + str(id_insert) + "\'"
            requette += ", \'" + machine + "\'"
            requette += ", \'" + ShopOrder + "\'"
            requette += ", \'" + type_arret + "\'"
            requette += ", \'" + operateur + "\'"
            requette += ", \'" + declaration + "\'"
            requette += ", \'" + str(Debut_declaration)[0:23] + "\'"
            requette += ", \'" + str(Debut_Arret)[0:23] + "\'"
            requette += ", \'" + str(Fin_Arret)[0:23] + "\'"
            requette += ", \'" + time.strftime('%H:%M:%S', time.gmtime(
                int((Debut_Arret - Debut_declaration).total_seconds()))) + "\'"
            requette += ", \'" + time.strftime('%H:%M:%S',
                                               time.gmtime(int((Fin_Arret - Debut_Arret).total_seconds()))) + "\'"
            requette += ", \'" + codeArret1 + "\'"
            requette += ", \'" + codeArret2 + "\'"
            requette += ", \'" + codeArret3 + "\'"
            requette += ", \'" + codeArret4 + "\'"
            requette += ", \'" + codeArret5 + "\'"
            requette += ")"
            print (requette)
            self.temps_arret_totale += int((Fin_Arret - Debut_declaration).total_seconds())

            cursor.execute(requette)
            conn.commit()
            return id_insert
        except:
            print('probleme connexion')

    #########################################################"
    # insertion tool number
    def insert_kpi(self, machine, date, shopordre, quantite_bon, quantite_rejet, temps_cycle_t, temps_cycle_m,
                   temps_arrets, TRS):
        try:

            conn = pymssql.connect(self.host, self.username, self.password, self.database)
            cursor = conn.cursor()
            cursor.execute("select count(id) from KPI")
            result = cursor.fetchall()
            id_insert = result[0][0] + 1

            requette = "INSERT INTO KPI VALUES ("
            requette += "\'" + str(id_insert) + "\'"
            requette += ", \'" + machine + "\'"
            requette += ", \'" + str(datetime.now())[0:19] + "\'"
            requette += ", \'" + shopordre + "\'"
            requette += ", \'" + str(quantite_bon) + "\'"
            requette += ", \'" + str(quantite_rejet) + "\'"
            requette += ", \'" + str(temps_cycle_t) + "\'"
            requette += ", \'" + str(temps_cycle_m) + "\'"
            requette += ", \'" + str(temps_arrets) + "\'"
            requette += ", \'" + str(TRS) + "\'"
            requette += ")"
            print(requette)
            cursor.execute(requette)
            conn.commit()
            return id_insert
        except:
            print('problem connexion serveur')

    def update_production(self, machine, type_notification, notificationID):

        if type_notification == 'cycle_time':
            notification = 'cycle_time'
            notificationValue = notificationID

        elif type_notification == 'TRS':
            notification = 'TRS'
            notificationValue = notificationID
        elif type_notification == 'temps':
            notification = 'temps'
            notificationValue = notificationID
        elif type_notification == 'Etat':
            notification = 'Etat'
            notificationValue = notificationID

        elif type_notification == 'Arrets':
            notification = 'Arrets'
            notificationValue = notificationID
        elif type_notification == 'shopordre':
            notification = 'shopordre'
            notificationValue = notificationID
        elif type_notification == 'quantite_produite':
            notification = 'quantite_produite'
            notificationValue = notificationID
        elif type_notification == 'quantite_planifier':
            notification = 'quantite_planifier'
            notificationValue = notificationID
        elif type_notification == 'debut_shop':
            notification = 'debut_shop'
            notificationValue = notificationID
        elif type_notification == 'quantite_rejet':
            notification = 'quantite_rejet'
            notificationValue = notificationID
        try:
            conn = pymssql.connect(self.host, self.username, self.password, self.database)
            cursor = conn.cursor()

            requette = "UPDATE ProductionM_Arburg SET  "
            requette += notification + " = "
            requette += "\'" + notificationValue + "\'"
            requette += "  where machine = "
            requette += "\'" + machine + "\'"
            print(requette)

            cursor.execute(requette)
            conn.commit()
        except:
            print('probleme connexion')


# Class Main
class moulding(App):

    def build(self):
        application = Manager()
        return application

    def on_pause(self):
        return True


if __name__ == '__main__':
    moulding().run()
