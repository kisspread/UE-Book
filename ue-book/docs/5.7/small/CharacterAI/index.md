# CharacterAI

> Adds code and assets related to implementing AI in a character-based project.

| 属性 | 值 |
|---|---|
| 中文名 | 角色 AI |
| 分类 | Gameplay |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `CharacterAI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-12-27 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CharacterAI) | |

## 用途

该插件最初旨在为基于角色的项目提供 AI 相关的代码和资产。然而，目前其代码库仅包含一个空的模块接口和日志宏，**没有实现任何实际的 AI 功能或公开的 API**。该插件很可能是一个早期的实验性尝试，现已废弃，不建议在新项目中使用。

## 使用场景

无实际使用场景。该插件不提供任何可调用的功能或资产。

## 蓝图用法

**无**。该插件未暴露任何蓝图可调用节点、函数或属性。

## C++ 用法

### 头文件引入

```cpp
#include "CharacterAIModule.h"
```

### 基本用法

该插件仅提供一个空模块类 `ICharacterAIModuleInterface`，无任何成员函数或属性。你可以通过模块管理器访问该模块，但无法执行任何有意义的操作：

```cpp
// 示例：获取模块实例，但模块无任何功能
ICharacterAIModuleInterface& AIModule = FModuleManager::LoadModuleChecked<ICharacterAIModuleInterface>(TEXT("CharacterAI"));
```

### 进阶用法

无。

## Demo 示例

无。该插件不提供任何可编译的示例。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EditorFramework` | 编辑器框架（通常用于编辑器插件，此处可能为误用） |
| `UnrealEd` | 编辑器核心模块（运行时模块不应依赖此模块） |

> ⚠️ 注意：该插件声明为 Runtime 类型，却依赖 EditorFramework 和 UnrealEd，这可能导致在发布构建中无法正常加载。

## 维护状态

### 近期更新

- 2023-01-16 bbc37aa2 [Engine/Plugins]（插件列表元数据更新）
- 2022-10-21 610c4676 Update vendor links for built-in plugins to use secure protocol.（链接协议更新）
- 2022-09-10 0eeac455 Pass 3 on cleaning up build.cs files.（清理构建文件）
- 2020-08-14 48113fc7 Adding EditorFramework to build.cs files（添加依赖）
- 2019-12-27 360d078c Second batch of remaining Engine copyright updates.（版权更新）

### 维护评价

- **创建时间**：2019年底（约6年）。
- **最近实质性更新**：2020年添加依赖，此后无功能更新。
- **活跃度**：长期不活跃，仅有过元数据和构建文件清理。
- **问题**：不提供任何功能，且运行时模块依赖编辑器模块，配置可疑。
- **推荐使用**：❌ 不推荐。该插件已废弃，无实际用途。如果项目需要角色 AI 功能，请使用 `AIModule`、`BehaviorTree` 等成熟插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CharacterAI)