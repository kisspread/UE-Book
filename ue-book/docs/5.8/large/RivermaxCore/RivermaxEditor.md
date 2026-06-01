# RivermaxCore

> Base plugin exposing rivermax to engine

| 属性 | 值 |
|---|---|
| 中文名 | Rivermax 核心 |
| 分类 | Virtual Production |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `RivermaxCore` (Runtime), `RivermaxEditor` (Runtime), `RivermaxRendering` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-30 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxCore) | |

## 用途

此插件是 NVIDIA Rivermax SDK 与 Unreal Engine 集成的基础。Rivermax SDK 用于在 IP 网络上进行超低延迟、高带宽的媒体传输，特别是用于专业视听（Pro AV）和广播环境。
`RivermaxCore` 插件将底层的 Rivermax SDK 功能（如设备管理、网络流收发）封装为引擎可使用的 C++ API，并提供相应的编辑器工具（如 `RivermaxEditor` 模块）用于在引擎中配置和选择设备/网络接口。
其核心用途是解决**基于 IP 的视频帧缓冲区的发送与接收**问题，服务于虚拟制作（Virtual Production）中的实时视频合成场景。

## 使用场景

- **LED 墙实时视频输出**：在虚拟制作影棚中，通过 IP 网络将引擎渲染的画面实时发送到 LED 墙控制器。
- **摄影机信号输入**：从支持 SMPTE ST 2110 或类似标准的广播级摄影机接收视频流，并实时合成到引擎场景中。
- **多机位制作与切换**：管理多个 IP 视频流的输入与输出，实现广播级的多路视频切换。
- **高带宽、低延迟媒体传输**：任何需要在局域网内进行未压缩或轻度压缩的高清/超高清视频流传输的场景。

## 蓝图用法

`RivermaxCore` 插件主要是一个 C++ 库，其核心功能（流管理、设备控制）未直接暴露给蓝图。`RivermaxEditor` 模块提供了编辑器内的属性自定义（Property Customization），用于在项目设置中配置 Rivermax 设备和 IP 地址，但这本身不是蓝图节点。
因此，**本插件没有直接可用的蓝图节点**。所有操作均需通过 C++ API 完成。

## C++ 用法

### 头文件引入

```cpp
#include "RivermaxCoreModule.h" // 访问模块及子系统
#include "RivermaxMediaOutput.h" // 或其他特定的流/设备头文件
```

### 基本用法

访问 Rivermax 子系统以初始化 SDK 和查询设备。

```cpp
// 引用自 RivermaxCore 模块的 API
#include "RivermaxCoreModule.h"

void MyFunction()
{
    // 获取 Rivermax 子系统，它负责管理底层 SDK 的生命周期
    IRivermaxCoreModule* RivermaxModule = FModuleManager::GetModulePtr<IRivermaxCoreModule>(TEXT("RivermaxCore"));
    if (RivermaxModule)
    {
        // 初始化 Rivermax SDK (通常在模块启动时已自动完成)
        RivermaxModule->InitializeLibrary();

        // 获取设备管理器以列出可用的 Rivermax 网络接口/设备
        TSharedPtr<IRivermaxDeviceManager> DeviceManager = RivermaxModule->GetDeviceManager();
        if (DeviceManager)
        {
            TArray<FString> DeviceIPs;
            DeviceManager->GetAvailableDeviceIPs(DeviceIPs);
            for (const FString& IP : DeviceIPs)
            {
                UE_LOG(LogTemp, Log, TEXT("Found Rivermax device at IP: %s"), *IP);
            }
        }
    }
}
```

### 进阶用法

使用编辑器模块中的自定义控件。`SRivermaxInterfaceComboBox` 是一个 Slate 控件，用于在编辑器 UI 中选择 Rivermax 网络接口的 IP 地址。

