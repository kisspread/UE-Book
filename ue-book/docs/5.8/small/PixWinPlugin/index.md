# PIX on Windows GPU Capture Plugin

> PIX on Windows graphics debugger integration.

| 属性 | 值 |
|---|---|
| 中文名 | PIX Windows GPU 捕获 |
| 分类 | Rendering |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PixWinPlugin` (DeveloperTool) |
| 实验性 | 否 |
| 创建时间 | 2021-03-18 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/PixWinPlugin) | |

## 用途

PixWinPlugin 将 Microsoft PIX 图形调试器与 Unreal Engine 5 集成。它允许开发者在 Windows 平台上直接从引擎编辑器或通过控制台命令启动 PIX 捕获，以捕获一帧或多帧 GPU 渲染数据。捕获的 `.pix3` 文件可用于分析渲染管线、诊断 GPU 瓶颈、检查渲染状态和调试着色器，是图形程序员进行性能优化和 Bug 排查的强大工具。

## 使用场景

- 你在 Windows 平台上开发并希望分析特定场景（如复杂光照、大量粒子效果）的 GPU 性能 → 用 PixWinPlugin 捕获该帧，然后在 PIX 中详细分析。
- 你遇到渲染错误（如黑块、闪烁、材质错误） → 捕获问题帧，在 PIX 中逐步调试渲染命令和资源状态。
- 你需要对比引擎版本或不同设置下的渲染差异 → 使用 PIX 同时打开两个捕获文件进行对比分析。

## 蓝图用法

该插件主要通过编辑器 UI 和控制台命令与用户交互，未直接暴露蓝图可调用函数。其功能集成在编辑器中。

### 核心交互

| 方式 | 说明 |
|---|---|
| 编辑器工具栏按钮 | `CaptureFrame` 按钮（在“性能分析”或相关分组下），点击后触发当前视口的 PIX 捕获。 |
| 控制台命令 | `Pix.CaptureFrame`，在控制台输入可触发捕获。 |

### 使用示例（编辑器操作）

1.  在编辑器中打开一个 3D 视口（例如，关卡编辑器视口）。
2.  确保 Windows 平台上已安装最新版的 [Microsoft PIX](https://aka.ms/pix-download)。
3.  点击编辑器工具栏中的 **PIX 捕获** 按钮（图标或文字取决于编辑器版本），或在控制台输入 `Pix.CaptureFrame`。
4.  引擎会立即冻结当前帧，并生成一个 `.pix3` 捕获文件。
5.  捕获完成后，文件通常保存在项目的 `Saved/Captures` 目录下。用 PIX 工具打开此文件进行分析。

## C++ 用法

### 头文件引入

```cpp
#include "IPixWinPlugin.h"
```

### 基本用法

通过模块接口检查 PIX 插件是否可用，并手动触发捕获。此方法适用于需要通过 C++ 代码在特定逻辑点启动捕获的场景。

```cpp
// 检查 PIX 插件是否加载并可用
if (IPixWinPlugin::IsAvailable())
{
    // 获取插件实例
    IPixWinPlugin& PixPlugin = IPixWinPlugin::Get();

    // 捕获当前活动的视口，使用默认标志和文件名
    PixPlugin.CaptureFrame(nullptr, 0, FString());

    // 或者，捕获特定视口并指定文件名
    // FViewport* MyViewport = ...;
    // PixPlugin.CaptureFrame(MyViewport, 0, TEXT("MyCapture"));
}
```

### 进阶用法

手动控制捕获的开始和结束，用于捕获跨越多帧的操作或在 RHI 命令流中进行精确控制。**注意：** 这是低级 API，使用需谨慎。

```cpp
#include "RHICommandList.h"

