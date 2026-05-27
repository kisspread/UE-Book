# Shader Toolkit

> A suite of tools to analyze your projects build and shaders to help reduce shader and material permutations.

| 属性 | 值 |
|---|---|
| 中文名 | 着色器审计 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ShaderAuditCore` (Editor), `ShaderAudit` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-05-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/ShaderToolkit) | |

## 用途

Shader Toolkit 是一套专注于分析和优化 Unreal Engine 项目中**着色器（Shader）** 和**材质（Material）** 变体的工具集。它旨在解决大型项目中常见的“着色器变体爆炸”问题，即过多的材质实例和继承导致的大量独特着色器编译，从而拖慢烘焙（Cook）和打包时间，并增加最终包体大小。

该插件通过以下核心功能实现目标：
1.  **构建材质继承图谱**：分析项目资产注册表（Asset Registry）中所有 `UMaterialInterface` 及其实例，构建出完整的父子关系网络。
2.  **着色器审计与检查**：深入检查材质和着色器节点图（可能通过 HLSL 代码分析），识别潜在的优化点、冗余或无用的着色器指令。
3.  **子对象材质路径解析**：提供一套可配置的规则（通过 `.ini` 文件），用于解析复杂资产（如 Niagara 系统）中嵌套的子对象材质路径，这对于准确分析继承关系至关重要。

它主要面向**技术美术（TA）** 和**图形程序员**，作为项目优化流水线中的一个分析环节，帮助团队识别并清理不必要的材质变体，从而提升引擎整体性能。

## 使用场景

-   **大型项目优化**：当你的项目因过多的材质变体导致 ShaderCompileWorker 持续高负载，或烘焙时间过长时，使用此工具分析根源。
-   **材质继承审计**：检查材质资产的继承链，识别过深、过广或存在循环的继承结构，这些结构是变体数量的倍增器。
-   **清理无用材质**：结合审计结果和资产引用分析，找出从未在场景中使用或仅被特定平台/配置使用的材质实例。
-   **验证自定义材质管线**：如果你使用了自定义的材质函数或节点，可以通过此工具查看生成的 HLSL 代码，验证其正确性和效率。
-   **支持复杂资产类型**：对于像 Niagara 这样拥有子对象材质的复杂资产系统，配置 `ShaderAudit.ini` 以正确定位和解析其内部材质。

## 蓝图用法

此插件主要通过其提供的**编辑器窗口/工具**和**C++ API** 进行交互，未发现公开的 `BlueprintCallable` 函数。其主要用户界面是集成到编辑器中的“Shader Audit”选项卡，用于执行分析和查看结果。

### 核心功能入口

功能主要通过编辑器子系统和工具函数提供，不直接暴露给蓝图。用户通过编辑器菜单访问分析工具。

## C++ 用法

### 头文件引入

```cpp
#include "ShaderAuditUtils.h"
```

### 基本用法：获取材质审计子系统

此插件提供了一个编辑器子系统 (`UShaderAuditEditorSubsystem`)，用于管理审计会话。你可以通过它来获取分析结果。

```cpp
// 来源: Internal/ShaderAuditEditorSubsystem.h
#include "EditorSubsystem.h"
#include "ShaderAuditSession.h"

// 获取 ShaderAudit 的编辑器子系统实例
UShaderAuditEditorSubsystem* AuditSubsystem = GEditor->GetEditorSubsystem<UShaderAuditEditorSubsystem>();
if (AuditSubsystem)
{
    // 获取当前所有的审计会话
    const TArray<TSharedPtr<FShaderAuditSession>>& Sessions = AuditSubsystem->GetSessions();
    
    // 监听新的审计会话加载完成事件
    AuditSubsystem->OnSessionLoaded().AddLambda([]()
    {
        UE_LOG(LogTemp, Log, TEXT("A new Shader Audit session has been loaded."));
    });
}
```

### 进阶用法：解析材质路径与构建继承关系

`ShaderAuditUtils.h` 中提供了核心的材质分析工具函数。

```cpp
// 来源: Public/ShaderAuditUtils.h
#include "ShaderAuditUtils.h"

// 1. 解析一个材质路径字符串（可能包含子对象路径），获取 UMaterialInterface 指针
FString MaterialPath = TEXT("/Game/Materials/BaseMaterial");
// 复杂的子对象路径示例: TEXT("/Game/Effects/NiagaraSystem.NiagaraSystem:Emitter_0.Material")
FString Error;
UMaterialInterface* ResolvedMaterial = UE::ShaderAudit::Utils::ResolveMaterialPath(MaterialPath, &Error);
if (ResolvedMaterial)
{
    UE_LOG(LogTemp, Log, TEXT("Successfully resolved material: %s"), *ResolvedMaterial->GetName());
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("Failed to resolve material path '%s': %s"), *MaterialPath, *Error);
}

