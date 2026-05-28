# Apple Image Utils

> Utilities that operate on CIImage, CVPixelBuffer, IOSurface, etc.

| 属性 | 值 |
|---|---|
| 中文名 | Apple图像工具 |
| 分类 | Experimental |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AppleImageUtils` (Runtime), `AppleImageUtilsBlueprintSupport` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-06-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AppleImageUtils) | |

## 用途

该插件提供了一套专门为 Apple 平台（iOS, macOS）优化的图像处理工具，其核心是操作平台原生的图像对象（如 `CIImage`, `CVPixelBuffer`, `IOSurface`）。它主要解决在 Unreal Engine 与 Apple 平台原生图像处理框架（如 Core Image, Core Video）之间进行高效数据转换和处理的问题。通过提供异步的蓝图节点，它允许开发者在不阻塞游戏线程的情况下，对纹理进行格式转换（如转为 JPEG、PNG、TIFF、HEIF），这对于移动应用或 macOS 应用中优化图片大小、性能以及与系统原生应用交互至关重要。

## 使用场景

- 你在开发一个 iOS 或 macOS 应用，需要将 UE 渲染的纹理导出为常见的图片格式（JPEG、PNG 等）用于分享、保存到相册。
- 你需要将游戏内的截图或画面，在后台线程异步转换为压缩率更高或平台支持更好的格式（如 HEIF），以减少内存占用和存储空间。
- 你正在开发一个工具，需要与 Apple 的原生图像处理管道（如使用 Core Image 进行滤镜处理）对接，需要频繁地在 UE 纹理和 `CIImage` 等对象间转换。

## 蓝图用法

该插件主要通过专门的蓝图异步节点进行工作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Convert To JPEG` | 异步将纹理转换为 JPEG 格式 | `UK2Node_ConvertToJPEG` |
| `Convert To PNG` | 异步将纹理转换为 PNG 格式 | `UK2Node_ConvertToPNG` |
| `Convert To TIFF` | 异步将纹理转换为 TIFF 格式 | `UK2Node_ConvertToTIFF` |
| `Convert To HEIF` | 异步将纹理转换为 HEIF 格式 | `UK2Node_ConvertToHEIF` |

### 使用示例（蓝图描述）

1.  在蓝图中，右键搜索并添加 “Convert To PNG” 节点。
2.  将输入的 `Source Texture`（纹理对象）连接到该节点的输入引脚。
3.  设置 `Quality` (0-100) 和 `bFlatten` (是否展平透明通道) 等参数。
4.  将节点的 `On Success` 和 `On Failure` 执行引脚连接到后续逻辑。成功时，可以通过 `Out Image Data` 引脚获取转换后的二进制图片数据。

## C++ 用法

该插件主要提供蓝图支持。对于高级用户，可以通过 C++ 调用底层平台功能，但插件本身主要暴露的是蓝图节点。

### 头文件引入

```cpp
// 主要用于蓝图扩展功能
#include "AppleImageUtilsBlueprintSupport.h"
```

### 基本用法

从插件提供的蓝图节点类可以推断，其主要用途是作为蓝图异步任务的 K2 节点。在 C++ 层面，通常直接使用 UE 的纹理处理接口结合平台原生 API。以下是一个概念性示例，展示了如何手动调用类似功能（非直接调用插件类）：

