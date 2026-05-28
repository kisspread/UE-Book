# Camera Shake Previewer

> Adds a new panel, accessible from the Level Editor, which lets the user preview camera shakes in editor viewports.

| 属性 | 值 |
|---|---|
| 中文名 | 相机抖动预览器 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `CameraShakePreviewer` (Editor) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2019-11-21 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/CameraShakePreviewer) | |

## 用途

本插件的核心价值在于**编辑器内的视觉化测试**。它解决了在游戏开发阶段，设计师和程序员需要反复进入游戏运行模式（PIE）来测试和调整 `Camera Shake` 效果的问题。

通过在编辑器视口中直接注入和预览相机抖动，开发者可以：
1.  **快速迭代**：实时调整抖动参数（如振幅、频率、时长），无需等待游戏编译和启动。
2.  **精准定位**：在特定的游戏视角和场景布局下预览效果，确保抖动与游戏场景、动画、镜头运镜完美配合。
3.  **提高效率**：避免在复杂的PIE流程中反复查找和触发抖动源，专注于效果本身。

## 使用场景

-   **关卡设计师/美术师**：在编辑器中预览并调整在特定剧情或游戏事件中应该发生的相机抖动效果。
-   **程序员**：在开发新的 `UCameraShakeBase` 子类时，快速进行原型验证和调试。
-   **游戏设计师**：需要在游戏设计文档或演示中展示特定的镜头表现时，直接在编辑器中生成预览。

## 蓝图用法

此插件主要是一个编辑器工具面板，其核心交互通过编辑器UI完成，而非蓝图节点。它暴露了少量用于脚本化控制的功能。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ToggleCameraShakesPreview` | 切换指定编辑器视口是否启用相机抖动预览。 | `FCameraShakePreviewerModule` |
| `HasCameraShakesPreview` | 检查指定编辑器视口是否已启用相机抖动预览。 | `FCameraShakePreviewerModule` |

### 使用示例（蓝图描述）

1.  **手动启用**：最常用的方式是在关卡编辑器的视口工具栏中，找到“相机”下拉菜单，选择“切换相机抖动预览”。这会为当前视口启用抖动效果，并打开专用的预览面板。
2.  **程序化控制**：在C++或蓝图（通过获取`FCameraShakePreviewerModule`实例）中调用`ToggleCameraShakesPreview`函数，传入目标`FLevelEditorViewportClient`指针，可以实现通过代码批量开启或关闭多个视口的预览功能。

## C++ 用法

### 头文件引入

```cpp
#include "CameraShakePreviewerModule.h"
```

### 基本用法

通过模块接口控制相机抖动预览的开关。以下代码片段展示了如何为当前关卡编辑器的第一个活动视口启用预览。

```cpp
// 来源: 基于 Public/CameraShakePreviewerModule.h 接口设计的用法
#include "CameraShakePreviewerModule.h"
#include "Editor.h"
#include "LevelEditorViewport.h"

void EnableShakePreviewForFirstViewport()
{
    FCameraShakePreviewerModule& CameraShakePreviewerModule = FModuleManager::GetModuleChecked<FCameraShakePreviewerModule>(TEXT("CameraShakePreviewer"));

    // 获取第一个活动的关卡编辑器视口客户端
    if (GEditor && GEditor->GetLevelViewportClients().Num() > 0)
    {
        FLevelEditorViewportClient* ViewportClient = GEditor->GetLevelViewportClients()[0];
        // 切换预览状态
        CameraShakePreviewerModule.ToggleCameraShakesPreview(ViewportClient);

        UE_LOG(LogTemp, Log, TEXT("Camera shake preview for viewport '%s' is now: %s"),
            *ViewportClient->GetName(),
            CameraShakePreviewerModule.HasCameraShakesPreview(ViewportClient) ? TEXT("Enabled") : TEXT("Disabled"));
    }
}
```

### 进阶用法

订阅模块的委托，以便在预览状态发生变化时执行自定义逻辑。

```cpp
// 来源: 基于 Public/CameraShakePreviewerModule.h 中的委托声明
#include "CameraShakePreviewerModule.h"

// 定义一个处理函数
void OnShakePreviewToggled(const FTogglePreviewCameraShakesParams& Params)
{
    if (Params.ViewportClient)
    {
        UE_LOG(LogTemp, Log, TEXT("Viewport '%s' preview toggled to: %s"),
            *Params.ViewportClient->GetName(),
            Params.bPreviewCameraShakes ? TEXT("ON") : TEXT("OFF"));
        // 在这里可以添加自定义的UI更新或状态保存逻辑
    }
}

