# Niagara Toolsets

> A collection of tool calls allowing an AI assistant the ability to interact with Niagara.

| 属性 | 值 |
|---|---|
| 分类 | FX |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `NiagaraToolsets` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/NiagaraToolsets) | |

## 用途

NiagaraToolsets 是一个专门为 **AI 助手** 设计的 Niagara 操作工具集。它并非面向普通开发者，而是为 AI 代理（Agent）提供一套结构化的 API，使其能够以编程方式创建、修改、查询和调试 Niagara 粒子系统。该插件解决了 AI 助手无法直接理解和操作 Niagara 复杂数据结构的问题，通过提供封装好的工具调用（Tool Calls），让 AI 能够像人类开发者一样与 Niagara 编辑器进行交互。

## 使用场景

- **AI 辅助特效创建**：当 AI 助手需要为游戏创建一个粒子特效（如爆炸、火焰、魔法效果）时，可以使用此插件来生成新的 Niagara 系统、添加发射器、配置模块参数。
- **AI 辅助特效修改**：AI 助手需要根据游戏逻辑或性能分析结果，动态调整现有 Niagara 系统的参数（如粒子数量、颜色、速度）。
- **AI 辅助特效调试**：当 Niagara 系统出现编译错误或运行时问题时，AI 助手可以利用此插件查询系统状态、获取错误信息，并尝试应用修复建议。
- **AI 生成蓝图包装器**：AI 助手可以将一个 Niagara 系统自动封装成一个蓝图 Actor，方便在关卡中快速放置和配置。

## 蓝图用法

此插件主要通过 `UFUNCTION(meta = (AICallable))` 标记的函数供 AI 助手调用，这些函数在蓝图中也可用。核心功能按操作对象分为几组。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ConstructNiagaraBPWrapperFromSystem` | 从一个 Niagara 系统资产创建一个新的蓝图 Actor 包装器。 | `UNiagaraToolset_Blueprint` |
| `ConstructNiagaraBPWrapperFromComponent` | 从一个已配置的 Niagara 组件创建一个新的蓝图 Actor 包装器，并保留其属性覆盖。 | `UNiagaraToolset_Blueprint` |
| `SetSystem` | 为 Niagara 组件设置要使用的 Niagara 系统资产。 | `UNiagaraToolset_Component` |
| `GetUserVariables` | 获取 Niagara 组件上所有用户变量的当前值。 | `UNiagaraToolset_Component` |
| `SetVariable` | 设置 Niagara 组件上一个用户变量的值。 | `UNiagaraToolset_Component` |
| `GetVariable` | 获取 Niagara 组件上一个特定用户变量的当前值。 | `UNiagaraToolset_Component` |
| `UEnum_Info` | 获取一个 UEnum 的所有枚举值信息，用于 AI 理解枚举类型。 | `UNiagaraToolset_Info` |
| `GetAssetDiscoveryInfo` | 获取 Niagara 相关资产（系统、发射器、模块等）的发现路径，指导 AI 查找资源。 | `UNiagaraToolset_Info` |

### 使用示例（蓝图描述）

假设 AI 助手需要为一个已有的 `NS_Fire` 系统创建一个蓝图 Actor：
1.  AI 调用 `ConstructNiagaraBPWrapperFromSystem` 节点。
2.  将 `NewAssetPath` 设置为 `/Game/FX/BP_Fire`。
3.  将 `System` 引用连接到 `NS_Fire` 资产。
4.  将 `ParentClass` 设置为 `AActor`。
5.  执行后，将在 `/Game/FX/` 目录下生成一个名为 `BP_Fire` 的新蓝图资产，该蓝图包含一个预配置了 `NS_Fire` 系统的 Niagara 组件。

## C++ 用法

此插件主要为 AI 助手设计，其 C++ API 通常通过 `ToolsetRegistry` 框架进行注册和调用。直接在 C++ 中使用这些工具类需要理解其底层机制。

### 头文件引入

```cpp
#include "NiagaraToolset_Component.h"
#include "NiagaraToolset_Blueprint.h"
#include "NiagaraToolset_Info.h"
```

### 基本用法

以下示例展示了如何在 C++ 中直接调用工具集函数来操作 Niagara 组件（通常由 AI 助手框架内部调用）。

```cpp
// 假设我们有一个指向 UNiagaraComponent 的指针
UNiagaraComponent* MyNiagaraComp = ...;

// 1. 设置组件使用的 Niagara 系统
UNiagaraSystem* NewSystem = LoadObject<UNiagaraSystem>(nullptr, TEXT("/Game/FX/NS_Explosion"));
UNiagaraToolset_Component::SetSystem(MyNiagaraComp, NewSystem, true);

