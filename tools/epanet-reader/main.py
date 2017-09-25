
import numpy as np
import time
import cStringIO
import itertools as it

import epanet_reader as er

def result_compare(path_test, path_ref, comp_args):

    isclose = True
    close = 0
    notclose = 0
    equal = 0
    total = 0
    output = cStringIO.StringIO()
    eps =  np.finfo(float).eps
    
    start = time.time()
    
    test_reader = er.reader(path_test)
    ref_reader = er.reader(path_ref)
    
    for test, ref in it.izip(test_reader, ref_reader):
        total += 1
        if total%100000 == 0:
            print(total)
        
        if test.size != ref.size:
            raise ValueError('Inconsistent lengths')
        
        # Skip results if they are zero or equal
        if np.array_equal(test, ref):
            equal += 1
            continue
        else:
            try:
                np.testing.assert_allclose(test, ref, 1.0e-06, 2*eps)
                close += 1
                
            except AssertionError as ae:
                notclose += 1
                output.write(str(ae))
                output.write('\n\n')
                continue       
        
    stop = time.time()
    
    print(output.getvalue())
    output.close()
    
    print('equal: %d  close: %d  notclose: %d  total: %d  in %f (sec)\n' % 
          (equal, close, notclose, total, (stop - start)))

    if notclose > 0:
        print('%d differences found\n' % notclose)
        isclose = False

    return isclose



from nrtest.testsuite import TestSuite
from nrtest.compare import compare_testsuite, validate_testsuite

def nrtest_compare(path_test, path_ref, (comp_args)): 

    ts_new = TestSuite.read_benchmark(path_test)
    ts_old = TestSuite.read_benchmark(path_ref)

    if not validate_testsuite(ts_new) or not validate_testsuite(ts_old):
        exit(1)

    try:
#        logging.info('Found %i tests' % len(ts_new.tests))
        compatible = compare_testsuite(ts_new, ts_old, comp_args[0], comp_args[1])
    except KeyboardInterrupt:
#        logging.warning('Process interrupted by user')
        compatible = False
#    else:
#        logging.info('Finished')

    # Non-zero exit code indicates failure
    exit(not compatible)

def nrtest_execute(app_path, test_path, output_path):
    import logging
    import glob
    from os import listdir
    from os.path import exists, isfile, isdir, join
    from nrtest.execute import execute_testsuite, validate_testsuite

#    for path in test_path + [app_path]:
#        if not exists(path):
#            logging.error('Could not find path: "%s"' % path)

    test_dirs = glob.glob(test_path)
    test_files = [p for p in test_path if isfile(p)]
    test_files += [p for d in test_dirs for p in glob.glob(d + '*.json')]
#                   if p.endswith('.json')]

    test_files = list(set(test_files))  # remove duplicates

    ts = TestSuite.read_config(app_path, test_files, output_path)

    if not validate_testsuite(ts):
        exit(1)

    try:
        logging.info('Found %i tests' % len(test_files))
        success = execute_testsuite(ts)
        ts.write_manifest()
    except KeyboardInterrupt:
        logging.warning('Process interrupted by user')
        success = False
    else:
        logging.info('Finished')

    # Non-zero exit code indicates failure
    exit(not success)


if __name__ == "__main__":
#    app_path = "apps\\swmm-5.1.11.json"
#    test_path = "tests\\examples\\example1.json"
#    output_path = "benchmarks\\test\\"
#    nrtest_execute(app_path, test_path, output_path)
    
#    test_path = "C:\\Users\\mtryby\\Workspace\\GitRepo\\Local\\epanet-testsuite\\benchmarks\\v2011a"
#    ref_path  = "C:\\Users\\mtryby\\Workspace\\GitRepo\\Local\\epanet-testsuite\\benchmarks\\v2012"
#    print(nrtest_compare(test_path, ref_path, (0.001, 0.0)))

    
    path_test = "C:\\Users\\mtryby\\Workspace\\GitRepo\\Local\\epanet-testsuite\\benchmarks\\v2011a\\Example_3\\example3.out"
    path_ref  = "C:\\Users\\mtryby\\Workspace\\GitRepo\\Local\\epanet-testsuite\\benchmarks\\v2012\\Example_3\\example3.out"    
    result_compare(path_test, path_ref, (0.001, 0.0))
