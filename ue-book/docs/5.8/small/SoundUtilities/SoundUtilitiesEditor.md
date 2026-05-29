# Sound Utilities

> A variety of BP functions, objects, and utilities for audio.

| 属性 | 值 |
|---|---|
| 中文名 | 音频工具集 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器扩展） |
| 模块 | `SoundUtilities` (Runtime), `SoundUtilitiesEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-03-22 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SoundUtilities) | |

## 用途

基于源码分析，SoundUtilities 插件的核心目的是为音频设计师提供一套**快速创建和组合声音资产**的编辑器扩展工具。

其主要功能是允许用户从一个或多个已有的 `USoundWave` 资产出发，在编辑器内快速生成一种名为“Simple Sound”（`USoundSimple`）的新资产类型。这简化了声音设计的工作流程，特别是当需要测试多种声音素材的简单组合或序列时，无需手动创建复杂的 `USoundCue` 图表。

插件默认关闭（`EnabledByDefault: false`）且标记为实验性（`IsBetaVersion: true`），表明它可能是一个功能原型或用于内部快速验证的工具集，并非引擎的核心稳定功能。

## 使用场景

- **音频原型制作**：你正在快速迭代游戏的音效方案，需要尝试几种不同的声音素材组合，例如不同的脚步声、枪声变体。使用此插件可以快速从素材库中选择几个 `SoundWave`，一键生成一个可用于测试播放的 `Simple Sound` 资产，而无需打开声音图表编辑器。
- **简化音频资产管理**：你希望创建一些由多个简单声音片段按顺序或随机播放的复合声音，但又不想每次都去搭建完整的 `SoundCue`。`Simple Sound` 可能提供了一种更轻量级的资产创建方式。

## 蓝图用法

该插件主要通过编辑器扩展（右键菜单、资产创建工厂）提供功能，不直接暴露传统意义上的“蓝图节点”。其功能主要通过资产浏览器和上下文菜单触发。

### 核心资产操作

| 操作 | 说明 | 触发方式 |
|---|---|---|
| 创建简单声音 | 从选中的一个或多个 `SoundWave` 资产创建一个新的 `Simple Sound` 资产。 | 在内容浏览器中选择 `SoundWave` 资产，右键找到 “Create Simple Sound” 选项。 |
| 简单声音编辑 | 编辑 `Simple Sound` 资产的属性，例如包含的 `SoundWave` 列表。 | 双击内容浏览器中的 `Simple Sound` 资产。 |

**使用示例（操作描述）**：
1. 在内容浏览器中，选中一个或多个你希望组合的 `USoundWave` 资源（例如三个不同的枪声素材）。
2. 右键点击，在弹出的菜单中找到 `Audio` 分类下的 `Create Simple Sound` 选项并点击。
3. 插件会弹出一个工厂对话框，允许你指定新资产的名称和位置，以及确认要组合的 `SoundWave` 列表。
4. 点击创建后，一个新的 `USoundSimple` 资产会生成在指定目录。你可以双击打开它进行进一步编辑或直接使用。

## C++ 用法

此插件主要提供编辑器集成代码，运行时模块 `SoundUtilities` 可能定义了核心数据资产（如 `USoundSimple`）。以下是基于编辑器模块代码的用法示例。

### 头文件引入

要使用该插件的编辑器功能（例如在自定义工具中触发声音创建），你需要包含编辑器模块的头文件：
```cpp
#include "SoundUtilitiesEditorModule.h"
```

### 基本用法

从源码 `Public/SoundWaveAssetActionExtender.h` 可以看出，插件注册了一个静态函数来执行创建操作。

```cpp
// 假设你已经获取到了要用于创建的 SoundWave 对象数组
TArray<UObject*> SelectedSoundWaves;
SelectedSoundWaves.Add(MySoundWave1);
SelectedSoundWaves.Add(MySoundWave2);

// 创建 FToolMenuContext 并调用静态方法（这是插件内部右键菜单的调用方式）
// 注意：FToolMenuContext 的构造需要上下文信息，这里仅为示意
FToolMenuContext Context;
Context.SelectedObjects = SelectedSoundWaves;

// 调用插件提供的静态函数来触发创建流程
FSoundWaveAssetActionExtender::ExecuteCreateSimpleSound(Context);
```
*来源: `Private/SoundWaveAssetActionExtender.h` 中的函数声明。*

### 进阶用法

更高级的用法可能涉及到直接使用 `USoundSimpleFactory`。不过，由于 `UFactory` 系统高度集成于编辑器，通常不直接在游戏代码中调用。

```cpp
// 这是一个概念性示例，展示 Factory 的内部逻辑
// 实际使用中，应通过内容浏览器的创建资产流程
USoundSimpleFactory* Factory = NewObject<USoundSimpleFactory>();
Factory->SoundWaves.Add(MySoundWave1); // 设置要包含的声波

