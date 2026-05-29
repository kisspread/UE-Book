# Customizable Sequencer Tracks (Experimental)

> Library that provides a blueprintable track type that can be added to sequencer

| 属性 | 值 |
|---|---|
| 中文名 | 可定制序列器轨道 |
| 分类 | Runtime |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CustomizableSequencerTracks` (Runtime), `CustomizableSequencerTracksEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-08-11 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/CustomizableSequencerTracks) | |

## 用途

该插件提供了一个用于扩展 Unreal Engine 序列器 (Sequencer) 的框架。其核心目的是允许开发者**完全使用蓝图**来定义和实现自定义的轨道类型、区段类型以及轨道实例。解决了当内置的 Sequencer 轨道（如变换、动画等）无法满足项目特定需求时，需要编写 C++ 代码来扩展 Sequencer 的难题。通过这个插件，你可以创建用于控制自定义游戏逻辑、特殊材质参数或任何随时间变化的属性的动画轨道，而无需接触 C++。

## 使用场景

- 你需要为 Sequencer 添加一条全新的、功能自定义的轨道，用于动画化一个特定的游戏玩法参数（如角色的怒气值、环境的天气强度）。
- 你希望用蓝图实现一个 Sequencer 轨道的内部逻辑，例如，当该轨道播放时，执行特定的游戏事件或更新特定的组件。
- 你需要为自定义的 Actor 或组件在 Sequencer 中提供专门的动画控制轨道。

## 蓝图用法

### 核心配置类

| 属性 | 说明 | 所在类 |
|---|---|---|
| `TrackType` | 定义轨道类型：`RootTrack`（根轨道）或 `ObjectTrack`（对象轨道） | `USequencerTrackBP` |
| `SupportedObjectType` | 当`TrackType`为`ObjectTrack`时，指定此轨道支持的对象类型 | `USequencerTrackBP` |
| `DefaultSectionType` | 此轨道默认使用的区段蓝图类 | `USequencerTrackBP` |
| `SupportedSections` | 此轨道支持的所有区段蓝图类列表 | `USequencerTrackBP` |
| `TrackInstanceType` | 定义此轨道的实例行为，用于在运行时处理轨道逻辑 | `USequencerTrackBP` |
| `bSupportsMultipleRows` | 是否支持在轨道内放置多个并行的区段 | `USequencerTrackBP` |
| `bSupportsBlending` | 是否支持区段间的混合与缓动 | `USequencerTrackBP` |
| `Icon` | 轨道在 Sequencer 编辑器中显示的图标 | `USequencerTrackBP` |

### 区段可实现事件

| 事件 | 说明 | 所在类 |
|---|---|---|
| `ImportEntityImpl` | 重写此事件以定义如何将此区段数据导入到实体系统中（高级用法） | `USequencerSectionBP` |

### 轨道实例蓝图可实现事件

| 事件 | 说明 | 所在类 |
|---|---|---|
| `K2_OnInitialize` | 轨道实例被创建并初始化时调用 | `USequencerTrackInstanceBP` |
| `K2_OnUpdate` | 每帧（或每个评估点）更新时调用，用于应用区段数据 | `USequencerTrackInstanceBP` |
| `K2_OnBeginUpdateInputs` | 在开始处理输入（即评估其包含的区段）之前调用 | `USequencerTrackInstanceBP` |
| `K2_OnInputAdded` | 当一个新的区段输入被添加到轨道时调用 | `USequencerTrackInstanceBP` |
| `K2_OnInputRemoved` | 当一个区段输入从轨道移除时调用 | `USequencerTrackInstanceBP` |
| `K2_OnEndUpdateInputs` | 在所有输入处理完成后调用 | `USequencerTrackInstanceBP` |
| `K2_OnDestroyed` | 轨道实例被销毁时调用 | `USequencerTrackInstanceBP` |

### 轨道实例蓝图可调用函数

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAnimatedObject` | 获取当前正在被此轨道实例动画化的对象 | `USequencerTrackInstanceBP` |
| `GetInputs` | 获取当前所有输入（区段）的列表 | `USequencerTrackInstanceBP` |
| `GetNumInputs` | 获取当前输入（区段）的数量 | `USequencerTrackInstanceBP` |
| `GetInput` | 根据索引获取指定的输入（区段） | `USequencerTrackInstanceBP` |

### 使用示例（蓝图描述）

1.  **创建轨道蓝图**：创建一个继承自 `SequencerTrack` 的蓝图类（例如 `BP_MyCustomTrack`）。在类默认值中设置 `TrackType`（如 `ObjectTrack`），`SupportedObjectType`（如 `StaticMeshActor`），`DefaultSectionType`（指向你下一步创建的区段蓝图），以及 `TrackInstanceType`（指向你之后创建的实例蓝图）。
2.  **创建区段蓝图**：创建一个继承自 `SequencerSection` 的蓝图类（例如 `BP_MyCustomSection`）。这个类主要用于数据承载，通常不需要额外逻辑。
3.  **创建轨道实例蓝图**：创建一个继承自 `SequencerTrackInstance` 的蓝图类（例如 `BP_MyCustomTrackInstance`）。在此蓝图中，重写 `K2_OnUpdate` 事件，使用 `GetAnimatedObject` 和 `GetInputs` 获取当前数据，并应用自定义逻辑（例如，根据区段中的曲线值设置 `AnimatedObject` 上的某个材质参数）。
4.  **使用**：在 Sequencer 编辑器中，为 `SupportedObjectType` 指定的对象添加轨道，应该能看到你自定义的 `BP_MyCustomTrack` 可选。添加后，即可在其上创建区段并动画化。

## C++ 用法

### 头文件引入

```cpp
#include "SequencerTrackBP.h"
#include "SequencerSectionBP.h"
#include "SequencerTrackInstanceBP.h"
```

### 基本用法

该插件的主要是蓝图驱动的，但可以在 C++ 中继承和扩展这些基类来实现更底层的控制。

```cpp
// 来源：Engine/Plugins/MovieScene/CustomizableSequencerTracks/Source/CustomizableSequencerTracks/Public/SequencerSectionBP.h

