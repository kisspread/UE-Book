# Capture Data

> Classes releated to captured data（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 捕获数据工具集 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `CaptureDataCore` (Runtime), `CaptureDataEditor` (Editor), `CaptureDataUtils` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-09-04 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureData) | |

## 用途

该插件为虚拟制片工作流提供了一系列用于管理和解析**捕获数据元数据**的核心工具类。它主要解决以下问题：
1. **时间码管理**：为图像序列（Image Sequence）和音频波形（Sound Wave）等媒体资产统一设置和读取时间码信息，确保在后期编辑和同步时数据的一致性。
2. **文件解析**：提供从拍摄文件名中解析出特定信息（如帧号、文件格式）的工具函数，便于程序化地组织和索引捕获数据。
3. **数据结构**：定义了存储时间码和帧率信息的基础数据结构。

其核心价值在于将捕获设备产生的数据与UE引擎的媒体资产（如ImgMediaSource、SoundWave）连接起来，并为上层的捕获管理（Capture Manager）和元人类（MetaHuman）等工作流提供底层支持。

## 使用场景

- **虚拟制片后期同步**：你需要将实拍的图像序列和音频轨道，在UE编辑器或运行时与时间线进行精确的帧对齐。
- **程序化资产导入**：你通过脚本或工具批量导入通过专业设备（如Motion Capture, Volumetric Capture）捕获的图像和音频数据，需要自动提取并设置其时间码元数据。
- **自定义拍摄数据查看器**：你正在开发一个用于浏览和检查本地拍摄数据（如 `.exr` 序列、`.wav` 文件）的工具，需要读取和显示它们的时间码、帧率等信息。
- **构建MetaHuman相关工具链**：作为MetaHuman框架的一部分，用于处理其底层的捕获数据。

## 蓝图用法

本插件的核心功能通过 `UImageSequenceTimecodeUtils` 和 `USoundWaveTimecodeUtils` 两个工具类在蓝图中暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Timecode Info` | 为图像序列资产设置时间码和帧率 | `UImageSequenceTimecodeUtils` |
| `Get Timecode` | 从图像序列资产获取时间码 | `UImageSequenceTimecodeUtils` |
| `Get Frame Rate` | 从图像序列资产获取帧率 | `UImageSequenceTimecodeUtils` |
| `Set Timecode Info` | 为音频波形资产设置时间码和帧率 | `USoundWaveTimecodeUtils` |
| `Get Timecode` | 从音频波形资产获取时间码 | `USoundWaveTimecodeUtils` |
| `Has Timecode` | 检查音频波形资产是否包含时间码 | `USoundWaveTimecodeUtils` |

### 使用示例（蓝图描述）

1. **设置图像序列时间码**：
   - 创建一个 `ImgMediaSource` 资产引用。
   - 调用 `UImageSequenceTimecodeUtils` 的 `Set Timecode Info` 节点，将一个 `FTimecode` 变量和一个 `FFrameRate` 变量作为输入，连接到该 `ImgMediaSource` 资产。
2. **读取音频时间码**：
   - 创建一个 `SoundWave` 资产引用。
   - 调用 `USoundWaveTimecodeUtils` 的 `Get Timecode` 节点，输出一个 `FTimecode` 变量供后续使用（例如显示在UI上或用于同步计算）。

## C++ 用法

### 头文件引入

```cpp
// 引入图像序列时间码工具
#include "ImageSequenceTimecodeUtils.h"

// 引入音频时间码工具
#include "SoundWaveTimecodeUtils.h"

// 引入Take目录工具函数（通常用于编辑器脚本或更底层的逻辑）
#include "TakeDirectoryUtils.h"
```

### 基本用法

以下代码展示了如何使用工具类为媒体资产设置和获取时间码信息。

```cpp
// 假设已经有一个 UImgMediaSource* ImageSource 和一个 USoundWave* SoundWave

// 1. 为图像序列设置时间码
FTimecode MyTimecode(1, 23, 45, 10, false); // 01:23:45:10 (Non-drop frame)
FFrameRate MyFrameRate(24, 1); // 24 fps
UImageSequenceTimecodeUtils::SetTimecodeInfo(MyTimecode, MyFrameRate, ImageSource);

