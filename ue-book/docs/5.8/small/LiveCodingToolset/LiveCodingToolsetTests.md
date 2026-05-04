# LiveCodingToolset

> Live Coding compile toolset.

| 属性 | 值 |
|---|---|
| 分类 | Experimental/Toolsets |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveCodingToolset` (Editor), `LiveCodingToolsetTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Toolsets/LiveCodingToolset) | |

## 用途

LiveCodingToolset 是一个围绕 Unreal Engine 的 **Live Coding（实时编码）** 功能构建的编辑器工具集插件。它为开发者在编辑器运行时进行 C++ 热重载提供了额外的编译工具支持。

该插件的核心价值在于：
- **增强 Live Coding 工作流**：在标准 Live Coding 功能基础上，提供额外的编译辅助工具
- **Toolset 架构集成**：作为 ToolsetRegistry 插件体系的一部分，遵循 UE5 的模块化工具集设计模式
- **编辑器专用**：仅在编辑器环境下加载，不影响打包后的运行时性能

## 使用场景

- 你在开发过程中频繁使用 Live Coding 热重载 C++ 代码，需要更完善的编译工具支持
- 你正在构建自定义的编辑器工具集（Toolset），需要参考 Live Coding 相关的工具实现
- 你需要在编辑器运行时调试和优化 C++ 编译流程

## 蓝图用法

本插件为编辑器工具集，主要面向 C++ 开发者。当前源码中未发现公开的 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。

## C++ 用法

### 头文件引入

```cpp
#include "LiveCodingToolset.h"
```

### 基本用法

本插件作为 ToolsetRegistry 体系的一部分，通过 ToolsetRegistry 进行注册和管理。使用前需要确保：
1. 在 `.uproject` 或插件配置中启用 `LiveCodingToolset`
2. 依赖模块 `LiveCoding` 已正确加载

### 模块依赖

从 Build.cs 分析，本插件依赖以下模块：

| 模块 | 用途 |
|---|---|
| `LiveCoding` | UE5 核心 Live Coding 功能，提供运行时 C++ 热重载能力 |
| `ToolsetRegistry` | 工具集注册框架，用于管理编辑器工具集的生命周期 |

## 维护状态

### 近期更新

由于该插件创建时间较新（2026-04-23），暂无足够的 git 历史记录可供分析。

### 维护评价

- **实验性插件**：`IsExperimentalVersion=true`，表明该功能仍处于实验阶段
- **未默认启用**：`EnabledByDefault=false`，需要手动在插件设置中启用
- **仅限编辑器**：`EditorOnly=true`，不会影响打包构建
- **小规模实现**：仅 8 个源文件，功能相对精简
- **建议**：可用于探索 Live Coding 工具链扩展，但不建议在生产环境中依赖此插件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Toolsets/LiveCodingToolset)
- [ToolsetRegistry 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Toolsets/ToolsetRegistry)（依赖插件）