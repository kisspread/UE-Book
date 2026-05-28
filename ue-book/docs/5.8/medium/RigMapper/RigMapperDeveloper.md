# Rig Mapper

> A set of animation remapping features

| 属性 | 值 |
|---|---|
| 中文名 | 骨骼映射器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资产） |
| 模块 | `RigMapper` (Runtime), `RigMapperEditor` (UncookedOnly), `RigMapperDeveloper` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-16 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RigMapper) | |

## 用途

RigMapper 是一套动画重定向工具集，用于解决不同骨骼结构之间的动画映射问题。它能将一个 Control Rig 或角色的动画数据（如姿势、变形）转换并应用到另一个拥有不同骨骼层级或命名规范的目标角色上。其核心思想是通过定义源骨骼到目标骨骼的映射关系，实现动画资产的跨骨骼复用。

## 使用场景

- 你有一个使用标准骨骼的角色A，和一个自定义骨骼结构的角色B，希望复用角色A的动画 → 使用 RigMapper 定义映射规则，将动画重定向到角色B。
- 你需要将一组面部捕捉数据（来自外部软件）映射到你的角色面部骨骼上 → 通过 RigMapper 定义输入/输出的对应关系。
- 在项目中，不同角色的骨骼命名不一致（如 Mixamo 角色与 UE Mannequin），需要批量统一动画资产 → 使用 RigMapper 进行批量转换。

## 蓝图用法

*注：提供的模块代码较少，以下节点基于插件功能和常见模式推断。实际节点需在编辑器中查看 `RigMapper` 分类。*

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Rig Mapper` | 创建一个骨骼映射器实例，用于定义和执行映射 | `URigMapperSubsystem` (推断) |
| `Add Bone Mapping` | 为映射器添加一条源骨骼到目标骨骼的映射规则 | `URigMapper` (推断) |
| `Remap Animation Sequence` | 将指定的动画序列通过映射器转换为适用于目标角色的新动画序列 | `URigMapper` (推断) |

### 使用示例（蓝图描述）

1. 在蓝图开始时，通过 `Create Rig Mapper` 节点创建一个新的映射器。
2. 使用 `Add Bone Mapping` 节点，为源角色和目标角色之间不一致的每一块骨骼添加映射（例如，将 “upperarm_l” 映射到 “LeftArm”）。
3. 当需要重定向一个动画时，获取源动画资产，调用 `Remap Animation Sequence` 节点，并将创建的映射器作为输入，输出即为重定向后的新动画序列。

## C++ 用法

*注：由于仅提供了 `RigMapperDeveloper` 模块的接口，以下为基于插件架构的合理推断。实际 API 请参考 `RigMapper` 运行时模块的头文件。*

### 头文件引入

```cpp
#include "RigMapper/RigMapper.h"
#include "RigMapper/RigMapperSubsystem.h"
```

### 基本用法

创建一个映射器并执行简单的重定向（推断示例）。

```cpp
// 在你的游戏模块或动画实例中
#include "RigMapperSubsystem.h"
#include "Animation/AnimSequence.h"

void YourClass::RemapAnimation(UAnimSequence* SourceAnim, USkeleton* TargetSkeleton)
{
    // 获取或创建骨骼映射子系统
    URigMapperSubsystem* MapperSubsystem = GEngine->GetEngineSubsystem<URigMapperSubsystem>();
    if (!MapperSubsystem) return;

    // 创建一个新的映射器实例
    URigMapper* NewMapper = MapperSubsystem->CreateRigMapper(TargetSkeleton);

    // 定义映射规则 (假设 BoneMapping 是一个包含源和目标骨骼名的结构)
    TMap<FName, FName> MappingRules;
    MappingRules.Add(TEXT("upperarm_l"), TEXT("LeftArm"));
    MappingRules.Add(TEXT("lowerarm_l"), TEXT("LeftForeArm"));
    // ... 添加更多映射

    NewMapper->SetBoneMappings(MappingRules);

    // 执行重定向
    UAnimSequence* RemappedAnim = NewMapper->RemapAnimSequence(SourceAnim);

    if (RemappedAnim)
    {
        // 使用重定向后的动画
    }
}
```

### 进阶用法

结合 `RigMapperDeveloper` 模块可能提供的调试和日志功能，监控映射过程。

```cpp
#include "RigMapperDeveloperModule.h"