// 自定义一个 C++ 版本的区段（较少用，蓝图更直接）
class UMyCustomSectionCPP : public USequencerSectionBP
{
    GENERATED_BODY()
public:
    UMyCustomSectionCPP(const FObjectInitializer& ObjInit) : Super(ObjInit) {}

    // 可以重写导入实体逻辑
    virtual void ImportEntityImpl(UMovieSceneEntitySystemLinker* EntityLinker, const FEntityImportParams& Params, FImportedEntity* OutImportedEntity) override
    {
        Super::ImportEntityImpl(EntityLinker, Params, OutImportedEntity);
        // 自定义实体生成逻辑...
    }
};
```

### 进阶用法

在 C++ 中创建完整的轨道系统。这通常是在需要极致性能或与现有 C++ 子系统深度集成时考虑。

```cpp
// 伪代码示例，展示C++中与蓝图类交互
void SomeFunction()
{
    // 假设你有一个蓝图创建的轨道资产的引用
    USequencerTrackBP* MyBlueprintTrack = ...;
    if (MyBlueprintTrack)
    {
        // 访问其属性
        bool bBlend = MyBlueprintTrack->bSupportsBlending;
        UClass* ObjType = MyBlueprintTrack->SupportedObjectType.Get();

        // 在运行时，你可以获取该轨道关联的实例
        // 注意：获取实例是Sequencer内部管理器的工作，通常不直接这样调用
        // USequencerTrackInstanceBP* Instance = ...;
        // if (Instance)
        // {
        //     UObject* Target = Instance->GetAnimatedObject();
        //     TArray<FSequencerTrackInstanceInput> Inputs = Instance->GetInputs();
        // }
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何定义一个自定义的轨道实例类头文件。实际的轨道和区段通常用蓝图定义。

```cpp
// MyCustomTrackInstance.h
#pragma once

#include "SequencerTrackInstanceBP.h"
#include "MyCustomTrackInstance.generated.h"

UCLASS(Blueprintable, DisplayName=MyCustomTrackInstance)
class UMyCustomTrackInstance : public USequencerTrackInstanceBP
{
    GENERATED_BODY()

public:
    // 重写蓝图事件，提供C++实现
    virtual void K2_OnInitialize_Implementation() override
    {
        // 初始化逻辑
        UE_LOG(LogTemp, Log, TEXT("MyCustomTrackInstance Initialized for object: %s"), *GetNameSafe(GetAnimatedObject()));
    }

    virtual void K2_OnUpdate_Implementation() override
    {
        // 核心更新逻辑
        UObject* AnimatedObject = GetAnimatedObject();
        TArray<FSequencerTrackInstanceInput> Inputs = GetInputs();

        for (const FSequencerTrackInstanceInput& Input : Inputs)
        {
            if (Input.Section)
            {
                // 从Input.Section中读取数据（例如，通过自定义函数获取曲线值）
                // float Value = Input.Section->GetCustomValueAtTime(Context.GetTime());
                // 应用这个值到AnimatedObject上
            }
        }
    }
};
```

## 模块依赖

无特殊依赖（仅标准 MovieScene/MovieSceneTracks 等 Sequencer 核心模块）。

| 模块 | 用途 |
|---|---|
| `MovieScene` | Sequencer 的核心框架模块 |
| `MovieSceneTracks` | Sequencer 内置轨道的实现，提供了基类 |
| `EntitySystem` | 用于 Sequencer 的新版实体评估系统 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-01-29 | `c262d4f9` | Sequencer: Outliner UX improvements | Sequencer 大纲视图用户体验改进 |
| 2023-12-09 | `64658cf6` | GetAssetRegistryTags deprecation: Make the old GetAssetRegistryTags and related functions deprecated | 将旧版 `GetAssetRegistryTags` 函数标记为弃用 |
| 2023-07-19 | `574e8e6e` | Add a ShortName to modules that generated paths over the 200 chars limit and a few modules that were | 为路径过长的模块添加简称 |
| 2023-05-16 | `de8db5ff` | Converting ARO-facing raw pointers to TObjectPtr ahead of raw pointer ARO API deprecation. | 将面向资产注册的原始指针转换为 `TObjectPtr` 以适配新API |
| 2023-02-21 | `d5a5a356` | Remove unnecessary Public and Private entries for the current module being added to PublicIncludePat | 清理构建配置中的冗余项 |

### 维护评价

该插件自 **2020年8月** 创建以来，一直处于**实验性**状态（`IsBetaVersion=true`，默认不启用）。最近的更新（截至2024年1月）主要是围绕 UE5 编译警告修复、API 弃用标记和内部清理，没有新的功能性改进。这表明 Epic 可能已将其视为一个稳定但暂无进一步开发计划的功能原型。

**结论**：该插件**功能可用，但缺乏维护和官方支持**。它对于需要蓝图化扩展 Sequencer 的项目来说是一个有价值的工具，尤其适合原型开发或特定需求。然而，对于需要长期稳定支持的核心生产功能，建议评估使用官方蓝图函数库或其他更成熟的扩展方案。使用前请充分测试，注意其可能包含的未知问题或限制。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/CustomizableSequencerTracks)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Sequencer) （相关测试可能在此目录下）