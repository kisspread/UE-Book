# Audio Properties

> Allows to define arbitrary derivable sets of properties to be injected in any audio asset

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产类） |
| 模块 | `AudioProperties` (Editor), `AudioPropertiesEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-14 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AudioProperties) | |

## 用途

AudioProperties 插件提供了一个用于管理音频资产参数的系统。它解决的核心问题是：如何在复杂的音频资产（如声音波形、音效类）上定义、组织和应用大量可配置的属性，并支持属性的继承与覆盖。

该插件允许设计师创建一个“属性表”（`UAudioPropertiesSheetAsset`），在其中定义一组属性（如音量、音高、衰减距离等）。这些属性表可以形成继承链，子表可以覆盖父表的属性值。然后，通过一个“解析器”（`UAudioPropertiesParserBase` 及其子类），可以将属性表中的值自动映射并应用到目标音频资产（如 `USoundWave` 或 `USoundCue`）的对应属性上。这极大地简化了音频资产的参数管理，特别是在需要批量调整或动态配置音频行为的场景中。

## 使用场景

- 你正在开发一个开放世界游戏，需要为数百种环境音效（风声、水流、城市噪音）统一管理音量、音高和空间化参数 → 使用 AudioProperties 创建一个基础环境音效属性表，所有音效资产引用它，修改一处即可全局生效。
- 你的游戏有一个动态音频系统，需要根据游戏状态（如战斗、潜行）调整所有音效的参数 → 创建不同的属性表（战斗表、潜行表），在运行时切换应用的属性表，即可改变所有关联音效的行为。
- 你需要为音频资产定义一套标准的、可扩展的元数据（如“情感标签”、“优先级”），并希望这些数据能方便地注入到资产中 → 使用 AudioProperties 定义这些自定义属性，并通过解析器注入。

## 蓝图用法

该插件的核心操作主要在编辑器资产中进行，蓝图可调用的运行时函数较少。主要的交互通过资产编辑器完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FitPropertiesForValidation` | （编辑器内调用）根据解析器的验证规则，调整当前属性表的属性结构，使其符合目标资产的要求。 | `UAudioPropertiesSheetAsset` |
| `CopyToObjectProperties` | （编辑器内调用）将当前属性表中的属性值复制到指定的目标 UObject 上。 | `UAudioPropertiesSheetAsset` |
| `BindPropertiesCopyToSheetChanges` | （编辑器内调用）将目标 UObject 的属性变化绑定到属性表的变更事件上，实现实时同步。 | `UAudioPropertiesSheetAsset` |

### 使用示例（蓝图描述）

1.  **创建属性表资产**：在内容浏览器中右键，选择 `Audio > Audio Properties Sheet` 创建一个新的属性表资产。
2.  **编辑属性**：打开资产，在 `Properties` 面板中添加你需要的属性（如 `Volume` (Float), `Pitch` (Float), `bSpatialize` (Bool)）。
3.  **设置继承**：在 `Parent` 字段中选择另一个属性表资产，当前表将继承父表的所有属性，并可以覆盖特定属性。
4.  **配置解析器**：在 `Parser` 字段中选择一个解析器（如 `Audio Properties Parser Name Match`），它决定了如何将属性表中的值映射到目标资产。
5.  **应用到资产**：在目标音频资产（如 `Sound Wave`）的细节面板中，找到由该插件添加的界面，选择你创建的属性表。属性表中的值将根据解析器的规则被应用到该资产的对应属性上。

## C++ 用法

### 头文件引入

```cpp
#include "AudioPropertiesSheet.h"
#include "AudioPropertiesParserBase.h"
#include "AudioPropertiesParserNameMatch.h"
#include "AudioPropertiesBindings.h"
```

### 基本用法

以下代码演示了如何在 C++ 中创建和操作音频属性表资产。

```cpp
// 来源：基于 AudioPropertiesSheet.h 和 AudioPropertiesParserBase.h 的 API 推断
#include "AudioPropertiesSheet.h"
#include "AudioPropertiesParserNameMatch.h"

void CreateAndUseAudioPropertySheet()
{
    // 1. 创建一个新的属性表资产
    UAudioPropertiesSheetAsset* NewSheet = NewObject<UAudioPropertiesSheetAsset>(GetTransientPackage(), FName("MySoundSheet"));

    // 2. 向属性表中添加属性
    FInstancedPropertyBag& Properties = NewSheet->PropertiesSheet.Properties;
    Properties.AddProperty(FName("MasterVolume"), EPropertyBagPropertyType::Float);
    Properties.SetValueFloat(FName("MasterVolume"), 0.8f);

    // 3. 设置解析器（例如，使用名称匹配解析器）
    UAudioPropertiesParserNameMatch* NameMatchParser = NewObject<UAudioPropertiesParserNameMatch>(NewSheet);
    NewSheet->PropertiesParser = NameMatchParser;

    // 4. 将属性表应用到一个目标对象（例如，一个 USoundWave）
    USoundWave* TargetSoundWave = LoadObject<USoundWave>(nullptr, TEXT("/Game/Sounds/MySound"));
    if (TargetSoundWave)
    {
        // CopyToObjectProperties 是一个编辑器函数，此处仅为示意
        // NewSheet->CopyToObjectProperties(TargetSoundWave);
    }
}
```

