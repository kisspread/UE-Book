# Remote Control API

> A suite of tools for controlling the Unreal Engine, both in Editor or at Runtime via a webserver. This allows users to control Unreal Engine remotely through HTTP or WebSockets requests. This functionality allows developers to control Unreal through 3rd party applications and web services.

| 属性 | 值 |
|---|---|
| 分类 | Messaging |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（UI框架和接口） |
| 模块 | `RemoteControl` (Runtime), `RemoteControlCommon` (Runtime), `RemoteControlLogic` (Runtime), `RemoteControlMultiUser` (Runtime), `RemoteControlProtocol` (Runtime), `RemoteControlProtocolWidgets` (Runtime), `RemoteControlUI` (Runtime), `WebRemoteControl` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-06-07 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl) | |

## 用途

Remote Control API 是一个用于远程控制虚幻引擎的工具套件。它通过内置的 Web 服务器，允许用户通过 HTTP 或 WebSocket 请求在编辑器或运行时与引擎进行交互。其核心价值在于将引擎的功能（如修改属性、调用函数）暴露为 API，使得第三方应用程序、Web 服务或自动化脚本能够远程操控引擎，是虚拟制片、自动化测试和自定义工具链开发的关键基础设施。

本文档聚焦于 `RemoteControlUI` 模块，该模块为 Remote Control 系统提供了编辑器内的用户界面框架和扩展接口。

## 使用场景

- **自定义远程控制面板**：你需要为 Remote Control 面板添加自定义列、修改属性显示方式或实现拖放交互。
- **协议特定 UI**：你正在开发一个自定义的远程控制协议（如基于特定硬件），并需要为其提供专属的 UI 控件和设置。
- **扩展实体列表**：你需要修改暴露实体列表的分组、排序或过滤逻辑。
- **集成外部工具**：你希望将 Remote Control 面板的功能深度集成到你的编辑器工具或自定义资产编辑器中。

## 蓝图用法

`RemoteControlUI` 模块主要提供 C++ 接口和数据结构，用于构建和扩展 UI。其中定义的枚举和结构体可以在蓝图中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ERCFieldGroupType` | 枚举，定义暴露实体的分组方式（无、按属性ID、按所有者）。 | `ERCFieldGroupType` |
| `ERCFieldGroupOrder` | 枚举，定义分组的排序方式（无、升序、降序）。 | `ERCFieldGroupOrder` |
| `FRCPanelExposedEntitiesListSettingsData` | 结构体，存储实体列表的分组和排序设置。 | `FRCPanelExposedEntitiesListSettingsData` |

### 使用示例（蓝图描述）

在蓝图中，你可以使用 `FRCPanelExposedEntitiesListSettingsData` 结构体来配置或读取 Remote Control 面板的列表设置。例如，你可以创建一个该结构体的变量，设置其 `FieldGroupType` 为 `Owner`，`FieldGroupOrder` 为 `Ascending`，然后将其传递给相关的 UI 函数或保存为用户偏好设置。

## C++ 用法

`RemoteControlUI` 模块的核心是其提供的丰富接口（Interface），用于扩展 Remote Control 面板的 UI。开发者通过实现这些接口来注入自定义逻辑。

### 头文件引入

```cpp
#include "IRemoteControlUIModule.h"
#include "UI/IRCPanelExposedEntityWidgetFactory.h"
#include "UI/IRCPanelExposedEntitiesGroupWidgetFactory.h"
#include "UI/IRCExposedEntitiesPanelExtender.h"
#include "UI/IRCPanelExposedEntitiesListSettingsForProtocol.h"
#include "UI/Signature/IRCSignatureCustomization.h"
```

### 基本用法

**1. 实现一个自定义的属性列工厂 (`IRCPanelExposedEntityWidgetFactory`)**

这个接口允许你为 Remote Control 面板的实体行添加自定义列。

```cpp
// MyCustomColumnFactory.h
#pragma once
#include "UI/IRCPanelExposedEntityWidgetFactory.h"

class FMyCustomColumnFactory : public IRCPanelExposedEntityWidgetFactory
{
public:
    // 创建自定义列的控件
    virtual TSharedRef<SWidget> MakePropertyWidget(const FRCPanelExposedPropertyWidgetArgs& Args) override
    {
        // Args.Property 包含了当前行的属性信息
        // Args.WeakPreset 是关联的 RemoteControlPreset
        // 这里可以返回任何 Slate 控件，例如一个显示属性路径的文本块
        return SNew(STextBlock).Text(FText::FromString(Args.Property->FieldPathInfo.ToString()));
    }

    // 指定此工厂为哪一列创建控件
    virtual FName GetColumnName() const override
    {
        return FName("MyCustomColumn");
    }
};
```
*(来源：`Engine/Plugins/VirtualProduction/RemoteControl/Source/RemoteControlUI/Public/UI/IRCPanelExposedEntityWidgetFactory.h`)*

**2. 实现一个面板扩展器 (`IRCExposedEntitiesPanelExtender`)**

这个接口允许你在暴露实体列表的上方添加自定义控件。

```cpp
// MyPanelExtender.h
#pragma once
#include "UI/IRCExposedEntitiesPanelExtender.h"