// 2. 获取组件上的所有用户变量
TArray<FNiagaraExt_VariableInst> UserVars = UNiagaraToolset_Component::GetUserVariables(MyNiagaraComp);

// 3. 设置一个特定的用户变量（例如颜色）
FNiagaraExt_VariableInst ColorVar;
ColorVar.Variable.Name = FName(TEXT("User.Color"));
// ... 设置 ColorVar 的值 ...
UNiagaraToolset_Component::SetVariable(MyNiagaraComp, ColorVar);
```

### 进阶用法

结合信息查询和蓝图创建功能，实现一个完整的 AI 工作流。

```cpp
// 1. AI 首先查询可用的 Niagara 资产路径
TArray<FNiagaraToolsetAssetDiscoveryGroup> AssetPaths = UNiagaraToolset_Info::GetAssetDiscoveryInfo();
// AI 分析 AssetPaths 来决定在哪里查找或创建新资产

// 2. AI 创建一个新的 Niagara 系统（此步骤可能需要其他 Niagara 编辑 API）
// ... 创建 UNiagaraSystem* NewSystem 的过程 ...

// 3. AI 将新系统包装成蓝图，以便在关卡中使用
FString BlueprintPath = TEXT("/Game/AI_Generated/BP_NewEffect");
UBlueprint* NewBP = UNiagaraToolset_Blueprint::ConstructNiagaraBPWrapperFromSystem(BlueprintPath, NewSystem, AActor::StaticClass());
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在一个自定义的 AI 工具类中使用 `NiagaraToolsets` 的功能。

**MyAITool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyAITool.generated.h"

class UNiagaraComponent;
class UNiagaraSystem;

UCLASS()
class UMyAITool : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "AI Tools")
    void CreateAndConfigureEffect(UNiagaraComponent* TargetComponent, UNiagaraSystem* SystemToUse);
};
```

**MyAITool.cpp**
```cpp
#include "MyAITool.h"
#include "NiagaraToolset_Component.h"
#include "NiagaraToolset_Blueprint.h"

void UMyAITool::CreateAndConfigureEffect(UNiagaraComponent* TargetComponent, UNiagaraSystem* SystemToUse)
{
    if (!TargetComponent || !SystemToUse)
    {
        UE_LOG(LogTemp, Warning, TEXT("Invalid input parameters."));
        return;
    }

    // 使用工具集设置系统
    UNiagaraToolset_Component::SetSystem(TargetComponent, SystemToUse, false);

    // 查询并打印当前用户变量
    TArray<FNiagaraExt_VariableInst> Variables = UNiagaraToolset_Component::GetUserVariables(TargetComponent);
    for (const auto& Var : Variables)
    {
        UE_LOG(LogTemp, Log, TEXT("User Variable: %s"), *Var.Variable.Name.ToString());
    }

    // 可选：为该系统创建一个蓝图包装器
    FString BPPath = FPaths::Combine(FPaths::GetPath(SystemToUse->GetPathName()),
                                      FString::Printf(TEXT("BP_%s"), *SystemToUse->GetName()));
    UNiagaraToolset_Blueprint::ConstructNiagaraBPWrapperFromSystem(BPPath, SystemToUse, AActor::StaticClass());
}
```

## 模块依赖

从 `.uplugin` 的 `Plugins` 部分可知，此插件依赖于其他插件。在你的模块中使用 `NiagaraToolsets` 的功能时，需要确保以下依赖可用。

| 模块 | 用途 |
|---|---|
| `Niagara` | 核心的 Niagara 粒子系统框架。 |
| `ToolsetRegistry` | AI 助手工具集注册和管理框架，`NiagaraToolsets` 的基础。 |

## 维护状态

### 近期更新

- `cceeda27` 2026-04-23 — Add a Diagnostics layer to the Niagara System toolset:
- `a378050c` 2026-04-23 — Add SetParameters module support to NiagaraExternalEditUtilities and NiagaraAIAssistantTools
- `c868841e` 2026-04-23 — Rename NiagaraAIAssistantTools plugin to NiagaraToolsets

### 维护评价

**活跃开发中**。该插件于 2026 年 4 月 23 日创建，所有提交记录均发生在同一天，表明它正处于密集的初始开发阶段。从提交信息看，功能正在快速迭代和添加（如诊断层、参数设置支持）。作为 `Experimental` 插件，其 API 和功能可能会发生较大变化。目前没有迹象表明它被废弃，但鉴于其极新的年龄和实验性状态，**不建议在生产环境中依赖此插件**，更适合用于研究和实验 AI 与编辑器交互的场景。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/NiagaraToolsets)
- [官方文档]() (无)
- [测试用例]() (未在提供信息中发现)