# Apple Image Utils

> Utilities that operate on CIImage, CVPixelBuffer, IOSurface, etc.

| 属性 | 值 |
|---|---|
| 分类 | Experimental |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | AppleImageUtils (Runtime), AppleImageUtilsBlueprintSupport (UncookedOnly) |
| 创建时间 | 2018-05-10 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AppleImageUtils) | |

## 用途

AppleImageUtils 提供了基于 Apple CoreImage / CoreGraphics 框架的图像格式转换工具。它的核心能力是将 UE 纹理（或 Apple 原生图像对象）异步转换为 JPEG、HEIF、PNG、TIFF 格式的字节数组。

这个 plugin 的存在意义在于：UE 原生的图像导出（如 `FImageUtils`）不支持 HEIF，且无法直接操作 Apple 平台原生的 CIImage、CVPixelBuffer、IOSurface 等类型。AppleImageUtils 填补了这个空缺，尤其在 iOS/macOS 上需要利用 GPU 加速编码、或需要与 Apple 原生图像管线对接的场景中不可替代。

此外，它还定义了 `IAppleImageInterface`——一个让自定义 Texture 类暴露 Apple 原生图像数据（CIImage、CVPixelBuffer、IOSurface、MTLTexture）的接口协议，被 AppleARKit 等 plugin 实现。

## 使用场景

- 你在 iOS 上截图后需要导出为 HEIF 格式（比 JPEG 更小更好）→ 用 AppleImageUtils 的 `ConvertToHEIF`
- 你需要从 ARKit 摄像头获取的 CVPixelBuffer 转成 PNG 保存到相册 → 用 `IAppleImageInterface` + `ConvertToPNG`
- 你需要将 UTexture2D 转换为 CGImageRef 以便传给 iOS 原生 API → 用 `UTexture2DToCGImage`
- 你需要在后台线程异步压缩大量截图 → 用异步版本的 Convert 函数，通过 `IAppleImageUtilsConversionTask` 轮询完成状态

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Convert To JPEG` | 异步将纹理转换为 JPEG 字节数组 | `UAppleImageUtilsBaseAsyncTaskBlueprintProxy` |
| `Convert To HEIF` | 异步将纹理转换为 HEIF 字节数组 | `UAppleImageUtilsBaseAsyncTaskBlueprintProxy` |
| `Convert To PNG` | 异步将纹理转换为 PNG 字节数组 | `UAppleImageUtilsBaseAsyncTaskBlueprintProxy` |
| `Convert To TIFF` | 异步将纹理转换为 TIFF 字节数组 | `UAppleImageUtilsBaseAsyncTaskBlueprintProxy` |

每个节点都是异步节点（Async Task），执行后通过 `OnSuccess` / `OnFailure` 委托返回结果。

### 通用参数

| 参数 | 类型 | 说明 |
|---|---|---|
| SourceImage | UTexture* | 源纹理（必须实现 `IAppleImageInterface`） |
| Quality | int32 | 压缩质量 0-100（仅 JPEG/HEIF 有效，默认 85） |
| bWantColor | bool | true=彩色 sRGB，false=灰度 |
| bUseGpu | true=GPU 加速编码，false=CPU 软编码 |
| Scale | float | 缩放比例（1.0=不缩放） |
| Rotate | ETextureRotationDirection | 旋转方向（None/Left/Right/Down + 镜像变体） |

### 使用示例（蓝图描述）

1. 获取一个实现了 `IAppleImageInterface` 的纹理引用（如来自 AppleARKit 的摄像头纹理）
2. 从蓝图中拖出引线，搜索 **Convert To JPEG** 节点
3. 连接 SourceImage、设置 Quality=90、bWantColor=true、bUseGpu=true
4. 将 **OnSuccess** 委托连接到自定义事件
5. 在自定义事件中，通过 `ConversionResult.ImageData`（`TArray<uint8>`）获取 JPEG 字节数据
6. 可以用 `ConversionResult.Error` 检查是否为 "Success"

## C++ 用法

### 头文件引入

```cpp
#include "IAppleImageUtilsPlugin.h"
#include "AppleImageUtilsBlueprintProxy.h"  // 如果需要蓝图代理
```

### 基本用法（异步转换）

通过模块接口异步将纹理转换为 JPEG：

```cpp
// 获取模块接口
IAppleImageUtilsPlugin& ImageUtils = IAppleImageUtilsPlugin::Get();

// 异步转换（源纹理必须实现 IAppleImageInterface）
TSharedPtr<FAppleImageUtilsConversionTaskBase, ESPMode::ThreadSafe> Task =
    ImageUtils.ConvertToJPEG(MyTexture, /*Quality=*/85, /*bWantColor=*/true, /*bUseGpu=*/true);