```cpp
// 假设需要将 UTexture2D 导出为 JPEG
// 这需要自己实现与 Apple 框架的桥接，插件的蓝图节点封装了这些复杂性
#include "IImageWrapperModule.h"
#include "IImageWrapper.h"
#include "Modules/ModuleManager.h"

void ConvertTextureToJPEG(UTexture2D* Texture)
{
    if (!Texture) return;

    IImageWrapperModule& ImageWrapperModule = FModuleManager::LoadModuleChecked<IImageWrapperModule>(FName("ImageWrapper"));
    TSharedPtr<IImageWrapper> ImageWrapper = ImageWrapperModule.CreateImageWrapper(EImageFormat::JPEG);

    FTexture2DMipMap& Mip = Texture->GetPlatformData()->Mips[0];
    void* Data = Mip.BulkData.Lock(LOCK_READ_WRITE);
    if (ImageWrapper->SetRaw(Data, Mip.BulkData.GetBulkDataSize(), Texture->GetSizeX(), Texture->GetSizeY(), ERGBFormat::BGRA, 8))
    {
        const TArray64<uint8>& CompressedData = ImageWrapper->GetCompressed(100);
        // 处理 CompressedData，例如保存到文件或转换为 NSData
    }
    Mip.BulkData.Unlock();
}
// 注意：此示例使用通用图像包装器，插件的核心价值在于其使用 Apple 原生 API 可能更高效，并提供异步节点。
```

### 进阶用法

插件的核心价值在于其蓝图异步节点。在 C++ 中创建自定义的类似异步节点，需要继承 `UK2Node_BaseAsyncTask` 并绑定到代理类，这与 `UK2Node_ConvertToPNG` 等类的实现方式一致。由于插件主要面向蓝图，C++ 高级用法通常涉及扩展或替换其中的平台特定实现逻辑。

## Demo 示例

以下示例展示了如何在蓝图中使用该插件的核心功能。

```cpp
// 此示例为蓝图使用步骤的文字描述，非代码。代码示例见上方 C++ 章节。
// 1. 确保 AppleImageUtils 插件已启用。
// 2. 在任意蓝图（如 Actor 蓝图）中，创建以下逻辑：
//    - 一个 UTexture2D 变量（例如，通过 “Make Literal Texture2D” 或从场景中获取）。
//    - 一个 “Convert To PNG” 节点。
//    - 一个 “Save to File” 节点或自定义的处理逻辑。
// 3. 连接：
//    Texture 变量 → Convert To PNG 的 “Source Texture”。
//    Convert To PNG 的 “On Success” → Save to File 的执行。
//    Convert To PNG 的 “Out Image Data” → Save to File 的 “File Data”。
// 4. 运行游戏或工具，触发此蓝图逻辑，即可异步将纹理转换为 PNG 并保存。
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。该插件的构建依赖主要是标准的引擎模块，用于提供基础支持和蓝图节点框架。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移到新的日志格式化宏。 |
| 2026-04-13 | `b905d146` | Fix/Silence unreachable code warnings | 修复或消除代码中无法到达的警告。 |
| 2026-04-10 | `e18acf19` | More unreachable code warning fixes | 进一步清理无法到达的代码警告。 |
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复了不支持可移植工具链的模块问题。 |
| 2026-01-24 | `99277a85` | Fixed compile errors when building UnrealGame with portable toolchain | 修复使用可移植工具链构建 UnrealGame 时的编译错误。 |

### 维护评价

该插件自 2019 年创建以来，已有约 6 年历史。从近期提交记录看，虽然在 2026 年初有多次更新，但这些更新主要集中在代码质量维护（修复警告、迁移日志宏）和构建系统兼容性修复上，**没有发现新增功能性特性**。最后一次涉及功能的改动时间未知，但从提交信息看，可能很久没有新功能加入了。

插件被标记为 `Experimental` 且 `SupportedPrograms` 仅限 `LiveLinkHub`，表明其仍处于实验阶段，应用场景有限。尽管代码仍在维护以跟上引擎版本升级，但其活跃开发期可能已过。

**综合评价**：这是一个处于维护状态但不再活跃开发的实验性插件。它提供了针对 Apple 平台特定的图像转换蓝图节点，如果你的项目严格依赖这些异步转换节点，可以使用。但由于其“实验性”标签和有限的官方支持范围，对于新项目，建议评估其必要性，或考虑使用更通用、文档更完善的图像处理方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AppleImageUtils)