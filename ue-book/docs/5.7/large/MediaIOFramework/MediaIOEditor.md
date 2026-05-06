# Media IO Framework

> Media Framework classes to support Professional Media IO used by the Virtual Production industry.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体IO编辑器 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MediaIOEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-10-03 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaIOFramework/Source/MediaIOEditor) | |

---

## 用途

`MediaIOEditor` 是 Media IO Framework 的编辑器支持模块。它提供了一系列**细节面板自定义（Property Type Customizations）**，让用户在编辑器界面中能够直观地从设备列表中选择媒体 IO 配置，而无需手动输入设备参数。

具体功能包括：
- 自定义 `FMediaIOConfiguration`、`FMediaIODevice`、`FMediaIOInputConfiguration`、`FMediaIOOutputConfiguration`、`FMediaIOVideoTimecodeConfiguration` 等结构体在 Details Panel 中的 UI。
- 提供一个通用的排列选择器小部件 `SMediaPermutationsSelector`，用于列出设备支持的所有排列（分辨率、帧率、传输类型等），并支持按列筛选。
- 提供 `FileMediaOutputFactory` 用于在 Content Browser 中创建 `UFileMediaOutput` 资产。
- 提供 `FAssetTypeActions_MediaOutput` 用于资产类型注册与图标。

该模块是典型的“编辑器增强”模块，**仅在 Editor 环境下加载**，不参与运行时逻辑。

---

## 使用场景

- **在 Virtual Production 项目中使用 SDI/NDI/DeckLink/AJA 等专业媒体设备输入输出时**，需要在资产或 Actor 的细节面板中配置设备连接。`MediaIOEditor` 提供的自定义 UI 让您直接从设备能力列表中选择匹配的参数，避免手动填写错误。
- **需要自定义媒体输出资产**（如文件输出）时，通过 Factory 和 AssetTypeActions 可以快速创建并编辑。
- **开发其他编辑器工具需要展示设备排列列表**时，可复用 `SMediaPermutationsSelector` 和 `FMediaIOPermutationsSelectorBuilder`。

---

## 蓝图用法

`MediaIOEditor` 模块是纯 Editor 模块，不提供任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。所有 API 仅在 C++ 编辑器模块中使用。

---

## C++ 用法

### 头文件引入

```cpp
#include "Customizations/MediaIOConfigurationCustomization.h"
#include "Customizations/MediaIODeviceCustomization.h"
#include "Customizations/MediaIOInputConfigurationCustomization.h"
#include "Customizations/MediaIOOutputConfigurationCustomization.h"
#include "Customizations/MediaIOVideoTimecodeConfigurationCustomization.h"
#include "Widgets/SMediaPermutationsSelector.h"
```

### 基本用法

#### 注册自定义化到 Detail Panel

通常在模块的 `StartupModule()` 中注册：

```cpp
#include "PropertyEditorModule.h"
#include "Customizations/MediaIOConfigurationCustomization.h"
#include "Customizations/MediaIODeviceCustomization.h"
#include "Customizations/MediaIOInputConfigurationCustomization.h"
#include "Customizations/MediaIOOutputConfigurationCustomization.h"
#include "Customizations/MediaIOVideoTimecodeConfigurationCustomization.h"

void FMediaIOEditorModule::StartupModule()
{
    FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");

    // 注册结构体自定义
    PropertyModule.RegisterCustomPropertyTypeLayout(
        "MediaIOConfiguration",
        FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FMediaIOConfigurationCustomization::MakeInstance)
    );
    PropertyModule.RegisterCustomPropertyTypeLayout(
        "MediaIODevice",
        FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FMediaIODeviceCustomization::MakeInstance)
    );
    PropertyModule.RegisterCustomPropertyTypeLayout(
        "MediaIOInputConfiguration",
        FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FMediaIOInputConfigurationCustomization::MakeInstance)
    );
    PropertyModule.RegisterCustomPropertyTypeLayout(
        "MediaIOOutputConfiguration",
        FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FMediaIOOutputConfigurationCustomization::MakeInstance)
    );
    PropertyModule.RegisterCustomPropertyTypeLayout(
        "MediaIOVideoTimecodeConfiguration",
        FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FMediaIOVideoTimecodeConfigurationCustomization::MakeInstance)
    );

    PropertyModule.NotifyCustomizationModuleChanged();
}
```

#### 使用 SMediaPermutationsSelector 创建选择器

```cpp
// 假设已有设备提供的排列列表
TArray<FMediaIOConfiguration> AllConfigs = /* from device provider */;
FMediaIOConfiguration CurrentSelection = /* current value */;

using SSelector = SMediaPermutationsSelector<FMediaIOConfiguration, FMediaIOPermutationsSelectorBuilder>;

SNew(SSelector)
    .PermutationsSource(MoveTemp(AllConfigs))
    .SelectedPermutation(CurrentSelection)
    .OnSelectionChanged(this, &MyCustomization::OnSelectionChanged)
    + SSelector::Column(FMediaIOPermutationsSelectorBuilder::NAME_DeviceIdentifier)
        .Label(LOCTEXT("DeviceLabel", "Device"))
    + SSelector::Column(FMediaIOPermutationsSelectorBuilder::NAME_TransportType)
        .Label(LOCTEXT("TransportLabel", "Transport"))
    + SSelector::Column(FMediaIOPermutationsSelectorBuilder::NAME_Resolution)
        .Label(LOCTEXT("ResolutionLabel", "Resolution"))
    + SSelector::Column(FMediaIOPermutationsSelectorBuilder::NAME_FrameRate)
        .Label(LOCTEXT("FrameRateLabel", "FrameRate"))
    + SSelector::Column(FMediaIOPermutationsSelectorBuilder::NAME_Standard)
        .Label(LOCTEXT("StandardLabel", "Standard"))
    + SSelector::Column(FMediaIOPermutationsSelectorBuilder::NAME_QuadType)
        .Label(LOCTEXT("QuadTypeLabel", "Quad"));
```