// 轮询任务完成（通常在 Tick 中）
if (Task.IsValid() && Task->IsDone())
{
    if (!Task->HadError())
    {
        TArray<uint8> JpegData = Task->GetData();  // MoveTemp，只调用一次
        FIntPoint ImageSize = Task->GetConvertedImageSize();
        float ElapsedMs = Task->GetElapsedTime();
    }
    else
    {
        FString Error = Task->GetErrorReason();
    }
}
```

> 来源：`Source/AppleImageUtils/Public/IAppleImageUtilsPlugin.h`、`Source/AppleImageUtils/Private/AppleImageUtilsPlugin.cpp`

### 进阶用法（CIImage 直接转换）

在 Apple 平台上可以直接传入 CIImage 进行同步转换（绕过 UTexture）：

```cpp
#if SUPPORTS_IMAGE_UTILS_1_0
    // 将 UTexture2D 转为 CGImageRef
    CGImageRef CGImage = IAppleImageUtilsPlugin::Get().UTexture2DToCGImage(MyTexture2D);

    // 同步转换 CIImage → JPEG 字节数组
    TArray<uint8> OutBytes;
    FIntPoint ConvertedSize;
    IAppleImageUtilsPlugin::Get().ConvertToJPEG(
        MyCIImage, OutBytes, /*Quality=*/85, /*bWantColor=*/true,
        /*bUseGpu=*/true, /*Scale=*/1.f, ETextureRotationDirection::None,
        &ConvertedSize
    );
#endif
```

> 注：CIImage 同步转换仅在 `SUPPORTS_IMAGE_UTILS_1_0`（iOS 10+ / macOS 10.12+）可用，HEIF/PNG/TIFF 需要 `SUPPORTS_IMAGE_UTILS_2_1`（iOS 11+）。

### 实现 IAppleImageInterface

如果你需要自定义纹理类型以支持 AppleImageUtils 转换，需要实现 `IAppleImageInterface`：

```cpp
// .h
#include "AppleImageUtilsTypes.h"

UCLASS()
class UMyAppleTexture : public UTexture, public IAppleImageInterface
{
    GENERATED_BODY()
public:
    virtual EAppleTextureType GetTextureType() const override { return EAppleTextureType::Image; }
    virtual CIImage* GetImage() const override { return MyCIImage; }
    // 或者返回 CVPixelBuffer / IOSurface / MTLTexture
};
```

## Demo 示例

一个完整的最小示例——在 iOS 上异步将纹理导出为 JPEG 数据：

```cpp
// MyImageExporter.h
#pragma once
#include "CoreMinimal.h"
#include "IAppleImageUtilsPlugin.h"

class FMyImageExporter
{
public:
    void ExportAsJPEG(UTexture* Texture)
    {
        if (!IAppleImageUtilsPlugin::IsAvailable())
        {
            UE_LOG(LogTemp, Warning, TEXT("AppleImageUtils not available"));
            return;
        }

        Task = IAppleImageUtilsPlugin::Get().ConvertToJPEG(Texture, 90, true, true);
    }

    void Tick()
    {
        if (Task.IsValid() && Task->IsDone())
        {
            if (!Task->HadError())
            {
                TArray<uint8> Data = Task->GetData();
                UE_LOG(LogTemp, Log, TEXT("JPEG export done: %d bytes, %.2f ms"),
                    Data.Num(), Task->GetElapsedTime());
            }
            Task.Reset();
        }
    }

private:
    TSharedPtr<FAppleImageUtilsConversionTaskBase, ESPMode::ThreadSafe> Task;
};
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.Add("AppleImageUtils");
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `Engine` | 纹理类型（UTexture、UTexture2D） |
| `CoreUObject` | UObject 系统（私有依赖） |

Apple 平台额外链接的 Framework：

| Framework | 用途 |
|---|---|
| `CoreImage` | CIImage、CIContext 等图像处理 API |
| `ImageIO` | CGImageDestination 等图像编码 API |

## 平台限制

- **运行时模块**（AppleImageUtils）：`.uplugin` 配置了 `SupportedPrograms: ["LiveLinkHub"]` 和 `ProgramAllowList: ["LiveLinkHub"]`，意味着此模块仅在 LiveLinkHub 程序中加载。普通游戏/编辑器项目中，该模块不会自动加载。
- **蓝图支持模块**（AppleImageUtilsBlueprintSupport）：仅在 Win64、Mac、Linux 编辑器中可用（UncookedOnly 类型，打包后不包含）。
- 异步转换接口（`ConvertToJPEG(UTexture*)` 等）在非 Apple 平台上会直接返回错误任务。
- CIImage 直接转换接口仅在 `#if SUPPORTS_IMAGE_UTILS_1_0` 条件下编译。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-05-30 | `2739c3d3` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types | 纯机械性 DLL 导出符号修复，无功能变更 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar | 同上，批量脚本化修改 |
| 2024-11-09 | `66e9bb39` | Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes | 清理废弃的 include 宏，无功能变更 |

### 维护评价

- **创建时间**：2018 年 5 月，从 Experimental 目录迁移到 Runtime
- **最近更新频率**：最近 3 次提交全部是编译工具链的机械性批量修改，无功能性更新
- **最后实质性更新**：长期无功能性变更
- **状态**：**维护不活跃** — 代码逻辑稳定但长期未有功能迭代
- **已知限制**：仅支持 Apple 平台；`.uplugin` 中 Category 仍标记为 "Experimental"（尽管已不在 Experimental 目录）；`SupportedPrograms` 限制为 LiveLinkHub
- **推荐使用**：如果你的项目确实需要 Apple 原生图像转换能力，该 plugin 可以正常使用且 API 稳定。但它是一个专用工具，适用场景有限。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AppleImageUtils)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 测试用例：无（未找到相关自动化测试）
- 使用方：[AppleARKit](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AR/AppleAR/AppleARKit)、[AppleARKitFaceSupport](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AR/AppleAR/AppleARKitFaceSupport)、[RemoteSession](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/RemoteSession)
