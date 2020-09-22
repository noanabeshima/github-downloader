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
from joblib import Parallel, delayed

from tqdm import tqdm

mime = magic.Magic(mime=True)


def id(x):
    return x

def nonzero(x):
    return filter(id, x)

def is_digit(x):
    return x in "1234567890"

def keep(x):
    num_digits = len(list(filter(is_digit, x)))
    num_newlines = len(list(filter(lambda x: x == '\n', x)))
    if num_digits / len(x) > 0.8:
        return False
    
    # avg line length
    if len(x) / (num_newlines+.001) > 200:
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

def process_repo_list(repo_data, archive_name='github_data'):
    ar = lmd.Archive(archive_name)

    for i, repo in enumerate(tqdm(repo_data)):
        name, stars, lang = repo
        meta = {'repo_name':name, 'stars':stars, 'repo_language':lang}
        repodir = f'./.tmp/{name.split("/")[-1]}'
        os.system(f'git clone --depth 1 --single-branch https://github.com/{name} {repodir}')
        shutil.rmtree(f'{repodir}/.git', ignore_errors=True)

        
        for curdir, dirs, files in os.walk(repodir):
            
            files = [curdir + '/' + f for f in files if '.git' not in f and f[0] is not '.' and 'LICENSE' not in f and f.split('.')[-1] not in ['rkt', 'ss', 'csv', 'tsv', ]]

            filenames = [f.split("/")[-1] for f in files]
            extensions = [mime.from_file(f) for f in files]
            text_outputs = list(map(get_content, files))
            for i in range(len(files)):
                text = text_outputs[i]
                if text is not None:
                    meta['file_name'] = filenames[i]
                    meta['mime_type'] = extensions[i]

                    ar.add_data(text, meta)

        shutil.rmtree(repodir, ignore_errors=True)
        if (i + 1) % 100 == 0:
            ar.commit()

    ar.commit()


if __name__ == '__main__':
    if '.tmp' not in os.listdir():
        os.makedirs('.tmp')
    if 'github_data' not in os.listdir():
        os.makedirs('github_data')

    with open('github_repositories.csv', 'r') as f:
        csv_reader = csv.reader(f)
        repo_data = list(map(tuple, csv_reader))

    repo_data.sort()
    random.seed(42)
    random.shuffle(repo_data)

    n_threads = 15
    assert n_threads != 0
    chunk_size = int(len(repo_data)/n_threads)

    repo_chunks = [None for _ in range(n_threads)]
    for i in range(n_threads-1):
        repo_chunks[i] = repo_data[i*chunk_size:(i+1)*chunk_size]
    repo_chunks[-1] = repo_data[(n_threads-1)*chunk_size:]


    Parallel(n_jobs=n_threads, prefer="threads")(
        delayed(process_repo_list)(chunk) for chunk in repo_chunks
        )