class FMyPanelExtender : public IRCExposedEntitiesPanelExtender
{
public:
    virtual TSharedRef<SWidget> MakeWidget(URemoteControlPreset* Preset, const FArgs& Args) override
    {
        // Args.ActiveProtocolAttribute 可以获取当前激活的协议名称
        return SNew(STextBlock).Text(FText::FromString(TEXT("My Custom Header")));
    }
};
```
*(来源：`Engine/Plugins/VirtualProduction/RemoteControl/Source/RemoteControlUI/Public/UI/IRCExposedEntitiesPanelExtender.h`)*

### 进阶用法

**为特定协议提供 UI 和设置存储 (`IRCPanelExposedEntitiesListSettingsForProtocol`)**

这个接口结合了 UI 扩展和设置持久化，适用于为自定义协议提供完整的 UI 支持。

```cpp
// MyProtocolListSettings.h
#pragma once
#include "UI/IRCPanelExposedEntitiesListSettingsForProtocol.h"

class FMyProtocolListSettings : public IRCPanelExposedEntitiesListSettingsForProtocol
{
public:
    virtual FName GetProtocolName() const override { return FName("MyProtocol"); }

    virtual FRCPanelExposedEntitiesListSettingsData GetListSettings(URemoteControlPreset* Preset) const override
    {
        // 从 Preset 或其他地方读取并返回该协议的列表设置
        FRCPanelExposedEntitiesListSettingsData Settings;
        Settings.FieldGroupType = ERCFieldGroupType::PropertyId;
        return Settings;
    }

    virtual void OnSettingsChanged(URemoteControlPreset* Preset, const FRCPanelExposedEntitiesListSettingsData& ListSettings) override
    {
        // 将用户修改后的设置保存起来
        // 例如，保存到 Preset 的自定义数据或配置文件中
    }
};
```
*(来源：`Engine/Plugins/VirtualProduction/RemoteControl/Source/RemoteControlUI/Public/UI/IRCPanelExposedEntitiesListSettingsForProtocol.h`)*

## Demo 示例

以下示例展示如何实现一个简单的自定义列工厂，并将其注册到 Remote Control UI 模块。

**MyCustomColumnFactory.h**
```cpp
#pragma once
#include "UI/IRCPanelExposedEntityWidgetFactory.h"

class FMyCustomColumnFactory : public IRCPanelExposedEntityWidgetFactory
{
public:
    virtual TSharedRef<SWidget> MakePropertyWidget(const FRCPanelExposedPropertyWidgetArgs& Args) override;
    virtual FName GetColumnName() const override;
};
```

**MyCustomColumnFactory.cpp**
```cpp
#include "MyCustomColumnFactory.h"
#include "Widgets/Text/STextBlock.h"

TSharedRef<SWidget> FMyCustomColumnFactory::MakePropertyWidget(const FRCPanelExposedPropertyWidgetArgs& Args)
{
    // 显示属性的完整路径作为示例
    FString PropertyPath = Args.Property->FieldPathInfo.ToString();
    return SNew(STextBlock)
        .Text(FText::FromString(PropertyPath))
        .ToolTipText(FText::FromString(TEXT("Custom Column: Property Path")));
}

FName FMyCustomColumnFactory::GetColumnName() const
{
    return FName("CustomPathColumn");
}
```

**注册工厂（通常在你的模块 StartupModule 中）：**
```cpp
#include "IRemoteControlUIModule.h"
#include "MyCustomColumnFactory.h"

void FMyModule::StartupModule()
{
    if (IRemoteControlUIModule* RCModule = FModuleManager::GetModulePtr<IRemoteControlUIModule>(TEXT("RemoteControlUI")))
    {
        // 注册自定义的列工厂
        TSharedRef<FMyCustomColumnFactory> Factory = MakeShared<FMyCustomColumnFactory>();
        RCModule->RegisterExposedEntityWidgetFactory(Factory);
    }
}
```

## 模块依赖

要使用 `RemoteControlUI` 模块，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `RemoteControlCommon` | Remote Control 系统的公共数据结构和工具 |
| `RemoteControlProtocol` | 协议抽象层，用于与不同的远程控制协议交互 |
| `RemoteControl` | Remote Control 的核心运行时逻辑 |

## 维护状态

### 近期更新

- 2025-10-03 683817828fdc Remote Control: Updated the tooltips and icons for the path behavior again.
- 2025-09-15 9ff05163cc53 Remote Control: Fixed RC Protocol Filter localization
- 2025-08-20 6860f3263f68 Remote Control: Small improvement to the icons and tooltips in the path behavior.

### 维护评价

`RemoteControlUI` 模块作为 Remote Control 插件的核心 UI 组件，仍在**积极维护**中。从近期提交记录看，更新集中在 UI 细节优化（图标、提示信息）和本地化修复，表明 Epic 团队仍在持续改进用户体验。该模块创建于 2019 年，已相当成熟，是虚拟制片工作流中的重要组成部分。鉴于其稳定的更新频率和在 VP 领域的关键作用，**推荐使用**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/remote-control-api-in-unreal-engine/)