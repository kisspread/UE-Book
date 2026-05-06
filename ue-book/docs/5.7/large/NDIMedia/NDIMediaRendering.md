# NDI Media

> Implements media source and media output using NDI protocol

| 属性 | 值 |
|---|---|
| 中文名 | NDI 媒体插件 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质模板、蓝图资产） |
| 模块 | `NDIMedia` (Runtime), `NDIMediaEditor` (Editor), `NDIMediaRendering` (Runtime), `NDISDK` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-07 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/NDIMedia) | |

## 用途

NDI（Network Device Interface）是一种低成本、低延迟的视频传输协议，广泛用于广播、直播和现场制作。此插件允许 Unreal Engine 通过 NDI 协议接收外部视频流（作为媒体源）和发送渲染画面（作为媒体输出），实现与 NDI 兼容设备（如摄像机、切换台、编码器）的实时交互。

- **接收**：将 NDI 流作为 `UMediaPlayer` 的源，在虚幻场景中显示（例如虚拟演播室背景、监控画面）。
- **发送**：将视口（或指定场景）渲染结果通过 NDI 推送至网络，供其他设备使用（例如游戏画面推流、虚拟摄像机输出）。

`NDIMediaRendering` 模块专注于像素格式转换，特别是 NDI 原生格式（如 UYVY 4:2:2 + 独立Alpha通道）到 Unreal 渲染所需的 RGBA 格式的 GPU 加速转换。

## 使用场景

- **虚拟制作**：在虚幻中构建虚拟场景，通过 NDI 实时输入真实摄像机画面，再进行合成输出。
- **演播室监控**：使用 NDI Monitor 接收多个信号源，在合成器或切换系统中预览。
- **游戏直播/教学**：将游戏画面通过 NDI 实时推送到 OBS 或其他编码器，无需采集卡。
- **多机位系统**：多个虚幻实例通过 NDI 互相传输视频流，实现分布式渲染。

## 蓝图用法

NDI Media 插件主要通过 `UMediaPlayer` 和 `UMediaSource` 类以及编辑器内的媒体面板使用，蓝图层面无需直接调用本模块的 shader。

> **注意**：`NDIMediaRendering` 是内部渲染模块，不暴露蓝图可调用函数。以下基于插件整体的常见操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开一个 NDI 媒体源（需先创建 `FileMediaSource` 并设置为 NDI 协议） | `MediaPlayer` |
| `OnMediaOpened` | 媒体成功打开时触发的事件 | `MediaPlayer` |
| `OnMediaOpenFailed` | 媒体打开失败时触发的事件 | `MediaPlayer` |
| `Play` / `Pause` / `Stop` | 控制播放 | `MediaPlayer` |
| `GetTexture` | 获取当前帧的渲染纹理（用于材质蓝图） | `MediaTexture` |

### 使用示例（蓝图描述）

1. **创建 NDI 媒体源**：  
   - 创建一个 `File Media Source` 资产，将其 `Media Protocol` 设置为 `NDI`。  
   - 在 `NDI Source Name` 属性中输入要连接的 NDI 设备名称（可以从 NDI Studio Monitor 等工具获取）。  
   - 将 `Duration` 设置为 0（无限循环）。  

2. **播放 NDI 流**：  
   - 在关卡蓝图中获取 `Media Player` 对象（可从 `File Media Source` 创建）。  
   - 连接 `Open Source` 节点到该媒体源。  
   - 连接 `On Media Opened` 事件到 `Play` 节点。  

3. **显示到 UI**：  
   - 创建一个 `Media Texture` 并关联到同一 `Media Player`。  
   - 将 `Media Texture` 赋值给 `Image` 控件的 `Brush` 属性，即可在 UI 中显示 NDI 画面。  

## C++ 用法

> `NDIMediaRendering` 模块主要提供着色器类 `FNDIMediaShaderUYVAtoBGRAPS`，用于将 NDI 特有的 UYVY+Alpha 双平面格式转换为标准的 BGRA 纹理，供引擎渲染管线使用。开发者通常不需要直接调用此类，而是通过 MediaIO 框架或 `FNDIMediaSampleConverter` 自动触发。

### 头文件引入

```cpp
#include "NDIMediaShaders.h"   // 位于 NDIMediaRendering 模块
```

### 基本用法

从源码提取，用于手动转换 NDI 帧（底层转换器自动调用时无需实现）：

```cpp
// 示例：在自定义媒体样本转换器中调用 NDI 着色器
void UMyMediaSampleConverter::ConvertGPU(
    FRHICommandListImmediate& RHICmdList,
    TRefCountPtr<FRHITexture>& InputUYVY,
    TRefCountPtr<FRHITexture>& InputAlpha,
    FIntPoint OutputSize,
    FNDIMediaShaderUYVAtoBGRAPS::FParameters ShaderParams)
{
    // 获取全局着色器实例
    auto* GlobalShader = GetGlobalShaderMap(GMaxRHIFeatureLevel)->GetShader<FNDIMediaShaderUYVAtoBGRAPS>();
    
    // 设置渲染参数（纹理、大小、颜色变换等）
    FNDIMediaShaderUYVAtoBGRAPS::FParameters Params(
        InputUYVY,
        InputAlpha,
        OutputSize,
        FMatrix44f::Identity,
        UE::Color::EEncoding::sRGB,
        FMatrix44f::Identity,
        MediaShaders::EToneMapMethod::None
    );
    
    // 运行 Draw 操作（省略具体 Draw 调用）
    // ...
}
```

