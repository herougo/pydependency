import argparse
import os
from pydependency.dependency_finder import DependencyFinder
from pydependency.utils import get_repo_path, is_repo_path


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('directory_of_repos')
    args = parser.parse_args()
    return (args.directory_of_repos,)

if __name__ == '__main__':
    directory_of_repos = get_args()[0]
    print('Loading existing dependency finder')
    df = DependencyFinder()
    for repo_path in os.listdir(directory_of_repos):
        if is_repo_path(repo_path):
            print('Processing repo: {}'.format(repo_path))
            if df.add_repo(get_repo_path(repo_path)):
                print('\tFinished')
            else:
                print('\t, Already exists (did nothing)')
    print('Done!')
