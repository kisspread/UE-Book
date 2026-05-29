# Apple Image Utils

> Utilities that operate on CIImage, CVPixelBuffer, IOSurface, etc.

| 属性 | 值 |
|---|---|
| 中文名 | 苹果图像工具 |
| 分类 | Experimental |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AppleImageUtils` (Runtime), `AppleImageUtilsBlueprintSupport` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2019-06-10 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AppleImageUtils) | |

## 用途

AppleImageUtils 插件并非用于通用的纹理处理，而是专门解决在苹果平台（iOS, macOS）上，使用原生苹果框架处理图像的需求。它提供了一套跨版本、异步的 API，核心功能是将 `UTexture` 或原生的苹果图像对象（如 `CIImage`）转换为多种标准图像格式的字节数组（JPEG, HEIF, PNG, TIFF），并支持在转换过程中进行缩放和旋转。

这个插件的存在是因为：
1.  **访问原生能力**：允许 UE 代码访问和使用 `CIImage`、`CVPixelBuffer`、`IOSurface`、`MTLTexture` 等苹果专有的高性能图像数据结构。
2.  **高效格式转换**：特别是支持 `HEIF` 这种苹果推广的高效图像格式，这是 UE 内置压缩功能所不具备的。
3.  **异步处理**：图像压缩（特别是使用 GPU）可能耗时，该插件将操作异步化，避免阻塞游戏线程。
4.  **版本兼容**：通过 `FAppleImageUtilsAvailability` 类运行时检测系统对不同版本 ImageUtils 框架的支持情况，确保代码在不同 OS 版本上安全运行。

## 使用场景

- 你的游戏或应用需要在 iOS 或 macOS 上实现高效率的屏幕截图、视频帧捕捉或 AR 图像捕获，并希望保存为苹果平台优化的 HEIF 格式。
- 你需要将 UE 的 `UTexture2D` 转换为 `CGImage`，以便用于苹果原生的图像处理或 UI 框架。
- 你在开发 LiveLink 或类似需要处理实时视频流的应用，并需要快速、异步地将纹理数据编码为可传输的格式。
- 你需要对从相机（如 ARKit）获取的 `CVPixelBuffer` 或 `IOSurface` 进行格式转换和压缩。

## 蓝图用法

蓝图功能主要通过 `UAppleImageUtilsBaseAsyncTaskBlueprintProxy` 类提供，它封装了异步转换任务，并提供了易于使用的蓝图事件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Proxy Object For Convert To JPEG` | 创建一个异步任务，将纹理转换为 JPEG 格式 | `UAppleImageUtilsBaseAsyncTaskBlueprintProxy` |
| `Create Proxy Object For Convert To HEIF` | 创建一个异步任务，将纹理转换为 HEIF 格式 | `UAppleImageUtilsBaseAsyncTaskBlueprintProxy` |
| `Create Proxy Object For Convert To PNG` | 创建一个异步任务，将纹理转换为 PNG 格式 | `UAppleImageUtilsBaseAsyncTaskBlueprintProxy` |
| `Create Proxy Object For Convert To TIFF` | 创建一个异步任务，将纹理转换为 TIFF 格式 | `UAppleImageUtilsBaseAsyncTaskBlueprintProxy` |

### 使用示例（蓝图描述）

1.  使用 “Convert To JPEG” 节点，传入一个 `UTexture` 引用（如渲染目标）。
2.  拖出该节点的返回值（`UAppleImageUtilsBaseAsyncTaskBlueprintProxy` 对象），并绑定 `OnSuccess` 和 `OnFailure` 事件。
3.  在 `OnSuccess` 事件中，从 `ConversionResult` 结构获取 `ImageData`（TArray<uint8>）和 `Error` 信息。
4.  你可以将 `ImageData` 保存到文件或通过网络发送。

## C++ 用法

C++ 用法分为两层：底层的 `IAppleImageUtilsPlugin` 接口用于直接调用转换函数，以及 `UAppleImageUtilsBaseAsyncTaskBlueprintProxy` 类用于蓝图代理模式。

### 头文件引入

```cpp
#include "IAppleImageUtilsPlugin.h"
#include "AppleImageUtilsBlueprintProxy.h"
```

### 基本用法

以下代码展示了如何通过模块接口异步转换一张纹理为 JPEG 数据，并轮询检查任务状态。

```cpp
// 来源: Public/IAppleImageUtilsPlugin.h
// 确保模块可用
if (IAppleImageUtilsPlugin::IsAvailable())
{
    IAppleImageUtilsPlugin& Plugin = IAppleImageUtilsPlugin::Get();
    UTexture* MyTexture = /* 获取或创建一张纹理 */;

    // 启动异步转换任务
    TSharedPtr<FAppleImageUtilsConversionTaskBase, ESPMode::ThreadSafe> Task =
        Plugin.ConvertToJPEG(MyTexture, 90, true, true, 1.0f, ETextureRotationDirection::None);

    // 在后续的 Tick 或定期检查中轮询任务状态
    if (Task.IsValid() && Task->IsDone())
    {
        if (!Task->HadError())
        {
            TArray<uint8> JpegData = Task->GetData();
            // 使用 MoveTemp 避免拷贝: JpegData = MoveTemp(Task->GetData());
            // 保存 JpegData 或进行其他处理
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Image conversion failed: %s"), *Task->GetErrorReason());
        }
    }
}
```