// 2. 构建项目中所有材质的父子关系图谱（批量操作）
UE::ShaderAudit::Utils::FMaterialParentMapResult ParentMapResult;
bool bSuccess = UE::ShaderAudit::Utils::BatchGetMaterialParents(ParentMapResult);
if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("Found %d material parent-child pairs."), ParentMapResult.Pairs.Num());
    // 可以遍历 ParentMapResult.Pairs 来分析继承链
    // 可以遍历 ParentMapResult.SubObjectPrimaries 来查看子对象材质的主包路径
}

// 3. 获取当前生效的材质解析器配置（来自 .ini 文件）
const UE::ShaderAudit::Utils::FMaterialResolverConfig& Config = UE::ShaderAudit::Utils::GetMaterialResolverConfig();
if (Config.bValid)
{
    UE_LOG(LogTemp, Log, TEXT("Material resolver config loaded. Extra root classes include: %s"), 
        *Config.ExtraRootClasses[0].ToString());
}
```

## Demo 示例

以下示例展示了如何在编辑器模块中初始化 Shader Audit 子系统并执行一次基本的材质路径解析。

```cpp
// MyShaderAuditDemo.h
#pragma once

#include "CoreMinimal.h"

class FMyShaderAuditDemo
{
public:
    static void RunDemo();
};
```

```cpp
// MyShaderAuditDemo.cpp
#include "MyShaderAuditDemo.h"
#include "ShaderAuditUtils.h"

void FMyShaderAuditDemo::RunDemo()
{
    UE_LOG(LogTemp, Log, TEXT("=== Starting Shader Audit Demo ==="));

    // 尝试解析一个普通的材质路径
    FString NormalPath = TEXT("/Game/Materials/M_Brick");
    FString NormalError;
    UMaterialInterface* NormalMat = UE::ShaderAudit::Utils::ResolveMaterialPath(NormalPath, &NormalError);
    if (NormalMat)
    {
        UE_LOG(LogTemp, Log, TEXT("Resolved normal material: %s"), *NormalMat->GetPathName());
    }

    // 尝试解析一个可能存在的子对象材质路径（需要配置 .ini）
    FString SubObjectPath = TEXT("/Game/Effects/FX_Fire.FX_Fire:ParticleEmitter.Material");
    FString SubObjectError;
    UMaterialInterface* SubObjectMat = UE::ShaderAudit::Utils::ResolveMaterialPath(SubObjectPath, &SubObjectError);
    if (SubObjectMat)
    {
        UE_LOG(LogTemp, Log, TEXT("Resolved sub-object material: %s"), *SubObjectMat->GetPathName());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Could not resolve sub-object path (this may be expected if not configured): %s"), *SubObjectError);
    }

    UE_LOG(LogTemp, Log, TEXT("=== Shader Audit Demo Complete ==="));
}
```

## 模块依赖

基于提供的 `Build.cs` 名称推断，使用者的模块可能需要依赖以下内容：

| 模块 | 用途 |
|---|---|
| `AssetRegistry` | 用于访问资产注册表，枚举项目中的所有材质资产 |
| `Slate`, `SlateCore` | 用于构建编辑器工具窗口和UI |
| `UMG` | 可能用于更复杂的编辑器控件 |
| `MaterialValidation` | 核心插件依赖，用于材质验证功能 |

**注意**：实际的 `Build.cs` 文件内容未被提供，上表为基于插件功能和头文件 (`#include`) 的合理推测。`Core`, `CoreUObject`, `Engine`, `UnrealEd` 等常见模块已被省略。

## 维护状态

### 近期更新

```
- 2026-05-12 c4351fff Create ShaderAuditCore module
- 2026-05-12 f78afe5d [Backout] - CL53715516
- 2026-05-12 0d38c80a Create ShaderAuditCore module
- 2026-05-12 d843e10b ShaderAudit: Replace remaining inline #if WITH_EDITOR with slate event for material hierarchy fetch
- 2026-05-12 263d8b5e Remove inline WITH_EDITOR in shaderaudit and instead use slate events that are setup from ShaderAudi
```

### 维护评价

-   **创建时间**：极新（基于提供的信息为 2026 年，但此日期明显为未来，疑为系统时间错误或占位符。假设为近期创建）。
-   **近期活动**：全部提交集中在同一天（2026-05-12），表明这是一个**刚刚创建或首次提交**的插件。提交内容涉及模块创建和初步的编辑器集成重构。
-   **状态**：**实验性新功能**。`.uplugin` 明确标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`。所有最近的代码提交都是建立基础设施。
-   **已知问题/限制**：作为实验性插件，API 不稳定，功能可能不完整。依赖于 `MaterialValidation` 插件。
-   **推荐使用**：**暂不推荐在生产环境中使用**。适合**早期技术评估**、**工具开发研究**或作为**Epic 未来可能提供的官方着色器分析功能的前瞻**。开发者可以关注其发展，或在其基础上开发自己项目的定制分析工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/ShaderToolkit)
- [官方文档]() （暂无）
- [测试用例]() （未在提供信息中发现）