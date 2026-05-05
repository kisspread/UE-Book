# Camera Shake Previewer

> Adds a new panel, accessible from the Level Editor, which lets the user preview camera shakes in editor viewports.

| 属性 | 值 |
|---|---|
| 分类 | Cameras |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | CameraShakePreviewer (Editor) |
| 创建时间 | 2019-11-21 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Cameras/CameraShakePreviewer) | |

## 用途

CameraShakePreviewer 是一个纯编辑器插件，让你在关卡编辑器的视口中实时预览 Camera Shake 效果，而无需运行游戏。

它解决的核心问题是：美术和设计师在配置 `ACameraShakeSourceActor` 时，需要反复 Play-In-Editor 才能看到效果，效率很低。这个插件在编辑器视口中直接播放 Camera Shake，所见即所得。

工作原理：
1. 在 Level Editor 的 **Window** 菜单下注册一个 "Camera Shake Previewer" 面板
2. 在视口选项菜单中添加 "Allow Camera Shakes" 开关
3. 面板自动扫描关卡中所有 `ACameraShakeSourceActor`，列出它们的 Camera Shake 类
4. 点击 Play 后，通过 `FCameraShakePreviewer`（来自 GameplayCameras 模块）将 shake 效果注入到编辑器视口的 View Modifier 管线中

## 使用场景

- 你关卡里放置了多个 `ACameraShakeSourceActor`，想快速预览每个 shake 的效果 → 打开面板，逐个播放
- 你正在迭代 Camera Shake 的曲线和参数，想即时看到修改效果 → 开启视口的 shake 预览，在 Details 面板修改参数后实时反馈
- 你需要同时预览多个 shake 叠加的效果 → 用 "Play/Stop All" 按钮

## 编辑器用法

这是一个纯 Editor 模块，没有 BlueprintCallable 接口。所有功能通过编辑器 UI 操作。

### 打开面板

**菜单路径**: Level Editor → **Window** → **Cinematics** → **Camera Shake Previewer**

面板会在编辑器底部以 Tab 形式打开。

### 启用视口预览

1. 在任意 Perspective 视口中，点击视口左上角的 **视口选项菜单** (⋮)
2. 找到 **Camera Options** 区域
3. 勾选 **Allow Camera Shakes**

> ⚠️ 该选项仅在 Perspective 视口中可见。正交视口不会显示此选项。

### 面板功能

面板显示三列列表：

| 列 | 说明 |
|---|---|
| Camera Shake Name | Camera Shake 蓝图类名 |
| Scene Actor Name | 场景中 Source Actor 的名称 |
| Status | Playing / Stopped / (Hidden) |

底部按钮：

- **Play/Stop All** — 同时播放或停止列表中所有 Camera Shake
- **Play/Stop Selected** — 仅播放或停止选中的 Camera Shake
- **Active Viewport** — 显示当前活跃视口编号

### 警告信息

面板会显示以下警告：

- **"Camera shakes previewing is off"** — 当前视口未启用 Allow Camera Shakes
- **"Real-time mode is off"** — 视口未开启实时模式，shake 效果会断断续续
- **"No active viewport"** — 没有选中的活跃视口

### 注意事项

- 隐藏（Hidden）的 Actor 的 Camera Shake 会自动停止并标记为 (Hidden)
- 如果在 Details 面板中修改了 Source Actor 的 Camera Shake 类，面板会自动切换到新类并保持播放状态
- 支持 Undo/Redo，撤销操作后列表会自动刷新

## C++ 用法

### 头文件引入

```cpp
#include "CameraShakePreviewerModule.h"
```

### 模块交互

可以通过 C++ 获取模块实例来程序化控制预览状态：

```cpp
// 获取模块实例
FCameraShakePreviewerModule& Module = FModuleManager::GetModuleChecked<FCameraShakePreviewerModule>("CameraShakePreviewer");

// 查询某个视口是否启用了 shake 预览
FLevelEditorViewportClient* ViewportClient = /* 获取视口客户端 */;
bool bIsPreviewing = Module.HasCameraShakesPreview(ViewportClient);

// 切换某个视口的 shake 预览状态
Module.ToggleCameraShakesPreview(ViewportClient);

// 监听预览状态变化
Module.OnTogglePreviewCameraShakes.AddLambda([](const FTogglePreviewCameraShakesParams& Params)
{
    UE_LOG(LogTemp, Log, TEXT("Viewport %p preview shakes: %s"),
        Params.ViewportClient,
        Params.bPreviewCameraShakes ? TEXT("ON") : TEXT("OFF"));
});
```