```cpp
// 引用自 RivermaxEditor 模块
#include "Customizations/RivermaxDeviceSelectionCustomization.h"
#include "Widgets/SRivermaxInterfaceComboBox.h"

// 在自定义的编辑器详情面板中，使用工具函数添加 IP 选择行
void FMyCustomization::CustomizeDetails(IDetailLayoutBuilder& DetailBuilder)
{
    TSharedRef<IPropertyHandle> NetworkInterfaceProperty = DetailBuilder.GetProperty(GET_MEMBER_NAME_CHECKED(FMySettings, NetworkInterfaceIP));
    UE::RivermaxCore::Utils::AddInterfaceAddressRow(
        DetailBuilder.EditDefaultProperty(NetworkInterfaceProperty),
        NetworkInterfaceProperty,
        CurrentValue,
        CustomizationUtils
    );
}
```

## Demo 示例

以下示例展示了如何在自定义的编辑器工具中创建和使用 `SRivermaxInterfaceComboBox` 控件。

```cpp
// MyEditorWidget.h
#pragma once
#include "Widgets/SCompoundWidget.h"

class SMyEditorWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyEditorWidget) {}
    SLATE_END_ARGS()
    void Construct(const FArguments& InArgs);

private:
    void OnIPAddressSelected(FString NewIP);
    TSharedPtr<SRivermaxInterfaceComboBox> InterfaceComboBox;
    FString SelectedIPAddress;
};
```

```cpp
// MyEditorWidget.cpp
#include "MyEditorWidget.h"
#include "Widgets/SRivermaxInterfaceComboBox.h" // 来自 RivermaxEditor 模块

void SMyEditorWidget::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        [
            SAssignNew(InterfaceComboBox, SRivermaxInterfaceComboBox)
            .InitialValue(TEXT("192.168.1.100"))
            .OnIPAddressSelected_Lambda([this](FString InIP)
            {
                OnIPAddressSelected(InIP);
            })
        ]
    ];
}

void SMyEditorWidget::OnIPAddressSelected(FString NewIP)
{
    SelectedIPAddress = NewIP;
    UE_LOG(LogTemp, Log, TEXT("User selected Rivermax IP: %s"), *NewIP);
    // 此处可以使用 SelectedIPAddress 初始化一个 Rivermax 流
}
```

## 模块依赖

要使用此插件的功能，你的项目模块需要依赖以下**特定**的插件模块。

| 模块 | 用途 |
|---|---|
| `RivermaxCore` | 访问 Rivermax SDK 的核心封装、设备管理和流 API。 |
| `RivermaxEditor` | （仅限编辑器）使用 IP 选择控件和项目设置自定义。 |
| `D3D12RHI` | Rivermax 渲染模块的底层图形 API 依赖。 |

**注意**：`RivermaxRendering` 模块处理与图形 API 的深度集成，通常由引擎内部使用，项目代码一般无需直接依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下，双精度常量截断为浮点数时产生的警告代码。 |
| 2026-04-29 | `bef86caa` | Whitespace: followup to migrate UE_LOG to UE_LOGF: Restore newlines in multi-line format strings tha | UE_LOG 迁移至 UE_LOGF 的后续工作：恢复了多行格式字符串中的换行符。 |
| 2026-04-28 | `3348026a` | Rivermax: ANC timecode input, input stream base class refactor, and pixel format unification | 新增 ANC 时间码输入支持，重构了输入流基类，并统一了像素格式处理。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用作用域枚举可能导致输出乱码的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了当参数为64位时，格式化说明符错误使用32位的问题，反之亦然。 |

### 维护评价

- **活跃维护**：尽管 `.uplugin` 标记为 `IsBetaVersion: true`，但根据 Git 历史，该插件在 2026 年 4 月和 5 月仍有**非常活跃的更新**。最近的提交包括新功能（ANC 时间码）、代码重构和关键的 Bug 修复。
- **状态**：插件处于**积极开发和优化**中。作为“Beta”版本，意味着其 API 可能不稳定，但 Epic Games 持续投入开发。
- **建议**：推荐在需要 Rivermax 集成的虚拟制作项目中使用。需要注意其 Beta 状态，关注后续版本的 API 变更。对于生产环境，建议密切跟踪更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxCore)
- [官方文档](（未提供）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxCore/Tests)