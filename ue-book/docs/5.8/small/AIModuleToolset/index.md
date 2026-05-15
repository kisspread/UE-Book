# AIModuleToolset

> Toolset for AIModule Systems

| 属性 | 值 |
|---|---|
| 中文名 | AI模块工具集 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AIModuleToolset` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-01 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/AIModuleToolset) | |

## 用途

AIModuleToolset 是一个极简的编辑器插件框架，作为 AI 模块系统工具集的注册入口。它本身不包含任何具体的 AI 功能实现，而是作为一个容器/占位模块，通过依赖 `ToolsetRegistry` 插件将 AI 相关的工具集注册到引擎的工具集管理系统中。

该插件目前仅包含基本的模块生命周期管理和日志类别声明，预期未来会扩展为包含具体的 AI 系统编辑器工具。

## 使用场景

- 你正在为引擎 AI 系统开发编辑器工具，并需要遵循 ToolsetRegistry 的注册规范
- 你作为 Epic 内部开发者，需要一个标准化的 AI 工具集挂载点

> ⚠️ 当前版本几乎没有可用户直接使用的内容，仅作为框架占位。

## 蓝图用法

当前版本不暴露任何蓝图可用的函数或属性。

## C++ 用法

### 头文件引入

```cpp
#include "AIModuleToolset.h"
```

### 基本用法

该模块仅提供日志类别，可在此基础上记录 AI 工具集相关日志：

```cpp
#include "AIModuleToolset.h"

UE_LOG(LogAIModuleToolset, Log, TEXT("AI Toolset operation completed"));
```

## Demo 示例

无。当前插件不包含任何可演示的功能实现。

## 模块依赖

无特殊依赖（仅标准 Core）。

插件级别依赖：
| 插件 | 用途 |
|---|---|
| `ToolsetRegistry` | 工具集注册框架，AIModuleToolset 通过它向引擎注册 AI 工具集 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-03 | `7f02bd73` | [AI Toolsets]: Move all toolsets to load at post engine init to simplify registration when toolset r | 将加载阶段改为 PostEngineInit，简化工具集注册流程 |
| 2026-04-01 | `f92c7327` | [AI Toolsets]: Move AIModuleToolset under the Toolsets directory | 首次创建，将 AIModuleToolset 迁移到 Toolsets 目录下 |

### 维护评价

- **非常新**：插件于 2026-04-01 创建，至今仅 2 次提交
- **极简框架**：当前仅包含模块骨架（日志类别 + 模块接口），无实际功能
- **实验性**：标记为 `IsExperimentalVersion=true`，且 `EnabledByDefault=false`，需要手动启用
- **依赖 ToolsetRegistry**：属于工具集系统的子模块，与 ToolsetRegistry 生态绑定
- **不推荐生产使用**：当前无任何可用功能，仅适合 Epic 内部框架开发参考

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/AIModuleToolset)
- [ToolsetRegistry 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/ToolsetRegistry)