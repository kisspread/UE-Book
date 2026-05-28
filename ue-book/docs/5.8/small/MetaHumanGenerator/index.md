# MetaHuman Generator

> Simplified MetaHuman toolset for AI-driven character creation and editing

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman生成器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MetaHumanGenerator` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-05-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/MetaHumanGenerator) | |

## 用途
该插件提供了一个简化版的 MetaHuman 创作与编辑工具集，旨在通过易于使用的接口（主要是蓝图）支持 AI 驱动的角色创建流程。它封装了底层 MetaHuman SDK 的复杂操作，提供了一组用于创建新 MetaHuman 角色、并对其肤色、瞳色、体型等基础参数进行读取和设置的工具函数。其核心功能是管理 `MetaHumanEditSession`，确保在对同一个 MetaHuman 角色资产进行连续多次工具调用时，无需反复打开和关闭资产，从而保持一个清晰、高效的编辑上下文。

## 使用场景
- **AI 角色原型设计**：当你正在开发一个 AI 驱动的流程，需要快速实例化和修改 MetaHuman 角色以用于测试、训练或内容生成时。
- **简化参数化操作**：你需要通过蓝图或简单的代码，对 MetaHuman 的肤色、瞳色、身体比例等关键参数进行批量或程序化的读取和设置，而不想直接处理复杂的 SDK 调用。
- **开发 MetaHuman 相关工具**：作为创建更高级 MetaHuman 编辑工具或自动化管线的基础框架。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Reset Neck to Body` | 将指定 MetaHuman 角色的颈部位置重置，使其与身体保持自然比例。常用于在修改身体形态参数后修复颈部连接。 | `UMetaHumanGeneratorSubsystemWrapper` |

### 使用示例（蓝图描述）
1.  **创建 MetaHuman 角色**：通过插件提供的专用工具节点（由底层子系统驱动）实例化一个新的 `UMetaHumanCharacter` 资产。
2.  **调整参数**：使用 `Set Skin Tone`、`Set Eye Color`、`Set Body Shape Parameter` 等节点修改角色外观。
3.  **修复姿态**：在修改身体参数后，调用 `Reset Neck to Body` 节点，传入目标 `MetaHumanCharacter` 引用，以自动调整颈部，避免拉伸或断裂。
4.  **结束会话**：当完成一系列编辑后，触发会话的结束（finalize），所有更改将被应用并保存到角色资产中。

## C++ 用法

### 头文件引入
```cpp
#include "MetaHumanGenerator.h"
```

### 基本用法
从插件的测试用例（代码中提及）可以推断，其核心是通过一个子系统或管理器类来操作 MetaHuman 角色。

```cpp
// 假设的 C++ 用法，基于插件描述和子系统模式
// 来源：基于对 MetaHumanEditSession 描述的推断

#include "MetaHumanGeneratorSubsystem.h" // 假设的子系统头文件
#include "MetaHumanCharacter.h"

void AMyActor::CreateAndEditMetaHuman()
{
    // 1. 获取生成器子系统实例
    UMetaHumanGeneratorSubsystem* GeneratorSubsystem = GEditor->GetEditorSubsystem<UMetaHumanGeneratorSubsystem>();
    if (!GeneratorSubsystem) return;

    // 2. 创建一个新的 MetaHuman 角色资产（示例函数，具体名称需查证）
    UMetaHumanCharacter* NewCharacter = GeneratorSubsystem->GenerateMetaHuman(/* 参数 */);
    if (!NewCharacter) return;

    // 3. 编辑角色参数（示例函数）
    GeneratorSubsystem->SetSkinTone(NewCharacter, ESkinTone::Medium);
    GeneratorSubsystem->SetEyeColor(NewCharacter, EEyeColor::Brown);

    // 4. 修改身体参数后，重置颈部
    UMetaHumanGeneratorSubsystemWrapper::ResetNeckToBody(NewCharacter);

    // 5. 结束编辑会话，保存更改
    GeneratorSubsystem->FinalizeEditSession(NewCharacter);
}
```

### 进阶用法
插件强调使用 `MetaHumanEditSession` 来管理上下文，以实现高效的连续编辑。

