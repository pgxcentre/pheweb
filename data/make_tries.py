#!/usr/bin/env python2

from __future__ import print_function, division, absolute_import

# Load config, utils, venv
import os.path
import imp
my_dir = os.path.dirname(os.path.abspath(__file__))
utils = imp.load_source('utils', os.path.join(my_dir, '../utils.py'))
conf = utils.conf
utils.activate_virtualenv()

import marisa_trie

def parse_line(line):
    chrom, pos, ref, alt, rsid, genes = line.rstrip('\n').split('\t')
    # Keys in marisa_trie must be unicode. Values in BytesTrie must be bytes.
    return (u'{}-{}-{}-{}'.format(chrom, pos, ref, alt), rsid)


sites_fname = os.path.join(conf.data_dir, 'sites', 'sites.tsv')
cpra_to_rsids_trie_fname = os.path.join(conf.data_dir, 'sites', 'cpra_to_rsids_trie.marisa')
rsid_to_cpra_trie_fname = os.path.join(conf.data_dir, 'sites', 'rsid_to_cpra_trie.marisa')
def should_replace(fname):
    return not os.path.exists(fname) or os.stat(fname).st_mtime < os.stat(sites_fname).st_mtime

def run(argv):

    should_replace = should_replace(cpra_to_rsids_trie_fname) or should_replace(rsid_to_cpra_trie_fname)

    if not should_replace:
        print('tries are up-to-date!')

    else:
        with open(conf.data_dir + '/sites/sites.tsv') as f:
            lines = [parse_line(line) for line in f]
        print('done loading.')


        cpra_to_rsids_trie = marisa_trie.BytesTrie(lines, order=marisa_trie.LABEL_ORDER)
        cpra_to_rsids_trie.save(cpra_to_rsids_trie_fname)
        print('done with cpra->rsids trie at ' + cpra_to_rsids_trie_fname)

        # TODO: What if several different chrom-pos-ref-alts have the same rsid?  Do we only get the first? Or the last?
        reversed_lines = ((rsid.decode('ascii'), cpra.encode('ascii')) for (cpra, rsids) in lines for rsid in rsids.split(','))
        rsid_to_cpra_trie = marisa_trie.BytesTrie(reversed_lines, order=marisa_trie.LABEL_ORDER)
        rsid_to_cpra_trie.save(rsid_to_cpra_trie_fname)
        print('done with rsid->cpra trie at ' + rsid_to_cpra_trie_fname)


if __name__ == '__main__':
    run([])
