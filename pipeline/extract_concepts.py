import argparse
import sys
from ace_run import main as cd
import os
import shutil

def parse_arguments(argv):
  """Parses the arguments passed to the run.py script."""
  parser = argparse.ArgumentParser()
  parser.add_argument('--source_dir', type=str,
      help='''Directory where the network's classes image folders and random
      concept folders are saved.''', default='./ImageNet')
  parser.add_argument('--working_dir', type=str,
      help='Directory to save the results.', default='./ACE')
  parser.add_argument('--model_to_run', type=str,
      help='The name of the model.', default='GoogleNet')
  parser.add_argument('--model_path', type=str,
      help='Path to model checkpoints.', default='./tensorflow_inception_graph.pb')
  parser.add_argument('--labels_path', type=str,
      help='Path to model checkpoints.', default='./imagenet_labels.txt')
  parser.add_argument('--target_class', type=str,
      help='The name of the target class to be interpreted', default='zebra')
  parser.add_argument('--bottlenecks', type=str,
      help='Names of the target layers of the network (comma separated)',
                      default='mixed4c')
  parser.add_argument('--num_random_exp', type=int,
      help="Number of random experiments used for statistical testing, etc",
                      default=20)
  parser.add_argument('--max_imgs', type=int,
      help="Maximum number of images in a discovered concept",
                      default=40)
  parser.add_argument('--min_imgs', type=int,
      help="Minimum number of images in a discovered concept",
                      default=40)
  parser.add_argument('--num_parallel_workers', type=int,
      help="Number of parallel jobs.",
                      default=0)
  return parser.parse_args(argv)
    
def main(args):
    print('Working dir: ', args.working_dir)
    target_classes = ['Electronic', 'Experimental', 'Folk', 'Hip-Hop', 'Instrumental', 'International', 'Pop', 'Rock']
    for t in target_classes:
        print('Extracting concepts for class: ', t)
        # os.chdir(args.working_dir)
        args.target_class = t
        cd(args)
        script_dir = os.getcwd()
        # print('Current working dir: ', os.getcwd())
        os.chdir(os.path.join(args.working_dir, '..'))
        old_concepts_dir = os.path.join(os.getcwd(), 'concepts')
        new_concept_dir = os.path.join(os.getcwd(), f'concepts_{t}')
        if os.path.isdir(new_concept_dir):
            shutil.rmtree(new_concept_dir)
        # os.makedirs(new_concept_dir)
        shutil.move(old_concepts_dir, new_concept_dir)
        os.chdir(script_dir)

if __name__ == '__main__':
    main(parse_arguments(sys.argv[1:]))
