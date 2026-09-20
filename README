# Vim 开发环境

本工程包含 Vim 配置、15 个插件及 Pathogen 加载器。可以放在任意目录，通过脚本启用或恢复原环境，无需重新下载插件。插件来源和提交版本记录在 `plugin-versions.json`。

## 启用和还原

适用于 Linux/macOS 的 Bash 环境。需要 Python 3 和 Vim，建议使用 Vim 9.1+ 且启用 `+python3`；SuperTab 要求 Vim 9+，UltiSnips 需要 Vim 的 Python 3 支持。可用 `vim --version` 检查。

进入项目目录执行：

```bash
./start.sh
```

脚本会保存当前用户原有的配置，并创建以下软链接：

| 用户路径 | 项目文件 | 用途 |
| --- | --- | --- |
| `~/.vimrc` | `vimrc` | Vim 主配置 |
| `~/.vim` | `.vim/` | 插件和辅助文件 |
| `~/.index.py` | `index.py` | 生成 cscope 文件列表的辅助脚本 |

项目路径会自动识别，支持路径中有空格。重复执行不会覆盖首次保存的原配置。启用后需要重新打开 Vim；启用期间请保留项目目录及其位置。

恢复原环境：

```bash
./stop.sh
```

恢复的是首次执行 `start.sh` 前的文件、目录或软链接；原来不存在的入口会移除。重复停用不会改动配置。脚本不会修改系统级 Vim 配置，也不会自动安装或卸载系统软件。

原配置及恢复记录保存在 `~/.local/state/workenv-vim/`，成功还原后清除。请勿手动删除该目录；它包含恢复所需的原文件。锁文件位于相邻的 `workenv-vim.lock`，可以保留。

如果启用后手动替换了某个入口，`stop.sh` 会停止并指出冲突，不会覆盖新文件。先将冲突文件移到其他位置，再重试。直接编辑软链接指向的项目配置不会阻止恢复。

注意：如果启用前已经手动链接到本项目，停用后也会恢复为该链接。脚本无法找回启用前就已丢失的旧配置。

## 外部工具

- `ctags`：Taglist 所需，从系统 `PATH` 查找。也可在代码目录运行 `ctags -R .` 生成标签，Vim 中使用 `Ctrl+]` 跳转、`Ctrl+t` 返回。
- `cscope`：代码索引查询所需，同时要求 Vim 支持 `+cscope`。
- Rust 工具链：仅运行 Rust 的编译、格式化等命令时需要 `cargo`、`rustc`、`rustfmt`。

插件已随项目提供，但上述工具需要通过目标机器的包管理器安装。`start.sh` 会提示缺少的 `ctags`、`cscope` 或 Vim Python 支持，不会自动安装软件。

## 插件简明用法

下表按当前配置说明。除特别标注外，快捷键在普通模式使用；`<Leader>` 为默认的反斜杠 `\`，例如 `\b` 表示先按反斜杠，再按 b。

| 插件 | 功能 | 常用操作 |
| --- | --- | --- |
| NERDTree | 文件目录树 | `F5` 开关；树内回车打开文件，`s` 左右分屏打开，`t` 新标签页打开，`m` 文件操作菜单；`:NERDTreeFind` 定位当前文件 |
| CtrlP | 模糊查找文件 | `Ctrl+p` 打开，输入文件名片段，`Ctrl+j/k` 选结果，回车打开，Esc 退出；`:CtrlPBuffer` 查找已打开文件，`:CtrlPMRUFiles` 查找最近文件 |
| UltiSnips | 展开代码模板 | 插入模式输入触发词后连续按 `ii`；`Ctrl+j/k` 切换填写位置；Python 中可试 `ifmain`、`def`、`class`；`:UltiSnipsEdit` 编辑自定义模板 |
| vim-snippets | 多语言模板集合 | 配合 UltiSnips 使用，按文件类型加载模板，没有单独的启动操作 |
| SuperTab | Tab 补全 | 插入模式输入单词前缀后按 Tab 触发补全，继续按 Tab 选择候选项 |
| delimitMate | 自动补齐括号和引号 | 插入模式输入左括号或引号，自动补出配对符号 |
| vim-easy-align | 对齐多行文本 | `V` 选中多行，按回车，再按 `=` 对齐赋值；按 `,` 对齐逗号；`gaip=` 对齐当前段落的等号 |
| vim-easymotion | 按屏幕提示快速跳转 | 按 `s`，输入两个目标字符，再按显示的提示字母；`\w` 跳到单词，`\L` 跳到行 |
| vim-multiple-cursors | 多光标编辑 | 光标放在单词上，连续按 `Ctrl+n` 选择多个匹配，按 `c` 输入替换内容；Esc 退出。上游已弃用，本工程保留其最后版本 |
| Taglist | 函数、类、变量列表 | `F7` 开关符号列表，回车跳转到符号；需要 ctags |
| rust.vim | Rust 高亮、缩进及工具集成 | 打开 `.rs` 自动启用；`:RustFmt` 格式化，`:Cargo build` 构建 Cargo 项目，相关命令需要 Rust 工具链 |
| bufferhint | 切换已打开的缓冲区 | 按 `\b` 打开列表，按列表提示选择文件 |
| rainbow_parentheses | 嵌套括号彩色高亮 | 已配置自动启用；`:RainbowParenthesesToggle` 切换显示 |
| visualmark | 可视化行书签 | `mm` 标记或取消当前行，`F2` 跳到下一书签，`Shift+F2` 跳到上一书签 |
| cscope_maps | 查询符号定义、引用和调用关系 | 加载数据库后，按 `Ctrl+\` 再按 `g` 查定义、`s` 查符号引用、`c` 查调用者 |
| Pathogen | 加载插件 | 启动时自动加载 `.vim/bundle/`，无需手动操作；不是自动更新工具 |

CtrlP 搜索窗口内的 `F5` 用于刷新文件缓存；普通编辑窗口中的 `F5` 用于开关 NERDTree。`Ctrl+w` 再按 `w` 可在分屏之间切换。

### cscope 示例

在需要索引的 C/C++ 项目根目录中执行：

```bash
find . -type f \( -name '*.c' -o -name '*.h' -o -name '*.cpp' \) > cscope.files
cscope -bq
```

然后在 Vim 中执行 `:cs add /完整路径/cscope.out`，即可使用上表的查询快捷键。

`python3 ~/.index.py` 也能生成文件列表，但会遍历当前目录的所有文件，并删除旧的 cscope 数据库；它不负责构建数据库。大型项目建议按语言筛选文件后再运行 `cscope -bq`。

## 已知限制

旧配置仍包含部分 Verilog/LaTeX 扩展入口，例如 `VerilogFollowInstance`、`print_wire.sh`、`delete_wire.sh` 和 `auctex.vim`。这些外部扩展未随本工程提供，对应操作需要额外安装；它们不属于上表中已提供的插件。

## 验证脚本

```bash
python3 -m unittest discover -s tests -v
```

测试使用临时用户目录，覆盖启用、重复执行、恢复原文件和目录、恢复软链接、冲突保护及失败回滚，不会切换当前用户的 Vim 环境。
