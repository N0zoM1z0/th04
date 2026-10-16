# TH04 reconstruction / port64 接手入口

更新：2026-10-16。两条任务线均在进行中。先做下列环境核验，再选一个有明确验收边界的任务；不要把历史函数 exact 数量当作全游戏完成度。

## 先确认当前机器的实际状态

本次交接开始时，本地 `main` 干净，远端已核验：

| 用途 | 已发布基线 | 本机可用性 |
| --- | --- | --- |
| DOS reconstruction / 比对工具 / 台账 | `main: 83c94d1ee995b8f164e843d1924e716d91ca93a3` | 当前仓库可用；本交接提交会在其后 |
| native x64 源码 | `port/modern-64: c0a1060371c5f8ba758ca8b10f6cbc99063ba3d6` | 远端和本地 Git 对象可用；旧工作树目录缺失 |

**2026-10-16 发现 `.analysis/worktrees/` 整体不存在，但 Git 仍有旧工作树登记。**
这包括 `native-natural-clear-v1432`、`native-main-pause-v1431` 和
`dos-smem-page-copy-v1423`。不知道缺失原因，不能认为旧产物已成功归档，也不能按旧记录声称这些文件仍在本机。

根目录下的 v1437/v1436 捕获、压缩 DGROUP/video、报告及恢复归档仍存在；
native v1432 的根目录报告/归档也存在，但其 retention 清单的 94 个 protected 文件全部位于缺失工作树，当前均不可读。
DOS v1437 candidate receipt 引用的 MAIN 和 MAP 同样位于缺失工作树。
因此当前不能直接完整重放这些历史验收。源码可从 Git 恢复，旧二进制、MAP、完整 native 路由证据需要找回原存储或按新 producer 重新构建/采集。
**新构建不能冒充历史 producer，不要改旧 receipt/seal 来迁就路径或哈希。**

```sh
git status --short
git ls-remote --heads origin main port/modern-64
git worktree list --porcelain
taskset -c 1 nice -n 19 python3 scripts/preflight.py
python3 scripts/status.py
```

先读 `AGENTS.md`、[当前状态](RE_HANDOFF.md)、[架构](ARCHITECTURE.md)、
[工作流](RE_WORKFLOW.md)、[知识库](KNOWLEDGE_BASE.md) 和相关 `.agents/skills/`。
从 `config/knowledge.csv` 检索已有实验，避免重复走否定路线。
原始目标 preflight 当前通过；来源仍是 `candidate-local-attested`，不是官方 pristine dump 证明。
使用数据库做原始反汇编前，另运行 `python3 scripts/ghidra.py ARTIFACT check`。

如需恢复 port64 开发，先确认没有其他写入会话，再从上述远端基线创建**新名称**的工作树/分支，例如：

```sh
git worktree add -b work/port64-next .analysis/worktrees/port64-next origin/port/modern-64
git -C .analysis/worktrees/port64-next status --short
```

名称已存在则换名。不要清理旧 Git 工作树登记来掩盖文件缺失，也不要 reset、覆盖历史冻结分支。主线提交不会自动提交或推送 native 分支。

## 已验证的结果和明确未通过的部分

以下是**历史 producer 的已记录结果**，不是本次重新采集的结果。
详细命令、证据 ID 和 ownership 在 [DOS 差分笔记](reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md)、
[port64 状态](PORTING_STATUS.md)、`config/evidence.csv` / `config/knowledge.csv`。

| 范围 | 已记录结果 | 不包含的验收 |
| --- | --- | --- |
| 四个 bundled Demo，各 3,996 updates | 消费输入、分数/RNG、9 个完整池、22 个状态块、所有配置的视频区域一致；Demo 1 原有分歧已修复 | 物理扫描时序、完整普通游戏 |
| 普通 Normal ReimuA，3,996 updates，v1434–1436 | 两次独立配对；36 个字段、1,369 次有序 RNG、自然死亡/复活；v1436 全 38 个视频区域一致 | 原始 GDC timing 每帧仍不同；v1436 聚合报告因 155 个 post-reset input 样本不同而失败 |
| 普通 Boss 前缀，7,500 updates，v1437 | 消费输入、36 字段、2,837 次有序 RNG、9 个完整池、22 个状态块一致；Boss phases 0/1/2，5 次自然损失 | **`passed=false`：258 个 post-reset input 样本不同**；没有 Boss 完整画面、击破或全流程验收 |
| native v1432 GNU / optimized UBSan | Easy ReimuA、Normal ReimuA、Normal MarisaA、同轮 Normal 存档解锁的 Extra ReimuA；两编译器完整逻辑捕获/存档一致，mask=1，无 Continue | `render_every=0` 的 headless 路由；不证明完整画面、原版全游戏一致、Windows 输入/音频或物理时序 |