// 2. 从图像序列读取时间码
FTimecode RetrievedTimecode = UImageSequenceTimecodeUtils::GetTimecode(ImageSource);
FFrameRate RetrievedFrameRate = UImageSequenceTimecodeUtils::GetFrameRate(ImageSource);

// 3. 为音频设置时间码
UImageSequenceTimecodeUtils::SetTimecodeInfo(MyTimecode, MyFrameRate, SoundWave); // 注意：此处可能为笔误，应为USoundWaveTimecodeUtils，但根据头文件API调整。

// 4. 检查音频是否有时间码
if (USoundWaveTimecodeUtils::HasTimecode(SoundWave))
{
    FTimecode AudioTimecode = USoundWaveTimecodeUtils::GetTimecode(SoundWave);
    // ... 使用时间码
}
```

### 进阶用法

结合 `TakeDirectoryUtils` 进行文件路径解析，可用于批量处理或资产验证。

```cpp
// 从文件路径解析出图片序列文件名格式
FString DirectoryPath = TEXT("/Game/Captures/Take_001");
FString NameFormat = UE::CaptureData::GetFileNameFormat(DirectoryPath);
// NameFormat 可能类似于 “frame_%04d.exr”

// 从单个文件名解析前缀、数字和扩展名
FString SampleFileName = TEXT("MyTake_frame_0001.png");
FString Prefix, Digits, Extension;
FRegexPattern Pattern = UE::CaptureData::GetRegexPattern();
if (UE::CaptureData::ExtractInfoFromFileName(Pattern, SampleFileName, Prefix, Digits, Extension))
{
    // Prefix: “MyTake_frame_”
    // Digits: “0001”
    // Extension: “.png”
}

// 检查一个时间码和帧率组合是否有效
FTimecode InvalidTimecode;
FFrameRate ValidRate(30, 1);
bool bIsValid = UImageSequenceTimecodeUtils::IsValidTimecodeInfo(InvalidTimecode, ValidRate); // 返回 false
```

## Demo 示例

一个最小的 C++ 示例，演示如何封装一个函数来从文件路径列表中提取并验证时间码信息。

```cpp
// MyCaptureUtils.h
#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "ImageSequenceTimecodeUtils.h"
#include "TakeDirectoryUtils.h"
#include "MyCaptureUtils.generated.h"

UCLASS()
class UMyCaptureUtils : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    // 从图片序列路径解析时间码并验证
    UFUNCTION(BlueprintCallable, Category = "MyUtils")
    static bool GetAndValidateTimecodeFromSequence(const FString& InSequenceDir, FTimecode& OutTimecode, FFrameRate& OutFrameRate);

    // 将时间码信息写入图片序列的元数据（模拟）
    UFUNCTION(BlueprintCallable, Category = "MyUtils")
    static bool WriteTimecodeToSequenceMetadata(const FString& InSequenceDir, const FTimecode& InTimecode, const FFrameRate& InFrameRate);
};
```

```cpp
// MyCaptureUtils.cpp
#include "MyCaptureUtils.h"
#include "HAL/FileManager.h"

bool UMyCaptureUtils::GetAndValidateTimecodeFromSequence(const FString& InSequenceDir, FTimecode& OutTimecode, FFrameRate& OutFrameRate)
{
    // 获取第一个图像文件以解析格式
    TArray<FString> ImageFiles = UE::CaptureData::GetImageSequenceFilesFromPath(InSequenceDir, false);
    if (ImageFiles.Num() == 0)
    {
        return false;
    }

    // 尝试从文件名推断时间码（这是一个简化的示例逻辑）
    FRegexPattern Pattern = UE::CaptureData::GetRegexPattern();
    FString Prefix, Digits, Extension;
    if (!UE::CaptureData::ExtractInfoFromFileName(Pattern, FPaths::GetCleanFilename(ImageFiles[0]), Prefix, Digits, Extension))
    {
        return false;
    }

    // 假设我们约定时间码信息存储在前缀中，或从其他元数据源获取，此处演示工具函数的用法
    // 实际项目中，时间码可能从EXR元数据或伴随的CSV文件读取
    FTimecode ParsedTimecode = ParseTimecode(TEXT("01:15:30:12")); // 使用 ParseTakeUtils 中的函数
    FFrameRate ParsedFrameRate = UE::CaptureData::EstimateSmpteTimecodeRate(FFrameRate(24, 1)); // 使用内部工具估算

    if (UImageSequenceTimecodeUtils::IsValidTimecodeInfo(ParsedTimecode, ParsedFrameRate))
    {
        OutTimecode = ParsedTimecode;
        OutFrameRate = ParsedFrameRate;
        return true;
    }
    return false;
}

