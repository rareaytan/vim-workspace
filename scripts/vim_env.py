"""Apply and restore this project's Vim configuration for the current user."""
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

PROJECT = Path(__file__).resolve().parents[1]
LINKS = {'.vimrc': 'vimrc', '.vim': '.vim', '.index.py': 'index.py'}


def exists(path):
    return os.path.lexists(path)


def owns_link(path, source):
    return path.is_symlink() and os.readlink(path) == source


def save(state_dir, state):
    temp = state_dir / 'state.tmp'
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
    temp.replace(state_dir / 'state.json')


def restore(home, state_dir, state):
    # Check all destinations before restoring any, so a conflict changes nothing.
    for item in state['entries']:
        target = home / item['name']
        backup = state_dir / item['name']
        if item['phase'] == 'restored':
            continue
        if item['phase'] == 'pending' and item['original'] and not exists(backup):
            continue  # Installation did not move the original yet.
        if item['phase'] == 'restoring' and item['original'] and not exists(backup):
            if not exists(target):
                raise RuntimeError('原配置和备份均缺失：' + str(target))
            continue  # Original has already been moved back.
        if exists(target) and not owns_link(target, item['source']):
            raise RuntimeError(f'{target} 已被修改。请先将它移到其他位置，再执行 stop.sh；备份保留在 {state_dir}')
        if item['original'] and not exists(backup):
            raise RuntimeError('原配置备份缺失：' + str(backup))
    for item in state['entries']:
        target = home / item['name']
        backup = state_dir / item['name']
        if item['phase'] == 'restored':
            continue
        if item['original'] and not exists(backup):
            item['phase'] = 'restored'
            save(state_dir, state)
            continue
        item['phase'] = 'restoring'
        save(state_dir, state)
        if owns_link(target, item['source']):
            target.unlink()
        if item['original']:
            shutil.move(str(backup), str(target))
        item['phase'] = 'restored'
        save(state_dir, state)
    (state_dir / 'state.json').unlink()
    state_dir.rmdir()


def start(home, state_dir):
    manifest = state_dir / 'state.json'
    if manifest.exists():
        state = json.loads(manifest.read_text())
        if state['project'] == str(PROJECT) and all(
            i['phase'] == 'linked' and owns_link(home / i['name'], i['source'])
            for i in state['entries']
        ):
            print('当前项目已启用，无需重复操作。')
            return
        raise RuntimeError('已有启用记录或未完成操作，请先运行 stop.sh。')
    for source in LINKS.values():
        if not (PROJECT / source).exists():
            raise RuntimeError('缺少项目文件：' + str(PROJECT / source))
    if not shutil.which('vim'):
        raise RuntimeError('未找到 Vim，请先安装 Vim 9+（带 Python 3 支持）。')
    version = subprocess.run(['vim', '--version'], capture_output=True, text=True, check=True).stdout
    if '+python3' not in version and '+python3/dyn' not in version:
        print('提示：当前 Vim 未启用 Python 3，UltiSnips 将不可用。', file=sys.stderr)
    for tool in ('ctags', 'cscope'):
        if not shutil.which(tool):
            print(f'提示：未找到 {tool}，相关代码索引功能不可用。', file=sys.stderr)
    # Never replace an existing state directory, even if its manifest is missing.
    state_dir.mkdir(mode=0o700)
    state = {'project': str(PROJECT), 'entries': [
        {'name': name, 'source': str(PROJECT / source),
         'original': exists(home / name), 'phase': 'pending'}
        for name, source in LINKS.items()
    ]}
    save(state_dir, state)
    try:
        for item in state['entries']:
            target = home / item['name']
            if item['original']:
                shutil.move(str(target), str(state_dir / item['name']))
            item['phase'] = 'backed_up'
            save(state_dir, state)
            target.symlink_to(item['source'])
            item['phase'] = 'linked'
            save(state_dir, state)
        (PROJECT / '.vim/tmp').mkdir(exist_ok=True)
    except Exception:
        restore(home, state_dir, state)
        raise
    print(f'已启用：{PROJECT}\n原环境恢复记录：{state_dir}\n请重新打开 Vim。')


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ('start', 'stop'):
        raise RuntimeError('用法：start.sh 或 stop.sh')
    home = Path.home()
    parent = home / '.local/state'
    parent.mkdir(parents=True, exist_ok=True)
    state_dir = parent / 'workenv-vim'
    # Keep the lock inode stable across repeated invocations.
    with (parent / 'workenv-vim.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if sys.argv[1] == 'start':
            start(home, state_dir)
        elif (state_dir / 'state.json').exists():
            state = json.loads((state_dir / 'state.json').read_text())
            restore(home, state_dir, state)
            print('已恢复启用前的环境，请重新打开 Vim。')
        elif state_dir.exists():
            raise RuntimeError('恢复记录不完整，请检查：' + str(state_dir))
        else:
            print('没有启用记录，无需恢复。')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as error:
        print('操作失败：' + str(error), file=sys.stderr)
        sys.exit(1)