UClass* ClassToCreate = USoundSimple::StaticClass(); // 假设 USoundSimple 是目标类
UObject* NewObject = Factory->FactoryCreateNew(
    ClassToCreate,
    GetTransientPackage(), // 父包，这里用瞬态包示意
    FName("MyNewSimpleSound"), // 新资产名
    RF_NoFlags,
    nullptr, // 上下文
    GWarn // 反馈上下文
);
```
*来源: `Private/SoundSimpleFactory.h` 中 `FactoryCreateNew` 的声明。*

## Demo 示例

以下示例展示如何在 C++ 中，利用该插件的模块和工厂类，以编程方式创建一个简单的声音资产。

```cpp
// MyAudioTool.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyAudioTool.generated.h"

class USoundWave;
class USoundSimple;

UCLASS(BlueprintType)
class UMyAudioTool : public UObject
{
    GENERATED_BODY()

public:
    // 从一组 SoundWave 创建 SimpleSound 资产
    UFUNCTION(BlueprintCallable, Category = "AudioTool")
    static USoundSimple* CreateSimpleSoundFromWaves(
        const TArray<USoundWave*>& InSoundWaves,
        const FString& InAssetName,
        UPackage* InOuterPackage
    );
};
```

```cpp
// MyAudioTool.cpp
#include "MyAudioTool.h"
#include "SoundSimpleFactory.h" // 来自插件
#include "SoundSimple.h"        // 来自插件的运行时资产类
#include "AssetToolsModule.h"   // 引擎模块

USoundSimple* UMyAudioTool::CreateSimpleSoundFromWaves(
    const TArray<USoundWave*>& InSoundWaves,
    const FString& InAssetName,
    UPackage* InOuterPackage)
{
    // 获取资产工具模块
    IAssetTools& AssetTools = FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools").Get();

    // 查找 USoundSimpleFactory 类
    UClass* FactoryClass = FindObject<UClass>(ANY_PACKAGE, TEXT("USoundSimpleFactory"));
    if (!FactoryClass)
    {
        UE_LOG(LogTemp, Error, TEXT("SoundSimpleFactory class not found. Is the SoundUtilities plugin enabled?"));
        return nullptr;
    }

    // 创建工厂实例
    USoundSimpleFactory* Factory = NewObject<USoundSimpleFactory>(GetTransientPackage(), FactoryClass);
    Factory->SoundWaves = InSoundWaves; // 设置工厂属性

    // 使用资产工具和工厂创建资产
    UObject* CreatedObject = AssetTools.CreateAsset(
        InAssetName,
        FPackageName::GetLongPackagePath(InOuterPackage->GetName()),
        USoundSimple::StaticClass(), // 目标资产类
        Factory
    );

    return Cast<USoundSimple>(CreatedObject);
}
```
*这个示例结合了 `FAssetToolsModule` 和插件提供的 `USoundSimpleFactory`，演示了创建资产的底层逻辑。实际应用中，通常使用编辑器UI而不是直接调用此代码。*

## 模块依赖

从插件的模块结构和常见音频插件依赖推断，使用者需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `SoundUtilities` | 使用插件定义的运行时资产类（如 `USoundSimple`） |
| `SoundUtilitiesEditor` | 在编辑器工具或自定义资产编辑器中访问插件的编辑器功能 |
| `AssetTools` | 通过资产管理系统创建新资产 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie… | 为源文件添加 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏，属于代码规范现代化更新。 |
| 2025-06-19 | `800d7a51` | Implement feedback & additional tidbits for right-click audio actions including… | 根据反馈改进了右键音频操作的菜单功能。 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar ins… | 统一设置函数和静态变量的 DLL 导出属性，属于代码规范性修改。 |
| 2025-04-11 | `b4924cdc` | Fixing crash in simple sound | 修复了“Simple Sound”相关的崩溃问题。 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 一次涉及引擎多个插件的批量更新。 |

### 维护评价

该插件**创建于2017年**，历史悠久。从最近的提交记录看，其维护状态为**低活跃维护**。
1.  **近期活动**：在2025年有几次提交，但主要是代码规范更新（如 `UE_INLINE_GENERATED_CPP_BY_NAME`）和一次关键的崩溃修复。
2.  **功能更新**：缺乏重大的功能性更新，最近一次功能相关提交是2025年6月对右键菜单的反馈调整。
3.  **稳定性**：标记为实验性（`IsBetaVersion: true`），默认不启用，表明Epic官方可能不认为它是经过全面验证的生产就绪功能。
4.  **结论**：此插件似乎是一个**稳定但不再积极开发**的工具集。它提供了基本功能，但可能不会获得新特性。对于快速原型制作或满足现有工作流，可以使用，但不建议基于它构建核心音频系统。考虑到其实验性质和长期未获实质性更新，在重要项目中使用需谨慎。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SoundUtilities)
- 官方文档：无
- 测试用例：未在提供的资料中发现独立的自动化测试文件。