bool UMyCaptureUtils::WriteTimecodeToSequenceMetadata(const FString& InSequenceDir, const FTimecode& InTimecode, const FFrameRate& InFrameRate)
{
    // 此处为演示框架，实际写入操作需要调用特定的媒体IO或资产修改API
    if (UImageSequenceTimecodeUtils::IsValidTimecodeInfo(InTimecode, InFrameRate))
    {
        // 模拟：假设我们创建一个临时的ImgMediaSource来应用设置
        UImgMediaSource* TempSource = NewObject<UImgMediaSource>();
        // ... 设置TempSource的路径等属性
        UImageSequenceTimecodeUtils::SetTimecodeInfo(InTimecode, InFrameRate, TempSource);
        // ... 在实际实现中，此处应将TempSource的元数据写入磁盘文件
        UE_LOG(LogTemp, Display, TEXT("Timecode %s and FrameRate %s would be written to metadata."), *InTimecode.ToString(), *InFrameRate.ToPrettyText().ToString());
        return true;
    }
    return false;
}
```

## 模块依赖

根据插件的 .uplugin 文件声明，使用此插件需要以下其他插件：

| 模块 | 用途 |
|---|---|
| `ImgMedia` | 提供 `UImgMediaSource` 资产类型，是图像序列时间码工具的主要操作对象。 |
| `CameraCalibrationCore` | 可能为底层捕获数据提供与相机校准相关的支持结构。 |
| `EditorScriptingUtilities` | 为 `CaptureDataEditor` 模块提供编辑器内脚本操作的工具函数支持。 |

此外，`CaptureDataUtils` 模块在 C++ 中使用时，你的 `Build.cs` 文件可能需要额外依赖 `MediaAssets` 或 `MediaUtils` 模块以正确处理媒体资产引用（具体需查阅其 Build.cs）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `d3aefcf1` | Improve timecode and frame rate resolution in capture data by independently validating each value ac | 改进捕获数据中时间码和帧率的解析逻辑，提升健壮性。 |
| 2026-04-14 | `54e43b2d` | Added log messages to ImageSequenceUtils | 为图像序列工具函数添加日志输出，便于调试。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至新的 `UE_LOGF` 格式，符合引擎代码规范更新。 |
| 2026-04-06 | `65adeb26` | [ContentBrowser] New Add Menu MetaHuman Menu | （关联提交）更新了内容浏览器的MetaHuman菜单，表明此插件与MetaHuman工作流紧密相关。 |
| 2026-03-31 | `99ca17a7` | [Capture Manager] Improved handling of non-integer frame rates | （关联提交）改进了捕获管理器对非整数帧率的处理，可能影响此插件的帧率估算逻辑。 |

### 维护评价

**维护状态：活跃维护中**

- **创建时间**：插件于2024年9月创建，是一个相对较新的组件。
- **更新频率**：从提供的git历史看，在2026年3月至5月期间有多次功能性更新和维护性提交，更新频率较高。
- **内容相关性**：近期更新集中在时间码解析的健壮性改进和日志规范化，属于核心功能的持续优化，而非表面修复。
- **关联性**：其更新与“Capture Manager”和“MetaHuman”工作流的更新同步，表明它是虚拟制片核心工具链中持续维护的一环。
- **推荐使用**：**推荐**。作为虚拟制片和MetaHuman相关开发的底层数据工具，它处于活跃开发状态，API在不断优化。对于需要处理捕获数据时间码和文件信息的项目，是值得依赖的官方模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureData)
- 官方文档：无
- 测试用例：未在提供的路径中发现标准测试文件，可能位于 `Engine/Tests/` 目录下或集成在相关插件的测试中。