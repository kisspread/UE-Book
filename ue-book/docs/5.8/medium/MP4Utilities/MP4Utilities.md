# MP4 (ISO/IEC 14496-12) utilities

> Provides helpers to work with mp4 files

| 属性 | 值 |
|---|---|
| 分类 | Media |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MP4Utilities` (Runtime), `MP4Boxes` (Runtime), `MP4Muxer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-02-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MP4Utilities) | |

## 用途

MP4Utilities 插件提供了一套底层的 C++ 工具库，用于直接操作符合 ISO/IEC 14496-12 (MP4 容器格式) 标准的文件。它并非一个媒体播放器或解码器，而是专注于 MP4 文件结构的读取、解析和封装。

**核心功能包括：**
1.  **MP4 文件读取**：提供抽象接口 (`IMP4DataReaderBase`) 和具体实现 (`FMP4FileDataReader`, `FMP4BufferDataReader`)，用于从文件路径或内存缓冲区中按偏移量读取原始字节。
2.  **MP4 Box 结构解析**：定义了 `FMP4BoxInfo` 结构来表示 MP4 文件中的基本单元（Box/Atom），并提供工具函数（如 `MakeBoxAtom`, `GetPrintableBoxAtom`）来处理四字符码（4CC）和字节序转换。
3.  **元数据提取**：通过 `FMP4MetadataParser` 类，专门解析嵌入在 MP4 文件中的元数据，目前支持 Apple iTunes 风格的元数据结构，并能将其转换为 JSON 或 `IMediaMetadataItem` 格式。
4.  **MP4 文件封装**：`MP4Muxer` 模块（虽然当前文档主要聚焦于 `MP4Utilities` 模块）暗示了该插件具备创建或修改 MP4 文件的能力。

**为什么存在？** 该插件为 Unreal Engine 内部或其他需要精细控制 MP4 文件结构的插件（如媒体录制、视频编辑工具、自定义媒体源）提供了基础构建块，避免了每个功能都从头实现 MP4 解析逻辑。

## 使用场景

-   你需要开发一个视频分析工具，需要读取 MP4 文件的元数据（如时长、编码信息、自定义标签）。
-   你在实现一个自定义的媒体录制器，需要将原始视频/音频流封装成 MP4 文件。
-   你需要检查或修复一个损坏的 MP4 文件的结构。
-   你的插件需要从内存中的 MP4 数据流（例如网络下载）中提取信息，而不仅仅是从磁盘文件。

## 蓝图用法

根据提供的头文件分析，`MP4Utilities` 模块主要提供的是 C++ 接口，未发现标记为 `BlueprintCallable` 或 `BlueprintReadWrite` 的函数。其功能主要面向 C++ 开发者。

## C++ 用法

### 头文件引入

```cpp
#include "MP4Utilities.h"
#include "MP4DataReader.h"
#include "MP4Metadata.h"
```

### 基本用法：读取 MP4 文件并解析元数据

以下示例展示了如何使用 `FMP4FileDataReader` 读取文件，并结合 `FMP4MetadataParser` 提取元数据。

```cpp
// 来源: 基于 Public/MP4DataReader.h 和 Public/MP4Metadata.h 的接口设计
#include "MP4Utilities.h"
#include "MP4DataReader.h"
#include "MP4Metadata.h"

void ReadAndParseMP4Metadata(const FString& FilePath)
{
    // 1. 创建文件数据读取器
    TSharedPtr<MP4Utilities::FMP4FileDataReader, ESPMode::ThreadSafe> Reader = MP4Utilities::FMP4FileDataReader::Create();
    if (!Reader->Open(FilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open MP4 file: %s"), *FilePath);
        return;
    }

    // 2. 读取文件头部数据（示例：读取前 1KB 用于初步解析）
    TArray<uint8> HeaderData;
    HeaderData.SetNumUninitialized(1024);
    int64 BytesRead = Reader->ReadData(HeaderData.GetData(), 1024, 0, MP4Utilities::IMP4DataReaderBase::FCancellationCheckDelegate());
    if (BytesRead <= 0)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to read MP4 file header."));
        return;
    }

    // 3. 使用 MP4Utilities 中的工具函数解析 Box 结构 (此处仅为示意，实际解析逻辑更复杂)
    // 通常需要遍历文件，根据 Box 的 Size 和 Type 字段递归解析。
    // 例如，检查第一个 Box 的类型：
    if (BytesRead >= 8)
    {
        uint32 FirstBoxSize = MP4Utilities::GetFromBigEndian(*reinterpret_cast<uint32*>(HeaderData.GetData()));
        uint32 FirstBoxType = MP4Utilities::GetFromBigEndian(*reinterpret_cast<uint32*>(HeaderData.GetData() + 4));
        FString BoxTypeStr = MP4Utilities::GetPrintableBoxAtom(FirstBoxType);
        UE_LOG(LogTemp, Log, TEXT("First Box Type: %s, Size: %d"), *BoxTypeStr, FirstBoxSize);
    }

    // 4. 解析元数据 (需要完整的 Box 列表，此处仅为接口调用示例)
    MP4Utilities::FMP4MetadataParser MetadataParser;
    // 假设我们已经通过某种方式得到了文件的 Box 信息列表 `Boxes`
    // TArray<MP4Utilities::FMP4BoxInfo> Boxes = ...;
    // auto Result = MetadataParser.Parse(handler, reserved, Boxes);
    // if (Result == MP4Utilities::FMP4MetadataParser::EResult::Success)
    // {
    //     FString JsonMetadata = MetadataParser.GetAsJSON();
    //     UE_LOG(LogTemp, Log, TEXT("MP4 Metadata JSON:\n%s"), *JsonMetadata);
    // }
}
```