// 假设在某个渲染相关的代码上下文中
if (IPixWinPlugin::IsAvailable())
{
    IPixWinPlugin& PixPlugin = IPixWinPlugin::Get();
    FRHICommandListImmediate& RHICmdList = FRHICommandListExecutor::GetImmediateCommandList();

    // 1. 开始捕获（指定一个窗口句柄用于 PIX 分析）
    HWND Hwnd = (HWND)GEngine->GameViewport->GetWindow()->GetNativeWindow()->GetOSWindowHandle();
    PixPlugin.BeginCapture(Hwnd, TEXT("AdvancedCapture"));

    // ... 在此处执行你想要捕获的渲染命令或游戏逻辑 ...

    // 2. 结束捕获
    PixPlugin.EndCapture(&RHICmdList, 0, TEXT("AdvancedCapture"));
}
```

## Demo 示例

一个最小化的可运行示例，展示如何在自定义编辑器按钮点击时触发 PIX 帧捕获。

### MyPixCaptureButton.h
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyPixCaptureButton
{
public:
    /** 注册一个编辑器工具栏按钮 */
    static void Register();
    static void Unregister();

private:
    /** 按钮点击回调 */
    static void OnCaptureButtonClicked();
};
```

### MyPixCaptureButton.cpp
```cpp
#include "MyPixCaptureButton.h"
#include "IPixWinPlugin.h"
#include "Framework/Commands/UIAction.h"
#include "Framework/MultiBox/MultiBoxBuilder.h"
#include "LevelEditor.h"

#define LOCTEXT_NAMESPACE "MyPixCaptureButton"

void FMyPixCaptureButton::Register()
{
    FLevelEditorModule& LevelEditorModule = FModuleManager::LoadModuleChecked<FLevelEditorModule>("LevelEditor");
    TSharedPtr<FExtender> Extender = MakeShareable(new FExtender);
    Extender->AddToolBarExtension("Play", EExtensionHook::After, nullptr,
        FToolBarExtensionDelegate::CreateStatic(&FMyPixCaptureButton::AddToolbarButton));
    LevelEditorModule.GetToolBarExtensibilityManager()->AddExtender(Extender);
}

void FMyPixCaptureButton::Unregister()
{
    // 在实际应用中，这里应移除扩展器
}

void FMyPixCaptureButton::AddToolbarButton(FToolBarBuilder& Builder)
{
    Builder.AddToolBarButton(
        FUIAction(FExecuteAction::CreateStatic(&FMyPixCaptureButton::OnCaptureButtonClicked)),
        NAME_None,
        LOCTEXT("CaptureLabel", "PIX Capture"),
        LOCTEXT("CaptureTooltip", "Capture a frame with PIX"),
        FSlateIcon(FCoreStyle::Get().GetStyleSetName(), "Icons.Camera")
    );
}

void FMyPixCaptureButton::OnCaptureButtonClicked()
{
    if (IPixWinPlugin::IsAvailable())
    {
        IPixWinPlugin::Get().CaptureFrame(nullptr, 0, FString());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("PIX on Windows plugin is not available."));
    }
}

#undef LOCTEXT_NAMESPACE
```

## 模块依赖

该插件的模块依赖在 `PixWinPlugin.Build.cs` 中定义。使用此插件本身不需要额外的模块依赖，因为它是一个独立的 DeveloperTool。但你需要确保项目已链接 PIX SDK 的动态链接库。

| 模块 | 用途 |
|---|---|
| 无特殊依赖（仅标准 Core/Engine/Slate 等） | |

**注意**：虽然模块本身没有特殊的运行时依赖，但实际使用 PIX 功能需要目标机器上安装 Microsoft PIX 应用程序。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `2a295e97` | Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 重构了 GPU 同步逻辑，用 `SubmitAndBlockUntilGPUIdle` 替换了旧函数。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 `UE_LOGF` 格式。 |
| 2026-03-16 | `a8820581` | [CaptureFrame] Give the RenderDoc, PixWin, and Xcode "CaptureFrame" toolbar entries each their own u… | 为不同图形调试工具（RenderDoc、PIX、Xcode）的捕获按钮设置了独立的唯一命令名称，避免冲突。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了上一次提交中的错误查找替换。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退了之前的某个提交（CL51314860）。 |

### 维护评价

- **活跃维护**：插件在 2026 年（按提交记录）仍有频繁更新，表明处于活跃维护状态。
- **功能完整**：作为 Microsoft PIX 的集成桥接插件，功能相对独立和稳定。
- **平台限制**：仅支持 Windows 平台 (`Win64`)。
- **推荐使用**：如果你在 Windows 上进行 UE5 图形开发和性能分析，**强烈推荐使用**。它是连接 UE5 和专业图形调试工具的关键桥梁，能极大提升调试效率。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/PixWinPlugin)
- [官方文档]() (无)
- [测试用例]() (源码中未包含专门测试文件)