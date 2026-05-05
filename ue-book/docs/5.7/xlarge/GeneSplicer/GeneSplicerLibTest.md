# GeneSplicer Plugin v9.8.2

> GeneSplicer plugin for facial animation

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GeneSplicerLib` (Runtime), `GeneSplicerLibTest` (Runtime), `GeneSplicerModule` (Runtime), `GeneSplicerEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-10-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GeneSplicer) | |

## 用途

GeneSplicer 是一个用于**面部动画 DNA 数据拼接与混合**的插件。它基于 MetaHuman DNA（.dna 文件）体系，允许开发者将多个面部 DNA 数据源进行"剪接"（splice），从而实现不同面部特征的组合与混合。核心功能包括：

- **DNA 数据拼接**：将来自不同源的面部 DNA 数据（骨骼、网格、动画曲线、关节权重等）按区域或层级进行拼接组合
- **面部动画生成**：基于拼接后的 DNA 数据驱动面部骨骼和 BlendShape 动画
- **与 RigLogic 集成**：依赖 RigLogic 插件进行底层的 DNA 解码和面部求值
- **与 ControlRig 集成**：通过 ControlRig 框架将拼接结果应用到动画蓝图中

该插件解决了"如何从多个面部资产中提取、组合、生成新的面部动画"这一问题，是 MetaHuman 工作流中面部动画定制的核心组件。

## 使用场景

- 你有一个 MetaHuman 角色，需要将不同演员的面部特征混合 → 用 GeneSplicer 拼接多个 DNA 源
- 你需要程序化生成大量不同的面部变体（如 NPC 群体）→ 用 GeneSplicer 按参数混合 DNA
- 你在做面部动捕数据的后处理，需要将动捕结果与基础面部模板融合 → 用 GeneSplicer 进行数据层拼接
- 你需要在运行时动态修改角色面部特征 → 用 GeneSplicer 的 Runtime API 进行实时 DNA 混合

## 模块架构

本插件包含 4 个模块，按职责分层：

| 模块 | 类型 | 职责 |
|---|---|---|
| `GeneSplicerLib` | Runtime (PreDefault) | 核心拼接算法库，DNA 数据解析与拼接逻辑 |
| `GeneSplicerModule` | Runtime (Default) | UE 运行时集成层，提供蓝图和动画系统接口 |
| `GeneSplicerEditor` | Runtime | 编辑器集成，DNA 资产导入/预览/编辑工具 |
| `GeneSplicerLibTest` | Runtime (Win64) | 单元测试模块，仅在 Win64 平台可用 |

### 模块依赖关系

```
GeneSplicerEditor ──→ GeneSplicerModule ──→ GeneSplicerLib
                                              ↑
GeneSplicerLibTest ──────────────────────────┘
```

## 蓝图用法

> ⚠️ 由于本插件规模为 xlarge（249 个源文件），且当前仅提供了测试模块的头文件，完整的蓝图 API 文档需要进一步分析 `GeneSplicerModule` 和 `GeneSplicerEditor` 模块的公开接口。以下为基于架构推断的核心功能分类。

### 核心功能（推断）

| 功能域 | 说明 | 所在模块 |
|---|---|---|
| DNA 数据加载 | 从 .dna 文件加载面部数据 | `GeneSplicerLib` |
| DNA 拼接配置 | 定义哪些区域从哪个源拼接 | `GeneSplicerLib` |
| DNA 执行拼接 | 执行实际的拼接运算 | `GeneSplicerLib` |
| 面部动画驱动 | 将拼接结果应用到骨骼/BlendShape | `GeneSplicerModule` |
| DNA 资产管理 | 编辑器中的 DNA 资产导入与预览 | `GeneSplicerEditor` |

## C++ 用法

### 头文件引入

```cpp
#include "GeneSplicerLibTest.h"
```

### 基本用法

由于当前仅提供了测试模块头文件，以下展示测试模块的结构。完整的 C++ API 需要分析 `GeneSplicerLib` 的公开头文件。

```cpp
// GeneSplicerLibTest 模块声明
// 来源: Engine/Plugins/Animation/GeneSplicer/Source/GeneSplicerLibTest/Public/GeneSplicerLibTest.h
#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

DECLARE_LOG_CATEGORY_EXTERN(LogGeneSplicerLibTest, Log, All);

class FGeneSplicerLibTest : public IModuleInterface
{
    // 测试模块，仅在 Win64 平台编译
    // 用于验证 GeneSplicerLib 的核心拼接逻辑
};
```

### 测试用例参考

测试模块使用 BDD 风格（GIVEN/WHEN/THEN）编写，可通过以下方式运行：

```bash
# 在编辑器控制台中运行自动化测试
Automation RunTests GeneSplicer
```

## Demo 示例

> ⚠️ 由于本插件为 xlarge 规模且当前仅获取到测试模块的头文件，无法提供完整的最小可编译示例。建议参考插件源码中的测试用例（`GeneSplicerLibTestSuite.cpp`）作为使用参考。

### 最小骨架（基于已知信息）

```cpp
// MyGeneSplicerExample.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyGeneSplicerExample.generated.h"

UCLASS()
class AMyGeneSplicerExample : public AActor
{
    GENERATED_BODY()

public:
    // 初始化 DNA 拼接器并执行拼接
    // 实际 API 需参考 GeneSplicerLib 公开头文件
    UFUNCTION(BlueprintCallable, Category = "GeneSplicer")
    void InitializeSplicer();
};
```

```cpp
// MyGeneSplicerExample.cpp
#include "MyGeneSplicerExample.h"
#include "GeneSplicerLibTest.h"  // 仅用于日志分类引用

void AMyGeneSplicerExample::InitializeSplicer()
{
    UE_LOG(LogGeneSplicerLibTest, Log, TEXT("GeneSplicer initialization placeholder"));
    // TODO: 参考 GeneSplicerLib 的实际 API 进行 DNA 加载和拼接
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RigLogic` | 底层 DNA 解码与面部求值引擎 |
| `ControlRig` | 动画蓝图集成框架，用于驱动面部骨骼 |

## 维护状态

### 近期更新

```
- 01af3ec4a357 Don't use SSE on Windows Arm64
- b886ae927090 Remove commented code from GeneSplicerLIbTestSuite.cpp
- 2e00e3074c6f Comment out unreachable code [FYI] thales.sabino #rnx #jira
```

### 维护评价

- **创建时间**：2024-10-21，约 1 年历史，属于较新的插件
- **更新频率**：近期有活跃提交，包括平台兼容性修复（Arm64 SSE 禁用）和代码清理
- **维护状态**：**活跃维护中** — 由 Epic Games 官方维护，作为 MetaHuman 工作流的核心组件
- **已知限制**：
  - 测试模块仅在 Win64 平台可用
  - 依赖 RigLogic 和 ControlRig 插件，需确保这些插件已启用
  - `Installed: false` 表示默认不随引擎安装，需手动启用
- **推荐程度**：⭐⭐⭐⭐ 如果你在做 MetaHuman 或高级面部动画工作流，这是必备插件。对于简单的面部动画需求，可能过于重量级。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GeneSplicer)
- [RigLogic 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/RigLogic)
- [ControlRig 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ControlRig)