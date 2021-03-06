#!/usr/bin/env python
# coding: utf-8

MILES = 'v0.6 v0.7 v0.8 v0.9 v1.0'.split()

#FMT_CAB = '     %(cab_num)-5s %(cab_descr)-40s'
FMT_CAB = """||'''%(cab_num)s'''||'''%(cab_descr)s'''|| ||"""
#FMT_ATIV = '%(feito)3.f%% %(num)-5s %(descr)-40s'
FMT_ATIV = '||%(num)s||%(descr)s||%(feito).f%%||'


def valor(s):
    try:
        return int(s)
    except ValueError:
        return 0

for off_mil, milestone in enumerate(MILES):
    print '== %s ==' % milestone

    miolo = False
    arq = open('milestones.txt')
    cabecalhos = []
    for lin in arq:
        lin = lin.rstrip()
        if not lin: continue
        lin = lin.decode('cp1252')
        partes = lin.split('\t')
        if partes[0] == '1':
            miolo = True
        if not miolo: continue 
        miles = []
        # x.y.z |descr| v0.6 | v0.7 | v0.8 | v0.9 | v1.0 | v2.0 |
        num, descr = partes[:2]
        miles[:] = (valor(s) for s in partes[2:2+len(MILES)])
        if len(num) < 5: 
            cabecalhos.append( (num, descr,) )
        if len(miles) > off_mil and miles[off_mil]:
            while cabecalhos:
                cab_num, cab_descr = cabecalhos.pop(0)
                if num.startswith(cab_num) and num != cab_num:
                    print FMT_CAB % locals()
            total = sum(miles)
            feito = sum(miles[:off_mil+1])/float(total)*100
            print FMT_ATIV % locals()

    arq.close()
