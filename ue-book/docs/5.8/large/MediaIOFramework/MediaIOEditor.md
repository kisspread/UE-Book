# Media IO Framework

> Media Framework classes to support Professional Media IO used by the Virtual Production industry.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体IO框架 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MediaIOCore` (Runtime), `MediaIOEditor` (Editor), `GPUTextureTransfer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-10-02 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaIOFramework) | |

## 用途

MediaIOFramework 是为**虚拟制作 (Virtual Production)** 和**专业广播**行业设计的核心媒体IO框架。它不是一个独立的播放器或采集卡驱动，而是一个**抽象层**，用于统一管理专业视频硬件（如 AJA、Blackmagic Design）与 Unreal Engine 之间的输入/输出流程。

**它解决的核心问题是**：将不同厂商、不同型号的专业视频设备（用于输入参考视频、时间码，输出渲染画面）的功能和配置，抽象成一套统一的、可序列化、可编辑的结构体（如 `FMediaIOConfiguration`、`FMediaIOMode`）和UI控件。这使得引擎的其他部分（如 nDisplay、Media Capture）能够通过统一的接口与各种硬件交互，而无需关心底层硬件的具体实现细节。

**为什么存在**：虚拟制作流程中，需要确保摄像机画面、渲染引擎画面、LED墙显示、时间码等在多个设备间精确同步和传递。每个硬件厂商有自己的SDK和配置方式。此插件提供了：
1.  **标准化的数据结构**：描述设备、连接、分辨率、帧率、同步等。
2.  **编辑器UI组件**：提供专业的、数据驱动的配置选择器（如 `SMediaPermutationsSelector`），方便美术和技术人员在编辑器中可视化地选择和配置设备参数。
3.  **属性编辑器集成**：自定义属性面板（Customization），让媒体配置结构体在细节面板中拥有友好的交互界面（如下拉选择、自动检测等）。

## 使用场景

-   **虚拟制片**：在 nDisplay 或 Stage Monitor 中配置输入/输出源，将渲染画面输出到 LED 墙，或将摄像机信号输入引擎进行合成。
-   **实时合成与监视**：通过专业的采集卡（如 AJA Corvid、Blackmagic DeckLink）将外部视频源（摄像机、播放器）输入引擎，或在特定监视器上输出最终画面。
-   **时间码同步**：配置外部时间码源，确保多个视频设备和 Unreal Engine 的时间线同步。
-   **开发自定义媒体设备插件**：作为基础框架，帮助开发者为新的专业视频硬件编写 UE 插件。

## 蓝图用法

由于 MediaIOEditor 模块主要提供编辑器自定义功能，而非运行时蓝图节点，因此其在蓝图中的直接使用较少。主要的“蓝图体验”体现在**编辑器UI**中。

### 核心UI组件（Slate控件）

| 组件 | 说明 | 所在类 |
|---|---|---|
| 媒体排列选择器 | 一个强大的多列组合选择控件，用于从一组复杂的媒体配置（如设备+连接+分辨率+帧率）中逐步筛选出目标配置。每列代表一个配置维度，用户逐列点击，选项会根据前一列的选择自动过滤。 | `SMediaPermutationsSelector` |

### 使用示例（编辑器界面）

当在细节面板中编辑一个 `FMediaIOConfiguration` 类型的属性时，系统会自动弹出一个配置选择器界面。该界面由 `FMediaIOConfigurationCustomization` 驱动，其内部核心就是 `SMediaPermutationsSelector`。

**界面流程描述**：
1.  用户点击一个媒体配置属性旁的下拉按钮。
2.  弹出一个多列选择器，列头可能显示为：“设备标识”、“传输类型”、“分辨率”、“帧率”等。
3.  每一列下方列出了该维度下所有可用的选项（例如，“分辨率”列下列出所有支持的分辨率）。
4.  用户首先在“设备标识”列选择一个设备（如 "AJA Corvid 88"）。
5.  选择后，右侧的“传输类型”、“分辨率”等列会**自动过滤**，只显示与所选设备兼容的选项。
6.  用户继续逐列选择，最终得到一个完整的配置（如：AJA Corvid 88, SDI, 1920x1080, 59.94fps）。
7.  点击“应用”按钮，将选定的配置写入属性。

## C++ 用法

本插件的 C++ 用法主要面向两类用户：
1.  **使用者**：在自己的 C++ 代码中，使用 `MediaIOCore` 模块提供的数据结构和接口来查询设备信息、配置IO。
2.  **扩展者**：在开发新的媒体设备插件时，继承和重写 `MediaIOCore` 的接口，并利用 `MediaIOEditor` 的组件来构建配置UI。

### 头文件引入