### 进阶用法

使用绑定解析器（`UAudioPropertiesParserBindings`）进行更灵活的属性映射。

```cpp
// 来源：基于 AudioPropertiesParserBindings.h 和 AudioPropertiesBindings.h 的 API 推断
#include "AudioPropertiesParserBindings.h"
#include "AudioPropertiesBindings.h"

void UseBindingsParser()
{
    // 1. 创建一个绑定资产，定义属性名映射关系
    UAudioPropertiesBindings* BindingsAsset = NewObject<UAudioPropertiesBindings>(GetTransientPackage());
    // 将属性表中的 “Vol” 映射到目标对象的 “Volume” 属性
    BindingsAsset->ObjectPropertyToSheetPropertyMap.Add(FName("Volume"), FName("Vol"));

    // 2. 创建一个绑定解析器，并指定绑定资产
    UAudioPropertiesParserBindings* BindingsParser = NewObject<UAudioPropertiesParserBindings>(GetTransientPackage());
    BindingsParser->BindingsAsset = BindingsAsset;

    // 3. 将解析器设置到属性表资产上
    UAudioPropertiesSheetAsset* SheetAsset = /* ... */;
    SheetAsset->PropertiesParser = BindingsParser;
}
```

## Demo 示例

一个最小的可编译示例，展示如何定义一个自定义的音频属性解析器。

**MyCustomAudioParser.h**
```cpp
#pragma once

#include "AudioPropertiesParserBase.h"
#include "MyCustomAudioParser.generated.h"

UCLASS()
class UMyCustomAudioParser : public UAudioPropertiesParserBase
{
    GENERATED_BODY()

public:
    // 重写解析函数，实现自定义的属性注入逻辑
    virtual bool ParseProperties(TObjectPtr<UObject> TargetObject, const FAudioPropertiesSheet& PropertiesToParse) const override;
};
```

**MyCustomAudioParser.cpp**
```cpp
#include "MyCustomAudioParser.h"
#include "AudioPropertiesSheet.h"
#include "Sound/SoundWave.h"

bool UMyCustomAudioParser::ParseProperties(TObjectPtr<UObject> TargetObject, const FAudioPropertiesSheet& PropertiesToParse) const
{
    USoundWave* SoundWave = Cast<USoundWave>(TargetObject);
    if (!SoundWave)
    {
        return false;
    }

    // 从属性表中获取值并应用到 SoundWave
    const FInstancedPropertyBag& Properties = PropertiesToParse.Properties;
    TOptional<float> Volume = Properties.GetValueFloat(FName("Volume"));
    if (Volume.IsSet())
    {
        SoundWave->Volume = Volume.GetValue();
    }

    TOptional<float> Pitch = Properties.GetValueFloat(FName("Pitch"));
    if (Pitch.IsSet())
    {
        SoundWave->Pitch = Pitch.GetValue();
    }

    return true;
}
```

## 模块依赖

从源码头文件包含关系推断，使用此插件需要以下模块依赖：

| 模块 | 用途 |
|---|---|
| `StructUtils` | 提供 `FPropertyBag` 等结构化数据工具，是属性表的核心。 |
| `PropertyBag` | `FInstancedPropertyBag` 的具体实现模块。 |
| `AssetRegistry` | 用于查询资产引用关系（如 `AudioPropertiesUtils` 中的函数）。 |

## 维护状态

### 近期更新

- 2026-04-14 `01c9ce5d` [ContentBrowser] New Add Menu Audio Menu
- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-02-12 `68131ef1` Instantiate Audio Properties Name Parser when creating new Property Sheet, as this is the de facto d
- 2026-01-15 `738ab46a` Fixed localization warnings
- 2026-01-14 `4b3fba09` Walk UClass inheritance when overriding property details from a property sheet to avoid visualizatio

### 维护评价

- **创建时间**：2026 年 1 月，非常新。
- **实验性**：`.uplugin` 中明确标记为 `IsExperimentalVersion: true`，且默认未启用 (`EnabledByDefault: false`)。
- **维护状态**：作为实验性插件，它正处于早期开发或验证阶段，API 和功能可能会发生重大变化。
- **推荐使用**：**不推荐**在生产项目中使用。仅建议用于学习、原型开发或对 UE 音频系统进行深度定制的研究。使用前请做好应对破坏性更改的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AudioProperties)
- 官方文档：暂无
- 测试用例：暂未发现公开的测试用例文件。