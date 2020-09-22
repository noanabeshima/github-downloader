import chardet
import magic
import lm_dataformat as lmd
import os
import random
import sys
import traceback
import time
import shutil
import csv
from multiprocessing import cpu_count, Pool
from tqdm import tqdm
import argparse


mime = magic.Magic(mime=True)

def split_into_chunks(l, n):
    n = max(1, n)
    return [l[i:i + n] for i in range(0, len(l), n)]

def is_digit(x):
    return x in "1234567890"


def keep(x):
    num_digits = len(list(filter(is_digit, x)))
    num_newlines = len(list(filter(lambda x: x == '\n', x)))
    if num_digits / len(x) > 0.8:
        return False

    # avg line length
    if len(x) / (num_newlines + .001) > 200:
        return False

    return True


def get_content(f):
    type = None
    try:
        enc = 'utf-8'
        type = mime.from_file(f)
        if not type.startswith('text'):
            return
        with open(f, 'rb') as fromfh:
            buf = fromfh.read()

        buf = buf.decode('UTF-8')
        if not keep(buf):
            return

        return buf
    except UnicodeDecodeError:
        # bad encoding, try different encoding
        try:
            enc = None
            enc = chardet.detect(buf)
            if enc['encoding'] is None:
                return
            buf = buf.decode(enc['encoding'])
            if not keep(buf):
                return
            return buf
        except UnicodeDecodeError:
            return
        except:
            traceback.print_exc()
            time.sleep(0.1)
            return
    except KeyboardInterrupt:
        sys.exit()
    except FileNotFoundError:
        # bad symlink
        import os.path
        if not os.path.islink(f):
            # something went horribly wrong!
            ...
    except:
        print(type, f, enc)
        traceback.print_exc()
        time.sleep(0.1)
        return


def process_repo_list(repo_data):
    out = None
    try:
        name, stars, lang = repo_data
        meta = {'repo_name': name, 'stars': stars, 'repo_language': lang}
        repodir = f'./.tmp/{name.split("/")[-1]}'
        os.system(f'git clone --depth 1 --single-branch https://github.com/{name} {repodir}')
        shutil.rmtree(f'{repodir}/.git', ignore_errors=True)
        for curdir, dirs, files in os.walk(repodir):
            bad_extensions = [
                'app',
                'bin',
                'bmp',
                'bz2',
                'class',
                'csv',
                'dat',
                'db',
                'dll',
                'dylib',
                'egg',
                'eot',
                'exe',
                'gif',
                'gitignore',
                'glif',
                'gradle',
                'gz',
                'ico',
                'jar',
                'jpeg',
                'jpg',
                'lo',
                'lock',
                'log',
                'mp3',
                'mp4',
                'nar',
                'o',
                'ogg',
                'otf',
                'p',
                'pdf',
                'png',
                'pickle',
                'pkl',
                'pyc',
                'pyd',
                'pyo',
                'rkt',
                'so',
                'ss',
                'svg',
                'tar',
                'tsv',
                'ttf',
                'war',
                'webm',
                'woff',
                'woff2',
                'xz',
                'zip',
                'zst'
            ]

            files = [curdir + '/' + f for f in files if '.git' not in f and f[
                0] is not '.' and 'LICENSE' not in f and 'node_modules' not in f and '.min.' not in f and f.split('.')[
                         -1] not in bad_extensions]

            filenames = [f.split("/")[-1] for f in files]
            extensions = [mime.from_file(f) for f in files]
            text_outputs = list(map(get_content, files))
            for i in range(len(files)):
                text = text_outputs[i]
                if text is not None:
                    meta['file_name'] = filenames[i]
                    meta['mime_type'] = extensions[i]

                    out = [text, meta]
        shutil.rmtree(repodir, ignore_errors=True)
    except:
        traceback.print_exc()
    return out

def process_args():
    parser = argparse.ArgumentParser(
        description='CLI for github downloader - A tool for scraping repos as text from github')
    parser.add_argument('--n_threads', help='number of threads for parallel processing, defaults to cpu_count',
                        default=0,
                        type=int)
    parser.add_argument('--n_stars', help='filter repos with less than n_stars stars',
                        default=-1,
                        type=int)
    parser.add_argument('--chunk_size', help='size of chunks to feed into each thread',
                        default=100,
                        type=int)
    return parser.parse_args()


def filter_by_stars(repo_data, n_stars):
    return [item for item in repo_data if int(item[1]) >= n_stars]


if __name__ == '__main__':

    args = process_args() # parse args

    # make output dirs
    if '.tmp' not in os.listdir():
        os.makedirs('.tmp')
    if 'github_data' not in os.listdir():
        os.makedirs('github_data')

    # read repo data to a tuple (reponame, n_stars, language)
    with open('github_repositories.csv', 'r') as f:
        csv_reader = csv.reader(f)
        repo_data = list(map(tuple, csv_reader))

    # filter by number of stars
    if args.n_stars != -1:
        repo_data = filter_by_stars(repo_data, args.n_stars)
    repo_data.sort()

    random.seed(420)
    random.shuffle(repo_data)

    n_threads = cpu_count() * 3 if args.n_threads == 0 else args.n_threads
    assert n_threads != 0

    # do work
    repo_chunks = split_into_chunks(repo_data, args.chunk_size)
    archive_name = 'github_data'
    ar = lmd.Archive(archive_name)
    pool = Pool(n_threads)
    pbar = tqdm(repo_chunks, total=len(repo_chunks), unit_scale=args.chunk_size)
    commit_every = 10
    for count, chunk in enumerate(pbar):
        repos_out = pool.map(process_repo_list, chunk)
        for r in repos_out:
            if r is not None:
                ar.add_data(r[0], meta=r[1])
        if count % commit_every == 0:
            ar.commit()
