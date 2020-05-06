#!/usr/bin/env python

"""
########################################################################
# Author:       Carlos A. Ruiz Perez
# Email:        cruizperez3@gatech.edu
# Github:       https://github.com/cruizperez
# Institution:   Georgia Institute of Technology
# Version:      0.9
# Date:         March 16, 2020

# Description: This script parses a table with protein IDs and searches
# these IDs in a SQL database to extract protein annotations.
# You can also include a column with the ids of your proteins (queries)
# so they will be included in the output (use query_col [int]).
########################################################################
"""
################################################################################
"""---0.0 Import Modules---"""
import sqlite3
import argparse, sys

################################################################################
"""---1.0 Define Functions---"""


def search_table(sql_database, database_table, input_list, outfile):
    """ Searches a table in a SQLite3 database and extracts the target_id annotation.
    
    Arguments:
        sql_database {string} -- SQLite3 database to use for searching.
        database_table {string} -- Table within SQLite3 database to search.
        input_list {list} -- List with (query_ids and target_ids) or just target_ids.
        
        outfile {string} -- File to write output
    """ 
    conn = sqlite3.connect(sql_database)
    cur = conn.cursor()
    if isinstance(input_list[0], tuple):
        query_present = True
    else:
        query_present = False
    # Check which columns to use for output
    if database_table == "swissprot" or database_table == "trembl":
        if query_present:
            col_names = ['#Query_ID' 'Target_ID', 'Accession', 'Name', 'KO_Uniprot', 'Organism', 'Taxonomy',
                        'Function', 'Compartment', 'Process']
        else:
            col_names = ['#Target_ID', 'Accession', 'Name', 'KO_Uniprot', 'Organism', 'Taxonomy',
                        'Function', 'Compartment', 'Process']
    elif database_table == "refseq":
        if query_present:
            col_names = ['#Query_ID', 'Target_ID', 'Gene_Name', 'Taxonomy', 'Note']
        else:
            col_names = ['#Target_ID', 'Gene_Name', 'Taxonomy', 'Note']
    # Search the DB and append results to Annotation_List
    with open(outfile, 'w') as output:
        output.write("{}\n".format("\t".join(col_names)))
        if query_present:
            for gene_id in (input_list):
                cur.execute("SELECT * FROM " + database_table + " WHERE ID=?", (gene_id[1],))
                rows = cur.fetchall()
                if len(rows) > 0:
                    annotation = "\t".join(rows[0])
                    output.write("{}\t{}\n".format(gene_id[0], annotation))
                else:
                    continue
        else:
            for gene_id in (input_list):
                cur.execute("SELECT * FROM " + database_table + " WHERE ID=?", (gene_id,))
                rows = cur.fetchall()
                if len(rows) > 0:
                    annotation = "\t".join(rows[0])
                    output.write("{}\n".format(annotation))
                else:
                    continue
    cur.close()
    conn.close()

def parse_input_table(input_file, query_col, target_col, table):
    """ Parses input file and returns query_ids and target_ids or just target_ids.
    
    Arguments:
        input_file {string} -- Tab-separated input file with blast results or just target ids.
        query_col {int} -- Column with query ids.
        target_col {int} -- Column with target ids.
    
    Returns:
        [list] -- List of (query_ids and target_ids) or just target_ids.
    """
    input_list = []
    with open(input_file, 'r') as infile:
        if table == "swissprot" or table  == "trembl":
            for line in infile:
                line = line.strip().split("\t")
                db_hit = line[target_col].split("|")[2]
                if query_col is not None:
                    input_query = line[query_col]
                    input_list.append((input_query, db_hit))
                else:
                    input_list.append(db_hit)
        else:
            for line in infile:
                line = line.strip().split("\t")
                db_hit = line[target_col]
                if query_col is not None:
                    input_query = line[query_col]
                    input_list.append((input_query, db_hit))
                else:
                    input_list.append(db_hit)
    return input_list

################################################################################
"""---3.0 Main Function---"""

def main():
    # Description: 
# 
# 
# 
    # Setup parser for arguments.
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
            description='''This script parses a table with protein IDs and searches\n'''
            '''these IDs in a SQL database to extract protein annotations.\n'''
            '''You can also include a column with the ids of your proteins (queries)\n'''
            '''so they will be included in the output (use query_col [int]).\n'''
            '''Usage: ''' + sys.argv[0] + ''' -i [Input Table] -d [Database Name] -t [Table Name] --query_col [Query Column]\n'''
            '''Global mandatory parameters: -i [Input Table] -d [Database Name] -t [Table Name] --query_col [Query Column]\n'''
            '''Optional Database Parameters: See ''' + sys.argv[0] + ' -h')
    parser.add_argument('-i', '--input', dest='input_file', action='store', required=True,
                        help='Input tab-delimited table to parse, by default assumes no headers are present')
    parser.add_argument('-o', '--output', dest='outfile', action='store', required=True,
                        help='Output tab-delimited table to store annotations')
    parser.add_argument('-d', '--database', dest='database', action='store', required=True,
                        help='SQL database where the annotations are stored')
    parser.add_argument('-t', '--table', dest='table', action='store', required=True,
                        help='Table within SQLite database to search in. Choose between "swissprot", "trembl" or "refseq"')
    parser.add_argument('--target_col', dest='target_col', action='store', required=False, type=int, default=1, 
                        help='Column with ids of database hits (targets) in the input file. By default 1, first column.')
    parser.add_argument('--query_col', dest='query_col', action='store', required=False, type=int,
                        help='Column with query ids in the input file, by default None, i.e. assumes only target ids are given.')
    args = parser.parse_args()

    input_file = args.input_file
    outfile = args.outfile
    database = args.database
    table = args.table.lower()
    target_col = args.target_col - 1
    query_col = args.query_col
    if query_col != None:
        query_col = query_col - 1

    # Read input table and extract ids.
    input_list = parse_input_table(input_file, query_col, target_col, table)
    search_table(database, table, input_list, outfile)

if __name__ == "__main__":
    main()
