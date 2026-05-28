# Character AI

> Adds code and assets related to implementing AI in a character-based project.

| 属性 | 值 |
|---|---|
| 中文名 | 角色AI |
| 分类 | Gameplay |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `CharacterAI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2014-08-19 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CharacterAI) | |

## 用途

该插件是一个**早期的框架原型**，旨在为角色项目提供基础的 AI 支持。但从提供的源码分析，该插件**几乎没有任何实际功能实现**，仅包含一个空的模块接口（`ICharacterAIModuleInterface`）和一个日志分类声明（`LogCharacterAI`）。它更像是一个为未来开发预留的骨架或占位符。该插件之所以存在，可能是作为早期（UE4 时代）角色AI功能探索的起点，但显然已被后续更成熟的 AI 系统（如行为树、AI 控制器等）所取代，并且从未被正式填充内容。

## 使用场景

鉴于该插件代码为空，它没有实际可用的场景。它本身不解决任何问题，也不存在有意义的使用方式。

## 蓝图用法

当前源码中没有定义任何蓝图可用的函数（`UFUNCTION(BlueprintCallable)`）或属性（`UPROPERTY(BlueprintReadWrite)`）。因此，**不存在可用的蓝图节点**。

## C++ 用法

当前源码中没有提供任何可供外部使用的 C++ API 或类。

### 头文件引入

```cpp
// 理论上，可以引入模块头文件，但其中没有可访问的 API
#include "CharacterAIModule.h"
```

### 基本用法

无可用示例。

## Demo 示例

该插件没有提供任何可演示的功能，因此没有最小示例。

## 模块依赖

该插件的模块依赖了一个编辑器特有模块，这对于一个标记为 `Runtime` 类型的模块来说是不寻常的，进一步说明了其不成熟性。

| 模块 | 用途 |
|---|---|
| `EditorFramework` | 编辑器框架支持（对于一个 Runtime 模块而言，此依赖存疑） |
| `UnrealEd` | Unreal 编辑器核心（对于一个 Runtime 模块而言，此依赖存疑） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 插件目录相关的批量改动，非功能性更新 |
| 2022-10-21 | `610c4676` | Update vendor links for built-in plugins to use secure protocol. | 更新内置插件的供应商链接为安全协议 |
| 2022-09-10 | `0eeac455` | Pass 3 on cleaning up build.cs files. | 清理 Build.cs 文件的第三轮工作 |
| 2020-08-14 | `48113fc7` | Adding EditorFramework to build.cs files | 向 Build.cs 文件中添加 EditorFramework 依赖 |
| 2019-12-27 | `360d078c` | Second batch of remaining Engine copyright updates. | 剩余引擎版权更新的第二批 |

### 维护评价

- **创建时间**：2014年8月，属于非常早期的 Unreal 插件。
- **最近更新**：最近的提交（2023年）仅为目录结构或构建文件的维护性修改，没有任何功能代码的更新或添加。
- **活跃度**：该插件**已停止开发**。自创建以来的近10年里，从未被填充有意义的功能代码。
- **已知问题**：代码库为空，无法实现任何宣传的功能；`Runtime` 模块错误地依赖了 `UnrealEd` 等编辑器模块。
- **推荐**：**强烈不推荐**使用。这是一个已被废弃的、功能缺失的实验性框架，不具备任何实用价值。应使用 UE 内置的、成熟的 AI 系统（如行为树、AI 控制器、EQS 等）来实现角色AI。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/CharacterAI)