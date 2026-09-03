import shutil
import os
import csv

all_genres = ['Electronic', 'Experimental', 'Folk', 'Hip-Hop', 'Instrumental', 'International', 'Pop', 'Rock']

def main():
    root_dir = '/mnt/f/Code/Music_Dataset/'
    concepts_dir = '/fourth_concepts/'

    all_results = []
    for g in all_genres:
        tcav_dir = f'{root_dir}{concepts_dir}concepts_{g}/results_summaries/ace_results.txt'
        with open(tcav_dir, 'r') as f:
            # for line in f:
            #     # if line == '\n':
            #     #     continue
            #     all_results.extend(line)
            all_results.extend(list(f))

    final_data = []
    for line in all_results:
        if line.startswith('layer'):
            concept = line.split(':')[1]
            tcav_score = round(float(line.split(',')[0].split(':')[-1]), 2)
            final_data.append((concept,tcav_score))

    dest_dir = '/mnt/f/Code/Thesis/why-pop/data/concepts_data.csv'
    with open(dest_dir, 'w') as f:
        csv_out = csv.writer(f)
        csv_out.writerow(('concept_name', 'tcav_score'))
        for row in final_data:
            csv_out.writerow(row)
    
    

if __name__=='__main__':
    main()

