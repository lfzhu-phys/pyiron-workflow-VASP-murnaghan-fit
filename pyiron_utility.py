#!/usr/bin/env python

import numpy as np

def create_job_name(alat):
    alat_str = str(round(alat,2)).replace('.', '_')
    return f'ham_{alat_str}Ang'

def run_EOS_vasp_jobs(project_parameter):
    pr = project_parameter['project']
    bulk = pr.create.structure.bulk(project_parameter['element'], cubic=True)
    a_eq = bulk.cell[0,0]
    alat_lst = np.linspace(a_eq-project_parameter['shift'],a_eq+project_parameter['shift'],project_parameter['npoints'])
    for alat in alat_lst:
        basis = pr.create.structure.crystal(element=project_parameter['element'], bravais_basis=project_parameter['crystal_structure'], lattice_constant=alat)
        print(create_job_name(alat))
        ham_EOS = pr.create.job.Vasp(create_job_name(alat))
        ham_EOS.structure = basis.repeat(project_parameter['supercell'])
        ham_EOS.input.potcar['xc'] = project_parameter['xc']
        ham_EOS.set_kpoints(mesh=[project_parameter['kmesh'],project_parameter['kmesh'],project_parameter['kmesh']], scheme='MP')
        ham_EOS.set_encut(project_parameter['encut'])
        ham_EOS.set_occupancy_smearing(ismear=project_parameter['ismear'], width=project_parameter['sigma'])
        ham_EOS.set_convergence_precision(electronic_energy=project_parameter['EDIFF'])
        ham_EOS.input.incar['PREC'] = project_parameter['PREC']
        ham_EOS.server.queue = project_parameter['cluster']
        ham_EOS.server.cores = project_parameter['cpu_cores']
        ham_EOS.run()

def print_job_status(project_parameter):
    pr = project_parameter['project']
    print("Total number of jobs is %d." % (len(pr.job_table())))
    print("Finished jobs is %d." % (len(pr.job_table(status='finished'))))
    print("Submitted jobs is %d." % (len(pr.job_table(status='submitted'))))
    print("Running jobs is %d." % (len(pr.job_table(status='running'))))
    print("Aborted jobs is %d." % (len(pr.job_table(status='aborted'))))


def print_cpu_time(project_parameter):
    df = project_parameter['project'].job_table(all_columns=True)
    print("For current project {} cores are used for calculations.".format(project_parameter['cpu_cores']))
    print("The shortest CPU time of finished jobs is %.4f in hours." % (np.min(df[df['status']=='finished']['totalcputime'].values)/60/60))
    print("The longest CPU time of finished jobs is %.4f in hours." % (np.max(df[df['status']=='finished']['totalcputime'].values)/60/60))
    print("The average CPU time of finished jobs is %.4f in hours." % (np.mean(df[df['status']=='finished']['totalcputime'].values)/60/60))


