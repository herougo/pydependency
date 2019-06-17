import argparse
from pydependency.dependency_finder import DependencyFinder
from pydependency.utils import get_repo_path


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('repo_path')
    args = parser.parse_args()
    return (args.repo_path,)

if __name__ == '__main__':
    repo_path = get_args()[0]
    print('Loading existing dependency finder')
    df = DependencyFinder()
    print('Processing repo: {}'.format(repo_path))
    if df.add_repo(get_repo_path(repo_path)):
        print('Finished')
    else:
        print('Already exists (did nothing)')
    print('Done!')