**来源：** `MediaIOPermutationsSelectorBuilder.h` 及 `SMediaPermutationsSelector.h`。

---

## Demo 示例

以下展示一个完整的编辑器模块，用于演示如何注册自定义化和使用 `SMediaPermutationsSelector`。

**MediaIOEditorDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

DECLARE_LOG_CATEGORY_EXTERN(LogMediaIOEditorDemo, Log, All);

class FMediaIOEditorDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

**MediaIOEditorDemo.cpp**
```cpp
#include "MediaIOEditorDemo.h"
#include "PropertyEditorModule.h"
#include "Customizations/MediaIOConfigurationCustomization.h"
#include "Customizations/MediaIODeviceCustomization.h"
#include "Customizations/MediaIOInputConfigurationCustomization.h"
#include "Customizations/MediaIOOutputConfigurationCustomization.h"
#include "Customizations/MediaIOVideoTimecodeConfigurationCustomization.h"
#include "Widgets/SMediaPermutationsSelector.h"
#include "MediaIOPermutationsSelectorBuilder.h"
#include "MediaIOCoreDefinitions.h"

IMPLEMENT_MODULE(FMediaIOEditorDemoModule, MediaIOEditorDemo)

DEFINE_LOG_CATEGORY(LogMediaIOEditorDemo)

void FMediaIOEditorDemoModule::StartupModule()
{
    FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");

    PropertyModule.RegisterCustomPropertyTypeLayout(
        TEXT("MediaIOConfiguration"),
        FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FMediaIOConfigurationCustomization::MakeInstance)
    );
    PropertyModule.RegisterCustomPropertyTypeLayout(
        TEXT("MediaIODevice"),
        FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FMediaIODeviceCustomization::MakeInstance)
    );
    PropertyModule.RegisterCustomPropertyTypeLayout(
        TEXT("MediaIOInputConfiguration"),
        FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FMediaIOInputConfigurationCustomization::MakeInstance)
    );
    PropertyModule.RegisterCustomPropertyTypeLayout(
        TEXT("MediaIOOutputConfiguration"),
        FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FMediaIOOutputConfigurationCustomization::MakeInstance)
    );
    PropertyModule.RegisterCustomPropertyTypeLayout(
        TEXT("MediaIOVideoTimecodeConfiguration"),
        FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FMediaIOVideoTimecodeConfigurationCustomization::MakeInstance)
    );

    PropertyModule.NotifyCustomizationModuleChanged();
}

void FMediaIOEditorDemoModule::ShutdownModule()
{
    // 一般在模块关闭时反注册，但为演示简化
}
```

**说明：** 将以上代码放入一个非约束的编辑器模块（`IsEditorModule = true`）中，依赖 `MediaIOEditor`、`PropertyEditor`、`MediaIOCore`。启动后即可在任意包含 `FMediaIOConfiguration` 等属性的细节面板中看到自定义 UI。

---

## 模块依赖

使用 `MediaIOEditor` 时，需在 `Build.cs` 的 `PublicDependencyModuleNames` 中添加以下模块：

| 模块 | 用途 |
|---|---|
| `MediaIOCore` | 提供媒体 IO 核心定义结构（如 `FMediaIOConfiguration`） |
| `UnrealEd` | 编辑器基础架构 |
| `EditorFramework` | 编辑器框架依赖 |
| `LevelEditor` | 编辑器窗口扩展 |

**注意：** 该模块本身是 Editor 模块，只能在 Editor 目标编译。

---

## 维护状态

### 近期更新

| 日期 | Hash | Commit |
|---|---|---|
| 2026-01-23 | `4c7dda9d` | Media IO - Fix Media Capture taking multiple frames to start outputting |
| 2025-12-18 | `38c0295d` | Media IO - When using ResizeInRenderPass, fix output getting resized even if the input resolution ma |
| 2025-10-17 | `ab15e769` | Media IO - Fix crash when refreshing media properties for Aja source |
| 2025-10-06 | `cefac266` | Media I/O: Avoid raw this pointer capture in async task, which could cause crashes if the texture sa |
| 2025-10-03 | `1b95a6c6` | Media IO - Fix Media Source not being able to unset AutoDetect in Media Profile |

### 维护评价

- **创建时间：** 2025-10-03（约 0 年，即不足 1 年）。
- **更新频率：** 近期（2025-10 至 2026-01）有多项 bug 修复和稳定性改进，说明项目处于**活跃维护**阶段。
- **功能完整性：** 该模块为 Media IO Framework 的核心编辑器组件，无已知巨大缺陷。
- **推荐使用：** ✅ 推荐在需要编辑器媒体配置功能的 Virtual Production 项目中使用。由于是新模块，API 可能随版本迭代微调，但整体稳定。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaIOFramework/Source/MediaIOEditor)
- [官方文档（暂无）](https://docs.unrealengine.com/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaIOFramework/Tests)