# Audio Properties

> Allows to define arbitrary derivable sets of properties to be injected in any audio asset

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频属性资产、绑定资产） |
| 模块 | `AudioProperties` (Editor), `AudioPropertiesEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-14 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AudioProperties) | |

## 用途

AudioProperties 插件为 Unreal Engine 的音频系统提供了一套可扩展、可继承的属性管理系统。它解决的核心问题是：如何在不同的音频资产（如 Sound Wave、Sound Cue、MetaSound 等）之间标准化、共享和覆盖一组自定义的音频相关属性（例如混响参数、空间化设置、音量衰减曲线等）。

该插件引入了两个关键资产类型：
1.  **Audio Properties Sheet Asset**：一个“属性表”资产，用于定义一组属性及其默认值。这些属性表可以形成一个继承链，子表可以继承父表的属性，并可以选择性地覆盖特定属性的值。
2.  **Audio Properties Bindings**：一个“绑定”资产，用于将一个属性表中的属性“注入”到一个具体的音频资产实例中。它允许在资产实例级别对属性表中的值进行本地覆盖。

通过这种方式，音频设计师可以创建一套基础的音频属性模板（属性表），然后将其应用到多个音频资产上，确保参数的一致性，同时又允许在具体实例上进行微调。

## 使用场景

-   你正在开发一个大型游戏项目，需要为所有环境音效（风声、雨声、水流声）统一设置一组空间化和滤波参数 → 创建一个“环境音效基础属性表”，然后将其绑定到各个具体的环境音效资产上。
-   你希望为游戏中的所有武器音效定义一个标准的“武器音效属性集”（如尾音衰减时间、距离衰减模型），但不同武器（手枪、步枪、火箭筒）需要不同的具体数值 → 创建一个“武器音效基础属性表”作为父表，然后为每类武器创建子表覆盖特定值，最后将子表绑定到对应的音效资产。
-   你需要在编辑器中快速预览和调整一组音频资产的共同参数，而无需逐个打开每个资产进行修改 → 通过修改它们共同引用的属性表来实现批量调整。

## 蓝图用法

该插件主要提供编辑器工具和资产类型，其核心功能（创建和编辑属性表、绑定）主要在编辑器 UI 中完成。蓝图中主要涉及资产的创建和引用。

### 核心资产类

| 资产类型 | 说明 | 所在类 |
|---|---|---|
| `Audio Properties Sheet` | 属性表资产，定义可继承的属性集。 | `UAudioPropertiesSheetAsset` |
| `Audio Properties Bindings` | 属性绑定资产，将属性表注入到音频资产并支持本地覆盖。 | `UAudioPropertiesBindings` |

### 使用示例（蓝图描述）

1.  **创建属性表**：在内容浏览器中右键 -> Audio -> Audio Properties Sheet。在打开的编辑器中，可以添加属性（如 `float`, `bool`, `FVector` 等），设置默认值，并指定一个父属性表以实现继承。
2.  **创建绑定**：在内容浏览器中右键 -> Audio -> Audio Properties Bindings。在该资产的细节面板中，指定要使用的“属性表”，然后将其拖拽到目标音频资产（如一个 Sound Wave）的细节面板中对应的“属性绑定”插槽上。
3.  **覆盖属性**：在目标音频资产的细节面板中，找到被注入的属性部分。每个属性旁边通常会有一个复选框或覆盖控件，允许你启用本地覆盖并输入新的值，这个值将只影响当前资产实例。

## C++ 用法

该插件主要面向编辑器扩展和工具开发。其核心运行时数据结构（如 `FAudioPropertiesSheet`）通常通过资产系统进行序列化和管理，而非直接在游戏逻辑中频繁操作。

### 头文件引入

```cpp
#include "AudioPropertiesSheet.h" // 核心数据结构
#include "AudioPropertiesBindings.h" // 绑定资产
#include "AudioPropertiesSheetAsset.h" // 属性表资产
```

### 基本用法（资产操作）

以下代码展示了如何在 C++ 中创建和操作音频属性表资产（通常在编辑器工具或命令行中使用）。

```cpp
// 来源：基于 AudioPropertiesSheetAssetFactory 和 AudioPropertiesSheetAssetBuilder 的推断
#include "AudioPropertiesSheetAsset.h"
#include "AudioPropertiesSheetAssetFactory.h"

// 创建一个新的属性表资产
UAudioPropertiesSheetAsset* CreateNewPropertySheet(UObject* InParent, FName Name)
{
    UAudioPropertiesSheetAssetFactory* Factory = NewObject<UAudioPropertiesSheetAssetFactory>();
    UObject* NewAsset = Factory->FactoryCreateNew(
        UAudioPropertiesSheetAsset::StaticClass(),
        InParent,
        Name,
        RF_Public | RF_Standalone,
        nullptr,
        GWarn
    );
    return Cast<UAudioPropertiesSheetAsset>(NewAsset);
}

