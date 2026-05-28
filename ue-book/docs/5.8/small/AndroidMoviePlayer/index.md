# Android Movie Player

> Android Platform Movie Player using Android Media library

| 属性 | 值 |
|---|---|
| 中文名 | Android电影播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidMoviePlayer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2014-11-20 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidMoviePlayer) | |

## 用途

此插件为 **Android 平台** 提供了 **IMovieStreamer** 接口的具体实现，专门用于播放 **启动电影** 和 **加载界面电影**。它使用 Android 原生的 Media Player 库，处理视频队列、纹理渲染到 Slate 视口以及播放状态管理。其主要存在的意义是为 Android 设备提供与平台原生媒体播放器兼容的、高性能的电影播放功能，解决在 Android 上播放启动/加载电影时的特定实现和优化问题。

## 使用场景

- 你需要为 Android 游戏播放启动时的公司 Logo、游戏片头动画。
- 你的游戏需要在关卡加载时播放一段过渡动画（加载界面电影）。
- 你使用 `MoviePlayer` 子系统来管理启动/加载电影的播放队列，并希望在 Android 平台上获得原生实现。

## 蓝图用法

此插件的核心功能主要通过 C++ 接口 `IMovieStreamer` 暴露，并由引擎的 `MoviePlayer` 子系统在内部调用。它不直接提供 `BlueprintCallable` 节点，但播放启动电影和加载电影的行为通常通过 **项目设置** 或 **蓝图** 中的 `Movie Player` 相关节点来触发和控制。

### 核心接口

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Init` | 初始化流媒体器，传入待播放的电影路径列表和播放类型。 | `IMovieStreamer` |
| `Tick` | 每帧更新电影播放状态、处理纹理提交。 | `IMovieStreamer` |
| `ForceCompletion` | 强制结束当前电影播放。 | `IMovieStreamer` |
| `Cleanup` | 清理所有资源，包括纹理和 Java 对象。 | `IMovieStreamer` |

### 使用示例（蓝图描述）

1.  **配置启动电影**：在“项目设置” -> “Movies”中配置启动电影列表。
2.  **蓝图触发加载电影**：在关卡蓝图或UI蓝图中，调用 `Get Movie Player` 节点获取 `Movie Player` 子系统对象，然后使用其提供的 `Play Movie` 等节点。
3.  引擎内部会根据平台（Android）自动选择并使用 `FAndroidMediaPlayerStreamer` 来处理实际的播放。

## C++ 用法

### 头文件引入

```cpp
#include "AndroidMovieStreamer.h"
```
（通常用于自定义或扩展，而非直接使用）

### 基本用法

此插件的代码主要用于被引擎的 `MoviePlayer` 模块在 Android 平台上自动实例化和使用。使用者无需直接操作它，除非需要深度定制。其初始化由引擎内部完成。

### 进阶用法

理论上，可以通过继承或修改 `FAndroidMediaPlayerStreamer` 来扩展电影播放行为（例如，自定义着色器效果）。但这需要深入了解 `MoviePlayer` 和 Slate 渲染管线。

## Demo 示例

以下示例展示了如何通过继承创建一个简单的自定义 Android 电影流媒体器（仅作结构参考，实际编译需更多上下文和依赖）。

**CustomAndroidMovieStreamer.h**
```cpp
#pragma once

#include "AndroidMovieStreamer.h"

class FCustomAndroidMovieStreamer : public FAndroidMediaPlayerStreamer
{
public:
    // 可以重写 Init, Tick 等方法加入自定义逻辑
    virtual bool Init(const TArray<FString>& MoviePaths, TEnumAsByte<EMoviePlaybackType> inPlaybackType) override;
    virtual bool Tick(FRHICommandListBase& RHICmdList, float DeltaTime) override;

    // 示例：添加一个自定义方法
    void ApplyCustomShaderEffect();
};
```

**CustomAndroidMovieStreamer.cpp**
```cpp
#include "CustomAndroidMovieStreamer.h"

bool FCustomAndroidMovieStreamer::Init(const TArray<FString>& MoviePaths, TEnumAsByte<EMoviePlaybackType> inPlaybackType)
{
    // 调用父类初始化
    bool bSuccess = FAndroidMediaPlayerStreamer::Init(MoviePaths, inPlaybackType);
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Custom Android Movie Streamer Initialized"));
    }
    return bSuccess;
}

bool FCustomAndroidMovieStreamer::Tick(FRHICommandListBase& RHICmdList, float DeltaTime)
{
    // 调用父类 Tick
    bool bResult = FAndroidMediaPlayerStreamer::Tick(RHICmdList, DeltaTime);

    // 在每一帧的 Tick 中执行自定义操作，例如应用自定义着色器
    ApplyCustomShaderEffect();

    return bResult;
}

void FCustomAndroidMovieStreamer::ApplyCustomShaderEffect()
{
    // 实现自定义效果逻辑...
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。具体依赖关系已由引擎的 `MoviePlayer` 模块和 Android 平台层处理。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从旧版 UE_LOG 迁移至新版 UE_LOGF。 |
| 2025-10-08 | `018dadd6` | Changing a number of places that use implicit command lists to instead use the one already available | 将多处使用隐式命令列表的代码，改为使用已存在的显式命令列表。 |
| 2025-08-08 | `40e2c8da` | Passing RHI Command Lists through to MoviePlayer and TickableObjectRenderThread functions. | 将 RHI 命令列表显式传递给 MoviePlayer 和 TickableObjectRenderThread 相关函数。 |
| 2025-06-16 | `ad86fe41` | Fixed black screen when playing start movies by forcing MovieStreamer to use BitmapRendererLegacy. | 修复播放启动电影时黑屏问题，强制电影流媒体器使用 BitmapRendererLegacy 渲染器。 |
| 2025-06-05 | `092054b1` | A temporary fix to the black screen when playing startup movies. | 临时修复播放启动电影时的黑屏问题。 |

### 维护评价

- **创建时间**：2014 年创建，是一个非常成熟的插件。
- **近期更新**：尽管年龄较大，但在 2025-2026 年仍有实质性更新，主要集中在 **RHI 命令列表传递重构** 和 **修复关键的启动黑屏问题**。这表明 Epic 仍在维护它以适应引擎底层渲染管线的变更。
- **活跃状态**：**维护中**。最近一年有多次重要提交，解决了实际问题。
- **已知限制**：仅限于 Android 平台。功能专一，仅用于播放启动/加载电影。
- **使用推荐**：**推荐使用**。对于需要在 Android 上播放启动电影或加载电影的项目，这是官方的、经过长期验证的解决方案。尽管代码结构老旧，但其功能稳定且持续维护。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AndroidMoviePlayer)