```cpp
// 基于“允许缓存编辑会话以串联多个工具调用”的设计思路
void AMyActor::BatchEditMetaHuman(UMetaHumanCharacter* Character)
{
    UMetaHumanGeneratorSubsystem* GeneratorSubsystem = GEditor->GetEditorSubsystem<UMetaHumanGeneratorSubsystem>();

    // 开始一个编辑会话（可能隐式开始，或显式调用）
    // 在这个会话上下文中，可以连续进行多次操作
    GeneratorSubsystem->BeginEditSession(Character); // 假设的 API

    // 连续调用多个设置方法，资产只在最后真正打开和保存
    GeneratorSubsystem->SetEyeColor(Character, EEyeColor::Blue);
    GeneratorSubsystem->SetBodyShapeParameter(Character, EBodyShape::Muscular, 0.8f);
    GeneratorSubsystem->ResetNeckToBody(Character);

    // 结束会话，一次性应用所有更改
    GeneratorSubsystem->FinalizeEditSession(Character); // 假设的 API
}
```

## Demo 示例
一个简单的 Actor，展示如何在 C++ 中调用 MetaHuman Generator 的 API。

```cpp
// MyMetaHumanEditorActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMetaHumanEditorActor.generated.h"

class UMetaHumanCharacter;

UCLASS()
class AMyMetaHumanEditorActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMetaHumanEditorActor();

    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category="MetaHuman")
    UMetaHumanCharacter* CharacterToEdit;
};
```

```cpp
// MyMetaHumanEditorActor.cpp
#include "MyMetaHumanEditorActor.h"
#include "MetaHumanGenerator.h"
#include "MetaHumanCharacter.h"

AMyMetaHumanEditorActor::AMyMetaHumanEditorActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMetaHumanEditorActor::BeginPlay()
{
    Super::BeginPlay();

    if (CharacterToEdit)
    {
        // 注意：以下函数为示意性调用，具体函数名和参数请以实际源码为准
        // 使用子系统包装类中的静态方法
        UMetaHumanGeneratorSubsystemWrapper::ResetNeckToBody(CharacterToEdit);

        UE_LOG(LogTemp, Log, TEXT("Attempted to reset neck for MetaHuman character."));
    }
}
```

## 模块依赖
该插件依赖于一系列 MetaHuman 核心插件。要使用此插件，你的项目或模块需要确保以下插件已启用，并在你的模块的 `.Build.cs` 文件中添加相应的模块依赖（如果需要直接链接）。

| 模块/插件 | 用途 |
|---|---|
| `MetaHumanCharacter` | MetaHuman 角色资产的核心定义和操作接口 |
| `MetaHumanCoreTech` | MetaHuman 核心技术栈，提供底层支持 |
| `MetaHumanSDK` | MetaHuman 的官方 SDK，包含生成、编辑等功能 |
| `StructUtils` | 提供通用的结构体工具集 |
| `ToolsetRegistry` | 用于注册和发现编辑器工具集 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `179668b7` | Re-land of CL 54366066 after backout. | 在之前回退后，重新引入了一个变更集，表明对初始功能的修复或调整。 |
| 2026-05-22 | `61954685` | [Backout] - CL54378532 | 回退了插件首次提交的变更，说明初始版本存在需要解决的问题。 |
| 2026-05-22 | `4cb1458a` | Adds MetaHumanGenerator Toolset plugin | 插件的首次提交，加入了基础的 MetaHuman 生成与编辑工具集。 |

### 维护评价
该插件创建于 **2026年5月22日**，年龄非常短，属于**实验性**插件（`IsExperimentalVersion=true`，`EnabledByDefault=false`）。

- **活跃度**：从 git 历史看，发布后立即经历了回退和重新部署，表明它处于**非常早期的开发和测试阶段**，接口和功能可能尚不稳定。
- **功能完整性**：提供了基础的 AI 驱动角色创建和参数编辑框架，但功能集有限。
- **推荐度**：**不建议在生产项目中依赖此插件**。它适合用于**实验性研究、原型开发或 MetaHuman 工具链的内部开发**。开发者需要密切关注其后续更新和可能的接口变动。
- **已知限制**：作为实验性插件，其稳定性、文档和功能完整性均未达到正式发布标准。使用它意味着接受可能遇到的未解决问题和未来不兼容的更改。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/MetaHumanGenerator)