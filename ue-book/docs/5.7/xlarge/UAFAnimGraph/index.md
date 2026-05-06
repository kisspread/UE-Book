# UAF Anim Graph

> Framework for defining animation graphs.

| 属性 | 值 |
|---|---|
| 中文名 | UAF 动画图表 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资源、测试套件） |
| 模块 | `UAFAnimGraph` (Runtime), `UAFAnimGraphEditor` (Runtime), `UAFAnimGraphTestSuite` (Runtime), `UAFAnimGraphUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFAnimGraph) | |

## 总体用途

UAF Anim Graph 是 **UAF（Unreal Animation Framework）** 插件的核心动画图表定义层。它提供了一个完整的框架，用于设计、编辑和评估动画图，支持通过蓝图或 C++ 定义动画逻辑、状态机、混合空间等节点。该插件解决了在传统动画蓝图基础上难以扩展和复用动画逻辑的问题，使开发者能够以模块化的方式构建复杂的动画系统。

> **注意**：目前该插件标记为实验性，需要手动启用，不适合生产环境。

## 模块列表

| 模块 | 类型 | 一句话说明 | 链接 |
|---|---|---|---|
| `UAFAnimGraph` | Runtime | 运行时动画图核心模块，提供图评估、节点执行、变量管理等基础能力 | [UAFAnimGraph.md](./UAFAnimGraph.md) |
| `UAFAnimGraphEditor` | Runtime | 编辑器集成模块，支持可视化编辑动画图、节点拖拽、属性面板等 | [UAFAnimGraphEditor.md](./UAFAnimGraphEditor.md) |
| `UAFAnimGraphTestSuite` | Runtime | 自动化测试套件，提供 BDD 风格的 GIVEN/WHEN/THEN 测试用例 | [UAFAnimGraphTestSuite.md](./UAFAnimGraphTestSuite.md) |
| `UAFAnimGraphUncookedOnly` | Runtime | 仅用于未打包环境，提供资源引用过滤、Legacy 内容适配等工具 | [UAFAnimGraphUncookedOnly.md](./UAFAnimGraphUncookedOnly.md) |

## 使用场景

- 你需要构建 **自定义动画图**，超越传统动画蓝图的功能限制。
- 你希望以 **模块化、可复用** 的方式组织动画逻辑（如状态机、混合、控制器）。
- 你的项目使用 **UAF 框架**，需要配套的动画图表编辑和运行支持。
- 你正在开发 **动画调试工具** 或 **测试框架**，需要访问动画图的内部结构。

## 维护状态

### 近期更新

- 2025-10-01 `6f23619b` — Moved UEdGraphSchema asset reference filtering for drag and drop operations to their various implementations.
- 2025-09-03 `bb48edd8` — Avoid invalid memory access on editor exit.
- 2025-09-03 `bc59af4e` — Avoid crash when opening the context menu on legacy UAF content.

### 维护评价

该插件创建于 2025 年 8 月，距今不足两个月，处于**快速迭代期**。近期提交主要集中在稳定性修复（崩溃、内存越界）和编辑器交互优化，无重大功能变更。开发活跃，commit 频率适中（约每月 3-5 次）。实验性标记尚未移除，建议仅用于试验和原型项目。

## 相关链接

- [源码（主仓库）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFAnimGraph)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAFAnimGraph/Source/UAFAnimGraphTestSuite)
- [UAF 插件（依赖）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAF/UAF)