普通 DOS 配对只替换 MAIN，OP/MAINE/ZUN、资源和起始文件仍用原版；不能说已经配对验收了四个还原 EXE 的完整进程链。
v1435/v1436/v1437 的 post-reset input 差异分别为 156/155/258，属于各自捕获，不能混用；消费输入一致不消除中间采样差异。
三个池在较短前缀中始终为空，不代表其活动路径已覆盖。

旧交接 `55cf73e` 中 Demo 1 帧 3343 的分歧已经不是当前阻塞。Stage 4 midboss toggle、carpet columns、bullet invalidation dimensions、point-number glyph 和 lighting-animation cell 的修复及冷构建证据见差分笔记。

历史 authored exact 为 **661/663**：OP 93/93、MAIN 493/495、MAINE 72/72、ZUN 3/3。
MAIN 独立函数台账的分母 494 属于另一统计口径。两项 carpet/checkerboard exact 案例继续 deferred；本任务不重开它们。
四个 DOS 产品已有 maintained-local-source 构建路线，native 无需复制原始 EXE 字节。

## 推荐下一步：先修复证据可用性，再推进有边界的配对

1. **恢复开发和重放环境。** 核验缺失工作树是否在其他存储；找不回时，从已发布源码创建新树，按现有构建文档产生新的冷构建和独立证据。保留历史 producer 的身份和“当前不可重放”状态。
2. **补齐普通 Boss 完整视频比较。** 以 7,500-update 成功前缀为起点，保留独立输入/RNG/池控制，增加双页四平面、TRAM、完整 palettes、modes 和已配置 GDC 字段。现有 capture 支持 `--end-after 7500 --dialog-at-frame 6548 --video-stream --video-layout RECEIPT`；但 `compare_th04_ordinary_video.py` 仍绑定旧 3,996-update 合同，必须先扩展并验证 reader/metadata/terminal 和反例，不能直接宣称 7,500 帧已被旧 gate 接受。
3. **真实 Game Over / Continue / 进程路由。** 原版第 7,547 帧自然进入 Game Over。held Shot 卡在 release-first 输入等待；先正常释放键再操作，不要改 lives/RNG/clock，也不要误判 IRQ 故障。Continue、Quit、MAINE、fresh OP/第二次 MAIN 需要分别记录进程和 resident 生命周期；旧单 MAIN 监视器不能自动代表多进程支持。
4. **port64 状态和效果逐项对齐。** 使用相同已消费输入和明确状态边界，比较 original DOS → reconstructed DOS → native；从完整游戏区域扩展到 HUD、页切换、文字、palettes、全画面。GNU/UBSan 互相相同或旧 40 个游戏区域样本相同，都不是全图原版验收。只为重现的差异或明确 ownership 修改源码。

原版 Game Over 的实测栈：相对 MAIN `0AAF:3B1E` → `130E:0149` input_wait release loop → `130E:00E3` frame_delay(1)；实际调用在 `0AAF:3B19`。
v1437 的 bounded terminal 位于原版 MAIN `0AAF:01B3`，load `10FC`；捕获后由 GDB flush/kill，**`natural_game_exit=false`**，不是自然退出。
Count1=0 单次采样也不能证明 IRQ 失效。

native 读档必须验证十个 section 的完整 16-bit checksum、角色/难度/shot partition、`mask < 4` 和所选 shot bit，以及 Ending、stage coverage、registration/fresh OP。
历史窗口/UBSan Normal 的 `0x19` sentinel 失败仍撤销；新 headless 通过不会恢复那项旧结论。

## 重放身份和路径

| 项目 | 路由 / 固定身份 |
| --- | --- |
| v1437 报告/控制/压缩恢复 | `.analysis/reconstruction/probes/dos-ordinary-boss-v1437/` |
| v1437 最终捕获 | `.analysis/runtime/candidates/dos-ordinary-boss-v1437-{original,candidate}-7500/` |
| v1436 视频 | `.analysis/runtime/candidates/dos-ordinary-video-v1436-{original,candidate}/` |
| v1434 独立 plain baselines | `.analysis/runtime/candidates/dos-clock-input-v1434-v8-{original,candidate}/` |
| pinned emulator receipt | `.analysis/runtime/emulators/demo-observer-build-v1365/receipt.json` |
| native v1432 根目录报告 | `.analysis/reconstruction/probes/native-natural-clear-v1432/` |

