# RemoteSession

> A plugin for Unreal that allows one instance to act as a thin-client (rendering and input) to a second instance

| 属性 | 值 |
|---|---|
| 中文名 | 远程会话 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资源、设置） |
| 模块 | `RemoteSession` (Runtime), `RemoteSessionEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-03-18 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RemoteSession) | |

## 用途

RemoteSession 插件允许一个 Unreal Engine 实例作为“瘦客户端”远程连接另一个实例，实现跨机器的渲染、输入和交互。它基于 PixelStreaming 技术栈，通过信令服务器建立通道，支持自定义协议（如 Hello 协议同步版本和端口）。该插件特别适合需要将编辑器或游戏画面流送到另一台设备并进行操控的场景，例如远程评审、多人协作调试或移动端预览。

RemoteSessionEditor 模块提供了编辑器内的 Slate UI 工具，用于管理远程会话流（Stream）的配置、启动和预览。它包含一个独立的 Nomad Tab 面板，允许用户选择 UMG Widget 或自定义通道，并实时查看远程渲染结果。

## 使用场景

- **远程协作评审**：在编辑器中将关卡或 UI 流送至另一台机器，供他人查看并提供反馈。
- **移动端预览**：通过局域网将游戏画面实时传输到手机或平板，并触摸控制。
- **多人远程调试**：一个实例作为主机，多个客户端连接查看不同视角或输入。
- **自定义协议扩展**：利用已有的 RemoteSession 通道机制，开发如数据仪表盘、远程控制台等专用工具。

## 蓝图用法

RemoteSessionEditor 模块主要提供编辑器 UI，不暴露公开的蓝图可调用函数。RemoteSession 运行时模块（`RemoteSession`）包含与远程会话交互的核心功能，但该模块的头文件未在本次分析范围内。

建议通过编辑器界面（Window → Remote Session）使用即可。

## C++ 用法

### 头文件引入

使用 RemoteSessionEditor 模块的 C++ API 时，包含：

```cpp
#include "RemoteSessionEditorModule.h"
#include "Widgets/SRemoteSessionStream.h"
```

### 基本用法

**启动远程会话流面板**（编辑器代码）：

```cpp
// 注册 Nomad Tab 间谍器（通常在模块 StartupModule 中调用）
TSharedPtr<FWorkspaceItem> WorkspaceGroup = ...;
SRemoteSessionStream::RegisterNomadTabSpawner(WorkspaceGroup.ToSharedRef());
```

**获取当前打开的流面板实例**：

```cpp
TSharedPtr<SRemoteSessionStream> StreamPanel = SRemoteSessionStream::GetPanelInstance();
if (StreamPanel.IsValid())
{
    // 可以访问面板的成员函数或状态
}
```

**自定义流设置**（使用 `URemoteSessionStreamWidgetUserData` 附加到资产）：

```cpp
// 在 UAssetUserData 子类中配置
URemoteSessionStreamWidgetUserData* UserData = NewObject<URemoteSessionStreamWidgetUserData>(YourAsset);
UserData->WidgetClass = UMyUserWidget::StaticClass();
UserData->Size = FVector2D(1920, 1080);
UserData->Port = 8888;
UserData->RenderTarget = MyRenderTarget;
```

### 进阶用法

**创建自定义通道**：继承 `IRemoteSessionChannel` 并注册到会话角色（`IRemoteSessionRole`），实现自定义数据传输。RemoteSessionEditor 模块的 `SRemoteSessionStream` 内部管理了这些通道的创建和销毁。

## Demo 示例

以下是一个最小示例，展示如何在编辑器模块启动时注册 RemoteSession 流 Tab，并提供默认设置。

### RemoteSessionEditorDemo.cpp

```cpp
#include "RemoteSessionEditorDemo.h"
#include "Widgets/SRemoteSessionStream.h"
#include "WorkspaceMenuStructureModule.h"

void FRemoteSessionEditorDemoModule::StartupModule()
{
    // 获取 Workspace 菜单组
    const auto& MenuStructure = WorkspaceMenu::GetMenuStructure();
    TSharedRef<FWorkspaceItem> RemoteSessionGroup = MenuStructure.GetDeveloperToolsMiscCategory()->AddGroup(
        LOCTEXT("RemoteSessionGroup", "Remote Session"),
        LOCTEXT("RemoteSessionGroup_Tooltip", "Open Remote Session tools"),
        FSlateIcon()
    );

    // 注册 Nomad Tab
    SRemoteSessionStream::RegisterNomadTabSpawner(RemoteSessionGroup);
}

void FRemoteSessionEditorDemoModule::ShutdownModule()
{
    SRemoteSessionStream::UnregisterNomadTabSpawner();
}

IMPLEMENT_MODULE(FRemoteSessionEditorDemoModule, RemoteSessionEditorDemo)
```

### RemoteSessionEditorDemo.h

```cpp
#pragma once

#include "Modules/ModuleInterface.h"

class FRemoteSessionEditorDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};
```

### 依赖配置

在 `Build.cs` 中添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "RemoteSession",           // 运行时模块
    "RemoteSessionEditor",     // 编辑器模块
    "PixelStreaming",          // 底层流媒体
    "PixelStreamingServers"    // 信令服务器
});
```

## 模块依赖

基于 `RemoteSessionEditor` 模块的 `Build.cs` 依赖列表，去除标准引擎模块后，独特依赖如下：

| 模块 | 用途 |
|---|---|
| `RemoteSession` | 运行时核心，管理会话通道和连接 |
| `PixelStreaming` | 提供视频编码和 WebRTC 传输 |
| `PixelStreamingServers` | 信令服务器（Signalling Server）的启动与管理 |
| `PixelStreamingEditor` | 编辑器侧 PixelStreaming 集成 |
| `PixelStreaming2` | 下一代 PixelStreaming 库 |
| `PixelStreaming2Settings` | PixelStreaming2 配置选项 |
| `EditorFramework` | 编辑器通用框架（Tab 注册等） |
| `UnrealEd` | 编辑器核心模块 |

> 说明：如果你希望在自己的模块中使用 RemoteSessionEditor 的 UI 功能，请确保依赖上述模块。

## 维护状态

### 近期更新

- 2025-09-23 `85a3d914` 新增 RemoteSession Hello 协议，用于同步 PixelStreaming 版本和信令服务器端口。
- 2025-09-03 `28e61d07` 之前 Backout 后重新提交相同更改。
- 2025-05-31 `52e3dac1` 更新头文件，修正 DLL 存储说明（UnrealCodeFixup）。
- 2025-03-18 `a6af603c` 修正 `FormatStringSan` 中缺失的说明符。

### 维护评价

RemoteSession 是一个相对较新的插件（创建于 2025 年 3 月），目前处于活跃维护状态。最近的提交增加了 Hello 协议功能，表明开发团队正在积极扩展协议能力。代码质量通过常规更新得到保证。插件分类为 Experimental，但已纳入引擎官方插件列表。推荐用于需要远程流媒体和轻量级客户端的项目，但请注意其仍属于实验性质，生产环境使用前应充分测试。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RemoteSession)
- [RemoteSessionEditor 模块头文件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/RemoteSession/Source/RemoteSessionEditor/Private/SRemoteSessionStream.h)
- [测试用例（可能位于引擎测试目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Tests)