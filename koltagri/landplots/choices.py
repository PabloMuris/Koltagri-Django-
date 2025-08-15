from django.db import models

class KoppenClimate(models.TextChoices):
    # A - Tropical
    AF = "Af", "Tropical - Floresta tropical (Af)"
    AM = "Am", "Tropical - Monçônico (Am)"
    AW = "Aw", "Tropical - Savana com inverno seco (Aw)"
    AS = "As", "Tropical - Savana com verão seco (As)"
    
    # B - Árido
    BWH = "BWh", "Desértico - Quente (BWh)"
    BWK = "BWk", "Desértico - Frio (BWk)"
    BSH = "BSh", "Semiárido - Quente (BSh)"
    BSK = "BSk", "Semiárido - Frio (BSk)"
    
    # C - Temperado
    CSA = "Csa", "Temperado - Mediterrâneo quente (Csa)"
    CSB = "Csb", "Temperado - Mediterrâneo frio (Csb)"
    CSC = "Csc", "Temperado - Mediterrâneo muito frio (Csc)"
    CFA = "Cfa", "Temperado - Subtropical úmido (Cfa)"
    CFB = "Cfb", "Temperado - Oceânico (Cfb)"
    CFC = "Cfc", "Temperado - Oceânico frio (Cfc)"
    
    # D - Continental
    DSA = "Dsa", "Continental - Verão quente, seco (Dsa)"
    DSB = "Dsb", "Continental - Verão ameno, seco (Dsb)"
    DSC = "Dsc", "Continental - Verão curto, seco (Dsc)"
    DSD = "Dsd", "Continental - Invernos rigorosos, seco (Dsd)"
    DFA = "Dfa", "Continental - Verão quente (Dfa)"
    DFB = "Dfb", "Continental - Verão ameno (Dfb)"
    DFC = "Dfc", "Continental - Subártico (Dfc)"
    DFD = "Dfd", "Continental - Invernos extremos (Dfd)"
    
    # E - Polar
    ET = "ET", "Polar - Tundra (ET)"
    EF = "EF", "Polar - Geleiras eternas (EF)"