### 进阶用法：从内存缓冲区读取

```cpp
// 来源: 基于 Public/MP4DataReader.h 中 FMP4BufferDataReader 的接口
void ParseMP4FromMemory(const uint8* DataPtr, int64 DataSize)
{
    // 创建内存数据读取器
    TConstArrayView<const uint8> DataView(DataPtr, DataSize);
    TSharedPtr<MP4Utilities::FMP4BufferDataReader, ESPMode::ThreadSafe> BufferReader = MP4Utilities::FMP4BufferDataReader::Create(DataView);

    // 后续操作与文件读取器类似，使用 ReadData 方法按偏移量读取
    // ...
}
```

## Demo 示例

一个最小化的示例，演示如何打开一个 MP4 文件并打印其总大小。

**MP4DemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MP4DemoActor.generated.h"

UCLASS()
class AMP4DemoActor : public AActor
{
    GENERATED_BODY()

public:
    AMP4DemoActor();

    UPROPERTY(EditAnywhere, Category = "MP4 Demo")
    FString MP4FilePath;

    UFUNCTION(BlueprintCallable, CallInEditor, Category = "MP4 Demo")
    void AnalyzeMP4File();

private:
    TSharedPtr<MP4Utilities::FMP4FileDataReader, ESPMode::ThreadSafe> MP4Reader;
};
```

**MP4DemoActor.cpp**
```cpp
#include "MP4DemoActor.h"
#include "MP4DataReader.h"
#include "MP4Utilities.h"

AMP4DemoActor::AMP4DemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMP4DemoActor::AnalyzeMP4File()
{
    if (MP4FilePath.IsEmpty())
    {
        UE_LOG(LogTemp, Warning, TEXT("MP4 File Path is not set."));
        return;
    }

    // 创建并打开读取器
    MP4Reader = MP4Utilities::FMP4FileDataReader::Create();
    if (!MP4Reader->Open(MP4FilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open file: %s"), *MP4FilePath);
        return;
    }

    // 获取文件大小
    int64 FileSize = MP4Reader->GetTotalFileSize();
    if (FileSize > 0)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully opened MP4 file: %s"), *MP4FilePath);
        UE_LOG(LogTemp, Log, TEXT("File Size: %lld bytes"), FileSize);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Could not determine file size. File may be unbounded or still loading."));
    }

    // 检查是否到达文件末尾
    if (MP4Reader->HasReachedEOF())
    {
        UE_LOG(LogTemp, Log, TEXT("Reader has reached the end of the file."));
    }

    // 检查错误
    FString LastError = MP4Reader->GetLastError();
    if (!LastError.IsEmpty())
    {
        UE_LOG(LogTemp, Error, TEXT("Reader Error: %s"), *LastError);
    }
}
```

## 模块依赖

从各模块的 `Build.cs` 文件分析，使用 `MP4Utilities` 模块时，你的项目模块需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `MP4Boxes` | 提供 MP4 Box 结构的基础定义和解析工具，是 `MP4Utilities` 的核心依赖。 |
| `MediaUtils` | 提供媒体相关的通用工具和类型，如 `IMediaMetadataItem`。 |

**注意**：`MP4Muxer` 模块依赖于 `MP4Utilities` 和 `MediaUtils`，如果你需要创建 MP4 文件，则需要额外依赖 `MP4Muxer`。

## 维护状态

### 近期更新

- 2026-04-23 `0cd64869` ElectraDecoders: Fixed an issue where mp4a audio is wrapped inside a wave box in a QuickTime file. T
- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-03-04 `3fbcc0a3` Protron: Await one sample from each selected track (video and audio, if enabled) to be ready before 
- 2026-03-03 `6ea9f319` MP4Utilities: fixed handling of encrypted tracks that have no senc box; only reading well-known root
- 2026-02-25 `ecaf73c3` Electra: Added a new mp4 handler path to the DASH and HLS segment reader; added common encryption ha

### 维护评价

-   **创建时间**：2026-02-25（非常新）。
-   **维护状态**：🆕 **新发布/积极开发中**。作为 Epic Games 官方维护的插件，且创建时间很近，预计会得到持续的支持和更新。
-   **已知限制**：目前元数据解析仅支持 Apple iTunes 风格的结构。蓝图支持有限，主要面向 C++ 开发者。
-   **推荐使用**：✅ **推荐**。如果你需要在 Unreal Engine 中进行底层的 MP4 文件操作，这是一个官方提供的、设计良好的工具库。由于它默认未启用 (`EnabledByDefault: false`)，你需要在项目的 `.uproject` 文件或插件设置中手动启用它。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MP4Utilities)
-   [官方文档]() (暂无)
-   [测试用例]() (可能位于 `Engine/Tests/` 目录下，具体路径需进一步查找)