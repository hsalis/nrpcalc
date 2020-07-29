import os

import pkg_resources

from Bio import SeqIO

import RNA

complement_table = str.maketrans('ATGCU', 'TACGA')

def stream_fasta_seq_list(fasta_filename):
    with open(fasta_filename, "rU") as handle:
        for record in SeqIO.parse(handle, "fasta"):
            yield str(record.seq)

def get_fasta_seq_list(fasta_filename):
    return list(stream_fasta_seq_list(fasta_filename))

def stream_txt_seq_list(text_filename):
    with open(text_filename) as infile:
        for line in infile:
            yield line.strip()

def get_txt_seq_list(text_filename):
    return list(stream_txt_seq_list(text_filename))

def uniquify_background_list(background_list):
    uniq_background_set = set()
    while background_list:
        uniq_background_set.add(background_list.pop())
    background_list = []
    while uniq_background_set:
        background_list.append(uniq_background_set.pop())
    return background_list

def stream_kmers(seq, k):
    if k >= len(seq):
        return [seq]
    return (seq[i:i+k] for i in range(len(seq)-k+1))

def get_comp(seq):
    return seq.translate(complement_table)

def get_revcomp(seq):
    return get_comp(seq)[::-1]

def stream_min_kmers(seq, k):
    for kmer in stream_kmers(seq, k):
        yield min(kmer, get_revcomp(kmer))

class Fold(object):

    def __init__(
        self,
        temp=37.0,
        dangles=2,
        part_type='RNA'):
        self.parameter_directory = os.path.dirname(
            os.path.abspath(__file__))#"/usr/local/share/ViennaRNA/"
        # Temperature in Celsius;
        # default=37.0 (float)
        RNA.cvar.temperature = temp
        # Dangling end energies (0,1,2);
        # see RNAlib documentation;
        # default=2 (int)
        RNA.cvar.dangles = dangles
        self.settings    = RNA.md("globals")

        if not part_type in ['RNA', 'DNA']:
            part_type = 'RNA'

        self.part_type = part_type
        
        parameter_file = pkg_resources.resource_filename(
            'nrpcalc', 'base/{}.par'.format(
                self.part_type))
        RNA.read_parameter_file(parameter_file)

    def evaluate_mfe(self, seq):
        # MFE Only
        struct = RNA.fold(seq)[0]
        return struct

    def evaluate_centroid(self, seq):
        # Centroid Only
        fc_obj = RNA.fold_compound(seq, self.settings)
        fc_obj.pf()
        struct = fc_obj.centroid()[0]
        return struct

    def design(self, seq, struct):
        inv = RNA.inverse_fold(seq, struct)[0]
        if self.part_type == 'DNA':
            inv = inv.replace('U', 'T').replace('u', 't')
        return inv

if __name__ == '__main__':
    pass