### 进阶用法

以下示例展示了如何为 `UTexture2D` 实现 `IAppleImageInterface` 接口，以便将其传递给需要该接口的原生函数，并获取对应的 `CGImageRef`。

```cpp
// 来源: Public/AppleImageUtilsTypes.h, Public/IAppleImageUtilsPlugin.h
class UMyAppleTexture2D : public UTexture2D, public IAppleImageInterface
{
    GENERATED_BODY()
public:
    virtual EAppleTextureType GetTextureType() const override
    {
        return EAppleTextureType::Image;
    }
    // 实现其他虚函数以返回有效的 CIImage 等...
};

// 获取 CGImage (需要平台特定代码)
#if SUPPORTS_IMAGE_UTILS_1_0
UMyAppleTexture2D* MyAppleTex = /* ... */;
if (IAppleImageUtilsPlugin::IsAvailable())
{
    CGImageRef CGImage = IAppleImageUtilsPlugin::Get().UTexture2DToCGImage(MyAppleTex);
    // 使用 CGImage ... (注意: CGImageRef 的所有权和生命周期)
}
#endif
```

## Demo 示例

一个最小的可编译示例，展示如何创建一个异步图像转换代理并处理其结果。

```cpp
// MyImageConverter.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AppleImageUtilsBlueprintProxy.h"
#include "MyImageConverter.generated.h"

UCLASS()
class AMyImageConverter : public AActor
{
    GENERATED_BODY()

public:
    AMyImageConverter();

    UFUNCTION(BlueprintCallable)
    void StartConvertingTexture(UTexture* TextureToConvert);

private:
    UPROPERTY()
    UAppleImageUtilsBaseAsyncTaskBlueprintProxy* ConversionProxy;

    UFUNCTION()
    void OnConversionSuccess(const FAppleImageUtilsImageConversionResult& Result);

    UFUNCTION()
    void OnConversionFailure(const FAppleImageUtilsImageConversionResult& Result);
};
```

```cpp
// MyImageConverter.cpp
#include "MyImageConverter.h"

AMyImageConverter::AMyImageConverter()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyImageConverter::StartConvertingTexture(UTexture* TextureToConvert)
{
    if (!TextureToConvert) return;

    // 创建异步转换代理 (例如，转换为 PNG)
    ConversionProxy = UAppleImageUtilsBaseAsyncTaskBlueprintProxy::CreateProxyObjectForConvertToPNG(TextureToConvert, true, true);

    // 绑定委托
    if (ConversionProxy)
    {
        ConversionProxy->OnSuccess.AddDynamic(this, &AMyImageConverter::OnConversionSuccess);
        ConversionProxy->OnFailure.AddDynamic(this, &AMyImageConverter::OnConversionFailure);
    }
}

void AMyImageConverter::OnConversionSuccess(const FAppleImageUtilsImageConversionResult& Result)
{
    if (Result.Error.IsEmpty())
    {
        UE_LOG(LogTemp, Log, TEXT("Conversion succeeded! Data size: %d"), Result.ImageData.Num());
        // 处理 Result.ImageData
    }
    ConversionProxy = nullptr;
}

void AMyImageConverter::OnConversionFailure(const FAppleImageUtilsImageConversionResult& Result)
{
    UE_LOG(LogTemp, Error, TEXT("Conversion failed: %s"), *Result.Error);
    ConversionProxy = nullptr;
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。该插件的 `Build.cs` 仅依赖 UE 核心模块，其对苹果原生框架（CoreImage, CoreVideo, Metal）的依赖通过平台特定的编译条件（`#if PLATFORM_MAC || PLATFORM_IOS`）和链接标志在引擎构建系统中处理。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的UE_LOGF格式。 |
| 2026-04-13 | `b905d146` | Fix/Silence unreachable code warnings | 修复或消除代码中不可达的警告。 |
| 2026-04-10 | `e18acf19` | More unreachable code warning fixes | 继续修复不可达代码警告。 |
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复了不支持可移植工具链的模块。 |
| 2026-01-24 | `99277a85` | Fixed compile errors when building UnrealGame with portable toolchain | 修复使用可移植工具链构建 UnrealGame 时的编译错误。 |

### 维护评价

- **年龄**：该插件创建于 2019 年，已有约 7 年历史。
- **更新频率**：最近更新集中在 2026 年初，但均为**维护性修复**（修复编译警告、工具链兼容性），**没有功能性更新**。
- **维护状态**：处于**被动维护**状态。Epic 仍在确保其与新版引擎和工具链的兼容性，但未主动添加新功能。
- **实验性标记**：虽然 `.uplugin` 的 `Category` 是 `Experimental`，但 `IsBetaVersion` 为 `false`，且长期存在，表明它是一个稳定但非核心的功能。
- **建议**：如果你的项目**必须**使用苹果原生图像数据结构（CIImage等）或需要 HEIF 格式支持，这是一个必要且可用的插件。对于其他平台或通用图像压缩需求，应优先考虑引擎内置的 `IImageWrapper` 模块。由于其长期无重大更新且标记为实验性，在新项目中采用时应评估其未来支持计划。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AppleImageUtils)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AppleImageUtils/Tests)