```cpp
// 核心数据结构和接口
#include "MediaIOCoreModule.h"
#include "MediaIOCoreDefinitions.h" // 包含 FMediaIOConfiguration, FMediaIOConnection 等

// 编辑器UI组件 (仅在编辑器模块中)
#include "Widgets/SMediaPermutationsSelector.h"
#include "Customizations/MediaIOCustomizationBase.h"
```

### 基本用法：查询媒体配置

此用法展示了如何从 MediaIOCore 模块获取当前系统中可用的专业媒体设备及其配置信息。通常用于初始化UI或运行时的设备发现。

```cpp
// 假设我们正在编写一个需要列出所有可用媒体输出的函数
// 来源参考: MediaIOCore 中的设备枚举逻辑

#include "MediaIOCoreModule.h"
#include "IMediaIOCoreModule.h"

void ListAvailableMediaConfigurations()
{
    // 获取 MediaIOCore 模块接口
    IMediaIOCoreModule& MediaIOCoreModule = FModuleManager::LoadModuleChecked<IMediaIOCoreModule>("MediaIOCore");

    // 获取所有注册的媒体设备提供者（通常是各硬件插件，如 AJA、Blackmagic）
    TArray<TSharedPtr<IMediaIOCoreDeviceProvider>> DeviceProviders = MediaIOCoreModule.GetDeviceProviders();

    for (const TSharedPtr<IMediaIOCoreDeviceProvider>& Provider : DeviceProviders)
    {
        UE_LOG(LogTemp, Log, TEXT("设备提供者: %s"), *Provider->GetProviderName().ToString());

        // 获取该提供者支持的所有输出配置
        TArray<FMediaIOConfiguration> OutputConfigurations;
        Provider->GetOutputConfigurations(OutputConfigurations);

        for (const FMediaIOConfiguration& Config : OutputConfigurations)
        {
            // 打印关键配置信息
            UE_LOG(LogTemp, Log, TEXT("  设备: %s, 传输类型: %s, 分辨率: %dx%d, 帧率: %s"),
                *Config.MediaConnection.DeviceIdentifier.ToString(),
                *UEnum::GetValueAsString(Config.MediaConnection.TransportType),
                Config.MediaMode.Resolution.X, Config.MediaMode.Resolution.Y,
                *Config.MediaMode.FrameRate.ToString());
        }
    }
}
```

### 进阶用法：自定义属性编辑器

此用法展示了如何为自定义的媒体相关结构体创建一个与 `SMediaPermutationsSelector` 类似的属性编辑器。这需要继承 `FMediaIOCustomizationBase`。

```cpp
// 假设我们有一个自定义的媒体采集配置结构体
USTRUCT(BlueprintType)
struct FMyCustomCaptureConfiguration
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category="Media")
    FMediaIOConnection Connection;

    UPROPERTY(EditAnywhere, Category="Media")
    FMediaIOCaptureOptions CaptureOptions;
};

// 为 FMyCustomCaptureConfiguration 创建自定义属性编辑器
// 来源参考: MediaIOEditor 中的 FMediaIOConfigurationCustomization 等实现

class FMyCustomCaptureConfigurationCustomization : public FMediaIOCustomizationBase
{
public:
    // 工厂方法
    static TSharedRef<IPropertyTypeCustomization> MakeInstance()
    {
        return MakeShared<FMyCustomCaptureConfigurationCustomization>();
    }

protected:
    // 实现基类接口：提供显示在组合按钮上的文本
    virtual TAttribute<FText> GetContentText() override
    {
        // 这里应该返回当前选中配置的摘要，例如 "AJA Corvid 88 (SDI)"
        // 简化实现，实际需要从 MediaProperty 中读取
        return NSLOCTEXT("MyCustomization", "DefaultContent", "选择媒体配置...");
    }

    // 实现基类接口：创建点击组合按钮后弹出的选择器内容
    virtual TSharedRef<SWidget> HandleSourceComboButtonMenuContent() override
    {
        // 填充配置列表数据源
        TArray<FMyCustomCaptureConfiguration> AvailableConfigs;
        // ... 从设备提供者获取所有可用配置并填充到 AvailableConfigs ...

        // 创建 SMediaPermutationsSelector
        using FConfigSelector = SMediaPermutationsSelector<FMyCustomCaptureConfiguration, FMyPermutationBuilder>;

        return SNew(FConfigSelector)
            .PermutationsSource(AvailableConfigs)
            .ColumnHeight(250)
            .OnSelectionChanged_Lambda([this](FMyCustomCaptureConfiguration SelectedItem)
            {
                // 将选中的值通过基类的方法写回属性
                AssignValue(SelectedItem);
            })
            + SMediaPermutationsSelector<FMyCustomCaptureConfiguration>::FColumn::FArguments()
                .ColumnName("Connection")
                .Label(NSLOCTEXT("MyCustomization", "ConnectionColumn", "连接"))
            + SMediaPermutationsSelector<FMyCustomCaptureConfiguration>::FColumn::FArguments()
                .ColumnName("CaptureOptions")
                .Label(NSLOCTEXT("MyCustomization", "OptionsColumn", "采集选项"));
    }

private:
    // 自定义的排列构建器，用于告诉选择器如何比较和显示 FMyCustomCaptureConfiguration
    struct FMyPermutationBuilder
    {
        static bool IdenticalProperty(FName ColumnName, const FMyCustomCaptureConfiguration& Left, const FMyCustomCaptureConfiguration& Right)
        {
            if (ColumnName == "Connection") return Left.Connection == Right.Connection;
            if (ColumnName == "CaptureOptions") return Left.CaptureOptions == Right.CaptureOptions;
            return false;
        }
        static FText GetLabel(FName ColumnName, const FMyCustomCaptureConfiguration& Item)
        {
            if (ColumnName == "Connection") return FText::FromString(Item.Connection.DeviceIdentifier.ToString());
            if (ColumnName == "CaptureOptions") return FText::FromString(TEXT("..."));
            return FText::FromName(ColumnName);
        }
        // ... 实现 Less 和 GetTooltip ...
    };
};
```

