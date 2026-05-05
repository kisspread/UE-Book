# VirtualCameraCore

> Code for actors, components, and utilities for controlling and viewing cameras via physical devices. See VirtualCamera for content.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `DecoupledOutputProvider` (Runtime), `PixelStreamingVCam` (Runtime), `VCamBlueprintNodes` (Runtime), `VCamCore` (Runtime), `VCamCoreEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-02-07 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/VirtualCameraCore) | |

## 用途

VirtualCameraCore 是 Unreal Engine 虚拟制作工具链的核心插件，它提供了一套完整的框架，用于通过物理设备（如 iPad、手机或专用硬件）在 Unreal Engine 中实时控制和查看虚拟摄像机。该插件本身不包含具体的设备连接逻辑或 UI 内容，而是定义了核心的 Actor、组件、修改器（Modifier）和连接系统，为构建自定义的虚拟摄像机解决方案（如官方的 VirtualCamera 插件）提供了基础。

其主要解决的问题是：如何将外部设备的输入（如触摸、陀螺仪、按钮）映射到引擎内摄像机的控制参数（如位置、旋转、焦距），并实时预览摄像机画面。它通过模块化的设计，允许开发者扩展或替换默认的输入处理、输出提供者和 UI 逻辑。

## 使用场景

- **LED 墙拍摄**：在 LED 虚拟影棚中，导演或摄影师使用 iPad 作为虚拟摄像机，实时调整虚拟场景中的摄像机视角，以匹配实拍演员的位置和动作。
- **实时合成预览**：在拍摄现场，通过虚拟摄像机设备预览最终合成效果，帮助导演做出实时决策。
- **远程摄像机控制**：在无法直接操作引擎编辑器的场景下（如在片场），通过移动设备远程控制引擎内的虚拟摄像机。
- **自定义虚拟摄像机工具开发**：开发者基于此核心框架，开发具有特定功能或针对特定硬件的虚拟摄像机应用。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get All VCam Components In Level` | 获取当前关卡中所有已加载的、由 Actor 拥有的 VCamComponent，排除待销毁、PIE 或预览编辑器中的 Actor。 | `UVCamEditorLibrary` |

### 使用示例（蓝图描述）

1.  在蓝图中，使用 `Get All VCam Components In Level` 节点获取一个 `UVCamComponent` 的数组。
2.  遍历该数组，可以对每个组件进行操作，例如获取其当前状态、修改其属性或触发其功能。
3.  此节点通常用于编辑器工具或调试脚本，以批量处理场景中的虚拟摄像机组件。

## C++ 用法

### 头文件引入

```cpp
#include "IVCamCoreEditorModule.h"
#include "Customization/IConnectionRemapCustomization.h"
```

### 基本用法：注册连接重映射定制器

此示例展示了如何为自定义的 `UVCamWidget` 子类注册一个连接重映射定制器，以在细节面板中自定义其连接目标的显示方式。

```cpp
// 来源：基于 IVCamCoreEditorModule.h 和 IConnectionRemapCustomization.h 的接口设计
// 假设你有一个自定义的 Widget 类 UMyCustomVCamWidget

// 1. 创建一个定制器类
class FMyConnectionRemapCustomization : public UE::VCamCoreEditor::IConnectionRemapCustomization
{
public:
    virtual bool CanGenerateGroup(const UE::VCamCoreEditor::FShouldGenerateArgs& Args) const override
    {
        // 判断是否需要为传入的 Widget 生成自定义组
        return Args.CustomizedWidget.IsValid() && Args.CustomizedWidget->IsA<UMyCustomVCamWidget>();
    }

    virtual void Customize(const UE::VCamCoreEditor::FConnectionRemapCustomizationArgs& Args) override
    {
        // 使用 Args.Utils 和 Args.Builder 来添加自定义的细节面板行
        // 例如，添加一个自定义的连接目标设置
        if (Args.CustomizedWidget.IsValid())
        {
            // ... 自定义逻辑
        }
    }
};

// 2. 在模块启动时注册
void FMyGameModule::StartupModule()
{
    UE::VCamCoreEditor::IVCamCoreEditorModule& VCamEditorModule = UE::VCamCoreEditor::IVCamCoreEditorModule::Get();
    VCamEditorModule.RegisterConnectionRemapCustomization(
        UMyCustomVCamWidget::StaticClass(),
        UE::VCamCoreEditor::FGetConnectionRemappingCustomization::CreateLambda([]()
        {
            return MakeShared<FMyConnectionRemapCustomization>();
        })
    );
}

// 3. 在模块关闭时注销
void FMyGameModule::ShutdownModule()
{
    UE::VCamCoreEditor::IVCamCoreEditorModule& VCamEditorModule = UE::VCamCoreEditor::IVCamCoreEditorModule::Get();
    VCamEditorModule.UnregisterConnectionRemapCustomization(UMyCustomVCamWidget::StaticClass());
}
```

### 进阶用法：使用 IConnectionRemapUtils 添加连接

在 `Customize` 函数内部，你可以使用 `IConnectionRemapUtils` 来方便地添加标准的连接目标设置行。

