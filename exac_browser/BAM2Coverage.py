#!/usr/bin/env python

__author__ = 'jessada'

import sys
import argparse
import tempfile
from os.path import join as join_path
import subprocess


# for creating temp file
from random import choice
from string import ascii_letters

# for parsing into ExAC format
import numpy as np
import numpy.lib.recfunctions as rfn

np.set_printoptions(threshold=np.inf)


def count_depth(bam_list, region, out_file):
    cmd = "samtools depth"
    cmd += " -f " + bam_list
    cmd += " -r " + region
    cmd += " > " + out_file

    print >> sys.stderr, "##INFO executing: " + cmd

    # error handling part might be incomplete
    p = subprocess.Popen(cmd,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         )
    stdout_data, stderr_data = p.communicate()
    print stdout_data
    print >> sys.stderr, stderr_data

def samtools_depth_to_panel_coverage(depth_file, out_file):
    chrom = np.genfromtxt(depth_file,
                          delimiter="\t",
                          dtype="S",
                          )[:,0:1]
    pos = np.genfromtxt(depth_file,
                        delimiter="\t",
                        dtype="S",
                        )[:,1:2]
    depths = np.genfromtxt(depth_file,
                           delimiter="\t",
                           )[:,2:]
    n_samples = float(depths.shape[1])
    print >> sys.stderr, "##INFO number of samples: " + str(int(n_samples))
    merged_arrays = [chrom,
                     pos,
                     np.mean(depths, axis=1),
                     np.median(depths, axis=1),
                     (depths > 1).sum(axis=1)/n_samples,
                     (depths > 5).sum(axis=1)/n_samples,
                     (depths > 10).sum(axis=1)/n_samples,
                     (depths > 15).sum(axis=1)/n_samples,
                     (depths > 20).sum(axis=1)/n_samples,
                     (depths > 25).sum(axis=1)/n_samples,
                     (depths > 30).sum(axis=1)/n_samples,
                     (depths > 50).sum(axis=1)/n_samples,
                     (depths > 100).sum(axis=1)/n_samples,
                     ]
    out_exac = rfn.merge_arrays(merged_arrays,
                                flatten = True,
                                usemask = False,
                                )

    # write calculated coverage to file
    header="#chrom"
    header+="\tpos"
    header+="\tmean"
    header+="\tmedian"
    header+="\t1"
    header+="\t5"
    header+="\t10"
    header+="\t15"
    header+="\t20"
    header+="\t25"
    header+="\t30"
    header+="\t50"
    header+="\t100"
    fmt="%s\t%s\t%.2f\t%.2f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f\t%.4f"
    np.savetxt(out_file,
               out_exac,
               fmt=fmt,
               delimiter="\t",
               header=header,
               comments="",
               )

def main(args):
    # tmp_depth_file is a temp file to keep depth count
    # please feel free to modify its name and location as you like
    tmp_depth_file = join_path(tempfile.mkdtemp(),
                               "tmp_" + ''.join([choice(ascii_letters) for i in range(6)]))       
    count_depth(args.bam_list, args.region, tmp_depth_file)

    panel_coverage_out = "Panel."
    panel_coverage_out += args.region.replace(":", "_").replace("-", "_")
    panel_coverage_out += ".coverage.txt"
    samtools_depth_to_panel_coverage(tmp_depth_file,
                                     join_path(args.out_dir, panel_coverage_out)
                                     )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()


    parser.add_argument('--region', '-r', metavar="CHR:FROM-TO", help='Only report depth in specified region.', required=True)
    parser.add_argument('--bam_list', '-b', metavar="FILE", help='Compute depth at list of positions or regions in specified BAM FILE.', required=True)
    parser.add_argument('--out_dir', '-o', metavar="DIR", help='Output directory.', required=True)
    args = parser.parse_args()
    main(args)
