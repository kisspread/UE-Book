# Remote Control API

> A suite of tools for controlling the Unreal Engine, both in Editor or at Runtime via a webserver. This allows users to control Unreal Engine remotely through HTTP or WebSockets requests. This functionality allows developers to control Unreal through 3rd party applications and web services.

| 属性 | 值 |
|---|---|
| 分类 | Messaging |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（UI 控件） |
| 模块 | `RemoteControlProtocolWidgets` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-06-07 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl) | |

## 用途

`RemoteControlProtocolWidgets` 模块是 Remote Control API 插件中负责**协议绑定 UI 展示与交互**的部分。它为编辑器提供了一套 Slate 控件，用于可视化地配置和管理远程控制字段（如属性、函数）与外部协议（如 OSC、MIDI、DMX）之间的绑定关系。

该模块的核心价值在于将复杂的协议映射配置过程图形化，允许用户在编辑器中直观地：
1.  **添加和移除协议绑定**：为暴露的远程控制字段关联一个或多个协议实体。
2.  **配置协议参数**：设置协议消息的地址、通道等具体参数。
3.  **管理数据掩码**：对于向量、颜色等复合数据类型，可以精细控制哪些分量（如 R, G, B, A 或 X, Y, Z）参与协议映射。
4.  **录制协议消息**：通过监听传入的协议消息来自动填充绑定参数，简化配置流程。

它解决了在虚拟制片、现场演出等场景中，需要将 Unreal Engine 的内部状态（如灯光参数、角色动画、材质属性）与外部控制设备或软件进行实时、灵活对接的配置难题。

## 使用场景

-   **虚拟制片 (Virtual Production)**：在 LED 墙拍摄现场，使用 OSC 协议从 iPad 或专用控制台实时调整场景中的灯光强度、颜色或摄像机参数。
-   **现场演出与交互装置**：通过 MIDI 控制器映射到引擎内的音频参数或粒子效果，实现音乐可视化或交互艺术装置。
-   **自动化测试与流水线**：通过 HTTP 或 WebSocket 请求，从外部脚本或 CI/CD 工具远程触发引擎内的函数或修改属性，实现自动化测试或内容生成。
-   **自定义控制界面**：开发者可以基于此模块提供的 UI 框架，构建符合特定项目需求的远程控制面板。

## 蓝图用法

本模块主要提供编辑器内的 Slate UI 控件，不直接暴露蓝图节点。其核心功能通过编辑器内的 Remote Control Panel 面板进行操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddProtocolBinding` | 为当前选中的远程控制字段添加一个指定类型的协议绑定。 | `IRemoteControlProtocolWidgetsModule` |
| `GenerateDetailsForEntity` | 为指定的协议实体生成详细的配置控件。 | `IRemoteControlProtocolWidgetsModule` |
| `GetProtocolBindingList` | 获取当前协议绑定列表的控件引用。 | `IRemoteControlProtocolWidgetsModule` |

### 使用示例（蓝图描述）

在编辑器中，通过 `Window > Virtual Production > Remote Control` 打开 Remote Control 面板。
1.  在面板左侧的 **Presets** 区域，选择或创建一个预设（Preset）。
2.  在 **Exposed Fields** 列表中，选中一个已暴露的属性或函数。
3.  在右侧的 **Protocol Bindings** 区域，点击 `+` 按钮，从下拉菜单中选择一个协议（如 `OSC`）。
4.  此时会调用 `AddProtocolBinding`，并为该协议实体生成一个配置行。
5.  在配置行中，可以手动输入协议地址（如 `/light/intensity`），或点击录制按钮（调用 `OnStartRecording`），然后从外部设备发送一个消息，地址会自动填充。
6.  对于向量或颜色属性，会出现掩码控件（`SRCProtocolMaskTriplet`），允许勾选 X, Y, Z 等分量来控制哪些数据通道参与映射。

## C++ 用法

### 头文件引入

```cpp
#include "IRemoteControlProtocolWidgetsModule.h"
```

### 基本用法

获取模块实例并添加一个协议绑定。
```cpp
// 获取 RemoteControlProtocolWidgets 模块实例
IRemoteControlProtocolWidgetsModule& ProtocolWidgetsModule = IRemoteControlProtocolWidgetsModule::Get();

// 假设我们有一个有效的 RemoteControlPreset 和 FieldId
URemoteControlPreset* MyPreset = ...;
FGuid MyFieldId = ...;

// 添加一个 OSC 协议绑定
ProtocolWidgetsModule.AddProtocolBinding(FName(TEXT("OSC")));

// 为该字段生成协议实体的详细配置控件
TSharedRef<SWidget> DetailsWidget = ProtocolWidgetsModule.GenerateDetailsForEntity(MyPreset, MyFieldId, EExposedFieldType::Property);
// 可以将 DetailsWidget 添加到自定义的 Slate 面板中
```
*来源：基于 `IRemoteControlProtocolWidgetsModule.h` 接口定义*

### 进阶用法

监听协议绑定的变化事件，并重置绑定列表。
```cpp
// 获取模块实例
IRemoteControlProtocolWidgetsModule& ProtocolWidgetsModule = IRemoteControlProtocolWidgetsModule::Get();

