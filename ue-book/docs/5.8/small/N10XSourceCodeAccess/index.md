# 10X Editor Integration

> Allows access to source code in the 10X Editor .

| 属性 | 值 |
|---|---|
| 中文名 | 10X编辑器集成 |
| 分类 | Programming |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `N10XSourceCodeAccess` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2023-06-09 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/N10XSourceCodeAccess) | |

## 用途

该插件为 **10X Editor** 提供源代码访问集成。10X 是一款新兴的高性能代码编辑器，此插件实现了 UE5 的 `ISourceCodeAccessor` 接口，允许开发者在使用 10X Editor 时，能够从虚幻编辑器内部直接打开源代码文件、定位到特定行，并与引擎的编辑器工具链（如蓝图编译、错误定位、调试等）无缝集成。它解决了在自定义编辑器环境下开发 UE 项目时的源代码跳转与管理问题。

## 使用场景

- 当你主要使用 **10X Editor** 进行 C++ 开发，但希望在虚幻编辑器中点击错误或蓝图节点时，能自动在 10X 中打开对应文件并定位。
- 你希望将 10X Editor 设置为项目的默认源代码访问器，替代 Visual Studio 或 Xcode。
- 你的开发环境仅限于 Windows（Win64），因为该插件仅支持此平台。

## 蓝图用法

此插件不提供任何蓝图可调用节点。它通过编辑器设置（`Editor Preferences -> Source Code`）进行配置，一旦被选为默认的源代码访问器，其功能将自动在后台运行。

## C++ 用法

该插件的核心是 `F10XSourceCodeAccessor` 类，它实现了 `ISourceCodeAccessor` 接口。通常不需要直接在项目代码中调用，而是通过编辑器设置选择。

### 头文件引入

要以编程方式与该插件交互，你可能需要引入其模块头文件，但这在常规项目中不常见。
```cpp
// 如果需要直接访问插件模块，可以引入
#include "N10XSourceCodeAccessModule.h"
```

### 基本用法（配置）

该插件通过编辑器偏好设置激活。在 C++ 中，没有直接调用的必要 API，其行为由引擎的源代码访问器管理系统统一调度。

### 进阶用法（接口参考）

从 `F10XSourceCodeAccessor` 的实现可以看到它支持以下核心操作，这些操作由引擎在需要时调用：
- `OpenSolution`: 打开整个解决方案。
- `OpenFileAtLine`: 在指定文件和行号处打开。
- `OpenSourceFiles`: 打开多个源文件。
- `SaveAllOpenDocuments`: 保存所有在 10X 中打开的文档。

## Demo 示例

该插件是一个编辑器集成模块，没有面向游戏运行时或蓝图使用的公开 API 示例。其使用方式是通过编辑器设置进行配置。

## 模块依赖

从 Build.cs 中的依赖关系来看，该插件仅依赖于一个非标准模块：

| 模块 | 用途 |
|---|---|
| `HotReload` | 用于支持代码热重载功能，这是源代码访问器与引擎编译系统交互的关键。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-10-31 | `bbe97454` | Fix mismatched LOCTEXT_NAMESPACE and AllowWindowsPlatformTypes | 修复本地化命名空间不匹配，并处理Windows平台特定类型 |
| 2025-03-25 | `3395567a` | PR #13018: 10x Source Code Editor: Fix files not opening when file path contains spaces | 修复当文件路径包含空格时无法打开文件的问题 |
| 2024-10-07 | `d69a4c88` | [UE] Fix 10x source code accessor to pull the correct solution file name | 修复获取正确解决方案文件名的问题 |
| 2024-07-18 | `9eaacc95` | [Backout] - CL34912307 - CIS Valk Error | 回退一次提交以修复CI错误 |
| 2024-07-18 | `413ba815` | [AutoRTFM] Migrate more critical sections to using the transactionally safe variants. | 将更多关键代码段迁移到事务安全变体 |

### 维护评价

- **活跃维护**：插件创建于 2023 年，最新更新在 2025 年 10 月，间隔不足一年，且修复了具体的使用问题（如路径空格、解决方案文件名），表明仍在积极维护。
- **状态稳定**：没有标记为实验性或测试版，且默认启用。
- **平台限制**：仅支持 Win64，使用其他平台的开发者无法使用。
- **推荐使用**：如果你在 Windows 上使用 **10X Editor** 作为主编辑器，这是一个推荐的、功能完善的集成插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/N10XSourceCodeAccess)
- [官方文档](https://epicgames.com)（无特定文档页，可参考编辑器源代码访问器通用文档）