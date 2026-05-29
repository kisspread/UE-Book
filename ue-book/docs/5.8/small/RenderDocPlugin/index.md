# RenderDoc Plugin

> RenderDoc graphics debugger/profiler integration.

| 属性 | 值 |
|---|---|
| 中文名 | 渲染调试集成 |
| 分类 | Rendering |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `RenderDocPlugin` (DeveloperTool) |
| 实验性 | 否 |
| 创建时间 | 2017-04-11 |
| 年龄标签 | 🏛️ 文物（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/RenderDocPlugin) | |

## 用途

RenderDoc Plugin 将 [RenderDoc](https://renderdoc.org/) 图形调试器直接集成到虚幻引擎中。RenderDoc 是一个开源的帧捕获工具，可以捕获 GPU 渲染调用、查看纹理/缓冲区状态、分析着色器执行，是排查渲染问题的利器。

这个插件解决的核心问题是：**无需手动附加 RenderDoc 进程，直接在编辑器或游戏中一键触发帧捕获**。插件负责：

1. **动态加载 RenderDoc DLL**：运行时查找并加载 `renderdoc.dll`，通过 `RENDERDOC_API` 接口与 RenderDoc 通信
2. **帧捕获管理**：支持单帧捕获、多帧捕获、延迟捕获（按帧数或秒数），通过 `IRenderCaptureProvider` 接口提供标准捕获能力
3. **编辑器集成**：在工具栏添加捕获按钮，在 PIE 运行时捕获
4. **丰富的配置选项**：通过开发者设置面板暴露所有 RenderDoc 捕获参数

## 使用场景

- 你需要调试某个材质在特定视角下出现的渲染伪影 → 用 RenderDoc 捕获该帧，逐个 Draw Call 排查
- 你在优化 GPU 性能，想查看每帧的资源绑定和状态 → 用 RenderDoc 的纹理查看器和管线状态检查
- 你遇到着色器编译错误或输出异常 → 用 RenderDoc 检查着色器输入输出和中间变量
- 你在开发自定义渲染 Pass，想验证 RHI 命令是否正确执行 → 用 BeginCapture/EndCapture 精确捕获
- 你只在 Linux/Win64 上开发，需要图形调试支持 → 此插件仅支持这两个平台

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CaptureFrame` | 捕获当前视口的单帧渲染数据 | `FRenderDocPluginModule` |

### 控制台命令

通过控制台变量（Console Variable）可控制捕获行为，所有设置也可在 **项目设置 → 开发者 → RenderDoc** 面板中配置：

| 命令 | 说明 | 默认值 |
|---|---|---|
| `renderdoc.CaptureAllActivity` | 捕获所有视口和编辑器窗口（而非仅当前视口） | `false` |
| `renderdoc.CaptureCallstacks` | 为所有 API 调用捕获调用栈 | `false` |
| `renderdoc.ReferenceAllResources` | 包含所有渲染资源（即使未使用），会显著增加文件大小 | `false` |
| `renderdoc.SaveAllInitials` | 始终保存所有资源的初始状态 | `false` |
| `renderdoc.CaptureDelayInSeconds` | 延迟单位为秒而非帧 | `false` |
| `renderdoc.CaptureDelay` | 触发捕获前的延迟帧数/秒数 | `0` |
| `renderdoc.CaptureFrameCount` | 捕获帧数（>1 时等同于 CaptureAllActivity） | `1` |
| `renderdoc.AutoAttach` | 启动时自动附加 RenderDoc | `false` |
| `renderdoc.EnableCrashHandler` | 使用 RenderDoc 的崩溃处理器 | `false` |

### 使用示例

**一键捕获当前帧**：
1. 确保已安装 RenderDoc 且 DLL 路径正确
2. 点击编辑器工具栏上的 **RenderDoc Capture Frame** 按钮
3. 捕获完成后自动打开 RenderDoc 查看捕获文件

**延迟捕获（调试特定时刻）**：
1. 打开 **项目设置 → 开发者 → RenderDoc**
2. 设置 `Capture Delay` 为 `120`，勾选 `Capture Delay In Seconds`
3. 触发捕获 → 120 秒后自动捕获，可在此期间准备场景状态

**程序化捕获（通过控制台）**：
- 输入 `renderdoc.CaptureFrame 1` 延迟 1 帧后捕获
- 输入 `renderdoc.CaptureAllActivity 1` 启用全活动捕获

## C++ 用法

### 头文件引入

```cpp
#include "IRenderDocPlugin.h"
#include "RenderDocPluginSettings.h"
```

### 基本用法

**检查插件可用性并触发帧捕获**：

```cpp
// 检查 RenderDoc 插件是否已加载
if (IRenderDocPlugin::IsAvailable())
{
    // 获取插件实例并触发当前视口的帧捕获
    IRenderDocPlugin& RenderDoc = IRenderDocPlugin::Get();
    
    // 通过 IRenderCaptureProvider 接口捕获当前视口
    // InFlags: 0 表示使用默认设置
    // InDestFileName: 空字符串表示使用默认文件名
    FViewport* Viewport = GEditor->GetActiveViewport();
    RenderDoc.CaptureFrame(Viewport, 0, TEXT(""));
}
```

**通过 RHI 命令列表进行精确捕获**：

```cpp
// 在渲染线程中，使用 BeginCapture/EndCapture 包裹特定渲染代码
FRHICommandListImmediate& RHICmdList = GRHICommandList.GetImmediateCommandList();

// 开始捕获
RenderDoc.BeginCapture(&RHICmdList, 0, TEXT("MyCustomCapture"));

// ... 执行你的自定义渲染命令 ...
RHICmdList.SetRenderTarget(MyRenderTarget, FTextureRHIRef());
RHICmdList.SetViewport(0, 0, 0, Width, Height, 0.0f, 1.0f);
DrawMyMesh(RHICmdList);

// 结束捕获（文件将自动保存）
RenderDoc.EndCapture(&RHICmdList);
```

### 进阶用法

**以编程方式配置捕获参数**：

```cpp
// 通过 CVar 系统动态修改捕获设置
IConsoleVariable* CVarCaptureAll = IConsoleManager::Get().FindConsoleVariable(TEXT("renderdoc.CaptureAllActivity"));
if (CVarCaptureAll)
{
    CVarCaptureAll->Set(1);  // 启用全活动捕获
}

IConsoleVariable* CVarCaptureDelay = IConsoleManager::Get().FindConsoleVariable(TEXT("renderdoc.CaptureDelay"));
if (CVarCaptureDelay)
{
    CVarCaptureDelay->Set(60);  // 延迟 60 帧/秒后捕获
}

IConsoleVariable* CVarDelayInSeconds = IConsoleManager::Get().FindConsoleVariable(TEXT("renderdoc.CaptureDelayInSeconds"));
if (CVarDelayInSeconds)
{
    CVarDelayInSeconds->Set(1);  // 切换为秒为单位
}
```

## Demo 示例

```cpp
// MyRenderDebugActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IRenderDocPlugin.h"
#include "MyRenderDebugActor.generated.h"

UCLASS()
class MYGAME_API AMyRenderDebugActor : public AActor
{
    GENERATED_BODY()

public:
    AMyRenderDebugActor();

    /** 触发 RenderDoc 帧捕获 */
    UFUNCTION(BlueprintCallable, Category = "RenderDoc")
    void TriggerCapture();

    /** 通过 RHI 命令列表进行精确捕获 */
    void CaptureRenderPass(FRHICommandListImmediate& RHICmdList, const FString& Label);

    /** 检查 RenderDoc 是否可用 */
    UFUNCTION(BlueprintPure, Category = "RenderDoc")
    bool IsRenderDocAvailable() const;
};
```

```cpp
// MyRenderDebugActor.cpp
#include "MyRenderDebugActor.h"
#include "IRenderDocPlugin.h"

AMyRenderDebugActor::AMyRenderDebugActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

bool AMyRenderDebugActor::IsRenderDocAvailable() const
{
    return IRenderDocPlugin::IsAvailable();
}

void AMyRenderDebugActor::TriggerCapture()
{
    if (!IRenderDocPlugin::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("RenderDoc plugin is not available."));
        return;
    }

    // 通过编辑器的活动视口触发捕获
    FViewport* Viewport = GEditor ? GEditor->GetActiveViewport() : nullptr;
    if (Viewport)
    {
        IRenderDocPlugin::Get().CaptureFrame(Viewport, 0, TEXT(""));
        UE_LOG(LogTemp, Log, TEXT("RenderDoc capture triggered on active viewport."));
    }
}