### FTogglePreviewCameraShakesParams 结构

```cpp
struct FTogglePreviewCameraShakesParams
{
    FLevelEditorViewportClient* ViewportClient = nullptr;  // 被切换的视口
    bool bPreviewCameraShakes = false;                      // 新的预览状态
};
```

## Demo 示例

本插件没有运行时 API，不需要 Demo。使用方式完全通过编辑器 UI。

如果你想在自己的编辑器工具中集成 Camera Shake 预览功能，可以参考以下模式：

```cpp
// MyEditorTool.cpp
#include "CameraShakePreviewerModule.h"
#include "LevelEditorViewport.h"

void FMyEditorTool::EnableShakePreviewOnActiveViewport()
{
    FCameraShakePreviewerModule& PreviewerModule = 
        FModuleManager::GetModuleChecked<FCameraShakePreviewerModule>("CameraShakePreviewer");

    // 遍历所有视口，对 Perspective 视口启用预览
    for (FLevelEditorViewportClient* VC : GEditor->GetLevelViewportClients())
    {
        if (VC->ViewportType == ELevelViewportType::LVT_Perspective)
        {
            if (!PreviewerModule.HasCameraShakesPreview(VC))
            {
                PreviewerModule.ToggleCameraShakesPreview(VC);
            }
        }
    }
}
```

Build.cs 依赖：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "CameraShakePreviewer"
});
```

> 注意：由于本插件是 Editor 类型，你的模块也必须是 Editor 模块才能依赖它。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础引擎功能 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（UWorld、AActor 等） |
| `InputCore` | 输入系统 |
| `GameplayCameras` | Camera Shake 核心实现（`FCameraShakePreviewer`） |
| `LevelEditor` | 关卡编辑器集成 |
| `Slate` / `SlateCore` | UI 框架 |
| `UnrealEd` | 编辑器框架 |
| `ToolMenus` | 菜单扩展系统 |
| `MovieScene` / `MovieSceneTracks` | Sequencer 集成（CameraShakePreviewer 来自 Sequencer 命名空间） |
| `PropertyEditor` | 属性编辑器 |
| `AppFramework` | 应用框架 |
| `ApplicationCore` | 应用核心 |
| `EditorFramework` | 编辑器框架 |

插件还依赖另一个插件：
- **GameplayCameras** — 提供 `FCameraShakePreviewer`、`UCameraShakeBase`、`ACameraShakeSourceActor` 等核心类

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-28 | `1c9d37f95bc0` | [Core] Fix bad use of remove during iteration | 修复迭代过程中删除元素的 bug |
| 2025-07-28 | `d1397571bc66` | [Backout] - CL44389834 | 回退了上一次提交 |
| 2025-07-28 | `6313e94677f5` | [Core] Fix bad use of remove during iteration | 第一次尝试修复，后被回退再重新提交 |

最近 3 次提交（均在 2025-07-28）都是同一个 bug fix：修复迭代时删除元素的问题。这是一个典型的先提交、回退、重新提交的流程，说明 Epic 内部对该修复有审查过程。

### 维护评价

- **年龄**: 创建于 2019 年 11 月，约 6.5 年历史
- **最近更新**: 2025-07-28，有实质性 bug 修复
- **维护状态**: 维护中 — 虽然更新频率不高，但仍有活跃的 bug 修复
- **Beta 状态**: `.uplugin` 中 `IsBetaVersion: true`，表明 Epic 仍将其视为实验性功能
- **已知限制**:
  - 仅支持 Perspective 视口
  - 需要视口开启 Real-time 模式才能正常预览
  - 仅扫描 `ACameraShakeSourceActor`，不支持通过代码手动触发的 Camera Shake
- **推荐**: ✅ 推荐使用。作为免费的编辑器工具，对 Camera Shake 的调试迭代非常有帮助。虽然标记为 Beta，但功能稳定可用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Cameras/CameraShakePreviewer)
- GameplayCameras 插件（提供底层 Camera Shake 实现）