## Demo 示例

以下示例展示了如何在编辑器模块中注册一个自定义的属性编辑器，用于编辑 `FMyCustomCaptureConfiguration` 结构体。

**MyCustomMediaEditorModule.cpp**
```cpp
#include "Modules/ModuleManager.h"
#include "PropertyEditorModule.h"
#include "MyCustomCaptureConfigurationCustomization.h" // 上文定义的编辑器类

class FMyCustomMediaEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override
    {
        FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");

        // 注册自定义属性编辑器
        PropertyModule.RegisterCustomPropertyTypeLayout(
            FMyCustomCaptureConfiguration::StaticStruct()->GetFName(),
            FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FMyCustomCaptureConfigurationCustomization::MakeInstance)
        );
    }

    virtual void ShutdownModule() override
    {
        if (FModuleManager::Get().IsModuleLoaded("PropertyEditor"))
        {
            FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
            PropertyModule.UnregisterCustomPropertyTypeLayout(FMyCustomCaptureConfiguration::StaticStruct()->GetFName());
        }
    }
};

IMPLEMENT_MODULE(FMyCustomMediaEditorModule, MyCustomMediaEditor);
```

## 模块依赖

从各模块的 `Build.cs` 文件分析，以下是该插件独特且主要的依赖：

| 模块 | 用途 |
|---|---|
| `VulkanRHI` | GPUTextureTransfer 模块用于在CPU和GPU之间高效传输纹理数据，依赖Vulkan RHI接口。 |
| `OpenColorIO` | 用于处理专业媒体工作流中的色彩空间转换，这是虚拟制作和广播行业的常见需求。 |

**说明**：`MediaIOCore` 和 `MediaIOEditor` 模块依赖了 `EditorFramework`, `UnrealEd`, `LevelEditor` 等编辑器模块，这表明其核心UI和编辑器集成部分是为了在编辑器内使用而构建的。运行时功能（如设备发现、数据获取）则封装在 `MediaIOCore` 中，但当前提供的依赖信息不完整。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 为Blackmagic和AJA采集卡的自动配置模式填充媒体配置信息。 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为媒体播放器和采集功能添加了额外的引擎分析数据。 |
| 2026-05-14 | `a43a62b2` | Media Profile: Changed media texture capture behavior to always preserve aspect ratio of texture eve | 媒体配置文件：修改了媒体纹理捕获行为，使其始终保留纹理的宽高比。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，代码因双精度常量截断为浮点数而产生的警告。 |
| 2026-05-12 | `a879de69` | Fix clang warnings when compiling MediaIODeinterlacerTests | 修复编译MediaIODeinterlacerTests时的Clang警告。 |

### 维护评价

**活跃维护**。该插件是 Epic Games 官方维护的 **Virtual Production** 工具链的核心组件之一，专注于专业媒体IO。从提交历史看：
1.  **更新频繁**：最近一个月内有多次实质性功能更新和优化（如自动配置填充、宽高比保持）。
2.  **技术前沿**：涉及Vulkan、GPU纹理传输、色彩管理等专业领域。
3.  **兼容性良好**：持续修复编译警告和测试用例，表明对工程质量和跨平台兼容性有要求。
4.  **重要性高**：是连接 Unreal Engine 与专业广播设备的关键桥梁，不太可能被废弃。

**推荐使用**：如果你正在从事虚拟制片、广播集成或需要专业视频IO的项目，此插件是必不可少的基础设施。但请注意它**默认不启用**，需要在插件设置中手动开启。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaIOFramework)
- [官方文档]() (无公开文档链接，建议参考 Epic Games 官方虚拟制作文档)
- [测试用例]() (未在提供的信息中明确指出测试文件路径，通常位于引擎的 `Engine/Tests/` 或插件内部的 `Tests/` 目录下)