// 绑定到“协议绑定被添加或移除”的委托
ProtocolWidgetsModule.OnProtocolBindingAddedOrRemoved().AddLambda([](ERCProtocolBinding::Op Operation)
{
    if (Operation == ERCProtocolBinding::Op::Added)
    {
        UE_LOG(LogTemp, Log, TEXT("A new protocol binding was added."));
    }
    else if (Operation == ERCProtocolBinding::Op::Removed)
    {
        UE_LOG(LogTemp, Log, TEXT("A protocol binding was removed."));
    }
});

// 绑定到“活动协议改变”的委托
ProtocolWidgetsModule.OnActiveProtocolChanged().AddLambda([](const FName NewActiveProtocolName)
{
    UE_LOG(LogTemp, Log, TEXT("Active protocol changed to: %s"), *NewActiveProtocolName.ToString());
});

// 在某些情况下（如预设重新加载）重置协议绑定列表的 UI
ProtocolWidgetsModule.ResetProtocolBindingList();
```
*来源：基于 `IRemoteControlProtocolWidgetsModule.h` 中的委托声明和方法*

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在自定义编辑器模块中集成 RemoteControlProtocolWidgets 的功能。

**MyEditorModule.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMyEditorModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    /** 用于存储委托句柄，以便在模块关闭时解绑 */
    FDelegateHandle OnProtocolBindingChangedHandle;
};
```

**MyEditorModule.cpp**
```cpp
#include "MyEditorModule.h"
#include "IRemoteControlProtocolWidgetsModule.h"

#define LOCTEXT_NAMESPACE "FMyEditorModule"

void FMyEditorModule::StartupModule()
{
    // 确保 RemoteControlProtocolWidgets 模块已加载
    if (IRemoteControlProtocolWidgetsModule::IsAvailable())
    {
        IRemoteControlProtocolWidgetsModule& ProtocolWidgetsModule = IRemoteControlProtocolWidgetsModule::Get();

        // 监听协议绑定变化，用于日志记录或自定义UI更新
        OnProtocolBindingChangedHandle = ProtocolWidgetsModule.OnProtocolBindingAddedOrRemoved().AddLambda(
            [](ERCProtocolBinding::Op Op)
            {
                UE_LOG(LogTemp, Display, TEXT("Remote Control Protocol Binding Operation: %d"), static_cast<int32>(Op));
            }
        );
    }
}

void FMyEditorModule::ShutdownModule()
{
    // 清理委托
    if (IRemoteControlProtocolWidgetsModule::IsAvailable())
    {
        IRemoteControlProtocolWidgetsModule& ProtocolWidgetsModule = IRemoteControlProtocolWidgetsModule::Get();
        ProtocolWidgetsModule.OnProtocolBindingAddedOrRemoved().Remove(OnProtocolBindingChangedHandle);
    }
}

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FMyEditorModule, MyEditor)
```

## 模块依赖

从模块名称和功能推断，`RemoteControlProtocolWidgets` 模块很可能依赖以下模块。由于未提供具体的 `Build.cs` 文件，此列表基于通用依赖和模块间关系推断。

| 模块 | 用途 |
|---|---|
| `RemoteControlCommon` | 提供远程控制的基础数据结构和通用功能。 |
| `RemoteControlProtocol` | 定义协议实体和协议处理的基类，是本模块配置的目标对象。 |
| `RemoteControlUI` | 提供 Remote Control 面板的基础 UI 框架和控件。 |
| `Slate`, `SlateCore` | 构建所有 UI 控件的基础。 |
| `EditorWidgets` | 可能用于一些通用的编辑器控件。 |

## 维护状态

### 近期更新

```
- 9415f7a3e695 Remote Control: Protocol bindings now correctly mark the preset modified when changing override mask.
- 3420c54257da Remote Control: fix bit shifting 32 bit value with subsequent expansion to 64 bit warning.
- 572ea757a0f4 Fix use of an expiring temporary in ProtocolPanelStyle.cpp
```

### 维护评价

-   **活跃维护**：最近的提交（2024年10月）集中在修复功能缺陷（掩码修改标记预设）和编译警告，表明该模块仍在被积极使用和维护。
-   **稳定性**：提交内容以 Bug 修复和代码质量改进为主，未见大规模重构或功能废弃标记，说明模块功能已趋于稳定。
-   **推荐使用**：作为 Remote Control API 这一重要虚拟制片工具链的关键 UI 组件，且维护状态良好，**推荐在需要协议绑定配置功能的项目中使用**。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl)
-   [官方文档](https://docs.unrealengine.com/5.7/en-US/remote-control-api-in-unreal-engine/) (Remote Control API 总体文档)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/RemoteControl/Tests) (插件级测试目录)