// 在某个类（如你的编辑器工具模块）的StartupModule中绑定委托
void FYourEditorModule::StartupModule()
{
    FCameraShakePreviewerModule* CameraShakePreviewerModule = FModuleManager::GetModulePtr<FCameraShakePreviewerModule>(TEXT("CameraShakePreviewer"));
    if (CameraShakePreviewerModule)
    {
        CameraShakePreviewerModule->OnTogglePreviewCameraShakes.AddRaw(this, &FYourEditorModule::OnShakePreviewToggled);
    }
}
```

## Demo 示例

一个最小化的编辑器工具命令示例，用于切换相机抖动预览。

**YourShakePreviewCommand.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FYourShakePreviewCommands
{
public:
    static void Register();
    static void Unregister();

    static void TogglePreview();
};
```

**YourShakePreviewCommand.cpp**
```cpp
#include "YourShakePreviewCommand.h"
#include "CameraShakePreviewerModule.h"
#include "Editor.h"
#include "LevelEditorViewport.h"
#include "Framework/Commands/UICommandInfo.h"
#include "Framework/Commands/Commands.h"

// 定义一个简单的UI命令
class FYourShakePreviewCommandsImpl : public TCommands<FYourShakePreviewCommandsImpl>
{
public:
    FYourShakePreviewCommandsImpl()
        : TCommands<FYourShakePreviewCommandsImpl>(
            TEXT("YourShakePreview"),
            NSLOCTEXT("YourShakePreview", "YourShakePreview", "Your Shake Preview Tool"),
            NAME_None,
            FAppStyle::GetAppStyleSetName())
    {
    }

    virtual void RegisterCommands() override
    {
        UI_COMMAND(TogglePreviewCommand, "Toggle Preview", "Toggle camera shake preview for the active viewport", EUserInterfaceActionType::Button, FInputChord());
    }

    TSharedPtr<FUICommandInfo> TogglePreviewCommand;
};

void FYourShakePreviewCommands::Register()
{
    FYourShakePreviewCommandsImpl::Register();
}

void FYourShakePreviewCommands::Unregister()
{
    FYourShakePreviewCommandsImpl::Unregister();
}

void FYourShakePreviewCommands::TogglePreview()
{
    FCameraShakePreviewerModule& CameraShakeModule = FModuleManager::GetModuleChecked<FCameraShakePreviewerModule>(TEXT("CameraShakePreviewer"));

    // 获取当前鼠标光标所在的视口
    FLevelEditorViewportClient* ActiveViewport = GEditor->GetLevelViewportClients().IsValidIndex(GCurrentLevelEditingViewportClient) ? GEditor->GetLevelViewportClients()[GCurrentLevelEditingViewportClient] : nullptr;

    if (ActiveViewport)
    {
        CameraShakeModule.ToggleCameraShakesPreview(ActiveViewport);
    }
}
```

## 模块依赖

本插件依赖于 `GameplayCameras` 插件提供的相机抖动核心功能。

| 模块 | 用途 |
|---|---|
| `GameplayCameras` | 提供 `UCameraShakeBase`、`FCameraShakePreviewer` 等核心抖动数据结构和逻辑 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-07-28 | `1c9d37f9` | [Core] Fix bad use of remove during iteration | 修复了迭代过程中错误移除元素的 bug |
| 2025-07-28 | `d1397571` | [Backout] - CL44389834 | 回滚了某个提交（CL44389834） |
| 2025-07-28 | `6313e946` | [Core] Fix bad use of remove during iteration | 再次修复迭代中移除元素的 bug |
| 2025-04-23 | `f10920cb` | [Slate] | Slate UI 相关的更新 |
| 2025-03-10 | `2d365f9e` | [Viewport Toolbar] Filter whole Camera submenu based on Perspective / Orthographic | 根据透视/正交视图模式过滤整个相机子菜单 |

### 维护评价

-   **状态**: **实验性但仍在维护中**。该插件自2019年创建，标记为 `IsBetaVersion=true`。尽管创建时间较长，但近期（2025年内）仍有活跃的代码提交，主要集中在修复核心迭代 bug 和适配编辑器UI的变更（如视口工具栏过滤），表明它仍在被 Epic 内部使用并维护。
-   **推荐**: **推荐用于开发和测试**。对于需要频繁调试相机抖动的项目，这是一个能极大提升效率的工具。由于是实验性功能，在未来的引擎版本中可能存在 API 变动的风险，但其核心价值（编辑器内预览）稳定。建议在项目中使用，并关注引擎升级时的兼容性说明。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/CameraShakePreviewer)
- 官方文档：暂无
- 测试用例：暂未发现独立的测试文件