void YourClass::DebugRigMapping(URigMapper* Mapper)
{
    // 确保开发者模块已启动（通常在编辑器环境下）
    if (FModuleManager::Get().IsModuleLoaded("RigMapperDeveloper"))
    {
        // 调用开发者模块提供的调试函数，输出详细的映射日志
        // 例如：FRigMapperDeveloperModule::LogMappingDetails(Mapper);
    }
}
```

## Demo 示例

*注：以下为概念性示例，展示如何集成 RigMapper。具体实现需参考插件提供的完整 API。*

**RigMapperExample.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RigMapperExample.generated.h"

class URigMapper;
class UAnimSequence;

UCLASS()
class ARigMapperExample : public AActor
{
    GENERATED_BODY()

public:
    ARigMapperExample();

    UPROPERTY(EditAnywhere, Category = "RigMapper")
    UAnimSequence* SourceAnimation;

    UPROPERTY(EditAnywhere, Category = "RigMapper")
    USkeleton* TargetSkeleton;

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "RigMapper")
    void RunRemappingExample();

private:
    UPROPERTY()
    URigMapper* CurrentMapper;
};
```

**RigMapperExample.cpp**
```cpp
#include "RigMapperExample.h"
#include "RigMapperSubsystem.h"
#include "RigMapper.h"
#include "Animation/AnimSequence.h"

ARigMapperExample::ARigMapperExample()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ARigMapperExample::RunRemappingExample()
{
    if (!SourceAnimation || !TargetSkeleton)
    {
        UE_LOG(LogTemp, Warning, TEXT("请设置源动画和目标骨骼"));
        return;
    }

    // 1. 获取映射子系统
    URigMapperSubsystem* Subsystem = GEngine->GetEngineSubsystem<URigMapperSubsystem>();
    if (!Subsystem) return;

    // 2. 创建映射器
    CurrentMapper = Subsystem->CreateRigMapper(TargetSkeleton);
    if (!CurrentMapper) return;

    // 3. (在此处设置映射规则，例如从数据表加载)
    // TMap<FName, FName> Rules = LoadMappingRulesFromTable();
    // CurrentMapper->SetBoneMappings(Rules);

    // 4. 执行重定向
    UAnimSequence* Result = CurrentMapper->RemapAnimSequence(SourceAnimation);

    if (Result)
    {
        UE_LOG(LogTemp, Log, TEXT("重定向成功！新动画资产: %s"), *Result->GetName());
        // 可以将 Result 保存到磁盘或直接应用
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("重定向失败。"));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ControlRig` | 核心依赖，RigMapper 建立在 ControlRig 的动画系统之上 |

*注：插件自身模块间的依赖关系未在提供的 Build.cs 中明确，但根据架构推断，`RigMapperEditor` 和 `RigMapperDeveloper` 依赖于 `RigMapper`。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `ab890466` | [RigMapper] Improved RigMapperDefinition logging and testing | 改进定义文件的日志输出和测试 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断到浮点数的警告 |
| 2026-05-12 | `40287b95` | [RigMapper] Fixed broken automated tests, added missing automated tests, fixed a bug detected by upd | 修复并完善自动化测试，修复了测试发现的bug |
| 2026-05-12 | `edf81547` | [RigMapper] Made importing inputs/outputs from Control Rig optional in order to reduce clatter | 将从 Control Rig 导入输入/输出设为可选，减少冗余 |
| 2026-05-12 | `7268ff8e` | [RigMapper] Fixed a bug with comment nodes not fully enclosing selected rig mapper nodes and not tri | 修复注释节点未能完全包围选中映射节点及触发相关操作的bug |

### 维护评价

RigMapper 是一个相对较新（约1年）的**实验性**插件。从最近的提交历史（2026年5月）来看，它正处于**非常活跃的开发阶段**，近期的更新集中在修复bug、完善测试和优化工作流程上。这表明 Epic 团队正在积极迭代此插件。

**优点**：活跃维护，功能持续改进。
**风险与限制**：
1.  **实验性**：API 和功能可能会发生破坏性变更，不建议在生产项目中关键路径上使用。
2.  **文档缺失**：官方文档链接为空，目前只能依赖源码和示例学习。
3.  **需要手动启用**：`EnabledByDefault: false`，必须在项目中手动启用。

**建议**：如果你有迫切的动画重定向需求，并且愿意承担实验性功能的风险，可以尝试使用。否则，建议观望其正式版本发布。对于学习和研究 ControlRig 与动画重定向的技术，这是一个非常好的参考。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RigMapper)
- [官方文档]() (暂无)
- [测试用例]() (测试代码通常位于模块内的 `Tests` 文件夹中，例如 `Engine/Plugins/Experimental/Animation/RigMapper/Source/RigMapper/Tests/`)