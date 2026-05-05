# Subsonic

> Subsonic is a high-level audio authoring and playback system. This plugin is experimental and as such there is no guarantee of backward compatibility.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器 Slate 图标资源） |
| 模块 | `SubsonicCore` (Runtime), `SubsonicEditor` (Runtime), `SubsonicEngine` (Runtime), `SubsonicEngineTest` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic) | |

## 用途

Subsonic 是一个面向音频设计师的**高级音频事件编排与回放系统**。它解决的核心问题是：如何以结构化、可复用的方式定义复杂的音频事件序列，并在运行时高效触发。

与传统的直接播放音频资产不同，Subsonic 引入了 **Event Collection（事件集合）** 的概念——一个资产中可以定义多个音频事件，每个事件包含一组有序的 Action（动作），并支持集合级和事件级的参数化 Property Bag，通过属性绑定机制将参数传递给具体的音频动作。

该插件的核心设计目标：
- **事件驱动的音频编排**：将音频播放抽象为"事件→动作"的层次结构
- **参数化与属性绑定**：支持在集合和事件级别定义参数，并通过绑定机制连接到动作属性
- **编辑器内试听**：提供专用编辑器，支持在编辑器中直接试听事件效果
- **可扩展的动作系统**：通过 Action Struct 缓存机制支持动态注册新的动作类型

## 使用场景

- 你在制作一个需要复杂音效触发系统的游戏（如 RPG 中的技能音效、环境音效组合）→ 用 Subsonic Event Collection 组织和管理音频事件
- 你需要在编辑器中快速试听和迭代音频事件效果 → 用 Subsonic 编辑器的 Audition 功能
- 你希望音频事件支持参数化（如音量、音调随游戏状态变化）→ 用 Subsonic 的 Property Bag 和属性绑定系统
- 你需要将音频事件逻辑与具体音频资产解耦 → 用 Subsonic 的事件-动作分层架构

## 蓝图用法

> ⚠️ 当前提供的源码主要为编辑器模块，运行时蓝图 API 需参考 SubsonicCore 和 SubsonicEngine 模块。

### 核心资产

| 资产类型 | 说明 |
|---|---|
| `USubsonicEventCollection` | Subsonic 事件集合资产，包含多个音频事件及其动作定义 |

### 编辑器子系统

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RebuildActionStructChildCache` | 重建动作结构体子类缓存（新模块加载/卸载后调用） | `USubsonicEditorSubsystem` |
| `ForEachActionStruct` | 遍历所有已注册的动作结构体类型 | `USubsonicEditorSubsystem` |

## C++ 用法

### 头文件引入

```cpp
// 编辑器模块
#include "SubsonicEventCollectionEditor.h"
#include "SubsonicEditorSubsystem.h"
#include "SubsonicEventCollectionObjects.h"

// 核心模块
#include "SubsonicEventCollection.h"
```

### 基本用法：访问编辑器子系统

```cpp
// 获取 Subsonic 编辑器子系统，用于查询已注册的动作结构体
USubsonicEditorSubsystem* Subsystem = GEditor->GetEditorSubsystem<USubsonicEditorSubsystem>();
if (Subsystem)
{
    // 遍历所有已注册的动作结构体类型
    Subsystem->ForEachActionStruct([](const UScriptStruct& Struct)
    {
        UE_LOG(LogTemp, Log, TEXT("Registered action struct: %s"), *Struct.GetName());
    });
}
```

### 进阶用法：打开事件集合编辑器

```cpp
// 通过资产编辑器工具包打开 Subsonic Event Collection 编辑器
USubsonicEventCollection* EventCollection = LoadObject<USubsonicEventCollection>(nullptr, TEXT("/Game/Audio/MyEventCollection"));
if (EventCollection)
{
    TSharedRef<UE::Subsonic::Editor::FEventCollectionEditor> Editor = MakeShared<UE::Subsonic::Editor::FEventCollectionEditor>();
    Editor->Init(EToolkitMode::Standalone, TSharedPtr<IToolkitHost>(), *EventCollection);
}
```

### 进阶用法：属性绑定扩展

```cpp
// FSubsonicPropertyBindingExtension 为属性提供绑定到 Subsonic 参数的能力
// 在编辑器中，属性会自动显示绑定下拉菜单（除非标记了 NoBinding 元数据）
// 绑定源包括集合级和事件级的 Property Bag 参数
```

## Demo 示例

```cpp
// SubsonicDemoActor.h
#pragma once

#include "GameFramework/Actor.h"
#include "SubsonicDemoActor.generated.h"

class USubsonicEventCollection;

UCLASS()
class ASubsonicDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ASubsonicDemoActor();

    // 引用 Subsonic 事件集合资产
    UPROPERTY(EditAnywhere, Category = "Audio")
    TObjectPtr<USubsonicEventCollection> EventCollection;

    // 要触发的事件名称
    UPROPERTY(EditAnywhere, Category = "Audio")
    FName EventName;

    // 触发音频事件
    UFUNCTION(BlueprintCallable, Category = "Audio")
    void TriggerAudioEvent();
};
```

```cpp
// SubsonicDemoActor.cpp
#include "SubsonicDemoActor.h"
#include "SubsonicEventCollection.h"

ASubsonicDemoActor::ASubsonicDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ASubsonicDemoActor::TriggerAudioEvent()
{
    if (!EventCollection)
    {
        UE_LOG(LogTemp, Warning, TEXT("No Event Collection assigned"));
        return;
    }

    // 通过事件集合触发指定事件
    // 具体的播放 API 取决于 SubsonicCore/SubsonicEngine 模块的运行时接口
    UE_LOG(LogTemp, Log, TEXT("Triggering event: %s from collection: %s"),
        *EventName.ToString(), *EventCollection->GetName());
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SubsonicCore` | Subsonic 核心数据结构（事件、动作、集合定义） |
| `SubsonicEngine` | Subsonic 运行时引擎（音频回放逻辑） |
| `AudioWidgets` | 音频编辑器 UI 组件（Slate 样式继承自 FAudioWidgetsStyle） |
| `PropertyAccessEditor` | 属性绑定编辑器支持（用于参数绑定下拉菜单） |
| `StructUtils` | PropertyBag 支持（用于参数化属性容器） |

## 维护状态

### 近期更新

- 2026-04-23 `129c3dc2` Fix/silence PVS warnings
- 2026-04-14 `01c9ce5d` [ContentBrowser] New Add Menu Audio Menu
- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-04-13 `cb602f27` Subsonic: Subscriber implementation consolidation and removal of action and event scope
- 2026-04-02 `cd4230bd` Remove code optimization submitted by mistake

> ⚠️ 由于创建时间为 2026-04-02（未来日期），此数据可能来自测试分支或时间戳异常。

### 维护评价

- **实验性插件**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，明确标注不保证向后兼容
- **新建插件**：创建时间极近，属于全新引入的功能模块
- **Epic 官方维护**：由 Epic Games, Inc. 创建和维护
- **模块划分清晰**：Core/Editor/Engine/Test 四模块架构，职责分离良好
- **编辑器功能完整**：包含完整的资产编辑器、属性自定义、Slate 样式、试听功能

**推荐程度**：⚠️ 谨慎使用。作为实验性插件，API 可能在后续版本中发生重大变更。适合用于原型开发和功能探索，不建议在生产环境中深度依赖。建议关注后续版本的稳定性声明。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Subsonic)
- [官方文档]()（暂无）