void AMyRenderDebugActor::CaptureRenderPass(FRHICommandListImmediate& RHICmdList, const FString& Label)
{
    if (!IRenderDocPlugin::IsAvailable())
    {
        return;
    }

    // 开始捕获 - 使用自定义标签作为文件名
    IRenderDocPlugin::Get().BeginCapture(&RHICmdList, 0, Label);

    // 此处放置你的自定义渲染代码
    // ...

    // 结束捕获
    IRenderDocPlugin::Get().EndCapture(&RHICmdList);
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

插件通过运行时动态加载 RenderDoc 的 DLL（`renderdoc.dll` / `librenderdoc.so`），不通过 Build.cs 链接。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `2a295e97` | Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 替换废弃的 GPU 等待函数为新的统一接口 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新的 UE_LOGF 格式 |
| 2026-03-16 | `a8820581` | [CaptureFrame] Give the RenderDoc, PixWin, and Xcode "CaptureFrame" toolbar entries each their own unique | 为不同捕获工具的工具栏按钮分配唯一标识 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复上次提交的查找替换错误 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退一个有问题的变更 |

### 维护评价

RenderDoc 插件创建于 2017 年，已有约 9 年历史，是虚幻引擎中成熟的图形调试工具集成。

- **活跃维护**：最近一次更新在 2026 年 4 月，主要跟进引擎 RHI 接口变更（如 `SubmitAndBlockUntilGPUIdle` 替换、`UE_LOG` 迁移），说明 Epic 持续维护此插件以兼容引擎演进
- **稳定可靠**：核心功能多年未有重大变化，说明插件已趋于稳定
- **平台限制**：仅支持 Win64 和 Linux，不支持 macOS 和主机平台
- **默认启用**：作为 DeveloperTool 类型模块默认启用，但仅在开发构建中生效
- **推荐使用**：对于 Win64/Linux 平台的图形调试需求，这是标准且推荐的工具。如果需要跨平台支持，需考虑替代方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/RenderDocPlugin)
- [官方文档](https://renderdoc.org/docs/index.html)
- [RenderDoc GitHub](https://github.com/baldurk/renderdoc)