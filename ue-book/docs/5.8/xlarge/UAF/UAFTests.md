# Unreal Animation Framework (UAF)

> Framework for defining functional data flow for animation systems（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 动画框架 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `UAF` (Runtime), `UAFEditor` (Runtime), `UAFTestData` (Runtime), `UAFUncookedOnly` (Runtime), `UAFTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAF) | |

## 用途

UAF（Unreal Animation Framework）是 Epic Games 开发的新一代动画系统框架，用于定义动画系统的**函数式数据流**。它最初以 "AnimNext" 的名称在 UE5 主分支中开发，后于 2025 年 6 月重命名为 UAF 并迁移到 `Experimental` 目录下。

与传统的基于状态机的动画系统不同，UAF 采用了**函数式数据流（functional data flow）**的架构理念，将动画求值过程建模为一组纯函数的组合与数据管道。这使得动画混合、IK 求值、骨骼约束等操作可以以声明式的方式进行组合，从而实现：

- 更可预测的动画更新顺序
- 更容易调试和测试的动画数据流
- 更好的并行化潜力
- 更清晰的关注点分离

该框架包含 652 个源文件，分为 5 个模块：核心运行时（UAF）、编辑器工具（UAFEditor）、测试数据（UAFTestData）、仅未打包模块（UAFUncookedOnly）和自动化测试（UAFTests）。

## 使用场景

- 你需要构建复杂的、可组合的动画求值图（Animation Evaluation Graph）
- 你需要将动画混合逻辑从状态机中解耦，改为数据流驱动的方式
- 你正在开发大型项目并希望动画系统更易于测试和维护
- 你需要自定义动画节点的求值逻辑，以函数式风格组合
- 你希望替代或补充现有的 `AnimInstance` + `AnimGraph` 工作流

> ⚠️ **注意**：UAF 目前为实验性插件（`IsExperimentalVersion=true`），未默认启用。API 可能在未来版本中发生重大变更。建议仅用于学习和原型验证，不建议在生产项目中使用。

## 蓝图用法

UAF 作为底层动画框架，其核心 API 主要面向 C++ 使用者。框架的设计理念偏向函数式数据流，大部分交互通过 C++ 的函数节点和数据图完成。目前没有发现直接暴露给蓝图的核心节点。

如需在蓝图中集成 UAF，通常需要通过自定义的 `UActorComponent` 或 `AnimInstance` 子类来桥接。

## C++ 用法

### 头文件引入

```cpp
#include "UAF/UAF.h"
```

### 模块概览

UAF 框架由以下 5 个模块组成：

| 模块 | 类型 | 职责 |
|---|---|---|
| `UAF` | Runtime | 核心运行时：数据流定义、求值图、动画节点 |
| `UAFEditor` | Runtime | 编辑器集成：自定义图表编辑器、节点工厂、属性面板 |
| `UAFTestData` | Runtime | 测试用的动画资产和数据定义 |
| `UAFUncookedOnly` | Runtime | 仅在未打包（编辑器/开发）环境加载的模块，含调试工具 |
| `UAFTests` | Runtime | 自动化测试用例，验证框架核心功能 |

> **注**：尽管所有模块在 Build.cs 中标记为 Runtime，但 UAFEditor 和 UAFUncookedOnly 实际上仅在编辑器/开发环境中使用。

### 基本架构概念

UAF 的核心概念包括：

- **数据节点（Data Node）**：表示动画数据的输入源（如骨骼变换、动画曲线等）
- **求值节点（Evaluation Node）**：对输入数据进行变换操作的纯函数
- **数据流图（Data Flow Graph）**：将多个节点连接为有向无环图，定义完整的求值路径
- **组件（Component）**：`UAFComponent` 作为 Actor 上的入口，负责驱动整个数据流图的 Tick

### 进阶用法

UAF 框架支持自定义求值节点的注册和求值图的动态构建。通过注册自定义的求值函数，可以扩展动画系统的功能：

```cpp
// 伪代码示例 - UAF 求值节点的概念用法
// 具体 API 请参考源码中的 Public/*.h 头文件

// 1. 定义自定义求值节点
// 2. 注册到 UAF 图系统
// 3. 在 UAFComponent 中指定使用的数据流图
```

## Demo 示例

由于 UAF 是实验性框架，目前完整的最小示例可参考 `Tests/UAFTests` 目录下的自动化测试用例。这些测试用例展示了框架核心功能的标准用法。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveCoding` | Live Coding 热重载支持，用于编辑器中实时编译和刷新 |

无特殊依赖（仅标准 Core/Engine/Slate 等 + LiveCoding）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `eeaff753` | UAF: Introduce optional tick dependency between the UAF Component targeting a ACharacters mesh compo | 引入 UAF 组件与 Character 网格组件之间的可选 Tick 依赖 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复函数类型转换警告在 MSVC 和 Clang 间的可移植性 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中枚举类型导致的错误输出 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式化说明符不匹配问题 |
| 2026-04-24 | `523ac953` | Fix incorrect quaternion attribute type usage | 修复四元数属性类型使用错误 |

### 维护评价

UAF 是一个 **活跃维护中的实验性框架**。

- **创建时间**：2025 年 6 月，非常年轻的框架（约 1 年）
- **更新频率**：近期有持续的功能性更新和 bug 修复，最近一次更新在 2026 年 5 月
- **代码规模**：652 个源文件，表明这是一个功能完整、体系庞大的框架
- **状态**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，API 稳定性不能保证
- **来源**：由 "AnimNext" 重命名迁移而来，继承了原项目的全部代码和历史

**推荐程度**：适合学习和研究 Epic 的动画系统设计思路，不建议在生产环境中使用。如果你对下一代 UE 动画系统感兴趣，这是一个非常有价值的参考。

## 子模块文档

由于 UAF 包含 652 个源文件，属于大型插件，以下按模块拆分：

- [UAF 核心模块](UAFCore.md) — 核心运行时：数据流图、求值节点、组件系统
- [UAFEditor 编辑器模块](UAFEditor.md) — 编辑器工具：图表编辑器、节点面板
- [UAFTestData 测试数据](UAFTestData.md) — 测试用动画资产定义
- [UAFUncookedOnly 未打包模块](UAFUncookedOnly.md) — 调试工具和开发辅助
- [UAFTests 测试模块](UAFTests.md) — 自动化测试用例

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAF)
- 官方文档（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAF/Tests)