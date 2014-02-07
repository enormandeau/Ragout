#!/usr/bin/env python

from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
import os, sys
import subprocess
from collections import namedtuple

Block = namedtuple("Block", ["id", "start", "length", "chr_id"])
SeqInfo = namedtuple("SeqInfo", ["id", "length"])


def main():
    coords_file = sys.argv[1]
    fasta = sys.argv[2:]
    blocks = parse_coords_file(coords_file)
    draw_dot_plot(blocks, fasta, "dot")


def draw_dot_plot(blocks, seq_files, out_dir):
    seqs = {}
    for file in seq_files:
        seq = SeqIO.parse(file, "fasta").next()
        seqs[seq.id] = seq.seq

    #for seq_id, blocks in permutations.iteritems():
    #    for block in blocks:
    #        by_block[abs(block.id)].append((block, seq_id))

    out_dir = os.path.abspath(out_dir)
    DIR = "/home/volrath/Bioinf/Tools/gepard-1.30/"
    os.chdir(DIR)
    EXEC = "./gepardcmd.sh"
    MATRIX = "matrices/blosum62.mat"

    for block_id, blocklist in blocks.iteritems():
        #print blocklist[1:3]
        block1, block2 = blocklist[0:2]

        s1 = seqs[block1.chr_id]
        s2 = seqs[block2.chr_id]
        if block1.id < 0:
            s1 = s1.reverse_complement()
        if block2.id < 0:
            s2 = s2.reverse_complement()

        seq1 = s1[block1.start : block1.start + block1.length]
        seq2 = s2[block2.start : block2.start + block2.length]

        file1 = os.path.join(out_dir, "block1.fasta")
        file2 = os.path.join(out_dir, "block2.fasta")

        SeqIO.write(SeqRecord(seq1), file1, "fasta")
        SeqIO.write(SeqRecord(seq2), file2, "fasta")

        out_dot = os.path.join(out_dir, "block{0}-{1}-{2}.png".
                                                    format(block_id, block1.chr_id, block2.chr_id))

        cmdline = [EXEC, "-seq1", file1, "-seq2", file2, "-outfile", out_dot, "-matrix", MATRIX, "-word", "20"]
        subprocess.check_call(cmdline)

        os.remove(file1)
        os.remove(file2)


def parse_coords_file(blocks_file):
    group = [[]]
    seq_info = {}
    blocks_info = {}
    line = [l.strip() for l in open(blocks_file) if l.strip()]
    for l in line:
        if l.startswith("-"):
            group.append([])
        else:
            group[-1].append(l)
    for l in group[0][1:]:
        seq_num, seq_len, seq_id = l.split()
        seq_num = int(seq_num)
        seq_info[seq_num] = SeqInfo(seq_id, int(seq_len))
    for g in [g for g in group[1:] if g]:
        block_id = int(g[0].split()[1][1:])
        blocks_info[block_id] = []
        for l in g[2:]:
            chr_num, bl_strand, bl_start, bl_end, bl_length = l.split()
            chr_num = int(chr_num)
            chr_id = seq_info[chr_num].id

            num_id = block_id if bl_strand == "+" else -block_id
            blocks_info[block_id].append(Block(num_id, int(bl_start), int(bl_length), chr_id))
    return blocks_info

if __name__ == "__main__":
    main()
