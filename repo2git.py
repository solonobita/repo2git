#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import xml.etree.ElementTree as ET
import re

# 处理真正的远程url


def produce_real_repositories(projects: dict, remotes: dict):
    repositories = {}
    for name in projects.keys():
        project = projects[name]
        remote = project.get('remote')
        url = None
        if is_repo_url(remote):
            url = remote + '/' + name + '.git'
        elif remotes.get(remote):
            url = remotes.get(remote) + '/' + name + '.git'
        if not url:
            print('无法找到项目{}的远程下载地址'.format(name))
            return None
        repositories[name] = {
            'name': name,
            'url': url,
            'revision': projects[name].get('revision'),
            'path': projects[name].get('path'),
            'branch': projects[name].get('branch')
        }
    return repositories


def get_repositories(manifest_file_path: str):
    tree = ET.parse(manifest_file_path)
    root = tree.getroot()
    projects = {}
    remotes = {}
    for child in root:
        if child.tag == 'project':
            name = child.attrib['name']
            path = child.attrib['path']
            remote = child.attrib['remote']
            branch = child.attrib.get('upstream', 'master')
            revision = child.attrib.get('revision', 'master')

            projects[name] = {
                'path': path,
                'remote': remote,
                'revision': revision,
                'branch': branch
            }
        elif child.tag == 'remote':
            name = child.attrib['name']
            fetch = child.attrib['fetch']

            remotes.update({name: fetch})

    return produce_real_repositories(projects, remotes)

# 将 Repo Manifest 中的所有仓库转换为 Git 子模块


def convert_to_git_submodules(manifest_file_path: str):
    if not check_file_exist(manifest_file_path):
        print('文件', manifest_file_path, '不存在', '退出解析... ...')
        return
    repositories = get_repositories(manifest_file_path)
    if not repositories:
        print('生成项目信息失败, 请检查输出信息！')
        return
    # 为每个仓库创建一个 Git 子模块
    for name, info in repositories.items():
        path = info.get('path')
        url = info.get('url')
        revision = info.get('revision')
        branch = info.get('branch')

        print(name, path, url, branch, revision)
        print()

        # 添加 Git 子模块
        os.system(f'git submodule add -b {branch} {url} {path} --reference {revision}')

        # # 拉取子模块的代码
        # #os.system(f'git submodule update --init --recursive {path}')

        # # 提交子模块
        # os.system(f'git add {path}')
        # os.system(f'git commit -m "Add {name} submodule"')

    # 删除 Repo Manifest
    #os.system('git rm repo manifest.xml')
    #os.system('git commit -m "Remove Repo Manifest"')

    print('All repositories have been converted to Git submodules.')

# 调用函数


def check_file_exist(path: str):
    return os.path.isfile(path)


def check_args():
    return True if len(sys.argv) == 2 else False


def help():
    print('usage', sys.argv[0], r'<repo manifest path>')


def is_repo_url(url: str):
    pattern = r'^(git|https|http)://.*$'
    return re.match(pattern, url)


def main():
    if check_args():
        convert_to_git_submodules(sys.argv[1])
    else:
        help()


if __name__ == '__main__':
    main()