v1437 历史 ordinary MAIN SHA-256：
`f21a5c7ca38ebaee0e0ae544540ed2c36b4429cd846c3a12d8a5ccb887728cd8`，200,279 bytes。
缺失的 build 在 `.analysis/worktrees/dos-smem-page-copy-v1423/.analysis/build/smem-page-copy-v1423/`；
其 MAP 是该树下 `.analysis/reconstruction/probes/product-20261012-005819-ac6f4873-main/source/obj/main-native.map`，
SHA-256 `2b6a74a073f98a2b53ab9583ad1bfee5775886b8954240b1efab2c5d089bdf59`。
不要把根目录旧 `.analysis/build/th04` / `th04-normal` 当成这个 producer。

native 的 frozen C++ producer 为 `554/31e6b3d7…`，reader consumer 为 `554/a79f199f…`；
完整 digest 和 553 个未变输入的合同见 [native 路由笔记](reconstruction/product/TH04_NATIVE_NATURAL_ROUTES_V1432.md)。
冻结 GNU/UBSan 程序原在 `native-main-pause-v1431` 树的 `.analysis/port64/native-main-pause-v1431-v5/`，当前缺失。

**只有找回并核验 receipt 引用的 MAIN/MAP、归档恢复 raw alias 后，才能运行旧完整比较：**

```sh
taskset -c 1 nice -n 19 python3 scripts/probes/compare_th04_bounded_ordinary.py \
  .analysis/runtime/candidates/dos-ordinary-boss-v1437-original-7500 \
  .analysis/runtime/candidates/dos-ordinary-boss-v1437-candidate-7500 \
  --original-main .analysis/targets/th04/main.exe --output /tmp/th04-boss-prefix.json
```

预期 exit 1：scalar / actor_pools / global_states 为 true，聚合因 258 个输入差异为 false。
文件缺失报错不是这个预期结果。旧 baseline source hash 如与当前工具不同，只能提供经旧 receipt 核验的 frozen snapshot；不得重签 producer。

## 资源、清理和收尾

本次只整理文档，不启动长 campaign，也不重新生成大型 build/capture。审计时根 `.analysis/` 约 6.3 GiB；旧工作树缺失不计作本次清理收益。
本次 preflight、486 项 root CI、tracking 和 diff 检查通过；v1437/v1436 的恢复器以只校验模式分别验证 24/8 个归档路径，没有展开大型文件。
native 354 项测试是其历史 CI 记录，本次未在缺失工作树中重跑。
后续重活用 CPU 1 / nice 19，串行 Borland/Wine。所有运行静音、headless 或私有 Linux Xvfb；不打开 Windows GUI、抢焦点或注入 host keys。

- scratch 和生成目录只放 `.analysis/`，每个实验新 namespace；保留失败 producer。
- 只清理本轮自己生成且可恢复的 intermediates；先核验归档 hash、CRC、完整内容及恢复后的 mode/nsmtime，再删明确清单。禁止一把删除 `.analysis/`、旧 worktree 或全部 build。
- v1437/v1436 用各 namespace 的 `recover.py --restore --prefix PATH`，v1434 用自己的 `recover.py`；v1434 旧 `verify_retention.py` 指向已被替代的全量归档，不应使用。
- native v1432 的 `verify_retention.py` 先检查 protected files；当前缺失 94 项，不能靠 `--restore` 恢复整棵工作树。先找回其受保护来源。
- 恢复只选需要的 prefix。临时 raw/HDI aliases 用完核验后退回归档状态，不重复计作新增节省。完整压缩帧流、原始 HDI/EXE/assets、compiler、receipts、source snapshots 和必要 MAP 不当作垃圾。
- 全局 header/flags/layout/link order 改动后，冷重放所有受影响 accepted units。源码恢复、运行时相同、exact 三类结论分开写。

收尾运行 focused comparison、`taskset -c 1 nice -n 19 python3 scripts/ci.py`、
`git diff --check`，更新 README / RE_HANDOFF / 当前 focused note；提交前确认未加入原版程序、资源、私有归档或凭证。
提交格式必须是 **`gpt-6.1-sol: ...`**。两分支分别提交/推送，并核验远端；不要把任务状态重新写成 paused。

## 可直接发给新 agent 的指令

> 继续 TH04 reconstruction 与 port64，先读 docs/NEXT_AGENT_HANDOFF.md 和 AGENTS.md，核验远端两分支、目标与真实文件可用性。旧 .analysis/worktrees 当前缺失，先恢复开发/证据环境，不得假装旧 producer 仍可重放。随后选一个有边界的 Boss 完整视频或 Game Over/Continue 配对任务，严查 original DOS / reconstructed DOS / native 的状态与效果。保留所有已知输入/GDC 差异与失败证据，不重开两项 deferred exact。单核低优先级串行、静音 headless，不干扰 Windows；及时清理自己生成的可恢复产物。收尾更新状态、跑 CI/diff，提交用 gpt-6.1-sol: 前缀。