*来源：基于 `NDIMediaShaders.h` 的 `FParameters` 构造函数和 `SetParameters` 方法。*

### 进阶用法

若需自定义颜色空间转换，可以修改 `FParameters` 中的 `ColorTransform`、`Encoding`、`CSTransform` 和 `ToneMapMethod`，例如：

```cpp
// 使用源文件的 Rec.709 色彩矩阵转换到线性 sRGB
FMatrix44f Rec709ToSRGB = // 计算转换矩阵
FNDIMediaShaderUYVAtoBGRAPS::FParameters Params(
    ..., 
    Rec709ToSRGB,
    UE::Color::EEncoding::Linear,
    Rec709ToSRGB,
    MediaShaders::EToneMapMethod::ACES
);
```

## Demo 示例

以下是一个最小化的 C++ 类，展示如何利用 `NDIMediaRendering` 的着色器在自定义媒体接收器中转换纹理（省略完整编译细节）：

**MyNDIReceiver.h**

```cpp
#pragma once
#include "CoreMinimal.h"
#include "RHI.h"
#include "RenderGraphDefinitions.h"
#include "NDIMediaShaders.h"

class FMyNDIReceiver
{
public:
    void ConvertNDIFrame(
        FRHICommandListImmediate& RHICmdList,
        TRefCountPtr<FRHITexture> UYVYTexture,
        TRefCountPtr<FRHITexture> AlphaTexture,
        FIntPoint OutputSize
    );
};
```

**MyNDIReceiver.cpp**

```cpp
#include "MyNDIReceiver.h"
#include "GlobalShader.h"
#include "RenderGraphBuilder.h"

void FMyNDIReceiver::ConvertNDIFrame(
    FRHICommandListImmediate& RHICmdList,
    TRefCountPtr<FRHITexture> UYVYTexture,
    TRefCountPtr<FRHITexture> AlphaTexture,
    FIntPoint OutputSize)
{
    // 获取着色器
    auto* Shader = GetGlobalShaderMap(GMaxRHIFeatureLevel)->GetShader<FNDIMediaShaderUYVAtoBGRAPS>();
    if (!Shader) return;

    // 准备参数
    FNDIMediaShaderUYVAtoBGRAPS::FParameters Params(
        UYVYTexture,
        AlphaTexture,
        OutputSize,
        FMatrix44f::Identity,      // 默认颜色变换
        UE::Color::EEncoding::sRGB,
        FMatrix44f::Identity,      // 默认色彩空间变换
        MediaShaders::EToneMapMethod::None
    );

    // 设置渲染目标并执行 Draw（简化：实际需创建 RDG 渲染）
    FRDGBuilder GraphBuilder(RHICmdList);
    // ... 创建输出纹理、Pass 等逻辑
    // Shader->SetParameters(...) 通过 BatchedParameters 设置
    // GraphBuilder.Execute();
}
```

> 实际生产代码建议通过 `IMediaSink` 或 `FNDIMediaSampleConverter` 处理，此示例仅供学习。

## 模块依赖

`NDIMediaRendering` 模块的 Build.cs 未提供，但从代码推断依赖如下（无特殊依赖，均为常见渲染模块）：

| 模块 | 用途 |
|---|---|
| `RHI` | 纹理资源接口 |
| `RenderCore` | 渲染管线基础 |
| `CoreUObject` | 对象系统 |
| `MediaShaders` | 媒体相关着色器工具（颜色转换、色调映射等） |

**注意**：若在插件中直接引用 `NDIMediaRendering`，还需确保已启用 `MediaIOFramework` 和 `MediaPlayerEditor`（从 .uplugin 的 Plugins 依赖中获取）。

## 维护状态

### 近期更新

- 2026-01-23 `1fa42043` — [NDIMedia] Fix Just in Time Rendering (JITR) and timecode synchronization.
- 2026-01-23 `d0f5497d` — [NDIMedia] Fix Framerate property to be editable in media profile.
- 2025-12-18 `c64f793f` — [NDIMedia] Fixing low quality render when receiving an NDI stream with alpha channel.
- 2025-10-14 `ad8c4215` — [NDI Media] Crash fix for NDIMediaOutput on Mac Platform - SupportsAnyThreadCapture is not supported
- 2025-10-07 `4137cc30` — Mac: Add NDI Support

### 维护评价

- **创建时间**：2025-10-07，距今约1年。
- **近期更新**：最近3个月内有多个 bug 修复，包括 JITR、帧率属性可编辑、Alpha 通道质量、Mac 崩溃等，表明处于积极维护状态。
- **模块状态**：虽标记为实验性，但功能逐渐完善，适合在项目中使用（注意启用时需要手工开启插件）。
- **兼容性**：支持 Win64、Mac、Linux，适用范围广。
- **推荐等级**：推荐用于生产环境，但建议在非关键系统上先行验证，尤其是带 Alpha 的流。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/NDIMedia)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/NDIMedia/Tests)（若存在）
- [官方文档](https://docs.unrealengine.com/latest/Interactive/NDIMedia)（NDI 集成说明，需自行搜索）