// 从现有 UObject 的属性构建属性表（概念性示例）
// 实际使用通常通过编辑器 UI 中的 SAudioPropertiesSheetBuilderWidget 完成
void BuildSheetFromObject(const UObject* SourceObject, UAudioPropertiesSheetAsset* TargetSheet)
{
    // FAudioPropertiesSheetAssetBuilder::BuildPropertySheetFromPropertyDataArray(...)
    // 此函数需要详细的属性请求数组，通常由编辑器工具构建。
}
```

### 进阶用法（细节面板定制）

该插件提供了 `FAudioPropertiesDetailsInjector` 类，用于在自定义资产的细节面板中正确显示和编辑由属性表注入的属性。

```cpp
// 来源：基于 AudioPropertiesDetailsInjector.h
#include "AudioPropertiesDetailsInjector.h"

class FMyAudioAssetDetails : public IDetailCustomization
{
public:
    static TSharedRef<IDetailCustomization> MakeInstance() { return MakeShareable(new FMyAudioAssetDetails); }

    virtual void CustomizeDetails(IDetailLayoutBuilder& DetailBuilder) override
    {
        // 获取属性绑定属性句柄
        TSharedRef<IPropertyHandle> BindingsPropertyHandle = DetailBuilder.GetProperty(GET_MEMBER_NAME_CHECKED(UMyAudioAsset, PropertyBindings));

        // 创建注入器并应用定制
        FAudioPropertiesDetailsInjector Injector;
        Injector.CustomizeInjectedPropertiesDetails(DetailBuilder, BindingsPropertyHandle);
        Injector.BindDetailCustomizationToPropertySheetChanges(DetailBuilder, BindingsPropertyHandle);
    }
};
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何定义一个使用音频属性绑定的自定义资产类。

**MyAudioAsset.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "AudioPropertiesBindings.h"
#include "MyAudioAsset.generated.h"

UCLASS(BlueprintType)
class MYPROJECT_API UMyAudioAsset : public UObject
{
    GENERATED_BODY()

public:
    // 音频属性绑定，用于注入来自属性表的属性
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Audio")
    TObjectPtr<UAudioPropertiesBindings> PropertyBindings;

    // 其他音频资产相关的属性...
    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Audio")
    USoundBase* Sound;
};
```

**MyAudioAssetDetails.cpp**
```cpp
#include "MyAudioAssetDetails.h"
#include "DetailLayoutBuilder.h"
#include "AudioPropertiesDetailsInjector.h"

TSharedRef<IDetailCustomization> FMyAudioAssetDetails::MakeInstance()
{
    return MakeShareable(new FMyAudioAssetDetails());
}

void FMyAudioAssetDetails::CustomizeDetails(IDetailLayoutBuilder& DetailBuilder)
{
    // 获取 PropertyBindings 属性句柄
    TSharedRef<IPropertyHandle> BindingsHandle = DetailBuilder.GetProperty(GET_MEMBER_NAME_CHECKED(UMyAudioAsset, PropertyBindings));

    // 使用插件提供的注入器来定制细节面板
    FAudioPropertiesDetailsInjector Injector;
    Injector.CustomizeInjectedPropertiesDetails(DetailBuilder, BindingsHandle);
    Injector.BindDetailCustomizationToPropertySheetChanges(DetailBuilder, BindingsHandle);
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

- 2026-04-14 `01c9ce5d` [ContentBrowser] New Add Menu Audio Menu
- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-02-12 `68131ef1` Instantiate Audio Properties Name Parser when creating new Property Sheet, as this is the de facto d
- 2026-01-15 `738ab46a` Fixed localization warnings
- 2026-01-14 `4b3fba09` Walk UClass inheritance when overriding property details from a property sheet to avoid visualizatio

### 维护评价

-   **创建时间**：非常新（约 0 年）。
-   **实验性状态**：`IsExperimentalVersion = true` 且 `EnabledByDefault = false`，表明这是一个处于早期开发或验证阶段的功能。
-   **维护活跃度**：作为实验性插件，其更新频率和内容可能不稳定，可能随时发生重大变更或被废弃。
-   **已知限制**：作为实验性功能，API 和资产格式可能不向后兼容。文档和社区支持可能有限。
-   **推荐使用**：**谨慎使用**。仅适用于愿意承担实验性功能风险的项目，或用于原型开发和内部工具。不建议在需要长期稳定支持的生产项目中作为核心依赖。建议密切关注引擎更新日志中关于此插件的状态变化。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AudioProperties)
-   [官方文档]() (暂无)