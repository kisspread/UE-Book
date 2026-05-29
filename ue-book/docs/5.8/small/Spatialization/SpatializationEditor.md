# Spatialization

> Plugin featuring a variety of basic audio spatialization solutions.

| 属性 | 值 |
|---|---|
| 中文名 | 空间化 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Spatialization` (Runtime), `SpatializationEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-01-25 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Spatialization) | |

## 用途
此插件提供了一组基础的音频空间化解决方案。它主要用于实现3D音频效果，使游戏或应用中的声音具有方向感和距离感，从而增强沉浸感。插件核心功能包含基于ITD（Interaural Time Difference，双耳时间差）算法的双耳空间化技术，可以模拟声音在左右耳之间的到达时间差异，产生精确的空间定位感。它通过可配置的资产来管理空间化参数。

## 使用场景
- **3D游戏**：当你的游戏需要让玩家通过声音判断敌人或事件的方向时（如脚步声、枪声来自左侧还是右侧）。
- **VR/AR 应用**：为了提供沉浸式体验，声音需要精确地跟随头部的转动和声源的移动而变化。
- **可视化音频调试**：在开发过程中，需要调整和测试不同空间化算法或参数对最终听感的影响。

## 蓝图用法
此插件主要通过配置资产（Settings Assets）进行工作，未提供直接暴露给蓝图的高频操作节点。开发者主要通过编辑器界面创建和管理空间化设置资产。

### 核心资产
| 资产类型 | 说明 | 所在类 |
|---|---|---|
| `ITD Source Spatialization Settings` | 基于ITD算法的空间化设置资产。用于配置双耳空间化行为的具体参数。 | `UITDSpatializationSourceSettings` |

### 使用示例（资产创建）
1.  在内容浏览器（Content Browser）中，右键点击。
2.  选择 **音频 (Audio)** -> **高级 (Advanced)** -> **双耳空间化 (Binaural Spatialization)** -> **ITD源空间化设置 (ITD Source Spatialization Settings)**。
3.  为新资产命名。
4.  双击打开资产，调整其内部参数以控制空间化效果（具体参数取决于引擎版本和子模块实现）。
5.  将该资产赋给需要空间化处理的声音源（Sound Source）或声音衰减（Sound Attenuation）设置。

## C++ 用法
此插件主要提供编辑器扩展以创建设置资产，以及运行时模块进行音频处理。基础用法涉及模块的加载和资产的创建。

### 头文件引入
```cpp
#include "SpatializationEditorModule.h"
#include "ITDSpatializationSourceSettingsFactory.h"
```

### 基本用法
此示例展示了如何通过代码创建一个 ITD 空间化设置资产。通常由编辑器模块内的工厂类处理。
（来源文件: `Private/AssetDefinition_ITDSpatializationSettings.h`, `Public/ITDSpatializationSourceSettingsFactory.h`）
```cpp
// 获取编辑器模块
ISpatializationEditorModule& EditorModule = FModuleManager::LoadModuleChecked<ISpatializationEditorModule>("SpatializationEditor");

// 创建资产工厂实例（通常由系统内部调用，但可用于了解流程）
UITDSpatializationSettingsFactory* Factory = NewObject<UITDSpatializationSettingsFactory>();
UObject* NewAsset = Factory->FactoryCreateNew(
    UITDSpatializationSourceSettings::StaticClass(),
    InParent, // 资产存储的父包 (UPackage)
    AssetName,
    RF_Public | RF_Standalone,
    nullptr,
    GWarn
);
```

### 进阶用法
在运行时，空间化处理由 `Spatialization` 模块在音频线程上自动完成。开发者的主要交互点是设置上述的 `UITDSpatializationSourceSettings` 资产。可以将该资产的引用赋给 `USoundSource` 或 `FSoundAttenuationSettings` 的相关属性，以启用特定的空间化行为。

## Demo 示例
一个演示如何创建 ITD 空间化设置资产的简化示例。
*（注意：此插件为框架和设置，实际音频处理由引擎音频子系统调用，以下为核心资产创建逻辑）*

### ITDSpatializationSettingsDemo.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "ITDSpatializationSettingsDemo.generated.h"

UCLASS()
class UITDSpatializationSettingsDemoLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    // 蓝图中可用的函数，用于创建一个默认的ITD空间化设置资产
    UFUNCTION(BlueprintCallable, Category = "Spatialization Demo", meta = (WorldContext = "WorldContextObject"))
    static UITDSpatializationSourceSettings* CreateITDSpatializationSettings(UObject* WorldContextObject, const FString& AssetName, UPackage* ParentPackage);
};
```

### ITDSpatializationSettingsDemo.cpp
```cpp
#include "ITDSpatializationSettingsDemo.h"
#include "ITDSpatializationSourceSettingsFactory.h"
#include "ITDSpatializationSourceSettings.h"

UITDSpatializationSourceSettings* UITDSpatializationSettingsDemoLibrary::CreateITDSpatializationSettings(
    UObject* WorldContextObject, const FString& AssetName, UPackage* ParentPackage)
{
    if (!ParentPackage)
    {
        UE_LOG(LogTemp, Error, TEXT("ParentPackage is null."));
        return nullptr;
    }

    // 使用插件内注册的工厂类来创建对象
    UITDSpatializationSettingsFactory* Factory = NewObject<UITDSpatializationSettingsFactory>();
    UObject* NewAsset = Factory->FactoryCreateNew(
        UITDSpatializationSourceSettings::StaticClass(),
        ParentPackage,
        FName(*AssetName),
        RF_Public | RF_Standalone,
        nullptr,
        GWarn
    );

    return Cast<UITDSpatializationSourceSettings>(NewAsset);
}
```

## 模块依赖
| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 更新了内容浏览器中的“添加”菜单，音频相关资产的菜单结构可能发生了变化。 |
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 代码优化：为源文件添加了UE_INLINE_GENERATED_CPP_BY_NAME宏，提升编译效率。 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar ins | 对代码进行了符号可见性调整，确保所有方法和静态变量在动态链接库（DLL）中正确导出。 |

### 维护评价
该插件创建于2019年初，已有约7年历史，属于“老古董”级别。其最近一次实质性的功能性更新（对内容浏览器菜单的调整）发生在2026年4月，表明它仍在被跟踪和维护，以适应引擎的最新变化（如编辑器界面重构）。然而，核心功能在近年来没有重大扩展或Bug修复的记录。由于它是基础音频解决方案的一部分，且Epic仍在维护，其功能是稳定可靠的。对于需要基础双耳空间化功能的项目，可以继续使用，但应意识到它并非一个处于快速迭代中的前沿模块。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Spatialization)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Runtime/AudioMixer/Tests) （音效测试通常位于此目录）