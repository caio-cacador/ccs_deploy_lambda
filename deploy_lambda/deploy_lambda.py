from boto3 import Session
import os
import shutil
import tempfile
import zipfile


def _zip_dir(path, destiny_path):
    zipf = zipfile.ZipFile(destiny_path, 'w')
    for root, dirs, files in os.walk(path):
        for file in files:
            fp = os.path.join(root, file)
            if not os.path.isfile(fp):
                continue
            arc = os.path.join(root.replace(path, ''),
                               os.path.basename(file))
            zipf.write(fp, arcname=arc)
    zipf.close()


def _list_files(path, ignore_list=None, ignore_hidden=True):
    if not ignore_hidden:
        ignore_list = ["__pycache__", "pip"]
    ret = []
    for item in os.listdir(path):
        if ignore_hidden and item.startswith("."):
            continue
        if item in ignore_list:
            continue
        item = os.path.join(path, item)
        if os.path.isdir(item):
            ret.extend(_list_files(item))
        else:
            ret.append(item)
    return ret


def _copy_files(src, dst):
    file_list = _list_files(src)
    for file_ in file_list:
        dst_file_path = os.path.join(dst, file_[len(src)+1:])
        if not os.path.exists(os.path.dirname(dst_file_path)):
            os.makedirs(os.path.dirname(dst_file_path))
        shutil.copy(file_, dst_file_path)


def _print(verbose, str_):
    if verbose:
        print(str_)


def deploy(function_name: str, bucket_name: str, aws_session: Session, code_path: str = None, verbose: bool = True):
    if not code_path:
        code_path = os.path.dirname(os.path.abspath(__file__))
        print(code_path)

    _print(verbose, '+ Zipping files ...')
    destiny_zip_path = os.path.join(tempfile.gettempdir(), "%s.zip" % function_name)
    print('destiny_zip_path: ', destiny_zip_path)
    tmp_dir = tempfile.mkdtemp()
    try:
        _copy_files(src=code_path, dst=tmp_dir)
        if os.path.exists(destiny_zip_path):
            os.remove(destiny_zip_path)
        _zip_dir(tmp_dir, destiny_zip_path)
    except Exception as ex:
        print('Error while zipping files: {}'. format(ex))
        from sys import exit
        exit()
    finally:
        shutil.rmtree(tmp_dir)
    _print(verbose, '- Done!')

    _print(verbose, "+ Sending zip to s3 ...")
    s3 = aws_session.resource('s3')
    s3_file_name = '%s.zip' % function_name
    s3.Bucket(bucket_name).put_object(Key=s3_file_name, Body=open(destiny_zip_path, 'rb'))
    _print(verbose, '- Done!')

    _print(verbose, "+ Updating lambda code ...")
    lambda_ = aws_session.client('lambda')
    lambda_.update_function_code(FunctionName=function_name,
                                 S3Bucket=bucket_name,
                                 S3Key=s3_file_name,
                                 Publish=True)
    _print(verbose, '- Done!')