```cpp
// 来源：基于 IConnectionRemapUtils.h 的接口设计
virtual void Customize(const UE::VCamCoreEditor::FConnectionRemapCustomizationArgs& Args) override
{
    // 假设我们有一个 FVCamConnection 数据
    FVCamConnection MyConnection;
    MyConnection.Name = TEXT("MyCustomInput");
    // ... 填充其他连接数据

    // 创建添加连接的参数
    UE::VCamCoreEditor::FAddConnectionArgs AddArgs(
        Args.WidgetGroup, // 要添加到的细节面板组
        MyConnection.Name,
        MyConnection,
        UE::VCamCoreEditor::FOnTargetSettingsChanged::CreateLambda([WeakWidget = Args.CustomizedWidget](const FVCamConnectionTargetSettings& NewSettings)
        {
            // 当用户在细节面板中修改设置时，此委托被调用
            // 将新设置应用到你的 Widget 或组件上
            if (UVCamWidget* Widget = WeakWidget.Get())
            {
                // ... 应用设置逻辑
            }
        }),
        Args.Utils->GetRegularFont()
    );

    // 使用 Utils 添加连接行
    Args.Utils->AddConnection(MoveTemp(AddArgs));
}
```

## Demo 示例

以下是一个最小化的自定义连接重映射定制器示例，它为所有 `UVCamWidget` 添加一个简单的连接行。

**MyConnectionCustomization.h**
```cpp
#pragma once

#include "Customization/IConnectionRemapCustomization.h"

class FMySimpleConnectionCustomization : public UE::VCamCoreEditor::IConnectionRemapCustomization
{
public:
    virtual bool CanGenerateGroup(const UE::VCamCoreEditor::FShouldGenerateArgs& Args) const override;
    virtual void Customize(const UE::VCamCoreEditor::FConnectionRemapCustomizationArgs& Args) override;
};
```

**MyConnectionCustomization.cpp**
```cpp
#include "MyConnectionCustomization.h"
#include "UI/VCamConnectionStructs.h"
#include "Customization/IConnectionRemapUtils.h"
#include "DetailLayoutBuilder.h"
#include "DetailGroup.h"

bool FMySimpleConnectionCustomization::CanGenerateGroup(const UE::VCamCoreEditor::FShouldGenerateArgs& Args) const
{
    // 为所有有效的 VCamWidget 生成组
    return Args.CustomizedWidget.IsValid();
}

void FMySimpleConnectionCustomization::Customize(const UE::VCamCoreEditor::FConnectionRemapCustomizationArgs& Args)
{
    // 创建一个示例连接数据
    FVCamConnection ExampleConnection;
    ExampleConnection.Name = TEXT("ExampleConnection");
    ExampleConnection.TargetSettings.bEnabled = true;

    // 定义设置变更回调
    auto OnSettingsChanged = UE::VCamCoreEditor::FOnTargetSettingsChanged::CreateLambda(
        [](const FVCamConnectionTargetSettings& NewSettings)
        {
            UE_LOG(LogTemp, Log, TEXT("Example connection settings changed. Enabled: %s"), NewSettings.bEnabled ? TEXT("True") : TEXT("False"));
        }
    );

    // 使用 Utils 添加连接
    UE::VCamCoreEditor::FAddConnectionArgs AddArgs(
        Args.WidgetGroup,
        ExampleConnection.Name,
        ExampleConnection,
        OnSettingsChanged,
        Args.Utils->GetRegularFont()
    );
    Args.Utils->AddConnection(MoveTemp(AddArgs));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PixelStreamingVCam` | 提供通过 Pixel Streaming 技术将虚拟摄像机画面流式传输到外部设备的功能。 |

## 维护状态

### 近期更新

- 462ec4ed8231 修复 V623 警告：检查 `?:` 运算符，避免创建临时对象后立即销毁。
- c2a96071abd5 修复虚拟制作编译器扩展，现在检查绑定的输入操作，因为 DefaultKeyMappings 位于不同的属性中。
- 21f9f4f5a41a 新创建的 `UEditorOnlyVCamModifier` 类现在是 `UEditorOnlyVCamModifierBlueprints`，这允许它们使用所有仅编辑器函数。

### 维护评价

VirtualCameraCore 是一个相对较新的插件（创建于 2023 年），目前处于 **Beta** 状态。从近期提交记录看，它仍在被 Epic Games 积极维护和开发，最近的提交集中在修复编译警告、适配引擎内部变更以及改进编辑器功能上。作为虚拟制作管线的核心组件，它预计会随着引擎版本持续更新。

**注意事项**：由于是 Beta 版本，其 API 和功能在未来版本中可能发生不兼容的更改。在生产环境中使用时需要谨慎，并做好应对更新的准备。

**推荐**：对于需要开发自定义虚拟摄像机解决方案或深度集成虚拟制作流程的项目，此插件是必要的基础。建议在开发环境中启用并测试，并密切关注其版本更新说明。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/VirtualCameraCore)
- [官方文档]()（暂无）